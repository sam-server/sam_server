"""
Facilities for delivering partial responses to json requests.

In the query portion of the url, a 'fields' parameter can be
specified which delineates the attributes on an object to fetch
with the request.

There are two types of selectors:
- A field selector selects a single key out of a map and returns
  a map containing the field and it's value

- A field list selector selects multiple keys out of a map and returns
  a map containg all the selected fields and values.

When applied to a list of maps, the selector will be applied in
turn to each of the maps in the list.

The syntax of the field specification is as follows:

field := ['a-zA-Z0-9_']

field_list := (field ',')+

p_field_list := '(' field_list ')'

field_specifier = field (('.' field) | p_field_list)?

selector := field | field_list
"""
from parsers import lexer, parser


class Selector(object):

    @classmethod
    def parse(cls, fields):
        """
        Parses a selector from the given `fields` specifier.
        """
        parser = SelectorParser()
        return parser.run(fields)

    def select(self, json):
        raise NotImplementedError('Select')


class FieldSelector(Selector):
    """
    A FieldSelector selects a single field from a json resource.
    If applied to a dict, returns the value associated with the field in the dict
    If applied to a list, selects the field from each resource in the list.
    """
    def __init__(self, field, subselector=None):
        self.subselector = subselector
        self.field = field

    def select(self, json):
        if isinstance(json, dict):
            return self.select_resource(json)
        if hasattr(json, '__iter__'):
            return self.select_resource_list(json)

    def select_resource(self, resource):
        try:
            selected = resource[self.field]
        except KeyError:
            return {self.field: None}
        if self.subselector is not None:
            selected = self.subselector.select(selected)
        return {self.field: selected}

    def select_resource_list(self, resource_list):
        return list(map(self.select_resource, resource_list))

    def __eq__(self, other):
        return (isinstance(other, FieldSelector) and
                other.field == self.field and
                other.subselector == self.subselector)

    def __hash__(self):
        h = hash(self.field)
        h = 37 * h + hash(self.subselector)
        return h

    def __repr__(self):
        return 'FieldSelector: {0}'.format(str(self))

    def __str__(self):
        s = self.field
        if isinstance(self.subselector, FieldSelector):
            s += ".{0}".format(self.subselector)
        elif isinstance(self.subselector, FieldListSelector):
            s += "({0})".format(self.subselector)
        return s


class FieldListSelector(Selector):
    """
    A FieldList selector specifies a selection of fields from
    """
    def __init__(self, fields=None):
        self.fields = list(fields or [])

    def select(self, json):
        if isinstance(json, dict):
            return self.select_resource(json)
        elif isinstance(json, list):
            return self.select_list(json)
        else:
            raise ValueError('Invalid json ({0})'.format(json))

    def select_resource(self, resource):
        selected = dict()
        for field in self.fields:
            field_selection = field.select(resource)
            selected.update(field_selection)
        return selected

    def select_list(self, resource_list):
        return list(map(self.select_resource, resource_list))

    def __eq__(self, other):
        return (isinstance(other, FieldListSelector) and
                other.fields == self.fields)

    def __hash__(self):
        h = 0
        for field in self.fields:
            h = 41 * h + hash(field)
        return h

    def __repr__(self):
        return 'FieldListSelector: {0}'.format(str(self))

    def __str__(self):
        return ', '.join(map(str, self.fields))


class SelectorParser(parser.Parser):
    LEXER_TOKENS = [
        ('L_PARENS', lexer.LiteralToken('(')),
        ('R_PARENS', lexer.LiteralToken(')')),
        ('COMMA', lexer.LiteralToken(',')),
        ('PERIOD', lexer.LiteralToken('.')),
        ('NAME', lexer.RegexToken(r'[a-zA-Z0-9_]+')),
    ]

    def __init__(self):
        lex = lexer.Lexer(self.LEXER_TOKENS)
        super(SelectorParser, self).__init__(lex)

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
        else:
            raise ParseError(self.position,
                             'Unexpected token in stream ({0})'.format(token))
        return FieldSelector(field_name, subselector)

    def parse_field_list(self):
        field_list = []
        token = self.move_next(lookahead=True)

        while token and token.name != 'R_PARENS':
            if token.name == 'NAME':
                field_list.append(self.parse_field())
            else:
                raise ParseError('Expected a field selector')
            token = self.move_next(lookahead=True)
            if token is None or token.name == 'R_PARENS':
                pass
            elif token.name == 'COMMA':
                self.move_next()
            else:
                raise ParseError(self.position,
                                 'Expected comma or end of selector list')
            token = self.move_next(lookahead=True)
        return FieldListSelector(field_list)

    def parse_parens_field_list(self):
        """ A parenthesised field list """
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


