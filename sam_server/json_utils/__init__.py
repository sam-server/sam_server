
from django.http import JsonResponse
from .field_selector import Selector


def partial_json_response(request, resource):
    """
    parses the selector 'fields' out of the request's query set
    and returns the partial response which results from selecting
    said fields from the provided resource
    """
    fields = request.GET('fields', None)
    if fields is not None:
        selector = Selector.parse(fields)
        resource = selector.select(resource)
    return JsonResponse(resource)
