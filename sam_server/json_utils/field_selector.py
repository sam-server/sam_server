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
import json
import re

from django.http import JsonResponse

FIELD_NAME = re.compile(r'[a-zA-Z0-9_]+')
WHITESPACE = re.compile(r'\s*')


def partial_response(request, resource):
    """
    Given the 'fields' specified in the query parameters of a
    request, returns the selected resource as a partial response
    """
    fields = request.GET.get('fields', None)
    if fields is not None:
        selector = Selector.parse(fields)
        resource = selector.select(resource)
    return JsonResponse(json.dumps(resource))


def _skip_ws(fields):
    match = WHITESPACE.match(fields)
    return fields[match.end():]


def _parse_field_name(fields):
    fields = _skip_ws(fields)
    match = FIELD_NAME.match(fields)
    if match is not None:
        return fields[:match.end()], fields[match.end():]
    return None, fields


def _match_start(remaining, start, consume_token=True):
    """
    Match the string 'start' against the start of remaining, ignoring
    whitespace

    If [:consume_token:] is `True`, the token will be removed from the head
    of remaining.
    """
    fields = _skip_ws(remaining)
    if fields.startswith(start):
        token = fields[:len(start)]
        if consume_token:
            remaining = remaining[len(start):]
        return token, remaining
    return None, fields


class ParseError(Exception):
    pass


class Selector(object):

    @classmethod
    def parse(cls, fields):
        field_list, remaining = FieldListSelector.parse(fields)
        if remaining:
            raise ParseError('Unexpected end of selector')
        return field_list

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

    @classmethod
    def parse(cls, remaining):
        """
        field_selector := selector_name [subselector]
        subselector := ('.' field_selector) | '(' fieldlistselector ')'
        """
        field_name, remaining = _parse_field_name(remaining)
        if not field_name:
            return None, remaining
        field_subselector, remaining = _match_start(remaining, '.')
        if field_subselector:
            subselector, remaining = FieldSelector.parse(remaining)
            if not subselector:
                raise ParseError('Expected field name')
            return FieldSelector(field_name, subselector), remaining
        lookahead_list, remaining = _match_start(remaining, '(',
                                                 consume_token=False)
        if lookahead_list:
            subselector, remaining = FieldListSelector.parse_subselector(remaining)
            return FieldSelector(field_name, subselector), remaining
        return FieldSelector(field_name), remaining

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
    def __init__(self, fields):
        self.fields = list(fields)

    @classmethod
    def _parse_selector_tail(cls, remaining):
        comma, remaining = _match_start(remaining, ',')
        tail_end, remaining = _match_start(remaining, ')', consume_token=False)
        if (not remaining) or tail_end:
            return [], remaining
        if not comma:
            raise ParseError('Expected \',\'')
        field, remaining = FieldSelector.parse(remaining)
        if not field:
            raise ParseError('Expected field selector')
        tail, remaining = cls._parse_selector_tail(remaining)
        tail.insert(0, field)
        return tail, remaining

    @classmethod
    def parse(cls, remaining):
        """
        list_subselector := '(' list_selector ')'
        list_selector := field_selector selector_tail
        list_selector_tail := (',' field_selector) list_selector_tail?
        """
        field, remaining = FieldSelector.parse(remaining)
        tail, remaining = cls._parse_selector_tail(remaining)
        tail.insert(0, field)
        return FieldListSelector(tail), remaining

    @classmethod
    def parse_subselector(cls, remaining):
        """
        A selector used to select multiple fields when not at
        the top level of the remaining must be parenthesised
        subselector := '(' field_list_selector ')'
        """

        open_parens, remaining = _match_start(remaining, '(')
        if not open_parens:
            raise ParseError('Expected open parens')
        subselector, remaining = cls.parse(remaining)
        close_parens, remaining = _match_start(remaining, ')')
        if not close_parens:
            raise ParseError('')
        return subselector, remaining

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
