from .exceptions import StateError


class Parser(object):
    """
    An implementation of an LL(1) parser
    """
    def __init__(self, lexer):
        self.lexer = lexer
        self._state = None

    def run(self, input):
        self._state = _ParserState(self.lexer, input)
        try:
            return self.begin()
        finally:
            self._state = None

    def begin(self):
        """
        Parse the top level statement/expression. Called automatically by
        `run`. It is an error if not implemented
        """
        raise NotImplementedError('Parser.begin')

    def move_next(self, lookahead=False):
        if self._state is None:
            raise StateError('No current parser state')
        return self._state.move_next(lookahead=lookahead)

    @property
    def position(self):
        if self._state is None:
            raise StateError('No current parser state')
        return self._state.position


class _ParserState(object):
    def __init__(self, lexer, input):
        self.iter_tokens = lexer.run(input)
        self.lookahead_token = None
        self.position = 0

    def _peek_next(self):
        if self.lookahead_token is None:
            try:
                self.lookahead_token = next(self.iter_tokens)
            except StopIteration:
                pass
        return self.lookahead_token

    def move_next(self, lookahead=False):
        if lookahead:
            return self._peek_next()
        if self.lookahead_token is not None:
            token = self.lookahead_token
            self.lookahead_token = None
        else:
            try:
                token = next(self.iter_tokens)
            except StopIteration:
                return None
        self.position = token.position
        return token
