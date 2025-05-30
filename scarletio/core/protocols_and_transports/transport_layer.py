__all__ = ('TransportLayerBase', 'SocketTransportLayer', 'SocketTransportLayerBase', 'DatagramSocketTransportLayer',)

import reprlib
from collections import deque as Deque
from itertools import islice
from selectors import EVENT_READ, EVENT_WRITE
from socket import (
    AF_INET as SOCKET_FAMILY_INET, AF_INET6 as SOCKET_FAMILY_INET6, IPPROTO_TCP as SOCKET_PROTOL_TCP,
    SHUT_WR as SOCKET_SHUTDOWN_WR, SOCK_STREAM as SOCKET_TYPE_STREAM, error as SocketError, socket as SocketType
)

from ...utils import copy_docs, include

from .abstract import AbstractTransportLayerBase
from .extra_info import (
    EXTRA_INFO_NAME_PEER_NAME, EXTRA_INFO_NAME_SOCKET, EXTRA_INFO_NAME_SOCKET_NAME, get_extra_info, has_extra_info,
    set_extra_info
)


try:
    from socket import TCP_NODELAY as SOCKET_OPTION_TCP_NODELAY
except ImportError:
    SOCKET_OPTION_TCP_NODELAY = 0

try:
    from os import sysconf as get_system_configuration
except ImportError:
    get_system_configuration = None

write_exception_async = include('write_exception_async')


if SOCKET_OPTION_TCP_NODELAY:
    def _set_nodelay(socket):
        if (
            (socket.family in (SOCKET_FAMILY_INET, SOCKET_FAMILY_INET6)) and
            (socket.type == SOCKET_TYPE_STREAM) and
            (socket.proto == SOCKET_PROTOL_TCP)
        ):
            socket.setsockopt(SOCKET_PROTOL_TCP, SOCKET_OPTION_TCP_NODELAY, 1)
else:
    def _set_nodelay(socket):
        pass


MAX_SIZE = 262144


if (get_system_configuration is None) or (not hasattr(SocketType, 'sendmsg')):
    MAX_SENT_MESSAGES = 0

else:
    try:
        MAX_SENT_MESSAGES = get_system_configuration('SC_IOV_MAX')
    except OSError:
        MAX_SENT_MESSAGES = 0


