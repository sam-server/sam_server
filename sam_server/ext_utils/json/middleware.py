import json
import re

from django.http import JsonResponse

CHARSET_PATTERN = re.compile(r'charset=([\w-]+)')


class JsonRequestMiddleware(object):
    def process_request(self, request):
        """
        Adds a 'json' field to request (by default to None)
        If the request's content type is application/json,
        populates the 'json' field with the parsed body
        """
        request.JSON = None
        try:
            content_type = request.META['CONTENT_TYPE']
        except KeyError:
            return
        if not content_type.startswith('application/json'):
            return
        charset_match = CHARSET_PATTERN.search(content_type)
        charset = 'utf-8'
        if charset_match is not None:
            charset = charset_match.group(1)
            print('CHARSET: {0}'.format(charset))
        try:
            content = str(request.body, encoding=charset)
            request.JSON = json.loads(content)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
