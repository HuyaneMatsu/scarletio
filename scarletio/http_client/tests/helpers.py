from ssl import create_default_context as create_default_ssl_context

from ...core import get_event_loop
from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import BasicAuth, URL
from ...web_common.headers import METHOD_GET

from ..client_request import ClientRequest
from ..connection_key import ConnectionKey
from ..ssl_fingerprint import SSLFingerprint


class Any:
    __slots__ = ('expected_type',)
    
    def __new__(cls, expected_type = None):
        self = object.__new__(cls)
        self.expected_type = expected_type
        return self
    
    
    def __eq__(self, other):
        expected_type = self.expected_type
        if expected_type is None:
            return True
        
        return type(other) is expected_type


def _get_default_connection_key():
    """
    Creates and returns a connection key.
    
    Returns
    -------
    connection_key : ``ConnectionKey``
    """
    host = '1.1.1.1'
    port = 96
    proxy_auth = BasicAuth('miau', 'land')
    proxy_headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    proxy_url = URL('https://orindance.party/')
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    return ConnectionKey(
        host,
        port,
        proxy_auth,
        proxy_headers,
        proxy_url,
        secure,
        ssl_context,
        ssl_fingerprint,
    )


def _get_default_request():
    """
    Creates and returns a client request.
    
    Returns
    -------
    client_request : ``ClientRequest``
    """
    loop = get_event_loop()
    url = URL('https://orindance.party/')

    return ClientRequest(
        loop,
        METHOD_GET,
        url,
        IgnoreCaseMultiValueDictionary(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
