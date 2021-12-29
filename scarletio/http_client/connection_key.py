__all__ = ()

class ConnectionKey:
    """
    Contains information about a host, like proxy, TLS to prevent reusing wrong connections from the pool.
    
    Attributes
    ----------
    host : `str`
        The host's ip address.
    is_ssl : `bool`
        Whether the connection is secure.
    port : `int`
        The host's port.
    proxy_auth : `None`, ``BasicAuth``
        Proxy authorization.
    proxy_url : `None`, ``URL``
        Proxy's url.
    ssl : `None`, ``SSLContext``, `bool`, ``Fingerprint``
        The connection's ssl type.
    """
    __slots__ = ('host', 'is_ssl', 'port', 'proxy_auth',  'proxy_url', 'ssl',) # + 'proxy_header_hash',
    
    def __init__(self, request):
        # proxy_headers = request.proxy_headers
        # if request.proxy_headers is not None:
        #     proxy_header_hash = hash(tuple(proxy_headers.items()))
        # else:
        #     proxy_header_hash = None
        
        self.host = request.host
        self.port = request.port
        self.is_ssl = request.is_ssl()
        self.ssl = request.ssl
        self.proxy_auth = request.proxy_auth
        self.proxy_url = request.proxy_url
        # self.proxy_header_hash = proxy_header_hash
    
    def __repr__(self):
        """Returns the connection key's representation."""
        return f'<{self.__class__.__name__} host={self.host!r}, port={self.port!r}>'
    
    def __eq__(self, other):
        """Returns whether the two connection keys are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.host != other.host:
            return False
        
        if self.port != other.port:
            return False
        
        if self.is_ssl != other.is_ssl:
            return False
        
        if self.ssl is None:
            if other.ssl is not None:
                return False
        else:
            if other.ssl is None:
                return False
            
            if self.ssl != other.ssl:
                return False
            
        if self.proxy_auth is None:
            if other.proxy_auth is not None:
                return False
        else:
            if other.proxy_auth is None:
                return False
            
            if self.proxy_auth != other.proxy_auth:
                return False

        if self.proxy_url is None:
            if other.proxy_url is not None:
                return False
        else:
            if other.proxy_url is None:
                return False
            
            if self.proxy_url != other.proxy_url:
                return False
        
        return True
    
    def __hash__(self):
        """Returns the connection key's hash value."""
        return hash(self.host) ^ (self.port << 17) ^ hash(self.is_ssl) ^ hash(self.ssl) ^ hash(self.proxy_auth) ^ \
               hash(self.proxy_url)
