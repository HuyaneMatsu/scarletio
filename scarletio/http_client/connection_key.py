__all__ = ()

from ..utils import RichAttributeErrorBaseType


class ConnectionKey(RichAttributeErrorBaseType):
    """
    Contains information about a host, like proxy, TLS to prevent reusing wrong connections from the pool.
    
    Attributes
    ----------
    host : `str`
        The host's ip address.
    
    port : `int`
        The host's port.
    
    proxy : `None | Proxy`
        Proxy if applicable.
    
    secure : `bool`
        Whether the connection is secure.
    
    ssl_context : `None | SSLContext``
        The connection's ssl type.
    
    ssl_fingerprint : `None | SSLFingerprint`
        Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
    """
    __slots__ = (
        'host', 'port', 'proxy', 'secure', 'ssl_context', 'ssl_fingerprint'
    )
    
    def __new__(cls, host, port, proxy, secure, ssl_context, ssl_fingerprint):
        """
        Creates a new connection key.
        
        Parameters
        ----------
        host : `str`
            The host's ip address.
        
        port : `int`
            The host's port.
        
        proxy : `None | Proxy`
            Proxy if applicable.
        
        secure : `bool`
            Whether the connection is secure.
        
        ssl_context : `None | SSLContext``
            The connection's ssl type.
        
        ssl_fingerprint : `None | SSLFingerprint`
            Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
        """
        self = object.__new__(cls)
        self.host = host
        self.port = port
        self.proxy = proxy
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
        
        # proxy
        proxy = self.proxy
        if (proxy is not None):
            repr_parts.append('proxy = ')
            repr_parts.append(repr(proxy))
        
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
        
        # proxy
        if self.proxy != other.proxy:
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
        
        # proxy
        proxy = self.proxy
        if (proxy is not None):
            hash_value ^= hash(proxy)
        
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
        new.proxy = None
        new.secure = self.secure
        new.ssl_context = self.ssl_context
        new.ssl_fingerprint = self.ssl_fingerprint
        return new
