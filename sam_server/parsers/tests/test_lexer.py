from django.test import TestCase

from collections import OrderedDict
from .. import lexer


class SampleLexer(lexer.Lexer):
    """
    The TestLexer follows the syntax of the selector
    (as defined in json_utils.field_selector
    """
    TOKENS = OrderedDict([
        ('R_PARENS', lexer.LiteralToken(')')),
        ('L_PARENS', lexer.LiteralToken('(')),
        ('PERIOD', lexer.LiteralToken('.')),
        ('COMMA', lexer.LiteralToken(',')),
        ('NAME', lexer.RegexToken('[a-zA-Z0-9_]+')),
    ])

    def __init__(self):
        super(SampleLexer, self).__init__(self.TOKENS, skip_whitespace=True)


class LexerTest(TestCase):
    def test_should_lex_tokens(self):
        test_lexer = SampleLexer()
        result = list(test_lexer.run('hello, world(can.you, you)'))

        self.assertEqual(result, [
            lexer.Match('NAME', 0, 'hello'),
            lexer.Match('COMMA', 5, ','),
            lexer.Match('NAME', 7, 'world'),
            lexer.Match('L_PARENS', 12, '('),
            lexer.Match('NAME', 13, 'can'),
            lexer.Match('PERIOD', 16, '.'),
            lexer.Match('NAME', 17, 'you'),
            lexer.Match('COMMA', 20, ','),
            lexer.Match('NAME', 22, 'you'),
            lexer.Match('R_PARENS', 25, ')'),
        ])


