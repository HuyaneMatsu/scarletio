__all__ = ('DatagramAddressedReadProtocol', 'DatagramMergerReadProtocol', 'ReadProtocolBase', 'ReadWriteProtocolBase',)

from collections import deque as Deque
from functools import partial as partial_func
from warnings import warn

from ...utils import copy_docs, to_coroutine

from ..traps import Future, Task, skip_ready_cycle

from .abstract import AbstractProtocolBase
from .payload_stream import PayloadStream


BUFFER_SIZE_MAX = 131072


def _get_end_intersection_sizes(chunk, offset, boundary):
    """
    Gets the end intersection sizes.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process.
    
    offset : `int`
        Data chunk offset.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    Returns
    -------
    intersection_sizes : `None | list<int>`
    """
    intersection_sizes = None
    
    chunk_length = len(chunk)
    boundary_length = len(boundary) - 1
    
    chunk_start_index = chunk_length - boundary_length
    if chunk_start_index < offset:
        chunk_start_index = offset
    elif chunk_start_index < 0:
        chunk_start_index = 0
    
    for chunk_start_index in range(chunk_start_index, chunk_length):
        for shift in range(0, chunk_length - chunk_start_index):
            if chunk[chunk_start_index + shift] != boundary[shift]:
                break
        
        else:
            if intersection_sizes is None:
                intersection_sizes = []
            
            intersection_sizes.append(chunk_length - chunk_start_index)
    
    return intersection_sizes


def _finish_intersection_sizes(chunk, boundary, intersection_sizes):
    """
    Finishes intersection sizes.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    intersection_sizes : `list<int>`
        Detected intersection sizes of on the previous chunk.
        The processed ones are removed from it while the too low values to finish processing on are left in it.
    
    Returns
    -------
    consumed_bytes : `int`
        Returns `-1` on failure.
    intersection_sizes : `None | list<int>`
        Leftover intersection sizes if chunk size is too small.
    """
    chunk_length = len(chunk)
    boundary_length = len(boundary) - 1
    continued_intersection_sizes = None
    
    for intersection_size in intersection_sizes:
        leftover_size = boundary_length - intersection_size + 1
        if leftover_size > chunk_length:
            if continued_intersection_sizes is None:
                continued_intersection_sizes = []
            continued_intersection_sizes.append(intersection_size)
            continue
        
        for shift in range(0, leftover_size):
            if chunk[shift] != boundary[intersection_size + shift]:
                break
        
        else:
            # Mark all as processed
            return leftover_size, None
    
    return -1, continued_intersection_sizes


def _continue_intersection_sizes(chunk, boundary, intersection_sizes):
    """
    Continues intersection sizes on a new chunk.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process. Must have length > 0.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    intersection_sizes : `list<int>`
        Detected the non matched intersection sizes.
    
    Returns
    -------
    intersection_sizes : `None | list<int>`
        The new matched intersection sizes.
    """
    chunk_length = len(chunk)
    continued_intersection_sizes = None
    
    for intersection_size in intersection_sizes:
        for shift in range(0, chunk_length):
            if chunk[shift] != boundary[intersection_size + shift]:
                break
        
        else:
            if continued_intersection_sizes is None:
                continued_intersection_sizes = []
            
            continued_intersection_sizes.append(intersection_size + shift + 1)
    
    return continued_intersection_sizes