class TransportLayerBase(AbstractTransportLayerBase):
    """
    Defines basic transport layer functionality.
    
    Attributes
    ----------
    _extra : `None | dict<str, object>`
        Optional transport information.
    
    _loop : ``EventThread``
        The event loop to what the transport is bound to.
    """
    __slots__ = ('_extra', '_loop',)
    
    def __new__(cls, loop, extra):
        """
        Creates a new transport layer instance.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the transport is bound to.
        extra : `None | dict<str, object>`
            Optional transport information.
        """
        self = object.__new__(cls)
        self._extra = extra
        self._loop = loop
        return self
    
    
    @copy_docs(AbstractTransportLayerBase.get_extra_info)
    def get_extra_info(self, name, default = None):
        return get_extra_info(self._extra, name, default)
    
    
    def _fatal_error(self, exception, message = 'Fatal error on transport layer'):
        """
        If a fatal error occurs on the transport, renders its traceback and closes itself.
        
        Parameters
        ----------
        exception : `BaseException`
            The occurred exception.
        message : `str` = `'Fatal error on transport layer'`, Optional
            Additional error message to render.
        """
        if not isinstance(exception, (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):
            write_exception_async(
                exception,
                [
                    message,
                    '\nException occurred at \n',
                    repr(self),
                    '.\n',
                ],
                loop = self._loop,
            )


class SocketTransportLayerBase(TransportLayerBase):
    """
    Defines commonly used logic between ``SocketTransportLayer`` and ``DatagramSocketTransportLayer``.
    
    Attributes
    ----------
    _buffer : `Deque`
        Transport's buffer.
    
    _closing : `bool`
        Whether the transport ic closing. Set when ``.close`` is called.
    
    _connection_lost : `bool`
        Set as `True`, when ``._call_connection_lost`` is scheduled.
    
    _extra : `dict<str, object>`
        Optional transport information.
    
    _high_water : `int`
        The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
    
    _file_descriptor : `int`
        The transport's socket's file descriptor identifier.
    
    _loop : ``EventThread``
        The event loop to what the transport is bound to.
    
    _low_water : `int`
        The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to `16384`.
    
    _paused : `bool`
        Whether the transport's reading is paused by the protocol.
    
    _protocol : `None`, ``SSLBidirectionalTransportLayer, ``ReadProtocolBase``, `object`
        Asynchronous protocol implementation used by the transport. After closing is set to `None`.
    
    _protocol_paused : `bool`
        Whether ``.protocol`` is paused writing.
    
    _socket : `SocketType`
        The socket used by the transport.
    """
    __slots__ = (
        '_buffer', '_closing', '_connection_lost', '_file_descriptor', '_high_water', '_low_water', '_paused',
        '_protocol', '_protocol_paused', '_socket', 
    )
    
    def __new__(cls, loop, extra, socket, protocol, waiter):
        """
        Creates a socket based transport layer.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the transport is bound to.
        extra : `None | dict<str, object>`
            Optional transport information.
        socket : `SocketType`
            The socket used by the transport.
        protocol : ``ReadProtocolBase``
            Asynchronous protocol implementation used by the transport.
        waiter : `None`, ``Future``
            Waiter, what's result is set, when the transport connected.
        """
        extra = set_extra_info(extra, EXTRA_INFO_NAME_SOCKET, socket)
        
        try:
            socket_name = socket.getsockname()
        except OSError:
            socket_name = None
        
        extra = set_extra_info(extra, EXTRA_INFO_NAME_SOCKET_NAME, socket_name)
        
        if has_extra_info(extra, EXTRA_INFO_NAME_PEER_NAME):
            try:
                peer_name = socket.getpeername()
            except SocketError:
                peer_name = None
            
            extra = set_extra_info(extra, EXTRA_INFO_NAME_PEER_NAME, peer_name)
        
        
        self = TransportLayerBase.__new__(cls, loop, extra)
        
        self._protocol_paused = False
        
        self._socket = socket
        self._file_descriptor = socket.fileno()
        self._protocol = protocol
        self._buffer = Deque()
        self._connection_lost = False
        self._closing = False
        self._paused = False
        
        self._set_write_buffer_limits()
        
        return self
    
    
    def __repr__(self):
        """Returns the socket transport layer's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # state
        if self._socket is None:
            state = 'closed'
        elif self._closing:
            state = 'closing'
        else:
            state = 'open'
        
        repr_parts.append(' state = ')
        repr_parts.append(state)
        
        # file_descriptor
        repr_parts.append(', file_descriptor = ')
        repr_parts.append(repr(self._file_descriptor))
        
        loop = self._loop
        
        # read
        if not loop.running:
            polling = False
        
        else:
            try:
                key = loop.selector.get_key(self._file_descriptor)
            except KeyError:
                polling = 0
            else:
                polling = key.events & EVENT_READ
        
        if polling:
            state = 'polling'
        else:
            state = 'idle'
        
        repr_parts.append(', read = ')
        repr_parts.append(state)
        
        # write
        if not loop.running:
            polling = False
        
        else:
            try:
                key = loop.selector.get_key(self._file_descriptor)
            except KeyError:
                polling = 0
            else:
                polling = key.events & EVENT_WRITE
        
        if polling:
            state = 'polling'
        else:
            state = 'idle'
        
        repr_parts.append(', write = ')
        repr_parts.append(state)
        
        # buffer size
        buffer_size = self.get_write_buffer_size()
        repr_parts.append(', buffer_size = ')
        repr_parts.append(str(buffer_size))
    
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __del__(self):
        """
        Closes the socket transport layer's ``.socket`` if not yet closed.
        """
        socket = self._socket
        if (socket is not None):
            self._socket = None
            socket.close()
    
    
    @copy_docs(TransportLayerBase.get_protocol)
    def get_protocol(self):
        return self._protocol
    
    
    @copy_docs(TransportLayerBase.set_protocol)
    def set_protocol(self, protocol):
        self._protocol = protocol
    
    
    @copy_docs(TransportLayerBase.is_closing)
    def is_closing(self):
        return self._closing
    
    
    @copy_docs(TransportLayerBase.close)
    def close(self):
        if self._closing:
            return
        
        self._closing = True
        self._loop.remove_reader(self._file_descriptor)
        if not self._buffer:
            self._connection_lost = True
            self._loop.remove_writer(self._file_descriptor)
            self._loop.call_soon(self._call_connection_lost, None)
    
    
    @copy_docs(TransportLayerBase.abort)
    def abort(self, exception = None):
        self._force_close(exception)
    
    
    @copy_docs(TransportLayerBase.set_write_buffer_limits)
    def set_write_buffer_limits(self, high = None, low = None):
        self._set_write_buffer_limits(high = high, low = low)
        self._maybe_pause_protocol()
    
    
    def _call_connection_lost(self, exception):
        """
        Calls the transport's connection lost method-
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        try:
            protocol = self._protocol
            if (protocol is not None):
                protocol.connection_lost(exception)
        finally:
            socket = self._socket
            if (socket is not None):
                self._socket = None
                socket.close()
            
            self._protocol = None
    
    
    @copy_docs(TransportLayerBase.get_write_buffer_limits)
    def get_write_buffer_limits(self):
        return self._low_water, self._high_water
    
    
    def _maybe_pause_protocol(self):
        """
        Called after data was ensured to be written into the socket to check whether it's protocol should be paused.
        """
        size = self.get_write_buffer_size()
        if size <= self._high_water:
            return
        
        if self._protocol_paused:
            return
            
        self._protocol_paused = True
        
        protocol = self._protocol
        if (protocol is not None):
            try:
                protocol.pause_writing()
            except BaseException as err:
                write_exception_async(
                    err,
                    [
                        'Exception occurred at:\n',
                        repr(self),
                        '._maybe_pause_protocol\n',
                    ],
                    loop = self._loop,
                )
    
    
    def _set_write_buffer_limits(self, high = None, low = None):
        """
        Sets the write buffer limits of the transport.
        
        Parameters
        ----------
        low : None`, `int` = `None`, Optional
            The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
        high : `None | int` = `None`, Optional
            The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to
            `16384`.

        Raises
        ------
        ValueError
            If `high` is lower than `low` or if `low` is lower than `0`.
        """
        if high is None:
            if low is None:
                high = 65536
                low = 16384
            else:
                high = low << 2
        else:
            if low is None:
                low = high >> 2
        
        if low < 0 or high < low:
            raise ValueError(
                f'High water must be greater or equal than low, what must be greater than equal than `0`, '
                f'got high = {high!r}; low = {low!r}.'
            )
        
        self._high_water = high
        self._low_water = low
    

    def _force_close(self, exception):
        """
        Closes the transport immediately.
        
        The buffered data will be lost.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        if self._connection_lost:
            return
        
        buffer = self._buffer
        if buffer:
            buffer.clear()
            self._loop.remove_writer(self._file_descriptor)
        
        if not self._closing:
            self._closing = True
            self._loop.remove_reader(self._file_descriptor)
        
        self._connection_lost = True
        self._loop.call_soon(self._call_connection_lost, exception)
    
    
    def _read_ready(self):
        """
        Added as a read callback on the respective event loop to be called when the data is received on the pipe.
        
        If this happens, since it is a write only pipe, means it should be closed, so we do like that.
        """
        pass
    
    
    def _maybe_resume_protocol(self):
        """
        Called after successful writing to the socket to check whether the protocol should be resumed.
        """
        if (not self._protocol_paused) or (self.get_write_buffer_size() > self._low_water):
            return
        
        self._protocol_paused = False
        protocol = self._protocol
        if (protocol is not None):
            try:
                protocol.resume_writing()
            except BaseException as err:
                write_exception_async(
                    err,
                    [
                        'Exception occurred at:\n',
                        repr(self),
                        '._maybe_resume_protocol\n',
                    ],
                    loop = self._loop,
                )


class SocketTransportLayer(SocketTransportLayerBase):
    """
    Socket transport layer.
    
    Attributes
    ----------
    _buffer : `Deque`
        Transport's buffer.
    
    _closing : `bool`
        Whether the transport ic closing.
    
    _connection_lost : `bool`
        Set as `True`, when ``._call_connection_lost`` is scheduled.
    
    _extra : `None | dict<str, object>`
        Optional transport information.
    
    _high_water : `int`
        The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
    
    _loop : ``EventThread``
        The event loop to what the transport is bound to.
    
    _low_water : `int`
        The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to `16384`.
    
    _paused : `bool`
        Whether the transport's reading is paused by the protocol.
    
    _protocol : `None`, ``SSLBidirectionalTransportLayer, ``ReadProtocolBase``, `object`
        Asynchronous protocol implementation used by the transport.
        
        After closing the transport is set to `None`.
    
    _protocol_paused : `bool`
        Whether ``.protocol`` is paused writing.
    
    _socket : `SocketType`
        The socket used by the transport.
    
    _file_descriptor : `int`
        The transport's socket's file descriptor identifier.
    
    _at_eof : `bool`
        Whether ``.write_eof`` was called.
    
    _server : `None`, ``Server``
        If the transport is server side, it's server is set as this attribute.
    """
    __slots__ = ('_at_eof', '_server')
    
    def __new__(cls, loop, extra, socket, protocol, waiter, server):
        """
        Creates a new socket transport layer.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the transport is bound to.
        extra : `None | dict<str, object>`
            Optional transport information.
        socket : `SocketType`
            The socket used by the transport.
        protocol : ``ProtocolBase``
            Asynchronous protocol implementation used by the transport.
        waiter : `None`, ``Future`
            Waiter, what's result is set, when the transport connected. Defaults to `None`.
        server : `None`, ``Server``
            If the transport is server side, it's server is set as this attribute. Defaults to `None`.
        """
        self = SocketTransportLayerBase.__new__(cls, loop, extra, socket, protocol, waiter)
        
        self._server = server
        self._at_eof = False
        
        if (server is not None):
            server._attach()
        
        loop.call_soon(protocol.connection_made, self)
        
        _set_nodelay(socket)
        
        # only start reading when connection_made() has been called
        loop.call_soon(loop.add_reader, self._file_descriptor, self._read_ready)
        if (waiter is not None):
            # only wake up the waiter when connection_made() has been called
            loop.call_soon(type(waiter).set_result_if_pending, waiter, None)
        
        return self
    
    
    @copy_docs(SocketTransportLayerBase.write)
    def write(self, data):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f'`data` can be `bytes-like`, got {type(data).__name__}; {reprlib.repr(data)}.'
            )
        
        if self._at_eof:
            raise RuntimeError(
                f'Cannot call `.write` after `.write_eof`; self = {self!r}.'
            )
        
        if not data:
            return
        
        if self._connection_lost:
            return
        
        buffer = self._buffer
        if not buffer:
            # Optimization: try to send now.
            try:
                bytes_sent = self._socket.send(data)
            except (BlockingIOError, InterruptedError):
                pass
            
            except BaseException as err:
                self._fatal_error(err, 'Fatal write error on socket transport')
                return
            
            else:
                if bytes_sent >= len(data):
                    return
                
                data = memoryview(data)[bytes_sent:]
            
            # Not all was written; register write handler.
            self._loop.add_writer(self._file_descriptor, self._write_ready)
        
        # Add it to the buffer.
        buffer.append(data)
        self._maybe_pause_protocol()
    
    # `.writelines` same as `SocketTransportLayerBase`'s.
    
    @copy_docs(SocketTransportLayerBase.write_eof)
    def write_eof(self):
        if self._at_eof:
            return
        
        self._at_eof = True
        
        if not self._buffer:
            self._socket.shutdown(SOCKET_SHUTDOWN_WR)
    

    @copy_docs(SocketTransportLayerBase.can_write_eof)
    def can_write_eof(self):
        return True
    
    
    @copy_docs(SocketTransportLayerBase.get_write_buffer_size)
    def get_write_buffer_size(self):
        size = 0
        for data in self._buffer:
            size += len(data)
        
        return size
        
    
    @copy_docs(SocketTransportLayerBase.pause_reading)
    def pause_reading(self):
        if self._closing or self._paused:
            return False
        
        self._paused = True
        self._loop.remove_reader(self._file_descriptor)
        return True
    
    
    @copy_docs(SocketTransportLayerBase.resume_reading)
    def resume_reading(self):
        if not self._paused:
            return False
        
        self._paused = False
        if not self._closing:
            self._loop.add_reader(self._file_descriptor, self._read_ready)
        
        return True
    
    
    @copy_docs(SocketTransportLayerBase._fatal_error)
    def _fatal_error(self, exception, message = 'Fatal error on transport layer'):
        SocketTransportLayerBase._fatal_error(self, exception, message)
        
        self._force_close(exception)
    
    
    @copy_docs(SocketTransportLayerBase._call_connection_lost)
    def _call_connection_lost(self, exception):
        try:
            SocketTransportLayerBase._call_connection_lost(self, exception)
        finally:
            server = self._server
            if (server is not None):
                self._server = None
                server._detach()
    
    
    @copy_docs(SocketTransportLayerBase._read_ready)
    def _read_ready(self):
        if self._connection_lost:
            return
        
        try:
            data = self._socket.recv(MAX_SIZE)
        except (BlockingIOError, InterruptedError):
            pass
        
        except BaseException as err:
            self._fatal_error(err, 'Fatal read error on socket transport')
            
        else:
            if data:
                self._protocol.data_received(data)
            
            elif self._protocol.eof_received():
                # We're keeping the connection open so the protocol can write more, but we still can't receive more,
                # so remove the reader callback.
                self._loop.remove_reader(self._file_descriptor)
            
            else:
                self.close()
    
    if MAX_SENT_MESSAGES <= 0:
        def _write_ready(self):
            """
            Added as a write callback on the respective event loop when the transport has unsent data. Called when the
            respective socket becomes writable.
            """
            if self._connection_lost:
                return
            
            buffer = self._buffer
            data = buffer[0]
            try:
                bytes_sent = self._socket.send(data)
            except (BlockingIOError, InterruptedError):
                return
            
            except BaseException as err:
                self._loop.remove_writer(self._file_descriptor)
                self._buffer.clear()
                self._fatal_error(err, 'Fatal write error on socket transport')
                return
            
            if bytes_sent > 0:
                if bytes_sent >= len(data):
                    del buffer[0]
                else:
                    buffer[0] = memoryview(data)[bytes_sent:]
            
            self._maybe_resume_protocol()
            
            if not buffer:
                self._loop.remove_writer(self._file_descriptor)
                
                if self._closing:
                    self._call_connection_lost(None)
                
                elif self._at_eof:
                    self._socket.shutdown(SOCKET_SHUTDOWN_WR)
    
    else:
        def _write_ready(self):
            """
            Added as a write callback on the respective event loop when the transport has unsent data. Called when the
            respective socket becomes writable.
            """
            if self._connection_lost:
                return
            
            buffer = self._buffer
            try:
                bytes_sent = self._socket.sendmsg(islice(buffer, MAX_SENT_MESSAGES))
            except (BlockingIOError, InterruptedError):
                return
            
            except BaseException as err:
                self._loop.remove_writer(self._file_descriptor)
                self._buffer.clear()
                self._fatal_error(err, 'Fatal write error on socket transport')
                return
            
            if bytes_sent > 0:
                while True:
                    data = buffer[0]
                    data_length = len(data)
                    
                    if data_length > bytes_sent:
                        buffer[0] = memoryview(data)[bytes_sent:]
                        break
                    
                    del buffer[0]
                    if (not buffer):
                        break
                    
                    if (data_length == bytes_sent):
                        break
                    
                    bytes_sent -= data_length
                    continue
            
            self._maybe_resume_protocol()
            
            if not buffer:
                self._loop.remove_writer(self._file_descriptor)
                
                if self._closing:
                    self._call_connection_lost(None)
                
                elif self._at_eof:
                    self._socket.shutdown(SOCKET_SHUTDOWN_WR)


class DatagramSocketTransportLayer(SocketTransportLayerBase):
    """
    Asynchronous transport implementation for datagram sockets.
    
    Attributes
    ----------
    _address : `None | (str, int)`
        The last address, where the transport sent data. Defaults to `None`. The send target address should not differ
        from the last, where the transport sent data.
    
    _buffer : `Deque`
        Transport's buffer.
    
    _closing : `bool`
        Whether the transport ic closing. Set when ``.close`` is called.
    
    _connection_lost : `bool`
        Set as `True`, when ``._call_connection_lost`` is scheduled.
    
    _extra : `None | dict<str, object>`
        Optional transport information.
    
    _high_water : `int`
        The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
    
    _loop : ``EventThread``
        The event loop to what the transport is bound to.
    
    _low_water : `int`
        The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to `16384`.
    
    _paused : `bool`
        Whether the transport's reading is paused by the protocol.
    
    _protocol : `None`, ``SSLBidirectionalTransportLayer, ``ReadProtocolBase``, `object`
        Asynchronous protocol implementation used by the transport.
        
        After closing the transport is set to `None`.
    
    _protocol_paused : `bool`
        Whether ``.protocol`` is paused writing.
    
    _socket : `SocketType`
        The socket used by the transport.
    
    _file_descriptor : `int`
        The transport's socket's file descriptor identifier.
    """
    __slots__ = ('_address', )
    
    def __new__(cls, loop, extra, socket, protocol, waiter, address):
        """
        Creates a datagram transport layer with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the transport is bound to.
        extra : `None | dict<str, object>`
            Optional transport information.
        socket : `SocketType`
            The socket used by the transport.
        protocol : ``ProtocolBase``
            Asynchronous protocol implementation used by the transport.
        waiter : `None`, ``Future`
            Waiter, what's result is set, when the transport connected. Defaults to `None`.
        address : `None`, `tuple` (`str`, `int`)
            The last address, where the transport sent data. The send target address should not
            differ from the last, where the transport sent data.
        """
        self = SocketTransportLayerBase.__new__(cls, loop, extra, socket, protocol, waiter)
        
        self._address = address
        
        loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        loop.call_soon(self._add_reader)
        
        if (waiter is not None):
            # only wake up the waiter when connection_made() has been called
            loop.call_soon(type(waiter).set_result_if_pending, waiter, None)
        
        return self
    
    
    # `write` inherited from `TransportLayerBase`.
    
    @copy_docs(SocketTransportLayerBase.writelines)
    def writelines(self, lines):
        pass
    
    # `write_eof` inherited from `TransportLayerBase`.
    
    
    # `can_write_eof` inherited from `TransportLayerBase`.
    
    @copy_docs(SocketTransportLayerBase.get_write_buffer_size)
    def get_write_buffer_size(self):
        size = 0
        for data, address in self._buffer:
            size += len(data)
        
        return size
    
    
    # `pause_reading` inherited from `TransportLayerBase`
    
    # `resume_reading` inherited from `TransportLayerBase`
    
    
    @copy_docs(SocketTransportLayerBase._fatal_error)
    def _fatal_error(self, exception, message = 'Fatal error on transport'):
        if not isinstance(exception, OSError):
            write_exception_async(
                exception,
                [
                    message,
                    '\nException occurred at ',
                    repr(self),
                    '.\n',
                ],
                loop = self._loop
            )
        
        self._force_close(exception)
    
    
    def _add_reader(self):
        """
        Call soon callback added by ``.__init__` to add reader to the event loop.
        """
        if self._closing:
            return
        
        self._loop.add_reader(self._file_descriptor, self._read_ready)
    
    
    @copy_docs(SocketTransportLayerBase._read_ready)
    def _read_ready(self):
        if self._connection_lost:
            return
        
        try:
            data, address = self._socket.recvfrom(MAX_SIZE)
        except (BlockingIOError, InterruptedError):
            pass
        
        except OSError as err:
            self._protocol.error_received(err)
        
        except BaseException as err:
            self._fatal_error(err, 'Fatal read error on datagram transport')
        
        else:
            self._protocol.datagram_received(data, address)
    
    
    def send_to(self, data, maybe_address = None):
        """
        Sends the given data to the target address. If target is already set, can be the parameter can be ignored.
        
        Parameters
        ----------
        data : `bytes-like`
            The data to send.
        maybe_address : `None`, `tuple` (`str`, `int`) = `None`, Optional
            The address to send the data to.
        
        Raises
        ------
        TypeError
            If `data` was not given as `bytes-like`.
        ValueError
            If `address` was given but it is different from the currently set one.
        """
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f'`data` can be `bytes-like`, got {data.__class__.__name__}; {reprlib.repr(data)}.'
            )
        
        if not data:
            return
        
        address = self._address
        if (address is not None):
            if (maybe_address is not None) or (maybe_address != address):
                raise ValueError(
                    f'Invalid address: `address` should be `None`, got {maybe_address!r}; current={address!r}.'
                )
            
            maybe_address = address
        
        if self._connection_lost:
            return
        
        buffer = self._buffer
        if not buffer:
            # Attempt to send it right away first.
            try:
                if get_extra_info(self._extra, EXTRA_INFO_NAME_PEER_NAME, None) is None:
                    self._socket.sendto(data, maybe_address)
                else:
                    self._socket.send(data)
            except (BlockingIOError, InterruptedError):
                self._loop.add_writer(self._file_descriptor, self._send_to_ready)
            
            except OSError as err:
                self._protocol.error_received(err)
                return
            
            except BaseException as err:
                self._fatal_error(err, 'Fatal write error on datagram transport')
                return
            
            else:
                return
        
        # Ensure that what we buffer is immutable.
        buffer.append((bytes(data), maybe_address))
        self._maybe_pause_protocol()
    
    
    def _send_to_ready(self):
        """
        Added callback by `.send_to` to the respective event loop, when the socket is not ready for writing.
        
        This method tries to send the data again.
        """
        buffer = self._buffer
        while buffer:
            data, address = buffer.popleft()
            try:
                if get_extra_info(self._extra, EXTRA_INFO_NAME_PEER_NAME, None) is None:
                    self._socket.sendto(data, address)
                else:
                    self._socket.send(data)
            except (BlockingIOError, InterruptedError):
                buffer.appendleft((data, address))  # Try again later.
                break
            
            except OSError as err:
                self._protocol.error_received(err)
                return
            
            except BaseException as err:
                self._fatal_error(err, 'Fatal write error on datagram transport')
                return
        
        self._maybe_resume_protocol() # May append to buffer.
        if not buffer:
            self._loop.remove_writer(self._file_descriptor)
            if self._closing:
                self._call_connection_lost(None)
