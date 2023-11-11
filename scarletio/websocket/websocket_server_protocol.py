__all__ = ('WebSocketCommonProtocol',)

import hashlib
from base64 import b64decode, b64encode
from binascii import Error as BinasciiError
from email.utils import formatdate

from ..core import AsyncQueue, CancelledError, Future, Lock, Task, write_exception_async
from ..utils import IgnoreCaseMultiValueDictionary, is_coroutine
from ..web_common import AbortHandshake, InvalidHandshake, InvalidOrigin, InvalidUpgrade, PayloadError
from ..web_common.header_building_and_parsing import (
    build_extensions, parse_connections, parse_extensions, parse_subprotocols, parse_upgrades
)
from ..web_common.headers import (
    CONNECTION, CONTENT_LENGTH, CONTENT_TYPE, DATE, ORIGIN, SEC_WEBSOCKET_ACCEPT, SEC_WEBSOCKET_EXTENSIONS,
    SEC_WEBSOCKET_KEY, SEC_WEBSOCKET_PROTOCOL, SEC_WEBSOCKET_VERSION, SERVER, UPGRADE
)

from .websocket_common_protocol import (
    BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, SERVICE_UNAVAILABLE, SWITCHING_PROTOCOLS, UPGRADE_REQUIRED,
    WEBSOCKET_KEY, WebSocketCommonProtocol
)


