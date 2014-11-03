## Was used by common.jsonrpc.middleware
## TODO: Remove jsonrpc middleware completely
# It's better to handle requests via rest.

from common.jsonrpc import service

import artist.services


## A list of services
services = (
    service('Artist', artist.services),
)
