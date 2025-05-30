__all__ = ('WebSocketServer', )

from functools import partial as partial_func
from warnings import warn

from ..core import Task, TaskGroup, skip_poll_cycle
from ..utils import IgnoreCaseMultiValueDictionary

from .web_socket_server_protocol import WebSocketServerProtocol


class WebSocketServer:
    """
    Asynchronous web socket server implementation.
    
    Attributes
    ----------
    loop : ``EventThread``
        The event loop to what the web socket server is bound to.
    web_sockets : `set` of (``WebSocketServerProtocol``, `object`)
        Active server side asynchronous web socket protocol implementations.
    close_connection_task : `None`, ``Task`` of ``_close``
        Close connection task, what's result is set, when closing of the web socket is done.
        
        Should not be cancelled.
        
        Set, when ``.close`` is called.
    handler : `async-callable`
        An asynchronous callable, what will handle a web socket connection.
        
        Should be given as an `async-callable` accepting `1` parameter the respective asynchronous server side
        web socket protocol implementations.
    server : `None`, ``Server``
        Asynchronous server instance. Set meanwhile the web socket server is running.
    protocol_parameters : `tuple` of `object`
        WebSocket protocol parameters.
        
        Contains the following elements:
            - `handler` : `async-callable` Same as ``.handler``.
            - `host` : `None`, `str`, `iterable` of (`None`, `str`). To what network interfaces the server be bound.
            - `port` :  `None | int`. The port used by the `host`(s).
            - `is_ssl` : `bool`
                Whether the server is secure.
            - `origin` : `None`, `str`. Value of the Origin header.
            - `available_extensions` : `None` or (`list` of `object`). Available web socket extensions.
                Each web socket extension should have the following `4` attributes / methods:
                - `name`: `str`. The extension's name.
                - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
                - `decode` : `callable`. Decoder method, what processes a received web socket frame. Should accept `2`
                    parameters: The respective ``WebSocketFrame``, and the ˙max_size` as `int`, what describes the
                    maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
                - `encode` : `callable`. Encoder method, what processes the web socket frames to send. Should accept `1`
                    parameter, the respective ``WebSocketFrame``.
            - `available_subprotocols` : `None` or (`list` of `str`). A list of supported subprotocols in order of
                decreasing preference.
            - `extra_response_headers` : `None` or (``IgnoreCaseMultiValueDictionary``, `dict-like`) of (`str`, `str`) items. Extra
                headers to send with the http response.
            - `request_processor` : `None`, `callable`. An optionally asynchronous callable, what processes the
                initial requests from the potential clients. Should accept the following parameters:
                - `path` : `str`. The requested path.
                - `request_headers` : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`). The request's headers.
                
                The `request_processor` on accepted request should return `None`, otherwise a `tuple` of
                ``AbortHandshake`` parameters.
            - `subprotocol_selector` : `None`, `callable`. User hook to select subprotocols. Should accept the
                following parameters:
                - `parsed_header_subprotocols` : `list` of `str`. The subprotocols supported by the client.
                - `available_subprotocols` : `list` of `str`. The subprotocols supported by the server.
            - `web_socket_keyword_parameters` : `dict<str, object>`.
                Extra parameters for creating the web socket protocol.
                
                Can have any of the following items:
                - `close_timeout` : `float`. The maximal duration in seconds what is waited for response after close
                    frame is sent. Defaults to `10.0`.
                - `max_size` : `int`.Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised.
                    Defaults to `67108864` bytes.
                - `max_queue` : `None | int`.
                    Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of
                    it is removed. Defaults to `None`.
    """
    __slots__ = ('loop', 'web_sockets', 'close_connection_task', 'handler', 'server', 'protocol_parameters')
    
    async def __new__(
        cls,
        loop,
        host,
        port,
        handler,
        *,
        protocol = WebSocketServerProtocol,
        available_extensions = None,
        extra_response_headers = None,
        origin = None,
        available_subprotocols = None,
        request_processor = None,
        subprotocol_selector = None,
        web_socket_keyword_parameters = None,
        ssl = None,
        websocket_kwargs = ...,
        **server_keyword_parameters,
    ):
        """
        Creates a new ``WebSocketServer`` with the given parameters.
        
        This method is a coroutine.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the web socket server is bound to.
        host : `None`, `str`, `iterable` of (`None`, `str`)
            To what network interfaces should the server be bound.
        port : `None | int`
            The port to use by the `host`(s).
        handler : `async-callable`
            An asynchronous callable, what will handle a web socket connection.
            
            Should be given as an `async-callable` accepting `1` parameter the respective asynchronous server side
            web socket protocol implementations.
        protocol : `object` = ``WebSocketServerProtocol``, Optional (Keyword only)
            Asynchronous server side web socket protocol implementation.
        available_extensions : `None` or (`list` of `object`) = `None`, Optional (Keyword only)
            Available web socket extensions.
            
            Each web socket extension should have the following `4` attributes / methods:
            - `name`: `str`. The extension's name.
            - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
            - `decode` : `callable`. Decoder method, what processes a received web socket frame. Should accept `2`
                parameters: The respective ``WebSocketFrame``, and the ˙max_size` as `int`, what decides the
                maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
            - `encode` : `callable`. Encoder method, what processes the web socket frames to send. Should accept `1`
                parameter, the respective ``WebSocketFrame``.
        extra_response_headers : `None` or (``IgnoreCaseMultiValueDictionary``, `dict-like`) of
                (`str`, `str`) items = `None`, Optional (Keyword only)
            Extra headers to send with the http response.
        origin : `None`, `str` = `None`, Optional (Keyword only)
            Value of the Origin header.
        available_subprotocols : `None` or (`list` of `str`) = `None`, Optional (Keyword only)
            A list of supported subprotocols in order of decreasing preference.
        request_processor : `None`, `callable` = `None`, Optional (Keyword only)
            An optionally asynchronous callable, what processes the initial requests from the potential clients.
            
            Should accept the following parameters:
            - `path` : `str`. The requested path.
            - `request_headers` : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`). The request's headers.
            
            The `request_processor` on accepted request should return `None`, otherwise a `tuple` of
            ``AbortHandshake`` parameters.
        subprotocol_selector `None`, `callable` = `None`, Optional (Keyword only)
            User hook to select subprotocols. Should accept the following parameters:
            - `parsed_header_subprotocols` : `list` of `str`. The subprotocols supported by the client.
            - `available_subprotocols` : `list` of `str`. The subprotocols supported by the server.
        web_socket_keyword_parameters : `None | dict<str, object>` = `None`, Optional (Keyword only)
            Extra parameters for creating the web socket protocol.
            
            Can have any of the following items:
            - `close_timeout` : `float`. The maximal duration in seconds what is waited for response after close
                frame is sent.
            - `max_size` : `int`.Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised.
            - `max_queue` : `None | int`.
                Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of
                it is removed.
        ssl : `None`, ``SSLContext`` = `None`, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        **server_keyword_parameters : Keyword parameters
            Additional keyword parameters to create the web socket server with.
        
        Other Parameters
        ----------------
        family : `AddressFamily`, `int`, Optional (Keyword only)
            Can be given either as `socket.AF_INET`, `socket.AF_INET6` to force the socket to use `IPv4`, `IPv6`.
            If not given, then  will be determined from host name.
        backlog : `int`, Optional (Keyword only)
            The maximum number of queued connections passed to `socket.listen()`.
        reuse_address : `bool`, Optional (Keyword only)
            Tells the kernel to reuse a local socket in `TIME_WAIT` state, without waiting for its natural timeout to
            expire. If not specified will automatically be set to True on Unix.
        reuse_port : `bool`, Optional (Keyword only)
            Tells to the kernel to allow this endpoint to be bound to the same port as an other existing endpoint
            already might be bound to.
            
            Not supported on Windows.
        
        Returns
        -------
        self : ``WebSocketServer``
        
        Raises
        ------
        TypeError
            - `extra_response_headers` is not given as `None`, neither as `dict-like`.
            - If `ssl` is not given either as `None`, `ssl.SSLContext`.
            - If `reuse_port` is given as non `bool`.
            - If `reuse_address` is given as non `bool`.
            - If `reuse_port` is given as non `bool`.
            - If `host` is not given as `None`, `str` and neither as `iterable` of `None`, `str`.
        ValueError
            - If `host`, `port` parameter is given, when `socket` is defined as well.
            - If `reuse_port` is given as `True`, but not supported.
            - If neither `host`, `port nor `socket` were given.
            - If `socket` is given, but it's type is not `module_socket.SOCK_STREAM`.
        OsError
            Error while attempting to binding to address.
        """
        if (websocket_kwargs is not None):
            warn(
                (
                    f'`{cls.__name__}.__new__`\'s `websocket_kwargs` parameter is deprecated and will be removed in '
                    f'2025 august. Please use `web_socket_keyword_parameters` instead.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            web_socket_keyword_parameters = websocket_kwargs
        
        if web_socket_keyword_parameters is None:
            web_socket_keyword_parameters = {}
        
        is_ssl = (ssl is not None)
        
        if available_extensions is None:
            available_extensions = []
        
        if (extra_response_headers is None):
            pass
        elif type(extra_response_headers) is IgnoreCaseMultiValueDictionary:
            pass
        elif hasattr(type(extra_response_headers), 'items'):
            extra_response_headers_local = IgnoreCaseMultiValueDictionary()
            
            for name, value in extra_response_headers.items():
                extra_response_headers_local[name] = value
            
            extra_response_headers = extra_response_headers_local
        else:
            raise TypeError(
                f'`extra_response_headers` can be `None`, `dict-like` with \'.items\' method, got '
                f'{type(extra_response_headers).__name__}; {extra_response_headers!r}.'
            )
        
        if (extra_response_headers is not None) and (not extra_response_headers):
            extra_response_headers = None
        
        self = object.__new__(cls)
        self.loop = loop
        self.handler = handler
        self.web_sockets = set()
        self.close_connection_task = None
        self.server = None
        self.protocol_parameters = (
            handler, host, port, is_ssl, origin, available_extensions, available_subprotocols, extra_response_headers,
            request_processor, subprotocol_selector, web_socket_keyword_parameters
        )
        
        factory = partial_func(protocol, self,)
        server = await loop.create_server_to(factory, host, port, ssl = ssl, **server_keyword_parameters)
        
        self.server = server
        await server.start()
        
        return self
    
    
    def register(self, protocol):
        """
        Registers a newly created server side web socket to the web socket server itself.
        
        Parameters
        ----------
        protocol : ``WebSocketServerProtocol``, `object`
            The connected server side web socket.
        """
        self.web_sockets.add(protocol)
    
    
    def unregister(self, protocol):
        """
        Unregisters a newly created server side web socket from the web socket server itself.
        
        Parameters
        ----------
        protocol : ``WebSocketServerProtocol``, `object`
            The disconnected server side web socket.
        """
        self.web_sockets.discard(protocol)
    
    
    def is_serving(self):
        """
        Returns whether the web socket server is serving.
        
        Returns
        -------
        is_serving : `bool`
        """
        server = self.server
        if server is None:
            return False
        
        if server.sockets is None:
            return False
        
        return True
    
    
    def close(self):
        """
        Closes the web socket server. Returns a closing task, what can be awaited.
        
        Returns
        -------
        close_connection_task : ``Task`` of ``_close``
            Close connection task, what's result is set, when closing of the web socket is done.
            
            Should not be cancelled.
        """
        close_connection_task = self.close_connection_task
        if close_connection_task is None:
            close_connection_task = Task(self.loop, self._close())
            self.close_connection_task = close_connection_task
        
        return close_connection_task
    
    
    async def _close(self):
        """
        Closes the web socket server. If the web socket task is already closed does nothing.
        
        This method is a coroutine.
        """
        server = self.server
        if server is None:
            return
        
        server.close()
        await server.wait_closed()
        
        loop = self.loop
        
        # Skip 1 full loop
        await skip_poll_cycle(loop)
        
        web_sockets = self.web_sockets
        if web_sockets:
            await TaskGroup(loop, (loop.create_task(web_socket.close(1001)) for web_socket in web_sockets)).wait_all()
            
        if web_sockets:
            tasks = []
            for web_socket in web_sockets:
                task = web_socket.handler_task
                if task is None:
                    continue
                
                tasks.append(task)
            
            task = None
            if tasks:
                future = TaskGroup(loop, tasks).wait_all()
                tasks = None
                await future
    
    
    @property
    def websockets(self):
        """
        Deprecated and will be removed in 2025 august. Please use ``.web_sockets` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.websockets` is deprecated and will be removed in 2025 august. '
                f'Please use `web_sockets` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.web_sockets
