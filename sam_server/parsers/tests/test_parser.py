
from django.test import TestCase

from ..parser import Parser
from ..exceptions import ParseError
from .test_lexer import SampleLexer

from json_utils.field_selector import (FieldSelector, FieldListSelector)


class SampleParser(Parser):
    """
    A parser which handles the same language that is parsed
    by json_utils.field_selector
    """
    def __init__(self):
        super(SampleParser, self).__init__(SampleLexer())

    def begin(self):
        return self.parse_field_list()

    def parse_field(self):
        token = self.move_next()
        if not token or token.name != 'NAME':
            raise ParseError(self.position, 'Expected a field name')
        field_name = token.string
        token = self.move_next(lookahead=True)
        if not token or token.name in {'R_PARENS', 'COMMA'}:
            return FieldSelector(field_name)
        elif token.name == 'PERIOD':
            self.move_next()
            subselector = self.parse_field()
        elif token.name == 'L_PARENS':
            subselector = self.parse_parens_field_list()
        return FieldSelector(field_name, subselector)

    def parse_field_list(self):
        field_list = []
        token = self.move_next(lookahead=True)
        while token and token.name != 'R_PARENS':
            if token.name == 'NAME':
                field_list.append(self.parse_field())
            else:
                raise ParseError(self.position,
                                 'Expected a field selector')
            token = self.move_next(lookahead=True)
            if token is None or token.name == 'R_PARENS':
                pass
            elif token.name == 'COMMA':
                self.move_next()
            else:
                raise ParseError(self.position,
                                 'Expected a comma or the end of the selector list')
            token = self.move_next(lookahead=True)
        return FieldListSelector(field_list)

    def parse_parens_field_list(self):
        """
        Parses a field list, surrounded by parens
        """
        token = self.move_next()
        if token is None or token.name != 'L_PARENS':
            raise ParseError(self.position,
                             'Expected start of selector list')
        field_list = self.parse_field_list()
        token = self.move_next()
        if token is None or token.name != 'R_PARENS':
            raise ParseError(self.position,
                             'Expected end of selector list')
        return field_list


class ParserTest(TestCase):
    def test_parse_simple_fieldlist(self):
        parser = SampleParser()
        input = 'arg1.arg2, arg3(arg4, arg5)'

        result = FieldListSelector([
            FieldSelector('arg1', subselector=FieldSelector('arg2')),
            FieldSelector('arg3', subselector=FieldListSelector([
                FieldSelector('arg4'),
                FieldSelector('arg5'),
            ])),
        ])
        self.assertEqual(parser.run(input), result)





























