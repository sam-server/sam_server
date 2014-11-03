from common.jsonrpc import service

import artist.services


## A list of services
services = (
    service('Artist', artist.services),
)
