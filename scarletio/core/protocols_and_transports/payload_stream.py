__all__ = ('PayloadStream', )

from collections import deque as Deque

from ...utils import RichAttributeErrorBaseType, include

from ..traps import Future


write_exception_async = include('write_exception_async')


STREAM_FLAG_WAIT_WHOLE = 1 << 0
STREAM_FLAG_WAIT_CHUNK = 1 << 1
STREAM_FLAG_DONE_SUCCESS = 1 << 2
STREAM_FLAG_DONE_EXCEPTION = 1 << 3
STREAM_FLAG_DONE_CANCELLED = 1 << 4
STREAM_FLAG_DONE_ABORTED = 1 << 5

STREAM_FLAG_WAIT_ANY = STREAM_FLAG_WAIT_WHOLE | STREAM_FLAG_WAIT_CHUNK
STREAM_FLAG_DONE_RAISE_ANY = STREAM_FLAG_DONE_EXCEPTION | STREAM_FLAG_DONE_CANCELLED | STREAM_FLAG_DONE_ABORTED
STREAM_FLAG_DONE_ANY = STREAM_FLAG_DONE_SUCCESS | STREAM_FLAG_DONE_RAISE_ANY

    
def _get_payload_stream_flags_name(flags):
    """
    Get flags name.
    
    Parameters
    ----------
    flags : `int`
        Flags to get their name of.
    
    Returns
    -------
    name : `str`
    """
    if not flags:
        return 'none'
    
    output_parts = []
    
    if flags & STREAM_FLAG_WAIT_WHOLE:
        output_parts.append('wait~whole')
    
    if flags & STREAM_FLAG_WAIT_CHUNK:
        output_parts.append('wait~chunk')
    
    if flags & STREAM_FLAG_DONE_SUCCESS:
        output_parts.append('done~success')
    
    if flags & STREAM_FLAG_DONE_EXCEPTION:
        output_parts.append('done~exception')
    
    if flags & STREAM_FLAG_DONE_CANCELLED:
        output_parts.append('done~cancelled')
    
    if flags & STREAM_FLAG_DONE_ABORTED:
        output_parts.append('done~aborted')
    
    return ', '.join(output_parts)


def _create_payload_stream_done_exception(flags):
    """
    Creates an exception used at payload reader cancellation.
    
    Parameters
    ----------
    flags : `int`
        Payload reader flags.
    
    Returns
    -------
    exception : ``ConnectionError``
    """
    if flags & STREAM_FLAG_DONE_CANCELLED:
        message = 'Payload reader cancelled.'
    else:
        message = 'Payload reader aborted.'
    
    return ConnectionError(message)


