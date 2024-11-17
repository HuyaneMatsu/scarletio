__all__ = ('Proxy',)

from ssl import SSLContext

from ..utils import IgnoreCaseMultiValueDictionary, RichAttributeErrorBaseType
from ..web_common import BasicAuthorization, URL, freeze_headers

from .ssl_fingerprint import SSLFingerprint


class Proxy(RichAttributeErrorBaseType):
    """
    Represents a proxy to do request through.
    
    Attributes
    ----------
    _hash_cache : `None | int`
        Cache field for `hash(self)`.
    
    authorization : `None | BasicAuthorization`
        Authorization header to send.
    
    headers : `None | IgnoreCaseMultiValueDictionary`
        Additional to send to the proxy.
    
    ssl_context : `None | SSLContext``
        The proxy connection's ssl type.
    
    ssl_fingerprint : `None | SSLFingerprint`
        Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
    
    url : ``URL``
        The url to proxy through.
    """
    __slots__ = ('_hash_cache', 'authorization', 'headers', 'ssl_context', 'ssl_fingerprint', 'url')
    
    def __new__(cls, url, *, authorization = ..., headers = ..., ssl_context = ..., ssl_fingerprint = ...):
        # url
        url = URL(url)
        if url.host is None:
            raise ValueError(f'Host could not be detected from url: {url!r}')
        
        # authorization
        if authorization is ...:
            authorization = None
        elif (authorization is not None) and (not isinstance(authorization, BasicAuthorization)):
            raise TypeError(
                f'`authorization` can be be given as `None`, {BasicAuthorization.__name__}. '
                f'Got {type(authorization).__name__}; {authorization!r}.'
            )
        
        # headers
        if headers is ...:
            headers = None
        elif (headers is None):
            headers = None
        else:
            headers = IgnoreCaseMultiValueDictionary(headers)
            if not headers:
                headers = None
        
        # ssl_context
        if ssl_context is ...:
            ssl_context = None
        elif (ssl_context is not None) and (not isinstance(ssl_context, SSLContext)):
            raise TypeError(
                f'`ssl_context` can be given as `None`, `{type(SSLContext).__name__}`'
            )
    
        # ssl_fingerprint
        if ssl_fingerprint is ...:
            ssl_fingerprint = None
        elif (ssl_fingerprint is not None) and (not isinstance(ssl_fingerprint, SSLFingerprint)):
            raise TypeError(
                f'`ssl_fingerprint` can be given as `None`, `{type(SSLFingerprint).__name__}`'
            )
        
        # Construct
        self = object.__new__(cls)
        self._hash_cache = None
        self.authorization = authorization
        self.headers = headers
        self.ssl_context = ssl_context
        self.ssl_fingerprint = ssl_fingerprint
        self.url = url
        return self
    
    
    def __repr__(self):
        """Returns the proxy's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # url
        repr_parts.append(' url = ')
        repr_parts.append(repr(self.url))
        
        # authorization
        authorization = self.authorization
        if (authorization is not None):
            repr_parts.append(', authorization = ')
            repr_parts.append(repr(authorization))
        
        # headers
        headers = self.headers
        if (headers is not None):
            repr_parts.append(', headers = ')
            repr_parts.append(repr(headers))
        
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
    
    
    def __hash__(self):
        """Returns the proxy's hash value."""
        hash_value = self._hash_cache
        if (hash_value is None):
            hash_value = self._create_hash()
            self._hash_cache = hash_value
        
        return hash_value
    
    
    def _create_hash(self):
        """
        Generates the proxy's hash.
        
        Returns
        -------
        hash_value : `int`
        """
        hash_value = 0
        
        # authorization
        authorization = self.authorization
        if (authorization is not None):
            hash_value ^= hash(authorization)
        
        # headers
        headers = freeze_headers(self.headers)
        if (headers is not None):
            hash_value ^= hash(headers)
        
        # ssl_context
        ssl_context = self.ssl_context
        if (ssl_context is not None):
            hash_value ^= hash(ssl_context)
        
        # ssl_fingerprint
        ssl_fingerprint = self.ssl_fingerprint
        if (ssl_fingerprint is not None):
            hash_value ^= hash(ssl_fingerprint)
       
        # url
        hash_value ^= hash(self.url)
        
        return hash_value
    
    
    def __eq__(self, other):
        """Returns whether the two proxies are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # authorization
        if self.authorization != other.authorization:
            return False
        
        # headers
        if self.headers != other.headers:
            return False
        
        # ssl_context
        if self.ssl_context != other.ssl_context:
            return False
        
        # ssl_fingerprint
        if self.ssl_fingerprint != other.ssl_fingerprint:
            return False
        
        # url
        if self.url != other.url:
            return False
        
        return True
    
    
    @property
    def host(self):
        """
        Returns the request's host.
        
        Returns
        -------
        host : `str`
        """
        return self.url.host
    
    
    @property
    def port(self):
        """
        Returns the request's port.
        
        Returns
        -------
        port : `None | int`
        """
        return self.url.port
    
    
    def is_secure(self):
        """
        Returns whether the request is secure.
        
        Returns
        -------
        is_secure : `bool`
        """
        scheme = self.url.scheme
        if scheme in ('http', 'ws'):
            return False
        
        if scheme in ('https', 'wss'):
            return True
        
        # If we have any other scheme let the user decide whether it is ssl or nah.
        return (self.ssl_context is not None)