def _get_released_from_held_back(held_back, amount_to_keep):
    """
    Releases from held back chunks.
    
    Parameters
    ----------
    held_back : `None | list<bytes | memoryview>`
        The held back chunks.
    
    amount_to_keep : `int`
        The amount of bytes to hold back.
    
    Returns
    -------
    released : `None | list<bytes | memoryview>`
    held_back : `None | list<bytes | memoryview>`
    """
    if held_back is None:
        return None, None
    
    if amount_to_keep <= 0:
        return held_back, None
    
    amount_to_release = sum(len(chunk) for chunk in held_back) - amount_to_keep
    if amount_to_release <= 0:
        return None, held_back
    
    released = []
    
    while True:
        chunk = held_back[0]
        chunk_length = len(chunk)
        
        amount_to_release -= chunk_length
        if amount_to_release > 0:
            del held_back[0]
            released.append(chunk)
            
            if not held_back:
                held_back = None
                break
            
            continue
        
        if amount_to_release < 0:
            split_at = len(chunk) + amount_to_release
            chunk = memoryview(chunk)
            held_back[0] = chunk[split_at :]
            released.append(chunk[: split_at])
            break
        
        del held_back[0]
        released.append(chunk)
        if held_back:
            break
        
        held_back = None
        break
    
    return released, held_back


def _merge_intersection_sizes(intersection_sizes_0, intersection_sizes_1):
    """
    Merges two intersection sizes.
    
    Parameters
    ----------
    intersection_sizes_0 : `None | list<int>`
        Intersection sizes to merge.
    
    intersection_sizes_1 : `None | list<int>`
        Intersection sizes to merge.
    
    Returns
    -------
    intersection_sizes : `None | list<int>``
    """
    if intersection_sizes_0 is None:
        return intersection_sizes_1
    
    if intersection_sizes_1 is None:
        return intersection_sizes_0
    
    return [*intersection_sizes_0, *intersection_sizes_1]


