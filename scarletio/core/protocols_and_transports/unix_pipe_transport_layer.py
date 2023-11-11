__all__ = ('UnixReadPipeTransportLayer', 'UnixWritePipeTransportLayer')

import errno, os, sys
from stat import S_ISCHR, S_ISFIFO, S_ISSOCK

from ...utils import copy_docs, include

from ..traps import skip_ready_cycle

from .extra_info import EXTRA_INFO_NAME_PIPE, set_extra_info
from .transport_layer import TransportLayerBase


write_exception_async = include('write_exception_async')

MAX_READ_SIZE = 262144
IS_AIX = sys.platform.startswith('aix')


class UnixReadPipeTransportLayer(TransportLayerBase):
    """
    Asynchronous read only transport implementation for pipes.
    
    Attributes
    ----------
    _extra : `dict` of (`str`, `object`) items
        Optional transport information.
    _loop : ``EventThread``
        The respective event loop of the transport.
    _closing : `bool`
        Whether the transport ic closing.
    _file_descriptor : `int`
        The used socket's file descriptor number.
    _pipe : `None`, `file-like`
        The pipe to connect to on read end.
        
        Is set to non-blocking mode.
        
        After closing the transport is set to `None`.
    _protocol : `None`, ``SubprocessReadPipeProtocol``
        Asynchronous protocol implementation used by the transport.
        
        After closing the transport is set to `None`.
    """
    __slots__ = ('_paused', '_closing', '_file_descriptor', '_pipe', '_protocol')
    
    async def __new__(cls, loop, extra, pipe, protocol):
        """
        Creates a new ``UnixReadPipeTransportLayer`` with the given parameters.
        
        This method is a coroutine.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop of the transport.
        pipe : `file-like`
            The pipe to connect to on read end.
        protocol : ``SubprocessReadPipeProtocol``, `object`
            Asynchronous protocol implementation used by the transport.
        extra : `None`, `dict` of (`str`, `object`) items
            Optional transport information.
        
        Raises
        ------
        ValueError
            If `pipe` was not given neither as pipe, socket or character device.
        """
        file_descriptor = pipe.fileno()
        mode = os.fstat(file_descriptor).st_mode
        if not (S_ISFIFO(mode) or S_ISSOCK(mode) or S_ISCHR(mode)):
            raise ValueError(
                f'`{cls.__name__}` is only for pipes, sockets and character devices, got '
                f'{pipe.__class__.__name__}; {pipe!r}.'
            )
        
        extra = set_extra_info(extra, EXTRA_INFO_NAME_PIPE, pipe)
        
        self = TransportLayerBase.__new__(cls, loop, extra)
        self._pipe = pipe
        self._file_descriptor = file_descriptor
        self._protocol = protocol
        self._closing = False
        self._paused = False
        
        try:
            os.set_blocking(file_descriptor, False)
            # skip 1 loop
            await skip_ready_cycle()
            
            protocol.connection_made(self)
            loop.add_reader(file_descriptor, self._read_ready)
        
        except:
            self.close()
            raise
        
        return self
    
    def __repr__(self):
        """Returns the transport layer's representation."""
        return f'<{self.__class__.__name__} file_descriptor={self._file_descriptor}>'
    
    
    def _read_ready(self):
        """
        Added as a read callback on the respective event loop to be called when the data is received on the pipe.
        """
        try:
            data = os.read(self._file_descriptor, MAX_READ_SIZE)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as err:
            self._fatal_error(err, 'Fatal read error on pipe transport')
        else:
            if data:
                self._protocol.data_received(data)
            else:
                self._closing = True
                loop = self._loop
                loop.remove_reader(self._file_descriptor)
                protocol = self._protocol
                loop.call_soon(protocol.__class__.eof_received, protocol)
                loop.call_soon(self.__class__._call_connection_lost, self, None)
    
    
    @copy_docs(TransportLayerBase.pause_reading)
    def pause_reading(self):
        if self._closing or self._paused:
            return False
        
        self._paused = True
        self._loop.remove_reader(self._file_descriptor)
        return True
    
    
    @copy_docs(TransportLayerBase.resume_reading)
    def resume_reading(self):
        """
        Resumes the receiving end.
        
        Data received will once again be passed to the respective protocol's ``.data_received`` method.
        
        Returns
        -------
        reading_resume : `bool`
            Whether reading was resumed.
        """
        if self._closing or not self._paused:
            return False
        
        self._paused = False
        self._loop.add_reader(self._file_descriptor, self._read_ready)
        return True
    
    
    @copy_docs(TransportLayerBase.set_protocol)
    def set_protocol(self, protocol):
        self._protocol = protocol
    
    
    @copy_docs(TransportLayerBase.get_protocol)
    def get_protocol(self):
        return self._protocol
    
    
    @copy_docs(TransportLayerBase.is_closing)
    def is_closing(self):
        return self._closing
    
    
    @copy_docs(TransportLayerBase.close)
    def close(self):
        if not self._closing:
            self._close(None)
    
    
    def __del__(self):
        """
        Closes the read pipe transport if not yet closed.
        """
        pipe = self._pipe
        if (pipe is not None):
            pipe.close()
    
    
    @copy_docs(TransportLayerBase._fatal_error)
    def _fatal_error(self, exception, message = 'Fatal error on pipe transport'):
        if not (isinstance(exception, OSError) and (exception.errno == errno.EIO)):
            write_exception_async(
                exception,
                [
                    message,
                    '\nException occurred at \n',
                    repr(self),
                    '.\n',
                ],
                loop = self._loop
            )
        
        self._close(exception)
    
    
    def _close(self, exception):
        """
        Starts the transport's closing process.
        
        Parameters
        ----------
        exception : `None`, ``BaseException``
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        self._closing = True
        loop = self._loop
        loop.remove_reader(self._file_descriptor)
        loop.call_soon(self.__class__._call_connection_lost, self, exception)
    
    
    def _call_connection_lost(self, exception):
        """
        Calls the read pipe transport's protocol's `.connection_lost` with the given exception and closes the
        transport's pipe.
        
        Parameters
        ----------
        exception : `None`, ``BaseException``
            Exception to call the protocol's ``.connection_lost`` with.
            
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        protocol = self._protocol
        if protocol is None:
            return
        
        try:
            protocol.connection_lost(exception)
        finally:
            pipe = self._pipe
            if (pipe is not None):
                self._pipe = None
                pipe.close()
            
            self._protocol = None