class WebSocketServerProtocol(WebSocketCommonProtocol):
    """
    Asynchronous server side websocket protocol implementation.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether the protocol received end of file.
    _chunks : `deque` of `bytes`
        Right feed, left pop queue, used to store the received data chunks.
    _exception : `None`, `BaseException`
        Exception set by ``.set_exception``, when an unexpected exception occur meanwhile reading from socket.
    _loop : ``EventThread``
        The event loop to what the protocol is bound to.
    _offset : `int`
        Byte offset, of the used up data of the most-left chunk.
    _paused : `bool`
        Whether the protocol's respective transport's reading is paused. Defaults to `False`.
        
        Also note, that not every transport supports pausing.
    _payload_reader : `None`, `GeneratorType`
        Payload reader generator, what gets the control back, when data, eof or any exception is received.
    _payload_waiter : `None` of ``Future``
        Payload waiter of the protocol, what's result is set, when the ``.payload_reader`` generator returns.
        
        If cancelled or marked by done or any other methods, the payload reader will not be cancelled.
    _transport : `None`, `object`
        Asynchronous transport implementation. Is set meanwhile the protocol is alive.
    _drain_waiter : `None`, ``Future``
        A future, what is used to block the writing task, till it's writen data is drained.
    _drain_lock : ``Lock``
        Asynchronous lock to ensure, that only `1` frame is written in `1` time.
    close_code : `int`
        The websocket's close code if applicable. Defaults to `0`.
    close_connection_task : `None`, ``Task`` of ``.close_connection``
        A task, what is present meanwhile the websocket is closing to avoid race condition.
    close_timeout : `float`
        The maximal duration in seconds what is waited for response after close frame is sent. Defaults to `10.0`.
    close_reason : `None`, `str`
        The reason, why the websocket was closed. Set only after the websocket is closed. Close reason might not be
        received tho.
    connection_lost_waiter : ``Future``
        A future, what's result is set as `None`, when the connection is closed. Used to wait for close frames.
        
        ``shield`` it if using from outside.
    extensions : `None` or (`list` of `object`)
        Web socket extensions. Defaults to `None`, if there is not any.
    host : `str`
        The respective server's address to connect to.
    max_queue : `None`, `int`
        Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of it is removed.
         Defaults to `None`.
    max_size : `int`
        Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised. Defaults to `67108864` bytes.
    messages : ``AsyncQueue``
        An asynchronous queue of the received messages.
    is_ssl : `bool`
        Whether the connection is secure. Defaults to `False`.
    pings : `OrderedDict` of (`bytes`, ``Future``) items
        An ordered dictionary of ping payloads and of their waiter futures.
    port : `int`
        The respective server's port to connect to.
    state : `str`
        The websocket's state.
        
        Can be set as one of the following values:
        
        +-------------------------------+-------------------+
        | Respective name               | Value             |
        +===============================+===================+
        | WEBSOCKET_STATE_CONNECTING    | `1`               |
        +-------------------------------+-------------------+
        | WEBSOCKET_STATE_OPEN          | `2`               |
        +-------------------------------+-------------------+
        | WEBSOCKET_STATE_CLOSING       | `3`               |
        +-------------------------------+-------------------+
        | WEBSOCKET_STATE_CLOSED        | `4`               |
        +-------------------------------+-------------------+
        
        Note, that state == compared by memory address and not by value.
    subprotocol : `None`, `str`
        Chosen subprotocol at handshake. Defaults to `None` and might be set as `str`. Chosen from the available
        subprotocols by their priority order.
    transfer_data_exception : `None`, `BaseException``
        Exception catched meanwhile processing received data.
    transfer_data_task : `None`, ``Task`` of ``.transfer_data``
        Data receiving task.
    available_extensions : `None` or (`list` of `object`)
        Available websocket extensions. Defaults to `None`.
        
        Each websocket extension should have the following `4` attributes / methods:
        - `name`: `str`. The extension's name.
        - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
        - `decode` : `callable`. Decoder method, what processes a received websocket frame. Should accept `2`
            parameters: The respective websocket ``WebSocketFrame``, and the ˙max_size` as `int`, what describes the
            maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
        - `encode` : `callable`. Encoder method, what processes the websocket frames to send. Should accept `1`
            parameter, the respective websocket ``WebSocketFrame``.
    available_subprotocols : `None` or (`list` of `str`)
        A list of supported subprotocols in order of decreasing preference.
    extra_response_headers : ``IgnoreCaseMultiValueDictionary``, `dict-like` with (`str`, `str`) items
        Extra response headers.
    handler : `async-callable`
        An asynchronous callable, what will handle a websocket connection.
        
        Should be given as an `async-callable` accepting `1` parameter the respective asynchronous server side
        websocket protocol implementations.
    handler_task : `None`, ``Task`` of ``.lifetime_handler``
        Handles the connected websocket meanwhile it is alive.
    origin : `None`, `str`
        Value of the Origin header.
    request_processor : `None`, `callable`
        An optionally asynchronous callable, what processes the initial requests from the potential clients.
        
        Should accept the following parameters:
        - `path` : `str`. The requested path.
        - `request_headers` : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`). The request's headers.
        
        The `request_processor` on accepted request should return `None`, otherwise a `tuple` of
        ``AbortHandshake`` parameters.
    server : ``WSServer``
        The owner websocket server instance.
    subprotocol_selector `None`, `callable`
        User hook to select subprotocols. Should accept the following parameters:
        - `parsed_header_subprotocols` : `list` of `str`. The subprotocols supported by the client.
        - `available_subprotocols` : `list` of `str`. The subprotocols supported by the server.
    request : `None`, ``RawRequestMessage``
        The received http request if applicable.
    response_headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        The server websocket's response's headers if applicable.
    """
    is_client = False
    
    __slots__ = (
        'available_extensions', 'available_subprotocols', 'extra_response_headers', 'handler', 'handler_task',
        'origin', 'origin', 'request_processor', 'server', 'subprotocol_selector', 'request', 'response_headers'
    )
    
    def __new__(cls, server):
        """
        Creates a new ``WebSocketServerProtocol`` with the given parameters.
        
        This method is usually wrapped into a partial function.
        
        Parameters
        ----------
        server : ``WSServer``
            The parent websocket server.
        """
        handler, host, port, is_ssl, origin, available_extensions, available_subprotocols , extra_response_headers, \
        request_processor, subprotocol_selector, websocket_kwargs = server.protocol_parameters
        
        self = WebSocketCommonProtocol.__new__(cls, server.loop, host, port, is_ssl = is_ssl, **websocket_kwargs)
        self.handler = handler
        self.server = server
        self.origin = origin
        self.available_extensions = available_extensions
        self.available_subprotocols = available_subprotocols
        self.extra_response_headers = extra_response_headers
        self.request_processor = request_processor
        self.subprotocol_selector = subprotocol_selector
        self.handler_task = None
        
        self.request = None
        self.response_headers = None
        self.origin = None
        
        return self
    
    
    def connection_made(self, transport):
        """
        Called when a connection is made.
        
        Parameters
        ----------
        transport : `object`
            Asynchronous transport implementation, what calls the protocol's ``.data_received`` when data is
            received.
        """
        WebSocketCommonProtocol.connection_made(self, transport)
        self.server.register(self)
        self.handler_task = Task(self._loop, self.lifetime_handler())
    
    
    async def lifetime_handler(self):
        """
        The asynchronous websocket protocol's main "lifetime" task.
        
        This method is a coroutine.
        """
        try:
            # handshake returns True if it succeeded
            if not (await self.handshake()):
                return
            
            try:
                await self.handler(self)
            except (GeneratorExit, CancelledError):
                raise
            
            except BaseException as err:
                write_exception_async(
                    err,
                    [
                        'Unhandled exception occurred at',
                        self.__class__.__name__,
                        '.lifetime_handler meanwhile running: ',
                        repr(self.handler),
                        '\n',
                    ],
                    loop = self._loop,
                )
                return
            
            await self.close()
        except:
            # We will let Task.__del__ to render the exception...
            
            transport = self._transport
            if transport is None:
                raise
                
            transport.close()
            transport.abort()
            raise
        
        finally:
            self.handler_task = None
            self.server.unregister(self)
    
    
    async def handshake(self):
        """
        Handles a received websocket connect request.
        
        This method is a coroutine.
        
        Returns
        -------
        handshake_succeeded : `bool`
            If the websocket handshake succeeded and starting, it's handler can begin, returns `True`.
        """
        try:
            self.request = request = await self.set_payload_reader(self._read_http_request())
            
            request_headers = request.headers
            if self.server.is_serving():
                path = request.path
                
                request_processor = self.request_processor
                if request_processor is None:
                    early_response = None
                else:
                    early_response = request_processor(path, request_headers)
                    if is_coroutine(early_response):
                        early_response = await early_response
                
                if (early_response is not None):
                    raise AbortHandshake(
                        *early_response,
                        request = request,
                    )
                
            else:
                raise AbortHandshake(
                    SERVICE_UNAVAILABLE,
                    'Server is shutting down.',
                    request = request,
                )
            
            connections = []
            connection_headers = request_headers.get_all(CONNECTION)
            if (connection_headers is not None):
                for connection_header in connection_headers:
                    connections.extend(parse_connections(connection_header))
        
            if not any(value.lower() == 'upgrade' for value in connections):
                raise InvalidUpgrade(
                    f'Invalid connection, no upgrade found, got {connections!r}.'
                )
            
            upgrade = []
            upgrade_headers = request_headers.get_all(UPGRADE)
            if (upgrade_headers is not None):
                for upgrade_header in upgrade_headers:
                    upgrade.extend(parse_upgrades(upgrade_header))
            
            if len(upgrade) != 1 and upgrade[0].lower() != 'websocket': # ignore case
                raise InvalidUpgrade(
                    f'Expected \'WebSocket\' for \'Upgrade\', but got {upgrade!r}.'
                )
            
            received_keys = request_headers.get_all(SEC_WEBSOCKET_KEY)
            if received_keys is None:
                raise InvalidHandshake(
                    f'Missing {SEC_WEBSOCKET_KEY!r} from headers',
                    request = request,
                )
            
            if len(received_keys) > 1:
                raise InvalidHandshake(
                    f'Multiple {SEC_WEBSOCKET_KEY!r} values at headers',
                    request = request,
                )
            
            key = received_keys[0]
        
            try:
                raw_key = b64decode(key.encode(), validate = True)
            except BinasciiError:
                raise InvalidHandshake(
                    f'Invalid {SEC_WEBSOCKET_KEY!r}: {key!r}.',
                    request = request)
            
            if len(raw_key) != 16:
                raise InvalidHandshake(
                    f'Invalid {SEC_WEBSOCKET_KEY!r}, should be length 16; {key!r}.',
                    request = request,
                )
            
            sw_version = request_headers.get_all(SEC_WEBSOCKET_VERSION)
            if sw_version is None:
                raise InvalidHandshake(
                    f'Missing {SEC_WEBSOCKET_VERSION!r} values at headers.',
                    request = request,
                )
            
            if len(sw_version) > 1:
                raise InvalidHandshake(
                    f'Multiple {SEC_WEBSOCKET_VERSION!r} values at headers.',
                    request = request,
                )
            
            sw_version = sw_version[0]
            if sw_version != '13':
                raise InvalidHandshake(
                    f'Invalid {SEC_WEBSOCKET_VERSION!r}: {sw_version!r}.',
                    request = request,
                )
            
            while True:
                origin = self.origin
                if (origin is None):
                    origin = None
                    break
                
                origin_headers = request_headers.get_all(ORIGIN)
                
                if (origin_headers is None):
                    raise InvalidOrigin('No origin at header.')
                
                if len(origin_headers) > 1:
                    raise InvalidOrigin('More than 1 origin at header.')
                
                origin = origin_headers[0]
                
                if origin in origin:
                    break
                    
                raise InvalidOrigin(origin)
            
            self.origin = origin
            
            while True:
                accepted_extensions = []
                
                available_extensions = self.available_extensions
                if (available_extensions is None):
                    extension_header = None
                    break
                
                extension_headers_ = request_headers.get_all(SEC_WEBSOCKET_EXTENSIONS)
                if (extension_headers_ is None):
                    extension_header = None
                    break
                
                extension_headers = []
                parsed_extension_values = []
                for extension_header_ in extension_headers_:
                    parsed_extension_values.extend(parse_extensions(extension_header_))
                
                for name, params in parsed_extension_values:
                    for extension in available_extensions:
                        # do names and params match?
                        if extension.name == name and extension.are_valid_params(params, accepted_extensions):
                            accepted_extensions.append(extension)
                            extension_headers.append((name, params))
                            break
                    else:
                        # no matching extension
                        raise InvalidHandshake(
                            f'Unsupported extension: name = {name!r}, params = {params!r}.',
                            request = request,
                        )
                    
                    # If we didn't break from the loop, no extension in our list matched what the client sent. The
                    # extension is declined.
                
                # Serialize extension header.
                if extension_headers:
                    extension_header = build_extensions(extension_headers)
                    break
                
                extension_header = None
                break
            
            self.extensions = accepted_extensions
            
            
            while True:
                available_subprotocols = self.available_subprotocols
                if (available_subprotocols is None):
                    selected_subprotocol = None
                    break
                    
                protocol_headers = request_headers.get_all(SEC_WEBSOCKET_PROTOCOL)
                if (protocol_headers is None):
                    selected_subprotocol = None
                    break
                
                parsed_header_subprotocols = []
                for protocol_header in protocol_headers:
                    parsed_header_subprotocols.extend(parse_subprotocols(protocol_header))
                
                subprotocol_selector = self.subprotocol_selector
                if (subprotocol_selector is not None):
                    selected_subprotocol = subprotocol_selector(parsed_header_subprotocols, available_subprotocols)
                    break
                    
                subprotocols = set(parsed_header_subprotocols)
                subprotocols.intersection_update(available_subprotocols)
                
                if not subprotocols:
                    selected_subprotocol = None
                    break
                
                lowest_priority = len(parsed_header_subprotocols) + len(available_subprotocols)
                selected_subprotocol = None
                
                for subprotocol in subprotocols:
                    priority = parsed_header_subprotocols.index(subprotocol) + available_subprotocols.index(subprotocol)
                    if priority < lowest_priority:
                        lowest_priority = priority
                        selected_subprotocol = subprotocol
                
                break
            
            self.subprotocol = selected_subprotocol
            
            response_headers = IgnoreCaseMultiValueDictionary()
    
            response_headers[UPGRADE] = 'websocket'
            response_headers[CONNECTION] = 'Upgrade'
            response_headers[SEC_WEBSOCKET_ACCEPT] = \
                b64encode(hashlib.sha1((key + WEBSOCKET_KEY).encode()).digest()).decode()
            
            if (extension_header is not None):
                response_headers[SEC_WEBSOCKET_EXTENSIONS] = extension_header
            
            if (selected_subprotocol is not None):
                response_headers[SEC_WEBSOCKET_PROTOCOL] = selected_subprotocol
            
            extra_response_headers = self.extra_response_headers
            if (extra_response_headers is not None):
                for key, value in extra_response_headers.items():
                    response_headers[key] = value
            
            response_headers.setdefault(DATE, formatdate(usegmt = True))
            response_headers.setdefault(SERVER, '')
            
            self.response_headers = response_headers
            self.write_http_response(SWITCHING_PROTOCOLS, response_headers)
            
            self.connection_open()
        
        except (GeneratorExit, CancelledError):
            raise
        
        except ConnectionError as err:
            write_exception_async(
                err,
                [
                    'Unhandled exception occurred at ',
                    self.__class__.__name__,
                    '.handshake, when handshaking:\n'
                ],
                loop = self._loop,
            )
            return False
        
        except BaseException as err:
            if isinstance(err, AbortHandshake):
                status = err.code
                headers = err.headers
                if headers is None:
                    headers = IgnoreCaseMultiValueDictionary()
                body = err.message
                if not body.endswith('\n'):
                    body = body + b'\n'
            
            elif isinstance(err, InvalidOrigin):
                status = FORBIDDEN
                headers = IgnoreCaseMultiValueDictionary()
                body = f'Failed to open a WebSocket connection: {err}.\n'.encode()
            
            elif isinstance(err, InvalidUpgrade):
                status = UPGRADE_REQUIRED
                headers = IgnoreCaseMultiValueDictionary()
                headers[UPGRADE] = 'websocket'
                body = (
                    f'Failed to open a WebSocket connection: {err}.\n\n'
                    f'You cannot access a WebSocket server directly with a browser. You need a WebSocket client.\n'
                ).encode()
            
            elif isinstance(err, InvalidHandshake):
                status = BAD_REQUEST
                headers = IgnoreCaseMultiValueDictionary()
                body = f'Failed to open a WebSocket connection: {err.message}.\n'.encode()
            
            elif isinstance(err, PayloadError):
                status = BAD_REQUEST
                headers = IgnoreCaseMultiValueDictionary()
                body = f'Invalid request body: {err}.\n'.encode()
            
            else:
                status = INTERNAL_SERVER_ERROR
                headers = IgnoreCaseMultiValueDictionary()
                body = b'Failed to open a WebSocket connection.\n'
            
            headers.setdefault(DATE, formatdate(usegmt = True))
            headers.setdefault(SERVER, '')
            headers.setdefault(CONTENT_LENGTH, repr(len(body)))
            headers.setdefault(CONTENT_TYPE, 'text/plain')
            headers.setdefault(CONNECTION, 'close')
            
            try:
                self.write_http_response(status, headers, body = body)
                self.fail_connection()
                await self.wait_for_connection_lost()
            except (GeneratorExit, CancelledError):
                raise
            
            except BaseException as err2:
                write_exception_async(
                    err2,
                    [
                        'Unhandled exception occurred at ',
                        self.__class__.__name__,
                        '.handshake, when handling an other exception;',
                        repr(err),
                        ':\n',
                    ],
                    loop = self._loop,
                )
            return False
        
        return True