class PayloadStream(RichAttributeErrorBaseType):
    """
    Payload stream.
    
    Attributes
    ----------
    _chunks : `Deque<bytes | memoryview>`
        Cached chunks.
    
    _done_callbacks : `None | list<callable>`
        Functions to call when the stream ended.
    
    _flags : `int`
        Bitwise flags storing the state of the stream.
    
    _exception : `None | BaseException`
        Payload reader exception.
    
    _protocol : ``ReadProtocolBase``
        The parent protocol.
    
    _waiter : `None | Future`
        Payload waiter used when waiting for a new chunk or for all chunks respectively.
    """
    __slots__ = ('_chunks', '_done_callbacks', '_exception', '_flags', '_protocol', '_waiter')
    
    def __new__(cls, protocol):
        """
        Creates a new payload stream.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            The parent protocol.
        """
        self = object.__new__(cls)
        self._chunks = Deque()
        self._done_callbacks = None
        self._exception = None
        self._flags = 0
        self._protocol = protocol
        self._waiter = None
        return self
    
    
    def __repr__(self):
        """Returns the payload streams representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' total_size = ')
        repr_parts.append(repr(self.get_total_size()))
        
        repr_parts.append(', flags = ')
        repr_parts.append(_get_payload_stream_flags_name(self._flags))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def get_total_size(self):
        """
        Gets the total size of the payload stream.
        
        Returns
        -------
        size : `int`
        """
        size = 0
        for chunk in self._chunks:
            size += len(chunk)
        
        return size
    
    
    def get_buffer_size(self):
        """
        Gets the buffer size of the payload stream. If we are expecting to receive the whole payload it returns `0`.
        
        Returns
        -------
        size : `int`
        """
        if self._flags & STREAM_FLAG_WAIT_WHOLE:
            return 0
        
        return self.get_total_size()
    
    
    def set_done_success(self):
        """
        Sets the payload stream to be done with success.
        
        Returns
        -------
        success : `bool`
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_ANY:
            return False
        
        self._flags |= STREAM_FLAG_DONE_SUCCESS
        
        waiter = self._waiter
        if (waiter is not None):
            self._waiter = None
            waiter.set_result_if_pending(None)
        
        self._run_done_callbacks()
        return True
    
    
    def set_done_cancelled(self):
        """
        Sets the payload stream to be done by cancellation.
        
        Returns
        -------
        success : `bool`
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_ANY:
            return False
        
        flags |= STREAM_FLAG_DONE_CANCELLED
        self._flags = flags
        
        waiter = self._waiter
        if (waiter is not None):
            self._waiter = None
            waiter.set_exception_if_pending(_create_payload_stream_done_exception(flags))
        
        self._chunks.clear()
        self._run_done_callbacks()
        return True
    
    
    def set_done_exception(self, exception):
        """
        Sets the payload stream to be done with exception.
        
        Parameters
        ----------
        exception : `BaseException`
            Exception to set.
        
        Returns
        -------
        success : `bool`
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_ANY:
            return False
        
        self._flags |= STREAM_FLAG_DONE_EXCEPTION
        
        waiter = self._waiter
        if (waiter is not None):
            self._waiter = None
            waiter.set_exception_if_pending(exception)
        
        self._exception = exception
        self._chunks.clear()
        self._run_done_callbacks()
        return True
    
    
    def add_received_chunk(self, chunk):
        """
        Adds a received chunk to the payload stream's queue.
        
        Parameters
        ----------
        chunk : `bytes | memoryview`
            Received chunk.
        
        Returns
        -------
        success : `bool`
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_ANY:
            return False
        
        if flags & STREAM_FLAG_WAIT_CHUNK:
            waiter = self._waiter
            if (waiter is not None):
                self._waiter = None
                if waiter.set_result_if_pending(chunk):
                    return True
        
        self._chunks.append(chunk)
        return True
    
    
    def add_done_callback(self, callback):
        """
        Adds a done callback to the payload stream.
        
        Parameters
        ----------
        callback : `callable`
            Callback to run when the stream is done.
        """
        if self._flags & STREAM_FLAG_DONE_ANY:
            self._run_done_callback(callback)
        else:
            done_callbacks = self._done_callbacks
            if (done_callbacks is None):
                done_callbacks = []
                self._done_callbacks = done_callbacks
            done_callbacks.append(callback)
    
    
    def _run_done_callbacks(self):
        """
        Runs the added done callbacks of the payload stream.
        """
        done_callbacks = self._done_callbacks
        if done_callbacks is None:
            return
        
        while done_callbacks:
            self._run_done_callback(done_callbacks.pop())
        
        self._done_callbacks = None
    
    
    def _run_done_callback(self, callback):
        """
        Runs a single callback.
        
        Parameters
        ----------
        callback : `callable`
            The callback to run.
        """
        try:
            callback(self)
        except BaseException as err:
            write_exception_async(
                err,
                [
                    'Exception occurred at ',
                    repr(self),
                    '._run_done_callbacks\nAt running ',
                    repr(callback),
                    '\n',
                ],
                loop = self._protocol._loop,
            )
    
    
    def _abort(self):
        """
        Aborts the payload stream.
        
        Returns
        -------
        success : `bool`
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_ANY:
            return False
        
        flags |= STREAM_FLAG_DONE_ABORTED
        self._flags = flags
        
        waiter = self._waiter
        if (waiter is not None):
            self._waiter = None
            if waiter.is_pending():
                waiter.set_exception(_create_payload_stream_done_exception(flags))
        
        self._run_done_callbacks()
        return True
    
    
    def is_aborted(self):
        """
        Returns whether the payload stream was aborted.
        
        Returns
        -------
        aborted : `bool`
        """
        return True if self._flags & STREAM_FLAG_DONE_ABORTED else False
    
    
    def _check_raise_flags(self):
        """
        Checks the raise flags of the payload reader. Raises if applicable.
        
        Raises
        ------
        ConnectionError
            Payload reading cancelled.
        BaseException
            Payload reader exception.
        """
        flags = self._flags
        if flags & STREAM_FLAG_DONE_RAISE_ANY:
            exception = self._exception
            if (exception is None):
                exception = _create_payload_stream_done_exception(flags)
            raise exception
    
    
    def _check_wait_flags(self, expected_flag):
        """
        Checks the wait flags of the payload reader.
        
        Raises
        ------
        RuntimeError
            Payload reader would go to an invalid state.
        """
        flags = self._flags
        wait_flags = flags & STREAM_FLAG_WAIT_ANY
        if wait_flags == expected_flag:
            pass
        
        elif not wait_flags:
            self._flags = flags | expected_flag
        
        else:
            raise RuntimeError(
                f'Payload stream is in invalid state to: {_get_payload_stream_flags_name(expected_flag)!s}. '
                f'Current state: {_get_payload_stream_flags_name(flags)!s}.'
            )
    
    
    def __await__(self):
        """
        Awaits the payload reader.
        
        This method is an awaitable generator.
        
        Returns
        -------
        data : `bytes`
        
        Raises
        ------
        ConnectionError
            Payload reading cancelled.
        RuntimeError
            Payload reader would go to an invalid state.
        BaseException
            Payload reader exception.
        """
        self._check_wait_flags(STREAM_FLAG_WAIT_WHOLE)
        self._check_raise_flags()
        
        if not self._flags & STREAM_FLAG_DONE_SUCCESS:
            waiter = self._waiter
            if (waiter is None):
                self._protocol._resume_reading()
                waiter = Future(self._protocol._loop)
                self._waiter = waiter
            
            try:
                yield from waiter
            except:
                self._abort()
                raise
        
        chunks = self._chunks
        data = b''.join(chunks)
        chunks.clear()
        return data
    
    
    async def __aiter__(self):
        """
        Iterates over the received chunks of the payload reader as they come.
        
        This method is an coroutine generator.
        
        Yields
        -------
        chunk : `bytes | memoryview`
        
        Raises
        ------
        ConnectionError
            Payload reading cancelled.
        RuntimeError
            Payload reader would go to an invalid state.
        BaseException
            Payload reader exception.
        """
        chunks = self._chunks
        self._check_wait_flags(STREAM_FLAG_WAIT_CHUNK)
        
        while True:
            self._check_raise_flags()
            
            if chunks:
                chunk = chunks.popleft()
                self._protocol._resume_reading()
            
            else:
                self._check_raise_flags()
                if self._flags & STREAM_FLAG_DONE_SUCCESS:
                    return
                
                waiter = self._waiter
                if (waiter is None):
                    waiter = Future(self._protocol._loop)
                    self._waiter = waiter
                
                try:
                    chunk = await waiter
                except:
                    self._abort()
                    raise
                
                if chunk is None:
                    return
            
            try:
                yield chunk
            except:
                self._abort()
                raise
            
            continue
