
from ..base.static_content import serve_static_content


def serve_svg_file(request, path):
    response = serve_static_content(request, path)
    response['Content-Type'] = 'image/svg+xml'
    return response


