

from ..base.static_content import serve_static_content

def serve_js_file(request, path):
    response = serve_static_content(request, path)
    response['Content-Type'] = 'application/json'
    return response
