from ..base.static_content import serve_static_content


INSTALLED_APP_PATHS = dict()


def serve_dart_file(request, path):
    response = serve_static_content(request, path)
    response['Content-Type'] = 'application/dart'
    return response
