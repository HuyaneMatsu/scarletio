__all__ = ()

from ..utils import RichAttributeErrorBaseType
from ..web_common.helpers import freeze_headers


class ConnectionKey(RichAttributeErrorBaseType):
    """
    Contains information about a host, like proxy, TLS to prevent reusing wrong connections from the pool.
    
    Attributes
    ----------
    host : `str`
        The host's ip address.
    
    port : `int`
        The host's port.
    
    proxy_auth : `None | BasicAuth`
        Proxy authorization sent with the request.
    
    proxy_headers_frozen : `None | tuple<(str, tuple<str>)>`
        Proxy headers to use if applicable.
    
    proxy_url : `None | URL`
        Proxy url to use if applicable.
    
    secure : `bool`
        Whether the connection is secure.
    
    ssl_context : `None | SSLContext``
        The connection's ssl type.
    
    ssl_fingerprint : `None | SSLFingerprint`
        Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
    """
    __slots__ = (
        'host', 'port', 'proxy_auth', 'proxy_headers_frozen', 'proxy_url', 'secure', 'ssl_context', 'ssl_fingerprint'
    )
    
    def __new__(cls, host, port, proxy_auth, proxy_headers, proxy_url, secure, ssl_context, ssl_fingerprint):
        """
        Creates a new connection key.
        
        Parameters
        ----------
        host : `str`
            The host's ip address.
        
        port : `int`
            The host's port.
        
        proxy_auth : `None | BasicAuth`
            Proxy authorization sent with the request.
        
        proxy_headers : `None | IgnoreCaseMultiValueDictionary`
            Proxy headers.
        
        proxy_url : `None | URL`
            Proxy url to use if applicable.
        
        secure : `bool`
            Whether the connection is secure.
        
        ssl_context : `None | SSLContext``
            The connection's ssl type.
        
        ssl_fingerprint : `None | SSLFingerprint`
            Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
        """
        proxy_headers_frozen = freeze_headers(proxy_headers)
        
        self = object.__new__(cls)
        self.host = host
        self.port = port
        self.proxy_auth = proxy_auth
        self.proxy_headers_frozen = proxy_headers_frozen
        self.proxy_url = proxy_url
        self.secure = secure
        self.ssl_context = ssl_context
        self.ssl_fingerprint = ssl_fingerprint
        return self
    
    
    def __repr__(self):
        """Returns the connection key's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # host
        repr_parts.append(' host = ')
        repr_parts.append(repr(self.host))
        
        # port
        repr_parts.append(', post = ')
        repr_parts.append(repr(self.port))
        
        # proxy_auth
        proxy_auth = self.proxy_auth
        if (proxy_auth is not None):
            repr_parts.append(', proxy_auth = ')
            repr_parts.append(repr(proxy_auth))
        
        # proxy_headers_frozen
        proxy_headers_frozen = self.proxy_headers_frozen
        if (proxy_headers_frozen is not None):
            repr_parts.append(', proxy_headers_frozen = ')
            repr_parts.append(repr(proxy_headers_frozen))
        
        # proxy_url
        proxy_url = self.proxy_url
        if (proxy_url is not None):
            repr_parts.append(', proxy_url = ')
            repr_parts.append(repr(proxy_url))
        
        # secure
        secure = self.secure
        if secure:
            repr_parts.append(', secure = ')
            repr_parts.append(repr(secure))
        
        # ssl_context
        ssl_context = self.ssl_context
        if (ssl_context is not None):
            repr_parts.append(', ssl_context = ')
            repr_parts.append(repr(ssl_context))
        
        # ssl_fingerprint
        ssl_fingerprint = self.ssl_fingerprint
        if (ssl_fingerprint is not None):
            repr_parts.append(', ssl_fingerprint = ')
            repr_parts.append(repr(ssl_fingerprint))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two connection keys are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # host
        if self.host != other.host:
            return False
        
        # port
        if self.port != other.port:
            return False
        
        # proxy_auth
        if self.proxy_auth != other.proxy_auth:
            return False
        
        # proxy_headers
        if self.proxy_headers_frozen != other.proxy_headers_frozen:
            return False
        
        # proxy_url
        if self.proxy_url != other.proxy_url:
            return False
        
        # secure
        if self.secure != other.secure:
            return False
        
        # ssl_context
        if self.ssl_context != other.ssl_context:
            return False
        
        # ssl_fingerprint
        if self.ssl_fingerprint != other.ssl_fingerprint:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the connection key's hash value."""
        hash_value = 0
        
        # host
        hash_value ^= hash(self.host)
        
        # port
        hash_value ^= self.port << 17
        
        # proxy_auth
        proxy_auth = self.proxy_auth
        if (proxy_auth is not None):
            hash_value ^= hash(proxy_auth)
        
        # proxy_headers_frozen
        proxy_headers_frozen = self.proxy_headers_frozen
        if (proxy_headers_frozen is not None):
            hash_value ^= hash(self.proxy_headers_frozen)
        
        # proxy_url
        proxy_url = self.proxy_url
        if (proxy_url is not None):
            hash_value ^= hash(proxy_url)
        
        # secure
        hash_value ^= self.secure
        
        # ssl_context
        ssl_context = self.ssl_context
        if (ssl_context is not None):
            hash_value ^= hash(ssl_context)
        
        # ssl_fingerprint
        ssl_fingerprint = self.ssl_fingerprint
        if (ssl_fingerprint is not None):
            hash_value ^= hash(ssl_fingerprint)
        
        return hash_value
    
    
    def copy_proxyless(self):
        """
        Copies the connection key without its proxy information.
        
        Returns
        -------
        new : `instance<type<self>>`
        """
        new = object.__new__(type(self))
        new.host = self.host
        new.port = self.port
        new.proxy_auth = None
        new.proxy_headers_frozen = None
        new.proxy_url = None
        new.secure = self.secure
        new.ssl_context = self.ssl_context
        new.ssl_fingerprint = self.ssl_fingerprint
        return new
