__all__ = ('FutureSyncWrapper', )

import reprlib, sys, warnings
from threading import Event as SyncEvent, Lock as SyncLock
from types import MethodType

from ...utils import copy_docs, export, ignore_frame, set_docs

from ..exceptions import CancelledError, InvalidStateError

from .future import (
    FUTURE_STATE_CANCELLED, FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED, Future,
    get_future_state_name
)


ignore_frame(__spec__.origin, 'result', 'raise exception',)
ignore_frame(__spec__.origin, 'wait', 'return self.result()', )

@export
class FutureSyncWrapper:
    """
    Sync wrapper for ``Future``-s enabling them to be waited from a sync threads.
    
    Attributes
    ----------
    _exception : `None`, `BaseException`
        The exception set to the future as it's result. Defaults to `None`.
    _future : `None`, ``Future``
        The waited future. If the future's state == modified by the sync wrapper, then ``._future`` is set as `None`,
        to not retrieve the result again.
    _lock : `threading.Lock`
        Threading lock to disable concurrent access to the future.
    _result : `None`, `Any`
        The result of the future. Defaults to `None`.
    _state : `str`
        The state of the future.
        
        Can be set as one of the following:
        
        +---------------------------+-----------+
        | Respective name           | Value     |
        +===========================+===========+
        | FUTURE_STATE_PENDING      | `0`       |
        +---------------------------+-----------+
        | FUTURE_STATE_CANCELLED    | `1`       |
        +---------------------------+-----------+
        | FUTURE_STATE_FINISHED     | `2`       |
        +---------------------------+-----------+
        | FUTURE_STATE_RETRIEVED    | `3`       |
        +---------------------------+-----------+
        
        Note, that states are checked by memory address and not by equality. Also ``FUTURE_STATE_RETRIEVED`` is
        used only if `__debug__` is set as `True`.
    _waiter : `threading.Event`
        An event, what is set, when the waited future is done.
    """
    __slots__ = ('_exception', '_future', '_lock', '_result', '_state', '_waiter')
    
    def __new__(cls, future):
        """
        Creates a new ``FutureSyncWrapper`` wrapping the given `future`
        
        Parameters
        ----------
        future : ``Future``
            The future on what we would want to wait from a sync thread.
        """
        self = object.__new__(cls)
        self._future = future
        self._lock = SyncLock()
        self._waiter = SyncEvent()
        self._state = FUTURE_STATE_PENDING
        self._result = None
        self._exception = None
        
        loop = future._loop
        loop.call_soon(future.add_done_callback, self._done_callback)
        loop.wake_up()
        
        return self
    
    
    def __call__(self, future):
        """
        By calling a ``FutureSyncWrapper`` you can make it bound to an other future.
        
        Parameters
        ----------
        future : ``Future``
            The future on what you would want to wait from a sync thread.
        
        Returns
        -------
        self : ``FutureSyncWrapper``
        """
        with self._lock:
            old_future = self._future

            if old_future is not None:
                loop = old_future._loop
                loop.call_soon(self._remove_callback, old_future)
                loop.wake_up()

            self._future = future
            self._state = FUTURE_STATE_PENDING
            self._result = None
            self._exception = None
            self._waiter.clear()

            loop = future._loop
            loop.call_soon(future.add_done_callback, self._done_callback)
            loop.wake_up()

        return self
    
    
    def __repr__(self):
        """Returns the future sync wrapper's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ', ]
        
        state = self._state
        repr_parts.append(get_future_state_name(state))
        
        if state >= FUTURE_STATE_FINISHED:
            
            exception = self._exception
            if exception is None:
                repr_parts.append(' result=')
                repr_parts.append(reprlib.repr(self._result))
            else:
                repr_parts.append(' exception=')
                repr_parts.append(repr(exception))
        
        future = self._future
        if future is not None:
            # we do not want to repr it, keep it thread safe
            repr_parts.append(' future=')
            repr_parts.append(future.__class__.__name__)
            repr_parts.append('(...)')
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    
    if __debug__:
        @copy_docs(Future.cancel)
        def cancel(self):
            state = self._state
            if state != FUTURE_STATE_PENDING:
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                
                return 0
            
            future = self._future
            if future is None:
                self._state = FUTURE_STATE_CANCELLED
                self._waiter.set()
                return 1
            
            loop = future._loop
            loop.call_soon(future.cancel)
            loop.wake_up()
            return 1
        
    else:
        @copy_docs(Future.cancel)
        def cancel(self):
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            future = self._future
            if future is None:
                self._state = FUTURE_STATE_CANCELLED
                self._waiter.set()
                return 1
            
            loop = future._loop
            loop.call_soon(future.cancel)
            loop.wake_up()
            return 1
    
    
    @copy_docs(Future.is_cancelled)
    def is_cancelled(self):
        return (self._state == FUTURE_STATE_CANCELLED)
    
    
    def cancelled(self):
        warnings.warn(f'{self.__class__.__name__}.cancelled is deprecated.', FutureWarning)
        return self.is_cancelled()
    
    
    @copy_docs(Future.is_done)
    def is_done(self):
        return (self._state != FUTURE_STATE_PENDING)
    
    
    def done(self):
        warnings.warn(f'{self.__class__.__name__}.done is deprecated.', FutureWarning)
        return self.is_done()
    
    
    @copy_docs(Future.is_pending)
    def is_pending(self):
        return (self._state == FUTURE_STATE_PENDING)
    
    
    def pending(self):
        warnings.warn(f'{self.__class__.__name__}.pending is deprecated.', FutureWarning)
        return self.is_pending()
    
    
    if __debug__:
        @copy_docs(Future.result)
        def result(self):
            with self._lock:
                state = self._state
                
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                    exception = self._exception
                    if exception is None:
                        return self._result
                    raise exception
                
                if state == FUTURE_STATE_RETRIEVED:
                    exception = self._exception
                    if exception is None:
                        return self._result
                    raise exception
                
                if state == FUTURE_STATE_CANCELLED:
                    raise CancelledError
            
            # still pending
            raise InvalidStateError(self, 'result')
    
    else:
        @copy_docs(Future.result)
        def result(self):
            with self._lock:
                if self._state == FUTURE_STATE_FINISHED:
                    exception = self._exception
                    if exception is None:
                        return self._result
                    raise exception
                
                if self._state == FUTURE_STATE_CANCELLED:
                    raise CancelledError
            
            # still pending
            raise InvalidStateError(self, 'result')
    
    
    if __debug__:
        @copy_docs(Future.exception)
        def exception(self):
            with self._lock:
                state = self._state
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                    return self._exception

                if state == FUTURE_STATE_RETRIEVED:
                    return self._exception

                if state == FUTURE_STATE_CANCELLED:
                    raise CancelledError

            # still pending
            raise InvalidStateError(self, 'exception')

    else:
        @copy_docs(Future.exception)
        def exception(self):
            with self._lock:
                if self._state == FUTURE_STATE_FINISHED:
                    return self._exception

                if self._state == FUTURE_STATE_CANCELLED:
                    raise CancelledError

            # still pending
            raise InvalidStateError(self, 'exception')
    
    
    if __debug__:
        def _done_callback(self, future):
            with self._lock:
                if (self._future is not future):
                    return
                
                state = future._state
                if state == FUTURE_STATE_FINISHED:
                    future._state = FUTURE_STATE_RETRIEVED
                elif state == FUTURE_STATE_RETRIEVED:
                    state = FUTURE_STATE_FINISHED
                
                self._state = state
                self._result = future._result
                self._exception = future._exception
                self._future = None
                self._waiter.set()
    else:
        def _done_callback(self, future):
            with self._lock:
                if (self._future is not future):
                    return
                
                self._state = future._state
                self._result = future._result
                self._exception = future._exception
                self._future = None
                self._waiter.set()
    
    
    set_docs(_done_callback,
        """
        Callback added to the waited future to retrieve it's result.
        
        Parameters
        ----------
        future : ``Future``
            The waited future.
        
        Notes
        -----
        If a different future is given as parameter than the currently waited one, then wont do anything.
        
        If `_debug__` is set as `True`, then this callback also marks the waited future as retrieved.
        """
    )
    
    def _remove_callback(self, future):
        """
        Removes ``._done_callback`` callback from the given `future`'s callbacks.
        
        Parameters
        ----------
        future : ``Future``
            The future, from what's callbacks the own one will be removed.
        """
        callbacks = future._callbacks
        if callbacks:
            for index in range(len(callbacks)):
                callback = callbacks[index]
                if (type(callback) is MethodType) and (callback.__self__ is self):
                    del callbacks[index]
                    break
    
    
    def wait(self, timeout=None, propagate_cancellation=False):
        """
        Waits till the waited future's result or exception is set.
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future has exception set with `.set_exception`, `.set_exception_if_pending` successfully, then raises
        the given exception.
        
        If the future has result set with `.set_result`, `.set_result_if_pending` successfully, then returns the
        given object.
        
        If the future is not done yet, raises ``InvalidStateError``.
        
        Parameters
        ----------
        timeout : `None`, `float` = `None`, Optional
            Timeout in seconds till the waited future's result should be set. Giving it as `None`, means no time limit.
        propagate_cancellation : `bool` = `False`, Optional
            Whether cancellation should be propagated towards the waited task.
        
        Raises
        ------
        TimeoutError
            If `timeout` is over and the waited future is still pending.
        CancelledError
            The future is cancelled.
        InvalidStateError
            The futures is not done yet.
        TypeError
            The future has non `BaseException` set as exception.
        BaseException
            The future's set exception.
        """
        try:
            result_set = self._waiter.wait(timeout)
        except:
            if propagate_cancellation:
                self.cancel()
            
            raise
        
        if result_set:
            return self.result()
        
        if propagate_cancellation:
            self.cancel()
        
        raise TimeoutError
    
    
    def _set_future_result(self, future, result):
        """
        Sets the given `result` as the `future`'s result if applicable.
        
        This method is put on the respective event loop to be called, by ``.set_result`` or by
        ``.set_result_if_pending``, if the future's result can be set.
        
        Parameters
        ----------
        future : ``Future``
            The future to set the result to.
        result : `Any`
            The result to set as the future's.
        """
        try:
            future.set_result(result)
        except (RuntimeError, InvalidStateError): # the future does not support this operation
            pass
        
        with self._lock:
            if self._future is future:
                self._state = FUTURE_STATE_RETRIEVED
                self._future = None
    
    
    @copy_docs(Future.set_result)
    def set_result(self, result):
        with self._lock:
            if self._state != FUTURE_STATE_PENDING:
                raise InvalidStateError(self, 'set_result')
            
            future = self._future
            
            if future is None:
                self._result = result
                self._state = FUTURE_STATE_FINISHED
                self._waiter.set()
                return
        
        loop = future._loop
        loop.call_soon(self.__class__._set_future_result, self, future, result)
        loop.wake_up()
    
    
    @copy_docs(Future.set_result_if_pending)
    def set_result_if_pending(self, result):
        with self._lock:
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            future = self._future

            if future is None:
                self._result = result
                self._state = FUTURE_STATE_FINISHED
                self._waiter.set()
                return 2

        loop = future._loop
        loop.call_soon(self.__class__._set_future_result, self, future, result)
        loop.wake_up()
        return 1
    
    
    def _set_future_exception(self, future, exception):
        """
        Sets the given `exception` as the `future`'s exception if applicable.
        
        This method is put on the respective event loop to be called, by ``.set_exception`` or by
        ``.set_exception_if_pending``, if the future's result can be set.
        
        Parameters
        ----------
        future : ``Future``
            The future to set the exception to.
        exception : `Any`
            The exception to set as the future's.
        """
        try:
            future.set_exception(exception)
        except (RuntimeError, InvalidStateError): # the future does not supports this operation
            pass
        
        with self._lock:
            if self._future is future:
                self._state = FUTURE_STATE_RETRIEVED
                self._future = None
    
    
    @copy_docs(Future.set_exception)
    def set_exception(self, exception):
        with self._lock:
            if self._state != FUTURE_STATE_PENDING:
                raise InvalidStateError(self, 'set_exception')
            
            if isinstance(exception, type):
                exception = exception()
            
            if isinstance(exception, StopIteration):
                raise TypeError(
                    f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
                )
            
            future = self._future
            if future is None:
                self._exception = exception
                self._state = FUTURE_STATE_FINISHED
                self._waiter.set()
                return
        
        loop = future._loop
        loop.call_soon(self._set_future_exception, future, exception)
        loop.wake_up()
    
    
    @copy_docs(Future.set_exception_if_pending)
    def set_exception_if_pending(self, exception):
        with self._lock:
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            if isinstance(exception, type):
                exception = exception()
            
            if isinstance(exception, StopIteration):
                raise TypeError(
                    f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
                )
            
            future = self._future
            if future is None:
                self._exception = exception
                self._state = FUTURE_STATE_FINISHED
                self._waiter.set()
                return 2
        
        loop = future._loop
        loop.call_soon(self._set_future_exception, future, exception)
        loop.wake_up()
        return 1
    
    
    if __debug__:
        def __del__(self):
            """
            If the future is pending, but it's result was not set, meanwhile anything waits at it, notifies it.
            
            Also notifies if the future's result was set with ``.set_exception``, or with
            ``.set_exception_if_pending``, and it was not retrieved.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            if self._state == FUTURE_STATE_PENDING:
                if self._future is not None:
                    sys.stderr.write(f'{self.__class__.__name__} is not finished, but still pending!\n{self!r}\n')
                return
            
            if self._state == FUTURE_STATE_FINISHED:
                if (self._exception is not None):
                    self._future._loop.render_exception_maybe_async(
                        self._exception,
                        [
                            self.__class__.__name__,
                            ' exception was never retrieved\n',
                            repr(self),
                            '\n',
                        ]
                    )
                return
            
            # no more notify case
        
        def __silence__(self):
            """
            Silences the future's `__del__`, so it will not notify if it would.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            self._state = FUTURE_STATE_RETRIEVED
    
    
    @copy_docs(Future.clear)
    def clear(self):
        with self._lock:
            future = self._future
            if future is not None:
                loop = future._loop
                loop.call_soon(self._remove_callback, future)
                loop.wake_up()
                self._future = None
            
            self._waiter.clear()
            self._state = FUTURE_STATE_PENDING
            self._exception = None
            self._result = None
