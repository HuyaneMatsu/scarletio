__all__ = ('RequestContextManager', )

from ..utils import RichAttributeErrorBaseType
from ..utils.trace.formatters import format_coroutine


class RequestContextManager(RichAttributeErrorBaseType):
    """
    Asynchronous context manager wrapping a request coroutine.
    
    Examples
    --------
    ``RequestContextManager`` are returned by ``HTTPClient`` request methods. Request context managers can be used as an
    asynchronous context manager or as a simple awaitable.
    
    ```py
    async with http_client.get('https://orindance.party/') as response:
        data = await response.read()
    ```
    
    ```py
    response = await http_client.get('https://orindance.party/')
    data = await response.read()
    ```
    
    Attributes
    ----------
    coroutine : `None | CoroutineType`
        The wrapped requester coroutine.
    
    response : `None | ClientResponse`
        Received client response if applicable.
    """
    __slots__ = ('coroutine', 'response')
    
    def __new__(cls, coroutine):
        """
        Creates a new request content manager.
        
        Parameters
        ----------
        coroutine : `CoroutineType`
            Requester coroutine to wrap.
        """
        self = object.__new__(cls)
        self.coroutine = coroutine
        self.response = None
        return self
    
    
    def __iter__(self):
        """
        Awaits the wrapped coroutine.
        
        This method is a generator. Should be used with `await` expression.
        
        Returns
        -------
        response : ``ClientResponse``
            Received client response if applicable.
        
        Raises
        ------
        BaseException
            Any exception raised by the request.
        """
        return (yield from self.__aenter__().__await__())
    
    
    __await__ = __iter__
    
    
    async def __aenter__(self):
        """
        Enters the request context manager as an asynchronous context manager. Releases the response when the context manager is
        exited.
        
        This method is a coroutine.
        
        Returns
        -------
        response : ``ClientResponse``
            Received client response if applicable.
        
        Raises
        ------
        BaseException
            Any exception raised by the request.
        """
        coroutine = self.coroutine
        if (coroutine is None):
            response = self.response
        else:
            response = await coroutine
            self.response = response
            self.coroutine = None
        
        return response
    
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        """
        Releases the response.
        
        This method is a coroutine.
        """
        response = self.response
        if (response is not None):
            self.response = None
            response.release()
        
        return False
    
    
    def __repr__(self):
        """Returns the request context manager's representation."""
        repr_parts = ['<', type(self).__name__]
        
        while True:
            coroutine = self.coroutine
            if (coroutine is not None):
                repr_parts.append(' coroutine = ')
                repr_parts.append(format_coroutine(coroutine))
                break
            
            response = self.response
            if (response is not None):
                repr_parts.append(' response = ')
                repr_parts.append(repr(response))
                break
            
            repr_parts.append(' exited')
            break
        
        repr_parts.append('>')
        return ''.join(repr_parts)
