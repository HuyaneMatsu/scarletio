__all__ = ()

class RequestInfo:
    """
    Base information representing a request.
    
    Attributes
    ----------
    headers : ``IgnoreCaseMultiValueDictionary``
        The respective request's headers.
    method : `str`
        The respective request's method.
    real_url : ``URL``
        The url given to request.
    url : ``URL``
        The requested url without fragments. Can be same as ``.real_url``.
    """
    __slots__ = ('headers', 'method', 'real_url', 'url',)
    
    def __init__(self, request):
        """
        Creates a new ``RequestInfo`` representing the given request.
        
        Parameters
        ----------
        request : ``ClientRequest``
            The represented request.
        """
        self.url = request.url
        self.method = request.method
        self.headers = request.headers
        self.real_url = request.original_url
    
    def __repr__(self):
        """Returns the request info's representation."""
        return f'<{self.__class__.__name__} url = {self.url!r}>'
