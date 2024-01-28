__all__ = ('DatagramAddressedReadProtocol', 'DatagramMergerReadProtocol', 'ReadProtocolBase', 'ReadWriteProtocolBase',)

from collections import deque

from ...utils import copy_docs

from ..exceptions import CancelledError
from ..traps import Future, Task, future_or_timeout, skip_ready_cycle

from .abstract import AbstractProtocolBase


CHUNK_LIMIT = 32

class ReadProtocolBase(AbstractProtocolBase):
    """
    Asynchronous read protocol implementation.
    
    Scarlet-io backend uses optimistic generator based chunked readers, which have really long and complicated
    implementation, but their speed is pretty good.
    
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
    """
    __slots__ = (
        '_at_eof', '_chunks', '_exception', '_loop', '_offset', '_paused', '_payload_reader', '_payload_waiter',
        '_transport'
    )
    
    def __new__(cls, loop):
        """
        Creates a new read protocol instance.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop, what the protocol uses for it's asynchronous tasks.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._transport = None
        self._exception = None
        self._chunks = deque()
        self._offset = 0
        self._at_eof = False
        self._payload_reader = None
        self._payload_waiter = None
        self._paused = False
        return self
    
    
    def __repr__(self):
        """Returns the transport's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
        ]
        
        if self._at_eof:
            repr_parts.append(' at eof')
            field_added = True
        else:
            field_added = False
        
        transport = self._transport
        if (transport is not None):
            if field_added:
                repr_parts.append(', ')
            else:
                field_added = True
            
            repr_parts.append(' transport = ')
            repr_parts.append(repr(transport))
        
        exception = self._exception
        if (exception is not None):
            if field_added:
                repr_parts.append(', ')
            else:
                field_added = True
            
            repr_parts.append(' exception = ')
            repr_parts.append(repr(exception))
        
        payload_reader = self._payload_reader
        if (payload_reader is not None):
            if field_added:
                repr_parts.append(', ')
            
            repr_parts.append(' payload_reader = ')
            repr_parts.append(repr(payload_reader))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    @copy_docs(AbstractProtocolBase.connection_made)
    def connection_made(self, transport):
        self._transport = transport
    
    
    @copy_docs(AbstractProtocolBase.connection_lost)
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
        if exception is None:
            self.eof_received()
        else:
            self.set_exception(exception)
    
    
    @copy_docs(AbstractProtocolBase.get_extra_info)
    def get_extra_info(self, name, default = None):
        transport = self._transport
        if transport is None:
            info = default
        else:
            info = transport.get_extra_info(name, default)
        
        return info
    
    
    @copy_docs(AbstractProtocolBase.close)
    def close(self):
        transport = self._transport
        if (transport is not None):
            transport.close()
    
    
    @copy_docs(AbstractProtocolBase.close_transport)
    def get_transport(self):
        return self._transport
    
    
    # read related
    @property
    def size(self):
        """
        Returns the received and not yet processed data's size by the protocol.
        
        Returns
        -------
        size : `int`
        """
        result = - self._offset
        for chunk in self._chunks:
            result += len(chunk)
        
        return result
    
    
    def at_eof(self):
        """
        Returns whether the protocol is at eof. If at eof, but has content left, then returns `False` however.
        
        Returns
        -------
        at_eof : `bool`
        """
        if not self._at_eof:
            return False
        
        if (self._payload_reader is not None):
            return False
        
        if self.size:
            return False
    
        return True
    
    
    @copy_docs(AbstractProtocolBase.set_exception)
    def set_exception(self, exception):
        self._exception = exception
        
        payload_waiter = self._payload_waiter
        if (payload_waiter is None):
            return
        
        self._payload_waiter = None
        payload_waiter.set_exception_if_pending(exception)
        
        self._payload_reader.close()
        self._payload_reader = None
    
    
    @copy_docs(AbstractProtocolBase.eof_received)
    def eof_received(self):
        self._at_eof = True
        
        payload_reader = self._payload_reader
        if payload_reader is None:
            return False
        
        try:
             payload_reader.throw(CancelledError())
        except CancelledError as err:
            new_exception = ConnectionError('Connection closed unexpectedly with EOF.')
            new_exception.__cause__ = err
            payload_waiter = self._payload_waiter
            self._payload_reader = None
            self._payload_waiter = None
            payload_waiter.set_exception_if_pending(new_exception)
        
        except StopIteration as err:
            args = err.args
            if not args:
                result = None
            elif len(args) == 1:
                result = args[0]
            else:
                result = args
            
            payload_waiter = self._payload_waiter
            self._payload_reader = None
            self._payload_waiter = None
            payload_waiter.set_result_if_pending(result)
        except GeneratorExit as err:
            payload_waiter = self._payload_waiter
            self._payload_reader = None
            self._payload_waiter = None
            exception = CancelledError()
            exception.__cause__ = err
            payload_waiter.set_exception_if_pending(exception)
        except BaseException as err:
            payload_waiter = self._payload_waiter
            self._payload_reader = None
            self._payload_waiter = None
            payload_waiter.set_exception_if_pending(err)
        
        return False
    
    
    @copy_docs(AbstractProtocolBase.data_received)
    def data_received(self, data):
        if not data:
            return
        
        payload_reader = self._payload_reader
        if (payload_reader is None):
            chunks = self._chunks
            chunks.append(data)
            if (len(chunks) > CHUNK_LIMIT) and (not self._paused):
                transport = self._transport
                if (transport is not None):
                    try:
                        transport.pause_reading()
                    except (AttributeError, NotImplementedError):
                        #cant be paused
                        self._transport = None
                    else:
                        self._paused = True
        else:
            try:
                payload_reader.send(data)
            except StopIteration as err:
                args = err.args
                if not args:
                    result = None
                elif len(args) == 1:
                    result = args[0]
                else:
                    result = args
                
                payload_waiter = self._payload_waiter
                self._payload_reader = None
                self._payload_waiter = None
                payload_waiter.set_result_if_pending(result)
            except GeneratorExit as err:
                payload_waiter = self._payload_waiter
                self._payload_reader = None
                self._payload_waiter = None
                exception = CancelledError()
                exception.__cause__ = err
                payload_waiter.set_exception_if_pending(exception)
            except BaseException as err:
                payload_waiter = self._payload_waiter
                self._payload_reader = None
                self._payload_waiter = None
                payload_waiter.set_exception_if_pending(err)
    
    
    def handle_payload_waiter_cancellation(self):
        """
        If you expect, that the payload waiter will be cancelled from outside, call this method to throw eof into the
        protocol at that case.
        """
        payload_waiter = self._payload_waiter
        if (payload_waiter is not None):
            payload_waiter.add_done_callback(self._payload_waiter_cancellation_callback)
    
    
    def _payload_waiter_cancellation_callback(self, future):
        """
        Callback to the ``.payload_waiter`` by ``.handle_payload_waiter_cancellation`` to throw eof into the
        ``.payload_reader`` task if payload waiter is cancelled from outside.
        
        Parameters
        ----------
        future : ``Future``
            The respective ``.payload_waiter``.
        """
        if future.is_cancelled():
            self.eof_received()
    
    
    def cancel_current_reader(self):
        """
        Cancels the current reader task of the protocol.
        
        Notes
        -----
        The used data by the payload reader task cannot be reused.
        """
        payload_reader = self._payload_reader
        if payload_reader is None:
            return
        
        self._payload_reader = None
        payload_reader.close()
        
        payload_waiter = self._payload_waiter
        self._payload_waiter = None
        payload_waiter.cancel()
    
    
    def set_payload_reader(self, payload_reader):
        """
        Sets payload reader to the protocol.
        
        Parameters
        ----------
        payload_reader : `GeneratorType`
            A generator, what gets control, every time a chunk is received, till it returns or raises.
        
        Returns
        -------
        payload_waiter : ``Future``
            Waiter, to what the result of the `payload_reader` is set.
        """
        assert self._payload_reader is None, 'Payload reader already set!'
        
        payload_waiter = Future(self._loop)
        exception = self._exception
        
        if (exception is None):
            try:
                payload_reader.send(None)
            except StopIteration as err:
                args = err.args
                if not args:
                    result = None
                elif len(args) == 1:
                    result = args[0]
                else:
                    result = args
                
                payload_waiter.set_result_if_pending(result)
            except GeneratorExit as err:
                exception = CancelledError()
                exception.__cause__ = err
                payload_waiter.set_exception_if_pending(exception)
            except BaseException as err:
                payload_waiter.set_exception_if_pending(err)
            
            else:
                self._payload_waiter = payload_waiter
                self._payload_reader = payload_reader
        else:
            payload_waiter.set_exception(exception)
        
        return payload_waiter
    
    
    async def read(self, n=-1):
        """
        Reads up to `n` amount of bytes from the protocol.
        
        If `n` is given as a negative integer, then will read until eof.
        
        This method is a coroutine.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read. Defaults to `-1`.
        
        Returns
        -------
        result : `bytes`
        """
        try:
            return await self.set_payload_reader(self._read_until_eof() if n < 0 else self._read_exactly(n))
        except EOFError as err:
            return err.args[0]
    
    
    async def read_exactly(self, n):
        """
        Read exactly `n` bytes from the protocol.
        
        This method is a coroutine.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read. Cannot be negative.
        
        Returns
        -------
        result : `str`
        
        Raises
        ------
        ValueError
            If `n` is less than `0`.
        EOFError
            Connection lost before `0` bytes were received.
        BaseException
            Connection lost exception if applicable.
        """
        exception = self._exception
        if (exception is not None):
            raise exception
        
        if n < 1:
            if n == 0:
                return b''
            
            raise ValueError(f'`.read_exactly` size can not be less than `0`, got {n!r}.')
        
        return await self.set_payload_reader(self._read_exactly(n))
    
    
    async def read_line(self):
        raise NotImplementedError
    
    
    async def read_until(self):
        raise NotImplementedError
    
    
    async def read_once(self):
        """
        Waits till exactly one chunk is of data is received.
        
        This method is a coroutine.
        
        Returns
        -------
        data : `bytes`
        
        Raises
        ------
        BaseException
            Connection lost exception if applicable.
        """
        exception = self._exception
        if (exception is not None):
            raise exception
        
        return await self.set_payload_reader(self._read_once())
    
    
    def _wait_for_data(self):
        """
        Payload reader task helper, what waits for 1 chunk to be receive, then adds it to ``._chunks`` and also returns
        it as well.
        
        This method is a generator.
        
        Returns
        -------
        chunk : `bytes`
        
        Raises
        ------
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        if self._paused:
            self._paused = False
            self._transport.resume_reading()
        
        chunk = yield
        self._chunks.append(chunk)
        return chunk
    
    
    def _read_exactly(self, n):
        """
        Payload reader task, what reads exactly `n` bytes from the protocol.
        
        This method is a generator.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        ValueError
            If `n` is given as a negative integer.
        EofError
            Connection lost before `n` bytes were received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        if n < 1:
            if n < 0:
                raise ValueError(f'`.read_exactly` called with negative `n`, got {n!r}.')
            else:
                return b''
        
        chunks = self._chunks
        if chunks:
            chunk = chunks[0]
            offset = self._offset
        else:
            if self._at_eof:
                raise EOFError(b'')
            
            chunk = yield from self._wait_for_data()
            offset = 0
        
        chunk_size = len(chunk)
        if offset == 0:
            if chunk_size > n:
                self._offset = n
                return chunk[:n]
            # chunk same size as the requested?
            elif chunk_size == n:
                del chunks[0]
                # offset is already 0, nice!
                return chunk
            
            else:
                n -= len(chunk)
                collected = [chunk]
                del chunks[0]
        else:
            end = offset + n
            if chunk_size > end:
                self._offset = end
                return chunk[offset:end]
            # chunk_size + offset end when the requested's end is.
            elif chunk_size == end:
                del chunks[0]
                self._offset = 0
                return chunk[offset:]
            
            else:
                n -= (chunk_size - offset)
                collected = [memoryview(chunk)[offset:]]
                del chunks[0]
        
        while True:
            if chunks:
                chunk = chunks[0]
            else:
                if self._at_eof:
                    self._offset = 0
                    raise EOFError(b''.join(collected))
                
                chunk = yield from self._wait_for_data()
            
            chunk_size = len(chunk)
            
            n -= chunk_size
            
            if n > 0:
                collected.append(chunk)
                del chunks[0]
                continue
            
            if n == 0:
                collected.append(chunk)
                del chunks[0]
                self._offset = 0
                return b''.join(collected)
            
            offset = self._offset = chunk_size + n
            collected.append(memoryview(chunk)[:offset])
            return b''.join(collected)
    
    
    def _read_until(self, boundary):
        """
        Payload reader task, what reads until `boundary` is hit.
        
        This method is a generator.
        
        Parameters
        ----------
        boundary : `bytes`
            The amount of bytes to read.
        
        Returns
        -------
        collected : `bytes`, `bytearray`
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        # This method is mainly used for multipart reading, and we can forget optimizations usually.
        boundary_length = len(boundary)
        chunks = self._chunks
        if chunks:
            chunk = chunks[0]
            offset = self._offset
        else:
            if self._at_eof:
                raise EOFError(b'')
            
            chunk = yield from self._wait_for_data()
            offset = 0
        
        # Optimal case is when we instantly hit boundary.
        if len(chunk) > boundary_length:
            index = chunk.find(boundary, offset)
            if index != -1:
                # Barrier found
                data = chunk[offset:index]
                offset += boundary
                if offset == len(chunk):
                    del chunks[0]
                    offset = 0
                self._offset = offset
                return data
            
            offset = len(chunk) - boundary_length
        
        # Second case, we create a bytearray and push the data to it.
        data = bytearray(chunk)
        while True:
            if chunks:
                chunk = chunks[0]
            else:
                if self._at_eof:
                    raise EOFError(b'')
                
                chunk = yield from self._wait_for_data()
            
            data.extend(chunk)
            index = chunk.find(boundary, offset)
            if index != -1:
                # Barrier found
                offset = len(chunk) - len(data) + index + boundary_length
                if offset == len(chunk):
                    del chunks[0]
                    offset = 0
                
                self._offset = offset
                del data[index:]
                return data
            
            offset = len(data) - boundary_length
            del chunks[0]
    
    
    def _read_until_eof(self):
        """
        Payload reader task, which reads the protocol until EOF is hit.
        
        This method is a generator.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        chunks = self._chunks
        
        if not self._at_eof:
            while True:
                try:
                    yield from self._wait_for_data()
                except (CancelledError, GeneratorExit):
                    if self._at_eof:
                        break
                    
                    raise
        
        if not chunks:
            return b''
        
        offset = self._offset
        if offset:
            chunks[0] = memoryview(chunks[0])[offset:]
        
        collected = b''.join(chunks)
        chunks.clear()
        return collected
    
    
    def _read_once(self):
        """
        Reader task for reading exactly one chunk out.
        
        This method is a generator.
        
        Returns
        -------
        chunk : `bytes`
            The read chunk. Returns empty `bytes` on eof.
        
        Raises
        ------
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        chunks = self._chunks
        if not chunks:
            try:
                yield from self._wait_for_data()
            except (CancelledError, GeneratorExit):
                if self._at_eof:
                    return b''
                
                raise
        
        chunk = chunks.popleft()
        offset = self._offset
        if offset:
            self._offset = 0
            chunk = chunk[offset:]
        
        return chunk



class ReadWriteProtocolBase(ReadProtocolBase):
    """
    Read-write asynchronous protocol implementation.
    
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
    """
    __slots__ = ('_drain_waiter', )
    
    def __new__(cls, loop):
        """
        Creates a new read-write protocol instance.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop, what the protocol uses for it's asynchronous tasks.
        """
        self = ReadProtocolBase.__new__(cls, loop)
        
        self._drain_waiter = None
        
        return self
    
    
    @copy_docs(AbstractProtocolBase.pause_writing)
    def pause_writing(self):
        self._paused = True
    
    
    @copy_docs(AbstractProtocolBase.resume_writing)
    def resume_writing(self):
        self._paused = False
        
        drain_waiter = self._drain_waiter
        if drain_waiter is None:
            return
        
        self._drain_waiter = None
        drain_waiter.set_result_if_pending(None)
    
    
    async def _drain_helper(self):
        """
        Called when the transport buffer after writing goes over the high limit mark to wait till it is drained.
        
        This method is a coroutine.
        """
        if not self._paused:
            return
        
        drain_waiter = Future(self._loop)
        self._drain_waiter = drain_waiter
        await drain_waiter
    
    @copy_docs(ReadProtocolBase.connection_lost)
    def connection_lost(self, exception):
        if exception is None:
            self.eof_received()
        else:
            self.set_exception(exception)
        
        # wake up the writer if currently paused.
        if not self._paused:
            return
        
        drain_waiter = self._drain_waiter
        if drain_waiter is None:
            return
        
        self._drain_waiter = None
        if drain_waiter.is_done():
            return
        
        if exception is None:
            drain_waiter.set_result(None)
        else:
            drain_waiter.set_exception(exception)
    
    
    @copy_docs(AbstractProtocolBase.write)
    def write(self, data):
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self={self!r}.')
        
        transport.write(data)
    
    
    @copy_docs(AbstractProtocolBase.writelines)
    def writelines(self, lines):
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self={self!r}.')
        
        transport.writelines(lines)
    
    
    @copy_docs(AbstractProtocolBase.write_eof)
    def write_eof(self):
        transport = self._transport
        if (transport is not None):
            transport.write_eof()
    
    
    @copy_docs(AbstractProtocolBase.can_write_eof)
    def can_write_eof(self):
        transport = self._transport
        if (transport is None):
            return False
        
        return transport.can_write_eof()
    
    
    @copy_docs(AbstractProtocolBase.drain)
    async def drain(self):
        # use after writing
        exception = self._exception
        if (exception is not None):
            raise exception
        
        transport = self._transport
        if (transport is not None):
            if transport.is_closing():
                # skip 1 loop, so connection_lost() will be called
                await skip_ready_cycle()
        
        await self._drain_helper()



class DatagramAddressedReadProtocol(AbstractProtocolBase):
    """
    Datagram reader protocol for reading from payloads form multiple addresses.
    
    Attributes
    ----------
    _by_address : `dict` of (`tuple` (`str`, `int`), ``ReadProtocolBase``) items
        Dictionary to store the alive readers by address.
    _loop : ``EventThread``
        The loop to what the protocol is bound to.
    _protocol_factory : `type`
        Protocol type to create for each address.
    _transport : `object`
        Asynchronous transport implementation, what calls the protocol's ``.datagram_received`` when data is
        received.
    _waiters : `None`, `list` of `Future`
        Waiters for any payload receive if applicable.
    """
    __slots__ = ('_by_address', '_loop', '_protocol_factory', '_transport', '_waiters',)
    
    def __new__(cls, loop, protocol_factory):
        """
        Creates a new datagram addressed read protocol instance bound to the given loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the protocol gonna be bound to.
        protocol_factory : `callable`
            Protocol type to create for each address.
            
            Defaults to ``ReadProtocolBase``.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._by_address = {}
        self._transport = None
        self._waiters = None
        self._protocol_factory = protocol_factory
        return self
    
    
    @copy_docs(AbstractProtocolBase.connection_made)
    def connection_made(self, transport):
        self._transport = transport
        for reader_protocol in self._by_address.values():
            reader_protocol.connection_made(transport)
    
    
    @copy_docs(AbstractProtocolBase.connection_lost)
    def connection_lost(self, exception):
        for reader_protocol in self._by_address.values():
            if exception is None:
                reader_protocol.eof_received()
            else:
                reader_protocol.set_exception(exception)
    
    
    @copy_docs(AbstractProtocolBase.datagram_received)
    def datagram_received(self, data, address):
        by_address = self._by_address
        try:
            protocol = by_address[address]
        except KeyError:
            protocol = self._protocol_factory()
            protocol.connection_made(self._transport)
            by_address[address] = protocol
        
        protocol.data_received(data)
        
        waiters = self._waiters
        if (waiters is not None):
            self._waiters = None
            result = (address, protocol)
            for waiter in waiters:
                waiter.set_result_if_pending(result)
    
    
    @copy_docs(AbstractProtocolBase.error_received)
    def error_received(self, exception):
        pass
    
    
    async def wait_for_receive(self, address = None, timeout = None):
        """
        Can be used to wait for payload to receive. Note, that this method should be used only initially, because the
        reader protocols implement the reading.
        
        This method is a coroutine.
        
        Parameters
        ----------
        address : `None`, `tuple` (`str`, `int`) = `None`, Optional
            The address of which payload is waiter for.
        timeout : `None`, `float = `None`, Optional
            The maximal amount of time to wait before raising `TimeoutError`.
        
        Returns
        -------
        result : `None`, ``ReadProtocolBase`` or (`tuple` (`str`, `int`), ``ReadProtocolBase``)
            - If `timeout` is given and timeout occur, then returns `None`.
            - if `address` is given and data is received from ir, then returns the respective ``ReadProtocolBase``.
            - If `address` is not given, then returns a `tuple` of the respective `address` and protocol.
        
        Raises
        ------
        TimeoutError
            - If timeout occurred.
        """
        if timeout is None:
            if address is None:
                waiters = self._waiters
                if waiters is None:
                    self._waiters = waiters = []
                
                waiter = Future(self._loop)
                waiters.append(waiter)
                
                return await waiter
            else:
                while True:
                    waiters = self._waiters
                    if waiters is None:
                        self._waiters = waiters = []
                    
                    waiter = Future(self._loop)
                    waiters.append(waiter)
                    
                    address, protocol = await waiter
                    if address == address:
                        return protocol
                    
                    continue
        
        else:
            waiter = Task(self._loop, self.wait_for_receive(address))
            waiter.apply_timeout(timeout)
            
            try:
                result = await waiter
            except TimeoutError:
                result = None
            
            return result
    
    
    @copy_docs(AbstractProtocolBase.close)
    def close(self):
        transport = self._transport
        if (transport is not None):
            transport.close()
    
    
    @copy_docs(AbstractProtocolBase.close_transport)
    def get_transport(self):
        return self._transport


class DatagramMergerReadProtocol(ReadProtocolBase):
    """
    Asynchronous read protocol implementation.
    
    Scarlet-io backend uses optimistic generator based chunked readers, which have really long and complicated
    implementation, but their speed is pretty good.
    
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
    """
    __slots__ = ()
    
    @copy_docs(AbstractProtocolBase.datagram_received)
    def datagram_received(self, data, address):
        self.data_received(data)