class ReadProtocolBase(AbstractProtocolBase):
    """
    Asynchronous read protocol implementation.
    
    Scarlet-io backend uses optimistic generator based chunked readers, which have really long and complicated
    implementation, but their speed is pretty good.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether the protocol received end of file.
    
    _chunks : `Deque` of `bytes`
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
    
    _payload_stream : `None | Stream``
        Payload stream of the protocol.
    
    _payload_reader : `None | GeneratorType | CoroutineType`
        Payload reader generator, what gets the control back, when data, eof or any exception is received.
    
    _transport : `None | AbstractTransportLayerBase`
        Asynchronous transport implementation. Is set meanwhile the protocol is alive.
    """
    __slots__ = (
        '_at_eof', '_chunks', '_exception', '_loop', '_offset', '_paused', '_payload_reader', '_payload_stream',
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
        self._at_eof = False
        self._loop = loop
        self._chunks = Deque()
        self._exception = None
        self._offset = 0
        self._paused = False
        self._payload_reader = None
        self._payload_stream = None
        self._transport = None
        return self
    
    
    @property
    def _payload_waiter(self):
        """
        Deprecated and will be removed at 2025 September. Please use `._payload_stream` instead.
        """
        warn(
            f'f`{type(self).__name__}._payload_stream` is deprecated and will be removed in 2025 September. '
            f'Please use `._payload_stream` instead.'
        )
        return self._payload_stream
    
    
    def __repr__(self):
        """Returns the transport's representation."""
        repr_parts = ['<', type(self).__name__]
        
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
    def get_size(self):
        """
        Returns the received and not yet processed data's size by the protocol.
        
        Returns
        -------
        size : `int`
        """
        size = -self._offset
        for chunk in self._chunks:
            size += len(chunk)
        
        payload_stream = self._payload_stream
        if (payload_stream is not None):
            size += payload_stream.get_buffer_size()
        
        return size
    
    
    def is_at_eof(self):
        """
        Returns whether the protocol is at eof. If at eof, but has content left, then returns `False` however.
        
        Returns
        -------
        at_eof : `bool`
        """
        if not self._at_eof:
            return False
        
        # Note:
        # we cannot have `payload_reader` set because that consumes all of our `size` at once.
        
        if self.get_size():
            return False
        
        return True
    
    
    @copy_docs(AbstractProtocolBase.set_exception)
    def set_exception(self, exception):
        self._exception = exception
        
        payload_stream = self._payload_stream
        if (payload_stream is None):
            return
        
        self._payload_stream = None
        payload_stream.set_done_exception(exception)
        
        self._payload_reader.close()
        self._payload_reader = None
    
    
    @copy_docs(AbstractProtocolBase.eof_received)
    def eof_received(self):
        self._at_eof = True
        payload_reader = self._payload_reader
        if payload_reader is None:
            return False
        
        payload_stream = self._payload_stream
        self._payload_reader = None
        self._payload_stream = None
        
        try:
            payload_reader.throw(EOFError(b''))
        except EOFError as exception:
            new_exception = ConnectionError('Connection closed unexpectedly with EOF.')
            new_exception.__cause__ = exception
            payload_stream.set_done_exception(new_exception)
        
        except StopIteration:
            payload_stream.set_done_success()
        
        except GeneratorExit as exception:
            new_exception = ConnectionError('Payload reader destroyed.')
            new_exception.__cause__ = exception
            payload_stream.set_done_exception(new_exception)
        
        except BaseException as exception:
            payload_stream.set_done_exception(exception)
        
        else:
            payload_reader.close()
            new_exception = RuntimeError('Payload stream ignored eof.')
            payload_stream.set_done_exception(new_exception)
        
        return False
    
    
    @copy_docs(AbstractProtocolBase.data_received)
    def data_received(self, data):
        if not data:
            return
        
        payload_reader = self._payload_reader
        if (payload_reader is None):
            chunks = self._chunks
            chunks.append(data)
        else:
            try:
                payload_reader.send(data)
            except BaseException as exception:
                payload_stream = self._payload_stream
                self._payload_reader = None
                self._payload_stream = None
                
                if isinstance(exception, StopIteration):
                    payload_stream.set_done_success()
                
                elif isinstance(exception, EOFError):
                    new_exception = ConnectionError('Connection closed unexpectedly with EOF.')
                    new_exception.__cause__ = exception
                    payload_stream.set_done_exception(new_exception)
                
                elif isinstance(exception, GeneratorExit):
                    new_exception = ConnectionError('Payload reader destroyed.')
                    new_exception.__cause__ = exception
                    payload_stream.set_done_exception(new_exception)
                
                
                else:
                    payload_stream.set_done_exception(exception)
        
        # Pause if buffer is too big
        self._pause_reading()
    
    
    def _pause_reading(self):
        """
        Called when the protocol should consider pausing reading of its transport.
        """
        if (self.get_size() > BUFFER_SIZE_MAX) and (not self._paused):
            transport = self._transport
            if (transport is not None):
                try:
                    transport.pause_reading()
                except (AttributeError, NotImplementedError):
                    # cant be paused
                    self._transport = None
                else:
                    self._paused = True
    
    
    def _resume_reading(self):
        """
        Called when the protocol should consider resuming reading of its transport.
        """
        if self._paused:
            self._paused = False
            self._transport.resume_reading()
    
    
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
        
        payload_stream = self._payload_stream
        self._payload_stream = None
        payload_stream.set_done_cancelled()
        
        payload_reader.close()
    
    
    def set_payload_reader(self, payload_reader_function):
        """
        Sets payload reader to the protocol.
        
        Parameters
        ----------
        payload_reader_function : `callable`
            A function, that gets control, every time a chunk is received.
        
        Returns
        -------
        payload_stream : ``PayloadStream``
        """
        assert self._payload_reader is None, 'Payload reader already set!'
        
        payload_stream = PayloadStream(self)
        
        exception = self._exception
        if (exception is not None):
            payload_stream.set_done_exception(exception)
        
        else:
            payload_reader = payload_reader_function(payload_stream)
            
            try:
                payload_reader.send(None)
            except StopIteration:
                payload_stream.set_done_success()
            
            except EOFError as exception:
                new_exception = ConnectionError('Connection closed unexpectedly with EOF.')
                new_exception.__cause__ = exception
                payload_stream.set_done_exception(new_exception)
            
            except GeneratorExit as exception:
                new_exception = ConnectionError('Payload reader destroyed.')
                new_exception.__cause__ = exception
                payload_stream.set_done_exception(new_exception)
            
            except BaseException as exception:
                payload_stream.set_done_exception(exception)
            
            else:
                self._payload_stream = payload_stream
                self._payload_reader = payload_reader
        
        return payload_stream
    
    
    def handle_payload_stream_abortion(self):
        """
        If you expect, that the payload waiter will be cancelled from outside, call this method to throw eof into the
        protocol at that case.
        """
        payload_stream = self._payload_stream
        if (payload_stream is not None):
            payload_stream.add_done_callback(self._payload_stream_abortion_callback)
    
    
    def _payload_stream_abortion_callback(self, payload_stream):
        """
        Callback added to ``._payload_stream`` by ``.handle_payload_stream_abortion`` to throw eof into the
        ``.payload_reader`` task if payload stream is aborted from outside.
        
        Parameters
        ----------
        payload_stream : ``PayloadStream``
            The respective ``._payload_stream``.
        """
        if payload_stream.is_aborted():
            self.eof_received()
    
    
    async def read(self, n = -1):
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
        if n < 0:
            payload_stream = self.set_payload_reader(self._read_until_eof)
        
        elif n > 0:
            payload_stream = self.set_payload_reader(partial_func(self._read_exactly, n, True))
        
        else:
            exception = self._exception
            if (exception is not None):
                raise exception
            
            return b''
        
        return (await payload_stream)
    
    
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
        ConnectionError
            Connection lost before `n` bytes were received.
        """
        
        if n > 0:
            return (await self.set_payload_reader(partial_func(self._read_exactly, n, False)))
        
        if n < 0:
            raise ValueError(f'`.read_exactly` size can not be less than `0`, got {n!r}.')
        
        # n == 0
        exception = self._exception
        if (exception is not None):
            raise exception
        
        return b''
    
    
    async def read_line(self):
        raise NotImplementedError
    
    
    async def read_until(self, boundary):
        """
        Reads until the given boundary.
        This method is a coroutine.
        
        Parameters
        ----------
        boundary : `bytes`
            The boundary to read until. Consumed but not returned.
        
        Raises
        ------
        ConnectionError
            Connection lost before boundary hit.
        """
        if not boundary:
            exception = self._exception
            if (exception is not None):
                raise exception
            
            return b''
        
        return await self.set_payload_reader(partial_func(self._read_until, boundary))
    
    
    async def read_once(self):
        """
        Waits till exactly one chunk is of data is received.
        
        This method is a coroutine.
        
        Returns
        -------
        data : `bytes`
        
        Raises
        ------
        ConnectionError
            At end of file.
        """
        return (await self.set_payload_reader(self._read_once))
    
    
    @to_coroutine
    def _wait_for_data(self):
        """
        Payload reader task helper, what waits for 1 chunk to be receive, then adds it to ``._chunks`` and also returns
        it as well.
        
        This method is an awaitable generator.
        
        Returns
        -------
        chunk : `bytes`
        """
        self._resume_reading()
        
        chunk = yield
        self._chunks.append(chunk)
        return chunk
    
    
    async def _read_exactly_by_chunk(self, n):
        """
        Reads exactly `n` chunks and yields them back.
        
        This method is a coroutine generator.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read. Must be greater than 0.
        
        Returns
        -------
        chunk : `bytes-like`
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        """
        chunks = self._chunks
        if chunks:
            chunk = chunks[0]
            offset = self._offset
        else:
            if self._at_eof:
                raise EOFError(b'')
            
            chunk = await self._wait_for_data()
            offset = 0
        
        chunk_size = len(chunk)
        if offset == 0:
            if chunk_size > n:
                self._offset = n
                yield memoryview(chunk)[:n]
                return
            
            # chunk same size as the requested?
            if chunk_size == n:
                del chunks[0]
                # offset is already 0, nice!
                yield chunk
                return
            
            n -= len(chunk)
            del chunks[0]
            yield chunk
        
        else:
            end = offset + n
            if chunk_size > end:
                self._offset = end
                yield memoryview(chunk)[offset : end]
                return
            
            # chunk_size + offset end when the requested's end is.
            if chunk_size == end:
                del chunks[0]
                self._offset = 0
                yield memoryview(chunk)[offset:]
                return
            
            n -= (chunk_size - offset)
            del chunks[0]
            yield memoryview(chunk)[offset:]
        
        while True:
            if chunks:
                chunk = chunks[0]
            else:
                if self._at_eof:
                    self._offset = 0
                    raise EOFError(b'')
                
                chunk = await self._wait_for_data()
            
            chunk_size = len(chunk)
            
            n -= chunk_size
            if n > 0:
                yield chunk
                del chunks[0]
                continue
            
            if n == 0:
                yield chunk
                del chunks[0]
                self._offset = 0
                return
            
            offset = self._offset = chunk_size + n
            yield memoryview(chunk)[:offset]
            return
    
    
    async def _read_exactly(self, n, allow_eof, payload_stream):
        """
        Payload reader task, what reads exactly `n` bytes from the protocol.
        
        This method is a generator.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read. Must be greater than 0.
        
        allow_eof : `bool`
            Whether end of file is allowed.
        
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        """
        try:
            async for chunk in self._read_exactly_by_chunk(n):
                payload_stream.add_received_chunk(chunk)
        except EOFError:
            if not allow_eof:
                raise
        
        payload_stream.set_done_success()
    
    
    async def _read_exactly_as_one(self, n):
        """
        Reads exactly `n` bytes of data at once and returns it. Can be used by other payload readers.
        
        This method is a coroutine.
        
        Parameters
        ----------
        n : `int`
            The amount of bytes to read. Must be greater than 0.
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        """
        chunks = []
        async for chunk in self._read_exactly_by_chunk(n):
            chunks.append(chunk)
        
        return b''.join(chunks)
    
    
    async def _read_until_by_chunk(self, boundary):
        """
        Payload reader task, what reads until `boundary` is hit. Yields back each data chunk.
        
        This method is a coroutine.
        
        Parameters
        ----------
        boundary : `bytes`
            The boundary to read until. Consumed but not returned.
        
        Raises
        ------
        EofError
            Connection lost before boundary hit.
        """
        chunks = self._chunks
        intersection_sizes = None
        held_back = None
        
        while True:
            if chunks:
                chunk = chunks[0]
                offset = self._offset
            else:
                if self._at_eof:
                    raise EOFError(b'')
                
                chunk = await self._wait_for_data()
                offset = 0
            
            if (intersection_sizes is not None):
                offset, intersection_sizes = _finish_intersection_sizes(chunk, boundary, intersection_sizes)
                # Found boundary in between?
                if offset != -1:
                    # Do not offset if offset if at the end of the chunk. Delete chunk instead.
                    if offset == len(chunk):
                        del chunks[0]
                        offset = 0
                    self._offset = offset
                    
                    released, held_back = _get_released_from_held_back(held_back, len(boundary) - offset)
                    if (released is not None):
                        for to_release in released:
                            yield to_release
                    released = None
                    return
                
                if (intersection_sizes is None):
                    # Release all.
                    for to_release in held_back:
                        yield to_release
                    held_back = None
                    self._offset = 0
                    offset = 0
                
                else:
                    del chunks[0]
                    self._offset = 0
                    # Chunk too small?
                    held_back.append(chunk)
                    intersection_sizes = _merge_intersection_sizes(
                        _continue_intersection_sizes(chunk, boundary, intersection_sizes),
                        _get_end_intersection_sizes(chunk, 0, boundary),
                    )
                    released, held_back = _get_released_from_held_back(held_back, len(boundary))
                    if (released is not None):
                        for to_release in released:
                            yield to_release
                    
                    released = None
                    continue
            
            index = chunk.find(boundary, offset)
            
            # Found boundary?
            if index != -1:
                original_offset = offset
                offset = index + len(boundary)
                if offset == len(chunk):
                    del chunks[0]
                    offset = 0
                self._offset = offset
                
                if original_offset != index:
                    yield memoryview(chunk)[original_offset : index]
                return
            
            del chunks[0]
            self._offset = 0
            if offset:
                chunk = memoryview(chunk)[offset:]
            intersection_sizes = _get_end_intersection_sizes(chunk, offset, boundary)
            if (intersection_sizes is not None):
                offset = len(chunk) - intersection_sizes[0]
                held_back = [memoryview(chunk)[offset:]]
                
                # Do not yield if `offset == 0` 
                if not offset:
                    continue
                
                chunk = memoryview(chunk)[:offset]
            
            yield chunk
            
            # Repeat loop
            continue
    
    
    async def _read_until(self, boundary, payload_stream):
        """
        Payload reader task, what reads until `boundary` is hit.
        
        This method is a coroutine.
        
        Parameters
        ----------
        boundary : `bytes`
            The boundary to read until. Consumed but not returned.
        
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        
        Raises
        ------
        EofError
            Connection lost before boundary hit.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        async for chunk in self._read_until_by_chunk(boundary):
            payload_stream.add_received_chunk(chunk)
    
    
    async def _read_until_as_one(self, boundary):
        """
        Reads until `boundary` is hit at once and returns it. Can be used by other payload readers.
        
        This method is a coroutine.
        
        Parameters
        ----------
        boundary : `bytes`
            The boundary to read until. Consumed but not returned.
        
        Raises
        ------
        EofError
            Connection lost before boundary hit.
        """
        chunks = []
        async for chunk in self._read_until_by_chunk(boundary):
            chunks.append(chunk)
        
        return b''.join(chunks)
    
    
    async def _read_until_eof(self, payload_stream):
        """
        Payload reader task, which reads the protocol until EOF is hit.
        
        This method is a coroutine.
        
        Parameters
        ----------
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        """
        chunks = self._chunks
        offset = self._offset
        self._offset = 0
        while chunks:
            chunk = chunks.popleft()
            if offset:
                chunk = memoryview(chunk)[offset :]
                offset = 0
            
            payload_stream.add_received_chunk(chunk)
        
        while not self._at_eof:
            try:
                chunk = await self._wait_for_data()
            except EOFError:
                break
            
            except GeneratorExit:
                payload_stream.set_done_exception(ConnectionError('Payload reader destroyed.'))
                raise
            
            del chunks[0]
            payload_stream.add_received_chunk(chunk)
        
        payload_stream.set_done_success()
    
    
    async def _read_once(self, payload_stream):
        """
        Reader task for reading exactly one chunk out.
        
        This method is a coroutine.
        
        Parameters
        ----------
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        """
        chunks = self._chunks
        offset = self._offset
        if chunks:
            self._offset = 0
            chunk = chunks.popleft()
            if offset:
                chunk = memoryview(chunk)[offset :]
            
            payload_stream.add_received_chunk(chunk)
            payload_stream.set_done_success()
            return
        
        if self._at_eof:
            return
        
        try:
            chunk = await self._wait_for_data()
        except EOFError:
            pass
        
        else:
            del chunks[0]
            payload_stream.add_received_chunk(chunk)


class ReadWriteProtocolBase(ReadProtocolBase):
    """
    Read-write asynchronous protocol implementation.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether the protocol received end of file.
    
    _chunks : `Deque` of `bytes`
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
    
    _payload_stream : `None | PayloadStream`
        Payload stream of the protocol.
    
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
    _chunks : `Deque` of `bytes`
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
    _payload_stream : `None` of ``Future``
        Payload waiter of the protocol, what's result is set, when the ``.payload_reader`` generator returns.
        
        If cancelled or marked by done or any other methods, the payload reader will not be cancelled.
    _transport : `None`, `object`
        Asynchronous transport implementation. Is set meanwhile the protocol is alive.
    """
    __slots__ = ()
    
    @copy_docs(AbstractProtocolBase.datagram_received)
    def datagram_received(self, data, address):
        self.data_received(data)
