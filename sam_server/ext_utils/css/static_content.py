

from ..base import static_content

def serve_css_file(request, path):
    response = static_content.serve_static_content(request, path)
    response['Content-Type'] = 'text/css'
    return response
