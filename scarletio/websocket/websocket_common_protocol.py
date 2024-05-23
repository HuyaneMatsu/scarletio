__all__ = ('WebSocketCommonProtocol', )

import codecs, reprlib
import http as module_http
from collections import OrderedDict
from os import urandom

from ..core import AsyncQueue, CancelledError, Future, Lock, Task, shield, write_exception_async
from ..utils import include
from ..web_common import ConnectionClosed, HttpReadWriteProtocol, PayloadError, WebSocketFrame, WebSocketProtocolError
from ..web_common.websocket_frame import (
    WEBSOCKET_DATA_OPERATIONS, WEBSOCKET_OPERATION_BINARY, WEBSOCKET_OPERATION_CLOSE, WEBSOCKET_OPERATION_CONTINUOUS,
    WEBSOCKET_OPERATION_PING, WEBSOCKET_OPERATION_PONG, WEBSOCKET_OPERATION_TEXT
)


FORBIDDEN = module_http.HTTPStatus.FORBIDDEN
UPGRADE_REQUIRED = module_http.HTTPStatus.UPGRADE_REQUIRED
BAD_REQUEST = module_http.HTTPStatus.BAD_REQUEST
INTERNAL_SERVER_ERROR = module_http.HTTPStatus.INTERNAL_SERVER_ERROR
SERVICE_UNAVAILABLE = module_http.HTTPStatus.SERVICE_UNAVAILABLE
SWITCHING_PROTOCOLS = module_http.HTTPStatus.SWITCHING_PROTOCOLS

WEBSOCKET_STATE_CONNECTING = 1
WEBSOCKET_STATE_OPEN = 2
WEBSOCKET_STATE_CLOSING = 3
WEBSOCKET_STATE_CLOSED = 4

WEBSOCKET_KEY = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

EXTERNAL_CLOSE_CODES = (1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011, 1013)

HTTPClient = include('HTTPClient')

DECODER = codecs.getincrementaldecoder('utf-8')(errors = 'strict')