class UnixWritePipeTransportLayer(TransportLayerBase):
    """
    Asynchronous write only transport implementation for pipes.
    
    Attributes
    ----------
    _buffer : `bytearray`
        Data ensured to be written on the wrapped pipe as it becomes readable again.
    _extra : `dict` of (`str`, `object`) items
        Optional transport information.
    _high_water : `int`
        The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
    _low_water : `int`
        The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to `16384`.
    _closing : `bool`
        Whether the transport ic closing.
    _file_descriptor : `int`
        The used socket's file descriptor number.
    _loop : ``EventThread``
        The respective event loop of the transport.
    _pipe : `None`, `file-like`
        The pipe to connect to on read end.
        
        Is set to non-blocking mode.
        
        After closing the transport is set to `None`.
    _protocol : `None`, ``SubprocessWritePipeProtocol``, `object`
        Asynchronous protocol implementation used by the transport.
        
        After closing the transport is set to `None`.
    _protocol_paused : `bool`
        Whether ``.protocol`` is paused writing.
    """
    __slots__ = (
        '_buffer', '_extra', '_high_water', '_low_water', '_closing', '_file_descriptor', '_loop', '_pipe',
        '_protocol', '_protocol_paused'
    )
    
    async def __new__(cls, loop, pipe, protocol, extra = None):
        """
        Creates a new ``UnixWritePipeTransportLayer`` with the given parameters.
        
        This method is a coroutine.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop of the transport.
        pipe `: file-like` object
            The pipe to connect to on read end.
        protocol : ``SubprocessWritePipeProtocol``, `object`
            Asynchronous protocol implementation used by the transport.
        extra : `None`, `dict` of (`str`, `object`) items = `None`, Optional
            Optional transport information.

        Raises
        ------
        ValueError
            If `pipe` was not given neither as pipe, socket or character device.
        """
        file_descriptor = pipe.fileno()
        mode = os.fstat(file_descriptor).st_mode
        is_char = S_ISCHR(mode)
        is_fifo = S_ISFIFO(mode)
        is_socket = S_ISSOCK(mode)
        if not (is_char or is_fifo or is_socket):
            raise ValueError(
                f'{cls.__name__} is only for pipes, sockets and character devices, got '
                f'{pipe.__class__.__name__}; {pipe!r}.'
            )
        

        extra = set_extra_info(extra, EXTRA_INFO_NAME_PIPE, pipe)
        
        self = TransportLayerBase.__new__(cls, loop, extra)
        self._extra = extra
        self._loop = loop
        self._protocol_paused = False
        self._pipe = pipe
        self._file_descriptor = file_descriptor
        self._protocol = protocol
        self._buffer = bytearray()
        self._closing = False  # Set when close() or write_eof() called.
        
        self._high_water = 65536
        self._low_water = 16384
        
        try:
            os.set_blocking(file_descriptor, False)
            # skip 1 loop
            await skip_ready_cycle()
            
            protocol.connection_made(self)
            
            # On AIX, the reader trick (to be notified when the read end of the  socket is closed) only works for
            # sockets. On other platforms it works for pipes and sockets.
            if is_socket or (is_fifo and not IS_AIX):
                loop.add_reader(file_descriptor, self._read_ready)
        except:
            self.close()
            raise
        
        return self
    
    def __repr__(self):
        """Returns the transport layer's representation."""
        return f'<{self.__class__.__name__} file_descriptor={self._file_descriptor}>'
    
    
    @copy_docs(TransportLayerBase.get_write_buffer_size)
    def get_write_buffer_size(self):
        return len(self._buffer)
    
    
    def _read_ready(self):
        """
        Added as a read callback on the respective event loop to be called when the data is received on the pipe.
        
        If this happens, since it is a write only pipe, means it should be closed, so we do like that.
        """
        # Pipe was closed by peer.
        if self._buffer:
            exception = BrokenPipeError()
        else:
            exception = None
            
        self._close(exception)
    
    
    @copy_docs(TransportLayerBase.write)
    def write(self, data):
        if not data:
            return
        
        if isinstance(data, bytearray):
            data = memoryview(data)
        
        if self._closing:
            return
        
        buffer = self._buffer
        if not buffer:
            try:
                n = os.write(self._file_descriptor, data)
            except (BlockingIOError, InterruptedError):
                n = 0
            except BaseException as err:
                self._fatal_error(err, 'Fatal write error on pipe transport')
                return
            
            if n == len(data):
                return
            
            if n > 0:
                data = memoryview(data)[n:]
            
            self._loop.add_writer(self._file_descriptor, self._write_ready)
        
        buffer.extend(data)
        self._maybe_pause_protocol()
    
    
    def _write_ready(self):
        """
        Added as a write callback on the respective event loop when the transport has unsent data. Called when the
        respective socket becomes writable.
        """
        buffer = self._buffer
        
        try:
            n = os.write(self._file_descriptor, buffer)
        except (BlockingIOError, InterruptedError):
            pass
        
        except BaseException as err:
            buffer.clear()
            self._loop.remove_writer(self._file_descriptor)
            self._fatal_error(err, 'Fatal write error on pipe transport')
        else:
            if n == len(buffer):
                buffer.clear()
                self._loop.remove_writer(self._file_descriptor)
                self._maybe_resume_protocol()  # May append to buffer.
                if self._closing:
                    self._loop.remove_reader(self._file_descriptor)
                    self._call_connection_lost(None)
                return
            
            if n > 0:
                del buffer[:n]
    
    
    @copy_docs(TransportLayerBase.can_write_eof)
    def can_write_eof(self):
        return True
    
    
    @copy_docs(TransportLayerBase.write_eof)
    def write_eof(self):
        if self._closing:
            return
        
        self._closing = True
        if not self._buffer:
            loop = self._loop
            loop.remove_reader(self._file_descriptor)
            loop.call_soon(self.__class__._call_connection_lost, self, None)
    
    
    @copy_docs(TransportLayerBase.set_protocol)
    def set_protocol(self, protocol):
        self._protocol = protocol
    
    
    @copy_docs(TransportLayerBase.get_protocol)
    def get_protocol(self):
        return self._protocol
    
    
    @copy_docs(TransportLayerBase.get_protocol)
    def is_closing(self):
        return self._closing
    
    
    @copy_docs(TransportLayerBase.close)
    def close(self):
        if (self._pipe is not None) and (not self._closing):
            self.write_eof()
    
    def __del__(self):
        """
        Closes the write pipe transport if not yet closed.
        """
        pipe = self._pipe
        if (pipe is not None):
            pipe.close()
    
    
    @copy_docs(TransportLayerBase.abort)
    def abort(self):
        self._close(None)
    
    
    @copy_docs(TransportLayerBase._fatal_error)
    def _fatal_error(self, exception, message = 'Fatal error on pipe transport'):
        if not isinstance(exception, OSError):
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
        
        self._close(exception)
    
    
    def _close(self, exception):
        """
        Starts the transport's closing process.
        
        Parameters
        ----------
        exception : `None`, ``BaseException``
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        self._closing = True
        
        loop = self._loop
        buffer = self._buffer
        if buffer:
            self._loop.remove_writer(self._file_descriptor)
            buffer.clear()
        
        loop.remove_reader(self._file_descriptor)
        loop.call_soon(self.__class__._call_connection_lost, self, exception)
    
    
    def _call_connection_lost(self, exception):
        """
        Calls the write pipe transport's protocol's `.connection_lost` with the given exception and closes the
        transport's pipe.
        
        Parameters
        ----------
        exception : `None`, ``BaseException``
            Exception to call the protocol's ``.connection_lost`` with.
            
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        protocol = self._protocol
        if protocol is None:
            return
        
        try:
            protocol.connection_lost(exception)
        finally:
            pipe = self._pipe
            if (pipe is not None):
                self._pipe = None
                pipe.close()
            
            self._protocol = None
    
    
    def _maybe_pause_protocol(self):
        """
        Called after data was ensured to be written into the pipe to check whether it's protocol should be paused.
        """
        size = self.get_write_buffer_size()
        if size <= self._high_water:
            return
        
        if self._protocol_paused:
            return
        
        self._protocol_paused = True
        
        protocol = self._protocol
        if protocol is None:
            return
        
        try:
            protocol.pause_writing()
        except BaseException as err:
            write_exception_async(
                err,
                [
                    repr(self),
                    '`._maybe_pause_protocol` failed\nOn: ',
                    repr(protocol),
                    '.pause_writing()\n'
                ],
                loop = self._loop,
            )
    
    
    def _maybe_resume_protocol(self):
        """
        Called after successful writing to the pipe to check whether the protocol should be resumed.
        """
        if (self._protocol_paused and self.get_write_buffer_size() <= self._low_water):
            self._protocol_paused = False
            protocol = self._protocol
            if (protocol is not None):
                try:
                    protocol.resume_writing()
                except BaseException as err:
                    write_exception_async(
                        err,
                        [
                            repr(self),
                            '`._maybe_resume_protocol` failed\nOn: ',
                            repr(protocol),
                            '.resume_writing()\n'
                        ],
                        loop = self._loop,
                    )
    
    
    @copy_docs(TransportLayerBase.get_write_buffer_limits)
    def get_write_buffer_limits(self):
        return self._low_water, self._high_water
    
    
    def _set_write_buffer_limits(self, low = None, high = None):
        """
        Sets the write buffer limits of the transport.
        
        Parameters
        ----------
        low : None`, `int` = `None`, Optional
            The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to `65536`.
        high : `None`, `int` = `None`, Optional
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
    
    
    @copy_docs(TransportLayerBase.set_write_buffer_limits)
    def set_write_buffer_limits(self, low = None, high = None):
        self._set_write_buffer_limits(low = low, high = high)
        self._maybe_pause_protocol()
