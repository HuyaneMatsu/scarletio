from .client_request import *
from .client_response import *
from .connection import *
from .connection_key import *
from .connector_base import *
from .connector_tcp import *
from .constants import *
from .host_info import *
from .host_info_basket import *
from .http_client import *
from .request_context_manager import *
from .request_info import *
from .protocol_basket import *  
from .proxy import *
from .ssl_fingerprint import *
from .web_socket_context_manager import *


__all__ = (
    *client_request.__all__,
    *client_response.__all__,
    *connection.__all__,
    *connection_key.__all__,
    *connector_base.__all__,
    *connector_tcp.__all__,
    *constants.__all__,
    *host_info.__all__,
    *host_info_basket.__all__,
    *http_client.__all__,
    *request_context_manager.__all__,
    *protocol_basket.__all__,
    *proxy.__all__,
    *request_info.__all__,
    *ssl_fingerprint.__all__,
    *web_socket_context_manager.__all__,
)


# Deprecations

from warnings import warn

def __getattr__(attribute_name):
    if attribute_name == 'TCPConnector':
        warn(
            (
                f'`TCPConnector` has been renamed to `ConnectorTCP`.'
                f'`ConnectorTCP` will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return ConnectorTCP
    
    raise AttributeError(attribute_name)
