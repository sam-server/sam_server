import base64
import uuid


# TODO: These functions should be moved to a utility library
# (perhaps mod_common?)
def uuid_to_urlpath(uuid):
    """Convert a uuid into a shorter urlsafe string using base64"""
    b64 = base64.urlsafe_b64encode(uuid.bytes)
    b64 = str(b64, encoding='utf-8')
    return b64.rstrip('=')


def urlpath_to_uuid(urlpath):
    """ A urlpath is a base64 encoded uuid with the padding chars
    trimmed"""
    # pad the path out to a multiple of 4 chars in length with '='
    num_pad_chars = 4 - len(urlpath) % 4
    if num_pad_chars > 2:
        ## Cannot have a url path with more than two pad chars
        raise ValueError(urlpath)
    urlpath += '=' * num_pad_chars
    uuid_bytes = base64.urlsafe_b64decode(urlpath)
    return uuid.UUID(bytes=uuid_bytes)

