__all__ = ('FutureAsyncWrapper', )

import reprlib
from types import MethodType

from ...utils import copy_docs, export, ignore_frame, set_docs
from ...utils.trace import format_callback

from ..exceptions import InvalidStateError

from .future import (
    FUTURE_STATE_CANCELLED, FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED, Future,
    get_future_state_name
)


ignore_frame(__spec__.origin, 'result', 'raise exception',)
ignore_frame(__spec__.origin, '__iter__', 'yield self',)

@export
class FutureAsyncWrapper(Future):
    """
    Async wrapper for ``Future``-s enabling them to be awaited from an another event loop.
    
    Attributes
    ----------
    _blocking : `bool`
        Whether the future is already being awaited, so it blocks the respective coroutine.
    _callbacks : `list` of `callable`
        The callbacks of the future, which are queued up on the respective event loop to be called, when the future is
        finished. These callback should accept `1` parameter, the future itself.
        
        Note, if the future is already done, then the newly added callbacks are queued up instantly on the respective
        event loop to be called.
    
    _exception : `None`, `BaseException`
        The exception set to the future as it's result. Defaults to `None`.
    _future : `None`, ``Future``
        The waited future. If the future's state == modified by the sync wrapper, then ``._future`` is set as `None`,
        to not retrieve the result again.
    _loop : ``EventThread``
        The loop to what the async future wrapper is bound to.
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
        
        Note, that states are checked by memory address and not by equality. Also ``FUTURE_STATE_RETRIEVED`` is used only if
        `__debug__` is set as `True`.
    """
    __slots__ = ('_blocking', '_callbacks', '_exception', '_future', '_loop', '_result', '_state',)

    def __new__(cls, future, loop):
        """
        Creates a new ``FutureAsyncWrapper`` object bound to the given `loop` and `future`.
        
        If the given `future` is an ``FutureAsyncWrapper``, then will wrap it's future instead.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop from where the created wrapper futures can be awaited.
        future : ``Future``, ``FutureAsyncWrapper``
            The future to wrap.
        
        Returns
        -------
        self : ``Future``, ``FutureAsyncWrapper``
            If the given `future` is bound to the given loop, returns the `future` itself instead of async wrapping it.
        """
        if future._loop is loop:
            return future
        
        if isinstance(future, cls):
            future = future._future
            if future._loop is loop:
                return future
        
        self = object.__new__(cls)
        self._future = future
        self._loop = loop
        self._state = FUTURE_STATE_PENDING
        self._result = None
        self._exception = None
        
        self._callbacks = []
        self._blocking = False
        
        loop = future._loop
        loop.call_soon(future.add_done_callback, self._done_callback)
        loop.wake_up()
        
        return self
    
    
    def __call__(self, future):
        """
        By calling a ``FutureAsyncWrapper`` you can make it bound to an other future.
        
        Parameters
        ----------
        future : ``Future``
            The future on what you would want to wait from the other event loop.
        
        Returns
        -------
        self : ``FutureAsyncWrapper``
        """
        old_future = self._future
        if old_future is not None:
            loop = old_future._loop
            loop.call_soon(self._remove_callback, old_future)
            loop.wake_up()
        
        self._future = future
        self._state = FUTURE_STATE_PENDING
        self._result = None
        self._exception = None
        self._blocking = False
        
        loop = future._loop
        loop.call_soon(future.add_done_callback, self._done_callback)
        loop.wake_up()
    
    
    def __repr__(self):
        """Returns the future async wrapper's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ']
        
        state = self._state
        repr_parts.append(get_future_state_name(state))
        
        if state >= FUTURE_STATE_FINISHED:
            exception = self._exception
            if exception is None:
                repr_parts.append(', result=')
                repr_parts.append(reprlib.repr(self.result))
            else:
                repr_parts.append(', exception=')
                repr_parts.append(repr(exception))
        
        callbacks = self._callbacks
        limit = len(callbacks)
        if limit:
            repr_parts.append(', callbacks=[')
            index = 0
            while True:
                callback = callbacks[index]
                repr_parts.append(format_callback(callback))
                index += 1
                if index == limit:
                    break
                
                repr_parts.append(', ')
                continue
            
            repr_parts.append(']')
        
        future = self._future
        if future is not None:
            # we do not want to repr it, keep it thread safe
            repr_parts.append(', future=')
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
                self._loop._schedule_callbacks(self)
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
                self._loop._schedule_callbacks(self)
                return 1
            
            loop = future._loop
            loop.call_soon(future.cancel)
            loop.wake_up()
            return 1
    
    
    if __debug__:
        def _done_callback(self, future):
            if self._future is not future:
                return
            
            state = future._state
            if state == FUTURE_STATE_FINISHED:
                future._state = FUTURE_STATE_RETRIEVED
            elif state == FUTURE_STATE_RETRIEVED:
                state = FUTURE_STATE_FINISHED
            
            loop = self._loop
            loop.call_soon(self.__class__._done_callback_re, self, state, future._result, future._exception)
            loop.wake_up()
    
    else:
        def _done_callback(self, future):
            if (self._future is not future):
                return
            
            loop = self._loop
            loop.call_soon(self.__class__._done_callback_re, self, future._state, future._result, future._exception)
            loop.wake_up()
    
    
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
    
    def _done_callback_re(self, state, result, exception):
        """
        Function queued up on the wrapper future's loop, by ``._done_callback``, marking this future as done.
        
        Parameters
        ----------
        state : `str`
            The future's new state.
        result : `Any`
            The future's new result.
        exception : `Any`
            The future's new exception.
        """
        self._state = state
        self._result = result
        self._exception = exception
        
        self._loop._schedule_callbacks(self)
    
    
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
        
        loop = self._loop
        loop.call_soon(self.__class__._set_future_any_re, self, future)
        loop.wake_up()
    
    
    def _set_future_any_re(self, future):
        """
        If self is still waiting on the given future, marks self as retrieved and removes `._future`, so further results
        wont be retrieved.
        
        Parameters
        ----------
        future : ``Future``.
        """
        if self._future is future:
            self._state = FUTURE_STATE_RETRIEVED
            self._future = None
    
    
    @copy_docs(Future.set_result)
    def set_result(self, result):
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(self, 'set_result')
        
        future = self._future
        
        if future is None:
            self._result = result
            self._state = FUTURE_STATE_FINISHED
            self._loop._schedule_callbacks(self)
            return
        
        loop = future._loop
        loop.call_soon(self._set_future_result, future, result)
        loop.wake_up()
    
    
    @copy_docs(Future.set_result_if_pending)
    def set_result_if_pending(self, result):
        if self._state != FUTURE_STATE_PENDING:
            return 1
        
        future = self._future
        
        if future is None:
            self._result = result
            self._state = FUTURE_STATE_FINISHED
            self._loop._schedule_callbacks(self)
            return 2
        
        loop = future._loop
        loop.call_soon(self._set_future_result, future, result)
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
            The future to set the result to.
        exception : `Any`
            The exception to set as the future's.
        """
        try:
            future.set_exception(exception)
        except (RuntimeError, InvalidStateError): #the future does not supports this operation
            pass
        
        loop = self._loop
        loop.call_soon(self._set_future_any_re, future)
        loop.wake_up()
    
    
    @copy_docs(Future.set_exception)
    def set_exception(self, exception):
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
            self._loop._schedule_callbacks(self)
            return
        
        loop = future._loop
        loop.call_soon(self._set_future_exception, future, exception)
        loop.wake_up()
    
    
    @copy_docs(Future.set_exception_if_pending)
    def set_exception_if_pending(self, exception):
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
            self._loop._schedule_callbacks(self)
            return 2
        
        loop = future._loop
        loop.call_soon(self._set_future_exception, future, exception)
        loop.wake_up()
        return 1
    
    
    @copy_docs(Future.clear)
    def clear(self):
        future = self._future
        if future is not None:
            loop = future._loop
            loop.call_soon(self._remove_callback, future)
            loop.wake_up()
            self._future = None

        self._state = FUTURE_STATE_PENDING
        self._exception = None
        self._result = None
        self.cancel_handles()
        self._blocking = False
