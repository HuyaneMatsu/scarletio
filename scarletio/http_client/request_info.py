__all__ = ()

from warnings import warn

from ..utils import RichAttributeErrorBaseType
from ..web_common.helpers import freeze_headers


class RequestInfo(RichAttributeErrorBaseType):
    """
    Base information representing a request.
    
    Attributes
    ----------
    headers : ``IgnoreCaseMultiValueDictionary``
        The respective request's headers.
    
    method : `str`
        The respective request's method.
    
    original_url : ``URL``
        The url given to request.
    
    url : ``URL``
        The requested url without fragments. Can be same as `original_url`.
    """
    __slots__ = ('headers', 'method', 'original_url', 'url',)
    
    def __new__(cls, headers, method, original_url, url):
        """
        Creates a new request info representing the given request.
        
        Parameters
        ----------
        headers : ``IgnoreCaseMultiValueDictionary``
            The respective request's headers.
        
        method : `str`
            The respective request's method.
        
        original_url : ``URL``
            The url given to request.
        
        url : ``URL``
            The requested url without fragments. Can be same as `original_url`.
        """
        self = object.__new__(cls)
        self.headers = headers
        self.method = method
        self.original_url = original_url
        self.url = url
        return self
    
    
    def __repr__(self):
        """Returns the request info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # method
        repr_parts.append(', method = ')
        repr_parts.append(repr(self.method))
        
        # url
        url = self.url
        repr_parts.append(', url = ')
        repr_parts.append(repr(url))
        
        # original_url
        original_url = self.original_url
        if (url != original_url):
            repr_parts.append(', original_url = ')
            repr_parts.append(repr(original_url))
        
        # headers
        headers = self.headers
        if headers:
            repr_parts.append(', headers = ')
            repr_parts.append(repr(headers))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two connection infos are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # headers
        if self.headers != other.headers:
            return False
        
        # method
        if self.method != other.method:
            return False
        
        # original_url
        if self.original_url != other.original_url:
            return False
        
        # url
        if self.url != other.url:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the request info's hash value."""
        hash_value = 0
        
        # headers
        headers_frozen = freeze_headers(self.headers)
        if (headers_frozen is not None):
            hash_value ^= hash(headers_frozen)
        
        # method
        hash_value ^= hash(self.method)
        
        # original_url
        original_url = self.original_url
        hash_value ^= hash(original_url)
        
        # url
        url = self.url
        if (url != original_url):
            hash_value ^= hash(url)
        
        return hash_value
    
    
    @property
    def real_url(self):
        """
        Deprecated and will be removed in 2025 August.
        """
        warn(
            (
                f'The `proxy_url` and `proxy_headers` parameters in `{type(self).__name__}.__new__` are moved to be '
                f'keyword only. Support for positional is deprecated and will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.original_url
