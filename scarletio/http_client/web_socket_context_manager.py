__all__ = ('WebSocketContextManager', )

from ..utils import RichAttributeErrorBaseType
from ..utils.trace.formatters import format_coroutine


class WebSocketContextManager(RichAttributeErrorBaseType):
    """
    Asynchronous context manager wrapping a web socket connecting coroutine.
    
    Examples
    --------
    web socket context managers are returned by the ``HTTPClient.connect_web_socket`` method. Web socket
    context managers can be used as an asynchronous context manager or as a simple awaitable.
    
    ```py
    async with http_client.connect_web_socket('http://ayaya.aya') as web_socket:
        await web_socket.send('ayaya')
    ```
    
    ```py
    web_socket = await http_client.connect_web_socket('http://ayaya.aya')
    await web_socket.send('ayaya')
    ```
    
    Attributes
    ----------
    coroutine : `None | CoroutineType`
        The wrapped requester coroutine.
    
    web_socket : `None | WebSocketClient`
        The connected web socket client if applicable
    """
    __slots__ = ('coroutine', 'web_socket')
    
    def __new__(cls, coroutine):
        """
        Creates a new web socket content manager.
        
        Parameters
        ----------
        coroutine : `CoroutineType`
            WebSocket connecting coroutine to wrap.
        """
        self = object.__new__(cls)
        self.coroutine = coroutine
        self.web_socket = None
        return self
    
    
    def __iter__(self):
        """
        Awaits the wrapped coroutine.
        
        This method is a generator. Should be used with `await` expression.
        
        Returns
        -------
        web_socket : ``WebSocketClient``
            The connected web socket client.
        
        Raises
        ------
        BaseException
            Any exception raised meanwhile connecting the web socket.
        """
        return (yield from self.__aenter__().__await__())
    
    __await__ = __iter__
    
    
    async def __aenter__(self):
        """
        Enters the web socket context manager as an asynchronous context manager. Closes the web socket when the
        context manager is exited.
        
        This method is a coroutine.
        
        Returns
        -------
        web_socket : ``WebSocketClient``
            The connected web socket client.
        
        Raises
        ------
        BaseException
            Any exception raised meanwhile connecting the web socket.
        """
        coroutine = self.coroutine
        if (coroutine is None):
            web_socket = self.web_socket
        else:
            web_socket = await coroutine
            self.web_socket = web_socket
            self.coroutine = None
        
        return web_socket
    
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        """
        Closes the connected web_socket.
        
        This method is a coroutine.
        """
        web_socket = self.web_socket
        if (web_socket is not None):
            self.web_socket = None
            await web_socket.close()
    
    
    def __repr__(self):
        """Returns the request context manager's representation."""
        repr_parts = ['<', type(self).__name__]
        
        while True:
            coroutine = self.coroutine
            if (coroutine is not None):
                repr_parts.append(' coroutine = ')
                repr_parts.append(format_coroutine(coroutine))
                break
            
            web_socket = self.web_socket
            if (web_socket is not None):
                repr_parts.append(' web_socket = ')
                repr_parts.append(repr(web_socket))
                break
            
            repr_parts.append(' exited')
            break
        
        repr_parts.append('>')
        return ''.join(repr_parts)