class WebSocketCommonProtocol(HttpReadWriteProtocol):
    """
    WebSocket protocol base which implements common functions between the client and the server side.
    
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
    __slots__ = (
        '_drain_lock', 'close_code', 'close_connection_task', 'close_timeout', 'close_reason',
        'connection_lost_waiter', 'extensions', 'host', 'is_ssl', 'max_queue', 'max_size', 'messages', 'pings', 'port',
        'state', 'subprotocol', 'transfer_data_exception', 'transfer_data_task'
    )
    
    is_client = True # placeholder for subclasses
    
    def __new__(cls, loop, host, port, *, is_ssl = False, close_timeout = 10.0, max_size = 1 << 26, max_queue = None):
        """
        Initializes the ``WebSocketCommonProtocol`` with setting it's common attributes.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop, what the protocol uses for it's asynchronous tasks.
        host : `str`
            The respective server's address to connect to.
        port : `int`
            The respective server's port to connect to.
        is_ssl : `bool` = `False`, Optional (Keyword only)
            Whether the connection is secure.
        close_timeout : `float` = `10.0`, Optional (Keyword only)
            The maximal duration in seconds what is waited for response after close frame is sent
        max_size : `int` = `67108864`, Optional (Keyword only)
            Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised.
        max_queue : `None`, `int` = `None`, Optional (Keyword only)
            Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of it is
            removed.
        """
        self = HttpReadWriteProtocol.__new__(cls, loop)
        self._set_common_websocket_attributes(host, port, is_ssl, close_timeout, max_size, max_queue)
        return self
    
    
    def _set_common_websocket_attributes(
        self, host, port, is_ssl, close_timeout = 10.0, max_size = 1 << 26, max_queue = None
    ):
        """
        Sets the common websocket specific attributes for the protocol.
        
        Parameters
        ----------
        host : `str`
            The respective server's address to connect to.
        port : `int`
            The respective server's port to connect to.
        is_ssl : `bool`
            Whether the connection is secure. Defaults to `False`.
        close_timeout : `float` = `10.0`, Optional
            The maximal duration in seconds what is waited for response after close frame is sent.
        max_size : `int` = `67108864`, Optional
            Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised.
            bytes.
        max_queue : `None`, `int` = `None`, Optional
            Max queue size of ``.messages``. If a new payload is added to a full queue, the oldest element of it is
            removed.
        """
        self.host = host
        self.port = port
        self.is_ssl = is_ssl
        self.close_timeout = close_timeout
        self.max_size = max_size # set it to a BIG number if u wanna ignore max size
        self.max_queue = max_queue
        
        self._drain_lock = Lock(self._loop)
        
        self.state = WEBSOCKET_STATE_CONNECTING
        
        self.extensions = None # set from outside
        self.subprotocol = None # set from outside
        
        self.close_code = 0
        self.close_reason = None
        
        self.connection_lost_waiter = Future(self._loop)
        self.messages = AsyncQueue(loop = self._loop, max_length = max_queue)
        
        self.pings = OrderedDict()
        
        self.transfer_data_task = None
        self.transfer_data_exception = None
        self.close_connection_task = None
    
    
    def connection_open(self):
        """
        Method called when the connection is established at the end of the handshake.
        
        Marks the websocket as open and start it's ``.transfer_data_task`` and ``.close_connection_task``.
        """
        self.state = WEBSOCKET_STATE_OPEN
        loop = self._loop
        self.transfer_data_task = Task(loop, self.transfer_data())
        self.close_connection_task = Task(loop, self.close_connection())
    
    
    @property
    def local_address(self):
        """
        Local address of the connection as a `tuple` of host and port. If the connection is not open yet, returns
        `None`.
        
        Returns
        -------
        local_address : `None`, `tuple` of (`str`, `int`)
        """
        return self.get_extra_info('socket_name')
    
    
    @property
    def remote_address(self):
        """
        Remote address of the connection as a `tuple` of host and port. If the connection is not open yet, returns
        `None`.
        
        Returns
        -------
        remote_address : `None`, `tuple` of (`str`, `int`)
        """
        return self.get_extra_info('peer_name')
    
    
    @property
    def open(self):
        """
        Returns whether the websocket is open.
        
        If the websocket is closed, ``ConnectionClosed`` is raised when using it.
        
        Returns
        -------
        open : `bool`
        """
        if self.state != WEBSOCKET_STATE_OPEN:
            return False
        
        transfer_data_task = self.transfer_data_task
        if transfer_data_task is None:
            return False
        
        if transfer_data_task.is_done():
            return False
        
        return True
    
    
    @property
    def closed(self):
        """
        Returns whether the websocket is closed.
        
        Note, meanwhile connection is establishing, ``.open`` and ``.close`` will return `False`.
        
        Returns
        -------
        closed : `bool`
        """
        return self.state == WEBSOCKET_STATE_CLOSED
    
    
    def receive(self):
        """
        Returns a future, what can be awaited to receive the next message of the websocket.
        
        Returns
        -------
        future : ``Future``
            The future returns `bytes`, `str` respective to the received payload's type. If the websocket
            is closed, ``ConnectionClosed`` is raised.
        """
        return self.messages.get_result()
    
    
    def receive_no_wait(self):
        """
        Returns a future, what can be awaited to receive the next message of the websocket.
        
        Returns
        -------
        message : `bytes`, `str`
            The received payload.
        
        Raises
        ------
        IndexError
            There are no messages to retrieve right now.
        ConnectionClosed
            WebSocket closed.
        """
        return self.messages.result_no_wait()
    
    
    async def send(self, data):
        """
        Sends the given data with the websocket.
        
        This method is a coroutine.
        
        Parameters
        ----------
        data : `bytes-like`, `str`
            The data to send
        
        Raises
        ------
        TypeError
            `data` was not given as `bytes-like`, neither as `str`.
        ConnectionClosed
            WebSocket connection closed.
        Exception
            WebSocket connection not yet established.
        """
        await self.ensure_open()
        
        if isinstance(data, (bytes, bytearray, memoryview)):
            operation_code = WEBSOCKET_OPERATION_BINARY
        elif isinstance(data, str):
            operation_code = WEBSOCKET_OPERATION_TEXT
            data = data.encode('utf-8')
        else:
            raise TypeError(
                f'Data must be `bytes-like`, `str`, got: {data.__class__.__name__}; {reprlib.repr(data)}.'
            )
        
        await self.write_frame(operation_code, data)
    
    
    async def close(self, code = 1000, reason = ''):
        """
        Closes the websocket.
        
        Writes close frame first and then if we don't receive close frame response in ``.close_timeout``, then we
        cancel the connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        code : `int` = `1000`, Optional.
            WebSocket close code. Defaults to `1000`. Can be one of:
            `(1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011) | [3000:5000)`.
        reason : `str` = `''`, Optional
            WebSocket close reason. Can be given as empty string.
        
        Raises
        ------
        WebSocketProtocolError
            Close code is not given as one of `(1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011) | [3000:5000)`.
        """
        # if no close frame is received within the close_timeout we cancel the connection
        close_message = self._serialize_close(code, reason)
        write_close_frame_task = Task(self._loop, self.write_close_frame(close_message))
        write_close_frame_task.apply_timeout(self.close_timeout)
        try:
            await write_close_frame_task
        except TimeoutError:
            self.fail_connection()
        
        # if close() is cancelled during the wait, self.transfer_data_task is cancelled before the close_timeout
        # elapses
        transfer_data_task = self.transfer_data_task
        transfer_data_task.apply_timeout(self.close_timeout)
        try:
            await transfer_data_task
        except TimeoutError:
            pass
        
        # quit for the close connection task to close the TCP connection.
        await shield(self.close_connection_task, self._loop)
    
    
    @staticmethod
    def _serialize_close(code, reason):
        """
        Packs the given `code` and `reason` together into a close message.
        
        Parameters
        ----------
        code : `int`
            WebSocket close code. Can be one of:
            `(1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011) | [3000:5000)`.
        reason : `str`
            WebSocket close reason. Can be given as empty string.
        
        Returns
        -------
        close_message : `bytes`
        
        Raises
        ------
        WebSocketProtocolError
            Close code is not given as one of `(1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011) | [3000:5000)`.
        """
        if not (code in EXTERNAL_CLOSE_CODES or 2999 < code < 5000):
            raise WebSocketProtocolError(
                f'Status can be in range [3000:5000), got {code!r}.'
            )
        
        return code.to_bytes(2, 'big') + reason.encode('utf-8')
    
    async def ping(self, data = None):
        """
        Sends a ping to the other side and waits till answer is received.
        
        This method is a coroutine.
        
        Parameters
        ----------
        data : `None`, `bytes-like`, `str`
            Ping payload to send. Defaults to `None`.
            
            If the given or generated payload is already waiting for response, then will regenerate it, till a free
            one is hit.
        
        Raises
        ------
        TypeError
            `data` is not given neither as `None`, `bytes-like`, `str`.
        ConnectionClosed
            WebSocket connection closed.
        Exception
            WebSocket connection not yet established.
        """
        await self.ensure_open()
        
        if data is None:
            data = urandom(4)
        elif isinstance(data, (bytes, bytearray, memoryview)):
            pass
        elif isinstance(data, str):
            data = data.encode('utf-8')
        else:
            raise TypeError(
                f'Data must be `bytes-like`, `str`, got: {data.__class__.__name__}; {reprlib.repr(data)}.'
            )
        
        pings = self.pings
        while data in pings:
            data = urandom(4)
        
        waiter = Future(self._loop)
        pings[data] = waiter
        
        await self.write_frame(WEBSOCKET_OPERATION_PING, data)
        
        await waiter
    
    async def pong(self, data = None):
        """
        Sends a pong payload to the other side.
        
        This method is a coroutine.
        
        Parameters
        ----------
        data : `None`, `bytes-like`, `str`
            Ping payload to send. Defaults to `None`.
        
        Raises
        ------
        TypeError
            `data` is not given neither as `None`, `bytes-like`, `str`.
        ConnectionClosed
            WebSocket connection closed.
        Exception
            WebSocket connection not yet established.
        """
        await self.ensure_open()
        
        if data is None:
            data = urandom(4)
        elif isinstance(data, (bytes, bytearray, memoryview)):
            pass
        elif isinstance(data, str):
            data = data.encode('utf-8')
        else:
            raise TypeError(
                f'Data must be `bytes-like`, `str`, got: {data.__class__.__name__}; {reprlib.repr(data)}.'
            )
        
        await self.write_frame(WEBSOCKET_OPERATION_PONG, data)
    
    # Private methods - no guarantees.
    
    async def ensure_open(self):
        """
        Checks whether the websocket is still open.
        
        This method is a coroutine.
        
        Raises
        ------
        ConnectionClosed
            WebSocket connection closed.
        Exception
            WebSocket connection not yet established.
        """
        state = self.state
        if state == WEBSOCKET_STATE_OPEN:
            # if self.transfer_data_task exited without a closing handshake.
            if self.transfer_data_task.is_done():
                await shield(self.close_connection_task, self._loop)
                raise ConnectionClosed(self.close_code, None, self.close_reason)
            
            return
        
        if state == WEBSOCKET_STATE_CLOSED:
            raise ConnectionClosed(self.close_code, None, self.close_reason) from self.transfer_data_exception
        
        if state == WEBSOCKET_STATE_CLOSING:
            if not self.close_code:
                #if we started the closing handshake, wait for its completion
                await shield(self.close_connection_task, self._loop)
            
            raise ConnectionClosed(self.close_code, None, self.close_reason) from self.transfer_data_exception
        
        raise Exception('WebSocket connection isn\'t established yet.')
    
    
    async def transfer_data(self):
        """
        The transfer data task of a websocket keeps reading it's messages and putting it into it's ``.messages``
        ``AsyncQueue``.
        
        Meanwhile runs, it wrapped inside of a ``Task`` and can be accessed as ``.transfer_data_task``.
        
        This method is a coroutine.
        """
        try:
            while True:
                message = await self.read_message()
                # exit the loop when receiving a close frame.
                if message is None:
                    break
                
                self.messages.set_result(message)
        
        except GeneratorExit as err:
            exception = ConnectionClosed(1013, err)
            self.fail_connection(self.close_code or 1013)
            to_reraise = err
        
        except CancelledError as err:
            # we already failed connection
            exception = ConnectionClosed(self.close_code or 1000, err, self.close_reason)
            to_reraise = err
        
        except WebSocketProtocolError as err:
            exception = ConnectionClosed(1002, err)
            self.fail_connection(1002)
            to_reraise = None
        
        except (ConnectionError, EOFError, TimeoutError) as err:
            exception = ConnectionClosed(1006, err)
            self.fail_connection(1006)
            to_reraise = None
        
        except UnicodeDecodeError as err:
            exception = ConnectionClosed(1007, err)
            self.fail_connection(1007)
            to_reraise = None
        
        except PayloadError as err:
            exception = ConnectionClosed(1009, err)
            self.fail_connection(1009)
            to_reraise = None
        
        except BaseException as err:
            await write_exception_async(
                err,
                [
                    'Unexpected exception occurred at ',
                    repr(self),
                    '.transfer_data\n',
                ],
                loop = self._loop,
            )
            # should not happen
            exception = ConnectionClosed(1011, err)
            self.fail_connection(1011)
            to_reraise = None
        
        else:
            # connection was closed
            exception = ConnectionClosed(self.close_code or 1000, None, self.close_reason)
            to_reraise = None
            
            # If we are a client and we receive this, we closed our own
            # connection, there is no reason to wait for TCP abort
            if self.is_client:
                self.connection_lost_waiter.set_result_if_pending(None)
        
        if self.transfer_data_exception is None:
            self.transfer_data_exception = exception
            self.messages.set_exception(exception)
        
        if (to_reraise is not None):
            raise to_reraise
    
    
    async def read_message(self):
        """
        Reads a message from the websocket.
        
        This method is a coroutine.
        
        Returns
        -------
        message : `None`, `bytes`, `str`
            A received message. It's type depend on the frame's type. returns `None` if close frame was received.
        
        Raises
        ------
        WebSocketProtocolError
            - Unexpected op code.
            - Incomplete fragmented message.
            - If the reserved bits are not `0`.
            - If the frame is a control frame, but is too long for one.
            - If the websocket frame is fragmented frame. (Might be supported if people request is.)
            - If the frame operation_code is not any of the expected ones.
            - Close frame received with invalid status code.
            - Close frame too short.
        CancelledError
            ``.transfer_data_task`` cancelled.
        """
        frame = await self.read_data_frame(max_size = self.max_size)
        if frame is None: # close frame
            return
        
        if frame.operation_code == WEBSOCKET_OPERATION_TEXT:
            text = True
        elif frame.operation_code == WEBSOCKET_OPERATION_BINARY:
            text = False
        else: # frame.operation_code == OP_CONT:
            raise WebSocketProtocolError(
                f'Unexpected operation_code, got {frame.operation_code!r}, expected {WEBSOCKET_OPERATION_TEXT!r} or '
                f'{WEBSOCKET_OPERATION_BINARY!r}.'
            )
        
        # we got a whole frame, nice
        if frame.is_final:
            message = frame.data
            
            if text:
                message = message.decode('utf-8')
            
            return message
        
        max_size = self.max_size # set max size to BIG number to ignore it
        
        frames = []
        while True:
            max_size -= len(frame.data)
            
            frames.append(frame)
            if frame.is_final:
                break
            
            frame = await self.read_data_frame(max_size = max_size)
            if frame is None:
                raise WebSocketProtocolError('Incomplete fragmented message.')
            
            if frame.operation_code != WEBSOCKET_OPERATION_CONTINUOUS:
                raise WebSocketProtocolError(
                    f'Unexpected operation_code, got {frame.operation_code!r}, expected '
                    f'{WEBSOCKET_OPERATION_CONTINUOUS!r}.'
                )
        
        if text:
            try:
                message = ''.join(DECODER.decode(frame.data, frame.is_final) for frame in frames)
            except:
                DECODER.reset()
                raise
        else:
            message = b''.join(frame.data for frame in frames)
        
        return message
    
    
    async def read_data_frame(self, max_size):
        """
        Reads a websocket frame from the websocket. If the frame is a control frame processes and loops for reading an
        another one.
        
        This method is a coroutine.
        
        Parameters
        ----------
        
        Returns
        -------
        frame : ``WebSocketFrame``, `None`
            The read websocket frame. Returns `None` if close frame was received.
        
        Raises
        ------
        WebSocketProtocolError
            - If the reserved bits are not `0`.
            - If the frame is a control frame, but is too long for one.
            - If the websocket frame is fragmented frame. (Might be supported if people request is.)
            - If the frame operation_code is not any of the expected ones.
            - Close frame received with invalid status code.
            - Close frame too short.
        CancelledError
            ``.transfer_data_task`` cancelled.
        """
        while True:
            
            frame = await self.set_payload_reader(self._read_websocket_frame(self.is_client, max_size))
            
            extensions = self.extensions
            if (extensions is not None):
                for extension in reversed(extensions):
                    frame = extension.decode(frame, max_size = max_size)
            
            frame.check()
            
            # most likely
            if frame.operation_code in WEBSOCKET_DATA_OPERATIONS:
                return frame

            if (await self._process_control_frame(frame)):
                continue
            
            return
    
    
    async def _process_control_frame(self, frame):
        """
        Processes a control websocket frame.
        
        This method is a coroutine.
        
        Parameters
        ----------
        frame : ``WebSocketFrame``
            A received control websocket frame.
        
        Returns
        -------
        can_continue : `bool`
            Returns `False` if the processed `frame` was a close frame.
        
        Raises
        ------
        WebSocketProtocolError
            - Close frame received with invalid status code.
            - Close frame too short.
        """
        operation_code = frame.operation_code
        if operation_code == WEBSOCKET_OPERATION_CLOSE:
            data = frame.data
            length = len(data)
            if length >= 2:
                code = int.from_bytes(data[:2], 'big')
                if not (code in EXTERNAL_CLOSE_CODES or 2999 < code < 5000):
                    raise WebSocketProtocolError(f'Invalid status code {code!r}.')
                reason = data[2:].decode('utf-8')
                self.close_code = code
                self.close_reason = reason
            elif length == 0:
                self.close_code = 1005
            else:
                raise WebSocketProtocolError(
                    f'Close frame too short: {length!r}; {reprlib.repr(data)}.'
                )
            
            await self.write_close_frame(frame.data)
            return False
        
        if operation_code == WEBSOCKET_OPERATION_PING:
            await self.pong(frame.data)
            return True
        
        # operation_code == OP_PONG:
        if frame.data in self.pings:
            #checking all pings up to the one matching this pong.
            ping_id = b''
            while ping_id != frame.data:
                ping_id, pong_waiter = self.pings.popitem(0)
                pong_waiter.set_resultd_if_pending(None)
        
        return True
    
    
    async def write_frame(self, operation_code, data, _expected_state = WEBSOCKET_STATE_OPEN):
        """
        Writes the data as websocket.
        
        This method is a coroutine.
        
        Parameters
        ----------
        operation_code : `int`
            The operation code of the websocket frame.
            
            Can be 1 of the following:
            
            +-----------------------------------+-------+
            | Respective name                   | Value |
            +===================================+=======+
            | WEBSOCKET_OPERATION_CONTINUOUS    | 0     |
            +-----------------------------------+-------+
            | WEBSOCKET_OPERATION_TEXT          | 1     |
            +-----------------------------------+-------+
            | WEBSOCKET_OPERATION_BINARY        | 2     |
            +-----------------------------------+-------+
            | WEBSOCKET_OPERATION_CLOSE         | 8     |
            +-----------------------------------+-------+
            | WEBSOCKET_OPERATION_PING          | 9     |
            +-----------------------------------+-------+
            | WEBSOCKET_OPERATION_PONG          | 10    |
            +-----------------------------------+-------+
        
        data : `bytes-like`
            The data to send.
        
        _expected_state : `str`
            Expected state of the websocket. If the websocket is in other state, an `Exception` it raised.
            Defaults to `'WEBSOCKET_STATE_OPEN'`.
            
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
        
        Raises
        ------
        WebSocketProtocolError
            - If an extension set a reserved bit not to `0`.
            - If an extension modified the frame to a control frame, what is too long one.
            - If an extension modified the frame to be a fragmented one. (Might be supported if people request is.)
            - If an extension modified the frame's op code to not any of the expected ones.
        ConnectionClosed
            WebSocket connection closed.
        RuntimeError
            Protocol has no attached transport.
            - WebSocket connection not yet established.
            - Cannot write to websocket with it's current state.
        """
        # Defensive assertion for protocol compliance.
        if self.state != _expected_state:
            raise RuntimeError(f'Cannot write to a WebSocket in the {self.state} state.')

        # we write only 1 frame at a time, so we 'queue' it
        async with self._drain_lock:
            try:
                frame = WebSocketFrame(True, operation_code, data)
                
                extensions = self.extensions
                if (extensions is not None):
                    for extension in extensions:
                        frame = extension.encode(frame)
                    
                    frame.check()
                
                self.write_websocket_frame(frame, self.is_client)
                await self.drain()
            except ConnectionError:
                self.fail_connection()
                # raise ConnectionClosed with the correct code and reason.
                await self.ensure_open()
    
    
    async def write_close_frame(self, data = b''):
        """
        Writes close frame to the websocket if the websocket is not yet closed.
        
        This method is a coroutine.
        
        Parameters
        ----------
        data : `bytes-like` = `b''`, Optional
            The data to send.
        
        Raises
        ------
        WebSocketProtocolError
            - If an extension set a reserved bit not to `0`.
            - If an extension modified the frame to a control frame, what is too long one.
            - If an extension modified the frame to be a fragmented one. (Might be supported if people request is.)
            - If an extension modified the frame's op code to not any of the expected ones.
        ConnectionClosed
            WebSocket connection closed.
        Exception
            - WebSocket connection not yet established.
            - Cannot write to websocket with it's current state.
        RuntimeError
            Protocol has no attached transport.
        """
        # check connection before we write
        if self.state == WEBSOCKET_STATE_OPEN:
            self.state = WEBSOCKET_STATE_CLOSING
            await self.write_frame(WEBSOCKET_OPERATION_CLOSE, data, WEBSOCKET_STATE_CLOSING)
    
    
    async def close_connection(self):
        """
        Makes sure that the websocket is closed correctly.
        
        Meanwhile the websocket is closing, it's ``.close_connection_task`` is set as a ``Task`` object wrapping the
        ``.close_connection`` coroutine to avoid race condition.
        
        This method is a coroutine.
        """
        generator_destroyed = False
        
        try:
            # Wait for the data transfer phase to complete.
            transfer_data_task = self.transfer_data_task
            if (transfer_data_task is not None):
                try:
                    await transfer_data_task
                except TimeoutError:
                    pass
            
            # Cancel all pending pings because they'll never receive a pong.
            for ping in self.pings.values():
                ping.cancel()
            
            # A client should wait for a TCP close from the server.
            if self.is_client and (self.transfer_data_task is not None):
                if (await self.wait_for_connection_lost()):
                    return
            
            if self.can_write_eof():
                self.write_eof()
                if (await self.wait_for_connection_lost()):
                    return
        
        except GeneratorExit:
            generator_destroyed = True
            raise
        
        finally:
            # finally ensures that the transport never remains open
            if self.connection_lost_waiter.is_done() and not self.is_ssl:
                return
            
            # Close the TCP connection
            transport = self._transport
            if (transport is not None):
                transport.close()
                
                if not generator_destroyed:
                    if (await self.wait_for_connection_lost()):
                        return
                
                # Abort the TCP connection
                transport.abort()
            
            if not generator_destroyed:
                # connection_lost() is called quickly after aborting.
                await self.wait_for_connection_lost()
    
    
    async def wait_for_connection_lost(self):
        """
        Waits until ``.connection_lost_waiter`` is set. If ``.close_timeout`` is over before it happens, returns.
        
        This method is a coroutine.
        
        Returns
        -------
        is_connection_lost : `bool`
            Returns `True` if the connection is lost.
        """
        connection_lost_waiter = self.connection_lost_waiter
        if not connection_lost_waiter.is_done():
            return True
        
        waiter = shield(connection_lost_waiter, self._loop)
        waiter.apply_timeout(self.close_timeout)
        try:
            await waiter
        except TimeoutError:
            pass
        
        # re-check self.connection_lost_waiter.is_done() synchronously because connection_lost() could run between the
        # moment the timeout occurs and the moment this coroutine resumes running.
        return connection_lost_waiter.is_done()
    
    
    def fail_connection(self, code = 1006, reason = ''):
        """
        Closes the websocket if any unexpected exception occurred.
        
        Parameters
        ----------
        code : `int` = `1006`, Optional
            WebSocket close code.
        reason : `str` = `''`, Optional
            WebSocket close reason.
        
        Returns
        -------
        close_connection_task : ``Task`` of ``.close_connection``
            Close connection task, what can be awaited to wait till the connection is closed.
        
        Raises
        ------
        WebSocketProtocolError
            - If an extension set a reserved bit not to `0`.
            - If an extension modified the frame to a control frame, what is too long one.
            - If an extension modified the frame to be a fragmented one. (Might be supported if people request is.)
            - If an extension modified the frame's op code to not any of the expected ones.
        RuntimeError
            Protocol has no attached transport.
        """
        # cancel transfer_data_task if the opening handshake succeeded
        transfer_data_task = self.transfer_data_task
        if transfer_data_task is not None:
            # Do not cancel with `CancelledError` because then we to silence it elsewhere.
            transfer_data_task.cancel_with(TimeoutError)
        
        # send a close frame when the state == WEBSOCKET_STATE_OPEN and the connection is not broken
        if code != 1006 and self.state == WEBSOCKET_STATE_OPEN:
            
            frame_data = self._serialize_close(code, reason)
            # Write the close frame without draining the write buffer.
            self.state = WEBSOCKET_STATE_CLOSING
            
            frame = WebSocketFrame(True, WEBSOCKET_OPERATION_CLOSE, frame_data)
            
            extensions = self.extensions
            if (extensions is not None):
                for extension in extensions:
                    frame = extension.encode(frame)
                
                frame.check()
            
            self.write_websocket_frame(frame, self.is_client)
        
        # start close_connection_task if the opening handshake didn't succeed.
        close_connection_task = self.close_connection_task
        if close_connection_task is None:
            close_connection_task = Task(self._loop, self.close_connection())
            self.close_connection_task = close_connection_task
        
        return close_connection_task
    
    
    # compatibility method (overwrite)
    def connection_lost(self, exception):
        """
        Called when the connection is lost or closed.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        self.state = WEBSOCKET_STATE_CLOSED
        if not self.close_code:
            self.close_code = 1006
        
        # `self.connection_lost_waiter` should be pending
        self.connection_lost_waiter.set_result_if_pending(None)
        
        HttpReadWriteProtocol.connection_lost(self, exception)
    
    
    # compatibility method (overwrite)
    def eof_received(self):
        """
        Calling ``.connection_lost`` without exception causes eof.
        
        Marks the protocols as it is at eof and stops payload processing if applicable.
        
        Returns
        -------
        transport_closes : `bool`
            Returns `False` if the transport will close itself. If it returns `True`, then closing the transport is up
            to the protocol.
            
            Returns `True` if the websocket is not secure.
        """
        HttpReadWriteProtocol.eof_received(self)
        return (not self.is_ssl)
