import re
from collections import OrderedDict

from .exceptions import ParseError


class Token(object):
    """
    The base type for lexer tokens
    """
    def match(self, input, position):
        """
        matches the token against remaining. If the token matches,
        return the position at the end of the token.
        Otherwise return None
        """
        raise NotImplementedError('Token.match')


class LiteralToken(object):
    def __init__(self, *strings):
        self.strings = strings

    def match(self, input, position):
        for string in self.strings:
            if input.startswith(string, position):
                return position + len(string)


class RegexToken(object):
    def __init__(self, pattern, flags=0):
        self.pattern = re.compile(pattern, flags=flags)

    def match(self, input, position):
        m = self.pattern.match(input, position)
        if m is not None:
            return m.end()


class Match(object):
    def __init__(self, name, position, string):
        self.name = name
        self.position = position
        self.string = string

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Match):
            return False
        return (self.name == other.name and self.position == other.position)

    def __str__(self):
        return ('<Match {0} at {1}: {2}>'
                .format(self.name, self.position, self.string))

    def __repr__(self):
        return str(self)


class Lexer(object):
    WSPACE = RegexToken(r'\s*')

    def __init__(self, tokens, skip_whitespace=True):
        self.skip_whitespace = skip_whitespace
        self.tokens = OrderedDict(tokens)

    def _leading_ws(self, input, position):
        if not self.skip_whitespace:
            return 0
        return self.WSPACE.match(input, position)

    def run(self, input):
        position = 0
        while position < len(input):
            position = self._leading_ws(input, position)
            if position >= len(input):
                break
            match = None
            for k, v in self.tokens.items():
                new_pos = v.match(input, position)
                if new_pos is not None:
                    match = Match(k, position, input[position:new_pos])
                    position = new_pos
                    break
            if match is None:
                char = input[position]
                raise ParseError(position,
                                 'Unexpected char in stream ({0})'.format(char))
            yield match
