__all__ = ('RequestContextManager', 'WebSocketContextManager')

class RequestContextManager:
    """
    Asynchronous context manager wrapping a request coroutine.
    
    Examples
    --------
    ``RequestContextManager`` are returned by ``HTTPClient`` request methods. Request context managers can be used as an
    asynchronous context manager or as a simple awaitable.
    
    ```py
    async with http_client.get('http://python.org') as response:
        data = await response.read()
    ```
    
    ```py
    response = await http_client.get('http://python.org')
    data = await response.read()
    ```
    
    Attributes
    ----------
    coroutine : `None`, `CoroutineType`
        The wrapped requester coroutine.
    response : `None`, ``ClientResponse``
        Received client response if applicable.
    """
    __slots__ = ('coroutine', 'response', )
    
    def __init__(self, coroutine):
        """
        Creates a new request content manager.
        
        Parameters
        ----------
        coroutine : `CoroutineType`
            Requester coroutine to wrap.
        """
        self.coroutine = coroutine
        self.response = None
    
    
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
        Enters the ``RequestContextManager`` as an asynchronous context manager. Releases the response when the context manager is
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
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Releases the response.
        
        This method is a coroutine.
        """
        response = self.response
        if (response is not None):
            self.response = None
            response.release()


class WebSocketContextManager:
    """
    Asynchronous context manager wrapping a websocket connecting coroutine.
    
    Examples
    --------
    ``WebSocketContextManager``-s are returned by the ``HTTPClient.connect_websocket`` method. WebSocket
    context managers can be used as an asynchronous context manager or as a simple awaitable.
    
    ```py
    async with http_client.connect_websocket('http://ayaya.aya') as websocket:
        await websocket.send('ayaya')
    ```
    
    ```py
    websocket = await http_client.connect_websocket('http://ayaya.aya')
    await websocket.send('ayaya')
    ```
    
    Attributes
    ----------
    coroutine : `CoroutineType`
        The wrapped requester coroutine.
    websocket : `None`, ``WebSocketClient``
        The connected websocket client if applicable
    """
    __slots__ = ('coroutine', 'websocket', )
    
    def __init__(self, coroutine):
        """
        Creates a new websocket content manager.
        
        Parameters
        ----------
        coroutine : `CoroutineType`
            WebSocket connecting coroutine to wrap.
        """
        self.coroutine = coroutine
        self.websocket = None
    
    
    def __iter__(self):
        """
        Awaits the wrapped coroutine.
        
        This method is a generator. Should be used with `await` expression.
        
        Returns
        -------
        websocket : ``WebSocketClient``
            The connected websocket client.
        
        Raises
        ------
        BaseException
            Any exception raised meanwhile connecting the websocket.
        """
        return (yield from self.__aenter__().__await__())
    
    __await__ = __iter__
    
    
    async def __aenter__(self):
        """
        Enters the ``WebSocketContextManager`` as an asynchronous context manager. Closes the websocket when the
        context manager is exited.
        
        This method is a coroutine.
        
        Returns
        -------
        websocket : ``WebSocketClient``
            The connected websocket client.
        
        Raises
        ------
        BaseException
            Any exception raised meanwhile connecting the websocket.
        """
        coroutine = self.coroutine
        if (coroutine is None):
            websocket = self.websocket
        else:
            websocket = await coroutine
            self.websocket = websocket
            self.coroutine = None
        
        return websocket
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the connected websocket.
        
        This method is a coroutine.
        """
        websocket = self.websocket
        if (websocket is not None):
            self.websocket = None
            await websocket.close()
