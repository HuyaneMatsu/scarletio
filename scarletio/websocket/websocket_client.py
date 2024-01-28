__all__ = ('WebSocketClient',)

import hashlib
from base64 import b64encode
from os import urandom

from ..core import AsyncQueue, Future, Lock
from ..utils import IgnoreCaseMultiValueDictionary, include
from ..web_common import BasicAuth, HttpVersion11, InvalidHandshake, URL
from ..web_common.header_building_and_parsing import (
    build_extensions, build_subprotocols, parse_connections, parse_extensions, parse_subprotocols, parse_upgrades
)
from ..web_common.headers import (
    AUTHORIZATION, CONNECTION, HOST, METHOD_GET, ORIGIN, SEC_WEBSOCKET_ACCEPT, SEC_WEBSOCKET_EXTENSIONS,
    SEC_WEBSOCKET_KEY, SEC_WEBSOCKET_PROTOCOL, SEC_WEBSOCKET_VERSION, UPGRADE
)

from .websocket_common_protocol import WEBSOCKET_KEY, WebSocketCommonProtocol


HTTPClient = include('HTTPClient')


class WebSocketClient(WebSocketCommonProtocol):
    """
    Asynchronous websocket client implementation.
    
    Inherits common websocket features from the ``WebSocketCommonProtocol`` class.
    
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
        WebSocket extensions. Defaults to `None`, if there is not any.
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
    
    Class Attributes
    ----------------
    is_client : `bool` = `True`
        Whether the websocket protocol is client or server side.
    """
    is_client = True
    
    __slots__ = ()
    
    async def __new__(
        cls,
        loop,
        url,
        *,
        origin = None,
        available_extensions = None,
        available_subprotocols = None,
        headers = None,
        http_client = None,
        **websocket_keyword_parameters,
    ):
        """
        Connects the websocket client to the given `url`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop, what the protocol uses for it's asynchronous tasks.
        url : `str`, ``URL``
            The url to connect to.
        origin : `None`, `str` = `None`, Optional (Keyword only)
            Value of the Origin header.
        available_extensions : `None`, `list` of `object` = `None`, Optional (Keyword only)
            Available websocket extensions. Defaults to `None`.
            
            Each websocket extension should have the following `4` attributes / methods:
            - `name`: `str`. The extension's name.
            - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
            - `decode` : `callable`. Decoder method, what processes a received websocket frame. Should accept `2`
                parameters: The respective websocket ``WebSocketFrame``, and the ˙max_size` as `int`, what describes the
                maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
            - `encode` : `callable`. Encoder method, what processes the websocket frames to send. Should accept `1`
                parameter, the respective websocket ``WebSocketFrame``.
        available_subprotocols : `None`, `list` of `str` = `None`, Optional (Keyword only)
            A list of supported subprotocols in order of decreasing preference.
        headers : `None`, ``IgnoreCaseMultiValueDictionary``, `dict-like` with (`str`, `str`) items = `None`
                , Optional (Keyword only)
            Extra request headers.
        http_client : `None`, ``HTTPClient`` = `None`, Optional (Keyword only)
            Http client to use to connect the websocket.
        **websocket_keyword_parameters : Keyword parameters
            Additional keyword parameters to create the websocket with.
        
        Other Parameters
        ----------------
        close_timeout : `float`, Optional (Keyword only)
            The maximal duration in seconds what is waited for response after close frame is sent. Defaults to `10.0`.
        max_size : `int`, Optional (Keyword only)
            Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised. Defaults to `67108864`
            bytes.
        max_queue : `None`, `int`, Optional (Keyword only)
            Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of it is
            removed.
        
        Returns
        -------
        self : ``WebSocketClient``
        
        Raises
        ------
        ConnectionError
            - Too many redirects.
            - Would be redirected to not `http`, `https`.
            - Connector closed.
        TypeError
            If `extra_response_headers` is not given as `None`, neither as `dict-like`.
        ValueError
            - Host could not be detected from `url`.
            - Received extension header is incorrect.
            - Received connection header is incorrect.
        TimeoutError
            - Did not receive answer in time.
        InvalidHandshake
            - The response's status code is invalid (not `101`).
            - The response's connection headers do not contain `'upgrade'`.
            - The response's headers contains 0 or more than 1 upgrade headers.
            - The response's upgrade header is not `'WebSocket'`.
            - The response's headers contain sec websocket accept 0 or more than 1 times.
            - The response's secret key not matches the send one.
            - No extensions are supported, but still received.
            - Unsupported extension received.
            - No subprotocols are supported, but still received.
            - Multiple subprotocols received.
            - Unsupported subprotocol received.
            - The response's http version is unsupported (not `HTTP1.1`).
        """
        if http_client is None:
            http_client = HTTPClient(loop)
        
        url = URL(url)
        is_ssl = (url.scheme == 'wss')
        
        # building headers
        sec_key = b64encode(urandom(16)).decode()
        request_headers = IgnoreCaseMultiValueDictionary()
        
        request_headers[UPGRADE] = 'websocket'
        request_headers[CONNECTION] = 'Upgrade'
        request_headers[SEC_WEBSOCKET_KEY] = sec_key
        request_headers[SEC_WEBSOCKET_VERSION] = '13'
        
        if url.port == (443 if is_ssl else 80):
            request_host = url.host
        else:
            request_host = f'{url.host}:{url.port}'
        
        request_headers[HOST] = request_host
        
        user = url.user
        password = url.password
        if (user is not None) or (password is not None):
            request_headers[AUTHORIZATION] = BasicAuth(user, password).encode()
        
        if origin is not None:
            request_headers[ORIGIN] = origin
        
        if available_extensions is not None:
            request_headers[SEC_WEBSOCKET_EXTENSIONS] = build_extensions(available_extensions)
        
        if available_subprotocols is not None:
            request_headers[SEC_WEBSOCKET_PROTOCOL] = build_subprotocols(available_subprotocols)
        
        if headers is not None:
            # we use especially items, so we check that
            if isinstance(headers, IgnoreCaseMultiValueDictionary) or hasattr(type(headers), 'items'):
                for name, value in headers.items():
                    request_headers[name] = value
            else:
                raise TypeError(
                    '`extra_response_headers` can be `dict-like` with `.items` method, got '
                    f'{headers.__class__.__name__}; {headers!r}.'
                )
        
        async with http_client.request(METHOD_GET, url, request_headers) as response:
           
            if response.raw_message.version != HttpVersion11:
                raise InvalidHandshake(
                    f'Unsupported HTTP version: {response.raw_message.version}.',
                    response = response,
                )
            
            if response.status != 101:
                raise InvalidHandshake(
                    f'Invalid status code: {response.status!r}.',
                    response = response,
                )
            
            response_headers = response.headers
            connections = []
            received_connections = response_headers.get_all(CONNECTION,)
            if (received_connections is not None):
                for received_connection in received_connections:
                    connections.extend(parse_connections(received_connection))
            
            if not any(value.lower() == 'upgrade' for value in connections):
                raise InvalidHandshake(
                    f'Invalid connection, no upgrade found, got {connections!r}.',
                    response = response,
                )
            
            upgrade = []
            received_upgrades = response_headers.get_all(UPGRADE)
            if (received_upgrades is not None):
                for received_upgrade in received_upgrades:
                    upgrade.extend(parse_upgrades(received_upgrade))
            
            if len(upgrade) != 1 and upgrade[0].lower() != 'websocket': # ignore case
                raise InvalidHandshake(
                    f'Expected \'WebSocket\' for \'Upgrade\', but got {upgrade!r}.',
                    response = response,
                )
            
            expected_key = b64encode(hashlib.sha1((sec_key + WEBSOCKET_KEY).encode()).digest()).decode()
            received_keys = response_headers.get_all(SEC_WEBSOCKET_ACCEPT)
            if received_keys is None:
                raise InvalidHandshake(
                    f'Expected 1 secret key {expected_key!r}, but received 0.',
                    response = response,
                )
            if len(received_keys) > 1:
                raise InvalidHandshake(
                    f'Expected 1 secret key {expected_key!r}, but received more: {received_keys!r}.',
                    response = response,
                )
            
            received_key = received_keys[0]
            if received_key != expected_key:
                raise InvalidHandshake(
                    f'Expected secret key {expected_key}, but got {received_key!r}.',
                    response = response,
                )
            
            #extensions
            accepted_extensions = []
            received_extensions = response_headers.get_all(SEC_WEBSOCKET_EXTENSIONS)
            if (received_extensions is not None):
                if available_extensions is None:
                    raise InvalidHandshake(
                        f'No extensions supported, but received {received_extensions!r}.',
                        response = response,
                    )
                
                parsed_extension_values = []
                for value in received_extensions:
                    parsed_extension_values.extend(parse_extensions(value))
                
                for name, params in parsed_extension_values:
                    for extension in available_extensions:
                        # do names and params match?
                        if extension.name == name and extension.are_valid_params(params, accepted_extensions):
                            accepted_extensions.append(extension)
                            break
                    else:
                        # no matching extension
                        raise InvalidHandshake(
                            f'Unsupported extension: name = {name!r}, params = {params!r}.',
                            response = response,
                        )
            
            subprotocol = None
            received_subprotocols = response_headers.get_all(SEC_WEBSOCKET_PROTOCOL)
            if (received_subprotocols is not None):
                if available_subprotocols is None:
                    raise InvalidHandshake(
                        f'No subprotocols supported, but received {received_subprotocols!r}.',
                        response = response,
                    )
                
                parsed_subprotocol_values = []
                for received_subprotocol in received_subprotocols:
                    parsed_subprotocol_values.extend(parse_subprotocols(received_subprotocol))
                
                if len(parsed_subprotocol_values) > 1:
                    raise InvalidHandshake(
                        f'Multiple subprotocols: {parsed_subprotocol_values!r}.',
                        response = response,
                    )
                
                subprotocol = parsed_subprotocol_values[0]
                
                if subprotocol not in available_subprotocols:
                    raise InvalidHandshake(
                        f'Unsupported subprotocol: {subprotocol}.',
                        response = response,
                    )
            
            connection = response.connection
            protocol = connection.protocol
            connection.detach()
            
            self = protocol.isekai_into(cls)
            self._set_common_websocket_attributes(url.host, url.port, is_ssl = is_ssl, **websocket_keyword_parameters)
            self.extensions = accepted_extensions
            self.subprotocol = subprotocol
            self._transport.set_protocol(self)
        
        self.connection_open()
        return self
