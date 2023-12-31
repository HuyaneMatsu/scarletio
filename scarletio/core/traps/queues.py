__all__ = ('AsyncLifoQueue', 'AsyncQueue',)

from collections import deque

from ...utils import copy_docs, copy_func, ignore_frame, to_coroutine

from ..exceptions import CancelledError

from .future import Future


ignore_frame(__spec__.origin, 'get_result_no_wait', 'raise exception',)
ignore_frame(__spec__.origin, '__aexit__', 'raise exception',)

class AsyncQueue:
    """
    An asynchronous FIFO queue.
    
    ``AsyncQueue`` is async iterable, so if you iterate over it inside of an `async for` loop do
    `.set_exception(CancelledError())` to stop it without any specific exception.
    
    Attributes
    ----------
    _exception : `None`, `BaseException`
        The exception set as the queue's result to raise, when the queue gets empty.
    
    _loop : ``EventThread``
        The loop to what the queue is bound to.
    
    _results : `deque`
        The results of the queue, which can be retrieved by ``.result``, ``.result_no_wait``, or by awaiting it.
    
    _set_result_waiters : `None`, `list` of ``Future``
        Result setter waiters for the queue to become empty.
    
    _waiter : `None`, ``Future``
        If the queue is empty and it's result is already waited, then this future is set. It's result is set, by the
        first ``.set_result``, ``.set_exception`` call.
    """
    __slots__ = ('_exception', '_loop', '_results', '_set_result_waiters', '_waiter',)
    
    def __new__(cls, loop, iterable = None, max_length = None, exception = None):
        """
        Creates a new ``AsyncQueue`` with the given parameter.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the created queue will be bound to.
        iterable : `None`, `iterable` = `None`, Optional
            A preset iterable to extend the queue with.
        max_length : `None`, `int` = `None`, Optional
            The maximal length of the queue.
        exception : `None`, `BaseException` = `None`, Optional
            Exception to raise when the queue is empty.
        
        Raises
        ------
        TypeError
            If `StopIteration` is given as `exception`.
        """
        if (exception is not None):
            if isinstance(exception, type):
                exception = exception()
            
            if isinstance(exception, StopIteration):
                raise TypeError(
                    f'{exception} cannot be raised to a(n) `{cls.__name__}`.'
                )
        
        if iterable is None:
            results = deque(maxlen = max_length)
        else:
            results = deque(iterable, maxlen = max_length)
        
        self = object.__new__(cls)
        self._loop = loop
        self._results = results
        self._waiter = None
        self._exception = exception
        self._set_result_waiters = None
        return self
    
    
    def set_result(self, element):
        """
        Puts the given `element` on the queue. If the queue is empty and it's result is already waited, feeds it to
        ``._waiter`` instead.
        
        Parameters
        ----------
        element : `object`
            The object to put on the queue.
        
        Returns
        -------
        set_result_state : `int` (`0`, `1`, `2`)
            If the result was set instantly, return `0`. If the result was not set, returns `1`.
        """
        # should we raise InvalidStateError?
        waiter = self._waiter
        if waiter is None:
            results = self._results
            max_length = results.maxlen
            if (max_length is None) or (len(results) < max_length):
                results.append(element)
                set_result = 0
            else:
                set_result = 1
        else:
            self._waiter = None
            waiter.set_result_if_pending(element)
            set_result = 0
        
        return set_result
    
    
    async def set_result_wait(self, element):
        """
        Puts the given `element` on the queue. If the queue is full, blocks till it's elements are exhausted.
        
        This method is an awaitable.
        
        Parameters
        ----------
        element : `object`
            The object to put on the queue.
        
        Returns
        -------
        set_result_state : `int` (`0`, `1`, `2`)
            If the result was set instantly, return `0`. If the result was not set, returns `1`. If you needed to wait
            for setting the result, returns `2`.
        """
        waiter = self._waiter
        if waiter is None:
            results = self._results
            max_length = results.maxlen
            if (max_length is None) or (len(results) < max_length):
                results.append(element)
                set_result = 0
            else:
                set_result_waiters = self._set_result_waiters
                if (set_result_waiters is None):
                    set_result_waiters = []
                    self._set_result_waiters = set_result_waiters
                
                waiter = Future(self._loop)
                
                set_result_waiters.append(waiter)
                
                try:
                    can_set_result = await waiter
                except:
                    try:
                        set_result_waiters.remove(waiter)
                    except ValueError:
                        pass
                    else:
                        if not set_result_waiters:
                            self._set_result_waiters = None
                    
                    raise
                
                else:
                    if can_set_result:
                        results.append(element)
                        set_result = 2
                    else:
                        set_result = 1
                
        else:
            self._waiter = None
            waiter.set_result_if_pending(element)
            set_result = 0
        
        return set_result
    
    
    def set_exception(self, exception):
        """
        Sets the given `exception` to raise, when it's queue gets empty. If the queue is empty and it's result is
        already waited, feeds it to ``._waiter`` instead.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Exception to raise when the queue is empty.
        
        Raises
        ------
        TypeError
            If `StopIteration` is given as `exception`.
        """
        # should we raise InvalidStateError?
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._exception = exception
        
        waiter = self._waiter
        if (waiter is not None):
            self._waiter = None
            waiter.set_exception_if_pending(exception)
        
        # cancel all waiters
        set_result_waiters = self._set_result_waiters
        if (set_result_waiters is not None):
            self._set_result_waiters = None
            
            while set_result_waiters:
                set_result_waiters.pop(0).set_result_if_pending(False)
            
    
    def __await__(self):
        """
        Waits till the next element of the queue is set. If the queue has elements set, yields the next of them, or if
        the queue has exception set, raises it.
        
        This method is a generator. Should be used with `await` expression.
        
        Returns
        -------
        result : `object`
            The next element on the queue.
        
        Raises
        ------
        BaseException
            Exception set to the queue, to raise when it is empty.
        """
        results = self._results
        if results:
            return results.popleft()
        
        exception = self._exception
        if exception is not None:
            raise exception
        
        waiter = self._waiter
        if waiter is None:
            waiter = Future(self._loop)
            self._waiter = waiter
        
        try:
            return (yield from waiter)
        finally:
            self._poll_from_set_result_waiters()
    
    get_result = to_coroutine(copy_func(__await__))
    
    @property
    def result(self):
        return self.get_result
    
    
    def _poll_from_set_result_waiters(self):
        """
        Polls one future from set result waiters.
        """
        set_result_waiters = self._set_result_waiters
        if (set_result_waiters is not None):
            while True:
                set_result = set_result_waiters.pop(0).set_result_if_pending(True)
                
                if (not set_result_waiters):
                    self._set_result_waiters = None
                    break
                
                if set_result == 1:
                    break
    
    
    def get_result_no_wait(self):
        """
        Returns the queue's next element if applicable.
        Waits till the next element of the queue is set. If the queue has elements set, yields the next of them, or if
        the queue has exception set, raises it.
        
        Returns
        -------
        result : `object`
            The next element on the queue.
        
        Raises
        ------
        IndexError
            The queue is empty.
        BaseException
            Exception set to the queue, to raise when it is empty.
        """
        results = self._results
        if results:
            result = results.popleft()
            self._poll_from_set_result_waiters()
            return result
        
        exception = self._exception
        if exception is None:
            raise IndexError('The queue is empty')
        
        raise exception
    
    
    @property
    def result_no_wait(self):
        return self.get_result_no_wait
    
    
    def __repr__(self):
        """Returns the async queue's representation."""
        repr_parts = [
            self.__class__.__name__,
            '([',
        ]
        
        results = self._results
        limit = len(results)
        if limit:
            index = 0
            while True:
                element = results[index]
                repr_parts.append(repr(element))
                index += 1
                if index == limit:
                    break
                
                repr_parts.append(', ')
            
        repr_parts.append(']')
        
        max_length = results.maxlen
        if (max_length is not None):
            repr_parts.append(', max_length = ')
            repr_parts.append(repr(max_length))
        
        exception = self._exception
        if (exception is not None):
            repr_parts.append(', exception = ')
            repr_parts.append(str(exception))
        
        repr_parts.append(')')
        return ''.join(repr_parts)
    
    __str__ = __repr__
    
    def __aiter__(self):
        """
        Async iterating over an ``AsyncQueue``, returns itself
        
        Returns
        -------
        self : ``AsyncQueue``
        """
        return self
    
    
    async def __anext__(self):
        """
        Waits till the next element of the queue is set. If the queue has elements set, yields the next of them, or if
        the queue has exception set, raises it.
        
        If the queue has ``CancelledError`` set as ``._exception``, then raises ``StopAsyncIteration`` to stop the queue
        instead.
        
        This method is a coroutine.
        
        Returns
        -------
        result : `object`
            The next element on the queue.
        
        Raises
        ------
        StopAsyncIteration
            If the queue was cancelled with ``CancelledError``.
        BaseException
            Exception set to the queue, to raise when it is empty.
        """
        results = self._results
        if results:
            result = results.popleft()
            self._poll_from_set_result_waiters()
            return result
        
        exception = self._exception
        if exception is not None:
            if type(exception) is CancelledError:
                raise StopAsyncIteration from CancelledError
            
            raise exception
        
        waiter = self._waiter
        if waiter is None:
            waiter = Future(self._loop)
            self._waiter = waiter
        
        try:
            return (await waiter)
        except CancelledError as err:
            raise StopAsyncIteration from err
    
    # deque operations
    
    @property
    def max_length(self):
        """
        Returns the queue's max length.
        
        Returns
        -------
        max_length: `int`
        """
        return self._results.maxlen
    
    
    def clear(self):
        """
        Clears the queue's results.
        """
        self._results.clear()
    
    
    def copy(self):
        """
        Copies the queue.
        
        Returns
        -------
        new : ``AsyncQueue``
        """
        new = object.__new__(type(self))
        
        new._loop = self._loop
        new._results = self._results.copy()
        new._waiter = None
        new._exception = self._exception
        new._set_result_waiters = None
        
        return new
    
    
    def reverse(self):
        """
        Reverses the queue's actual results.
        """
        self._results.reverse()
    
    
    def __len__(self):
        """
        Returns the queue's actual length.
        """
        return len(self._results)
    
    
    if __debug__:
        def __del__(self):
            """
            If the queue has ``_waiter`` set, silences it.
            
            Notes
            -----
            This function is only present, when `__debug__` is set as `True`.
            """
            waiter = self._waiter
            if waiter is not None:
                waiter.silence()


class AsyncLifoQueue(AsyncQueue):
    """
    An asynchronous LIFO queue.
    
    ``AsyncLifoQueue`` is async iterable, so if you iterate over it inside of an `async for` loop do
    `.set_exception(CancelledError())` to stop it without any specific exception.
    
    Attributes
    ----------
    _exception : `None`, `BaseException`
        The exception set as the queue's result to raise, when the queue gets empty.
    _loop : ``EventThread``
        The loop to what the queue is bound to.
    _results : `deque`
        The results of the queue, which can be retrieved by ``.result``, ``.result_no_wait``, or by awaiting it.
    _waiter : `None`, ``Future``
        If the queue is empty and it's result is already waited, then this future is set. It's result is set, by the
        first ``.set_result``, ``.set_exception`` call.
    """
    __slots__ = ()
    
    @copy_docs(AsyncQueue.__await__)
    def __await__(self):
        results = self._results
        if results:
            return results.pop()
        
        exception = self._exception
        if exception is not None:
            raise exception
        
        waiter = self._waiter
        if waiter is None:
            waiter = Future(self._loop)
            self._waiter = waiter
        
        return (yield from waiter)
    
    @copy_docs(AsyncQueue.result_no_wait)
    def get_result_no_wait(self):
        results = self._results
        if results:
            return results.pop()
        
        exception = self._exception
        if exception is None:
            raise IndexError('The queue is empty')
        
        raise exception
    
    
    @property
    def result_no_wait(self):
        return self.get_result_no_wait
    
    
    @copy_docs(AsyncQueue.__anext__)
    async def __anext__(self):
        results = self._results
        if results:
            return results.pop()
        
        exception = self._exception
        if exception is not None:
            if type(exception) is CancelledError:
                raise StopAsyncIteration from CancelledError
            
            raise exception
        
        waiter = self._waiter
        if waiter is None:
            waiter = Future(self._loop)
            self._waiter = waiter
        
        try:
            return (await waiter)
        except CancelledError as err:
            raise StopAsyncIteration from err
