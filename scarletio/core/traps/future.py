__all__ = ('Future',)

import reprlib, sys, warnings

from ...utils import export, ignore_frame, include, set_docs, to_coroutine
from ...utils.trace import format_callback

from ..exceptions import CancelledError, InvalidStateError

from .handle_cancellers import _HandleCancellerBase


FutureSyncWrapper = include('FutureSyncWrapper')
FutureAsyncWrapper = include('FutureAsyncWrapper')

ignore_frame(__spec__.origin, 'result', 'raise exception',)
ignore_frame(__spec__.origin, '__iter__', 'yield self',)

FUTURE_STATE_PENDING = 0
FUTURE_STATE_CANCELLED = 1
FUTURE_STATE_FINISHED = 2
FUTURE_STATE_RETRIEVED = 3

FUTURE_STATE_TO_NAME = {
    FUTURE_STATE_PENDING: 'pending',
    FUTURE_STATE_CANCELLED: 'cancelled',
    FUTURE_STATE_FINISHED: 'finished',
    FUTURE_STATE_RETRIEVED: 'retrieved'
}

@export
def get_future_state_name(state):
    """
    Returns the given future's state's name.
    
    Parameters
    ----------
    state : `int`
        The future's name.
    
    Returns
    -------
    state_name : `str`
    """
    try:
        state_name = FUTURE_STATE_TO_NAME[state]
    except KeyError:
        state_name = f'unknown[{state}]'
    
    return state_name


class Future:
    """
    A Future represents an eventual result of an asynchronous operation.
    
    Future is an awaitable object. Coroutines can await on ``Future`` objects until they either have a result or an
    exception set, or until they are cancelled.
    
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
    _loop : ``EventThread``
        The loop to what the created future is bound.
    _result : `None`, `Any`
        The result of the future. Defaults to `None`.
    _state : `int`
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
        
        Note, that states are checked by memory address and not by equality. Also `RETRIEVED` is used only if
        `__debug__` is set as `True`.
    """
    __slots__ = ('_blocking', '_callbacks', '_exception', '_loop', '_result', '_state')
    
    # If parameters are not passed will not call `__del__`
    def __new__(cls, loop):
        """
        Creates a new ``Future`` object bound to the given `loop`.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._state = FUTURE_STATE_PENDING

        self._result = None
        self._exception = None
        
        self._callbacks = []
        self._blocking = False

        return self

    def __repr__(self):
        """Returns the future's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ']
        
        state = self._state
        repr_parts.append(get_future_state_name(state))
        
        if state > FUTURE_STATE_FINISHED:
            exception = self._exception
            if exception is None:
                repr_parts.append(', result=')
                repr_parts.append(reprlib.repr(self._result))
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
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    if __debug__:
        def cancel(self):
            state = self._state
            
            if state != FUTURE_STATE_PENDING:
                # If the future is cancelled, we should not show up not retrieved message at `.__del__`
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                
                return 0
            
            self._state = FUTURE_STATE_CANCELLED
            self._loop._schedule_callbacks(self)
            return 1
    else:
        def cancel(self):
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            self._state = FUTURE_STATE_CANCELLED
            self._loop._schedule_callbacks(self)
            return 1
    
    set_docs(cancel,
        """
        Cancels the future if it is pending.
        
        Returns
        -------
        cancelled : `int` (`0`, `1`)
            If the future is already done, returns `0`, if it got cancelled, returns `1`-
        
        Notes
        -----
        If `__debug__` is set as `True`, then `.cancel()` also marks the future as retrieved, causing it to not render
        non-retrieved exceptions.
        """
    )
    
    def is_cancelled(self):
        """
        Returns whether the future is cancelled.
        
        Returns
        -------
        is_cancelled : `bool`
        """
        return (self._state == FUTURE_STATE_CANCELLED)
    
    
    def cancelled(self):
        warnings.warn(f'`{self.__class__.__name__}.cancelled` is deprecated.', FutureWarning)
        return self.is_cancelled()
    
    
    def is_done(self):
        """
        Returns whether the future is done.
        
        Returns
        -------
        is_done : `bool`
        """
        return (self._state != FUTURE_STATE_PENDING)
    
    
    def done(self):
        warnings.warn(f'`{self.__class__.__name__}.done` is deprecated.', FutureWarning)
        return self.is_done()
    
        
    def is_pending(self):
        """
        Returns whether the future is pending.
        
        Returns
        -------
        pending : `bool`
        """
        return (self._state == FUTURE_STATE_PENDING)
    
    
    def pending(self):
        warnings.warn(f'`{self.__class__.__name__}.pending` is deprecated.', FutureWarning)
        return self.is_pending()
    
    
    if __debug__:
        def result(self):
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
        def result(self):
            state = self._state
            
            if state == FUTURE_STATE_FINISHED:
                exception = self._exception
                if exception is None:
                    return self._result
                raise exception
            
            if state == FUTURE_STATE_CANCELLED:
                raise CancelledError
            
            # still pending
            raise InvalidStateError(self, 'result')
    
    
    set_docs(result,
        """
        Returns the result of the future.
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future has exception set with `.set_exception`, `.set_exception_if_pending` successfully, then raises
        the given exception.
        
        If the future has result set with `.set_result`, `.set_result_if_pending` successfully, then returns the
        given object.
        
        If the future is not done yet, raises ``InvalidStateError``.
        
        Returns
        -------
        result : `Any`
        
        Raises
        ------
        CancelledError
            The future is cancelled.
        InvalidStateError
            The futures is not done yet.
        TypeError
            The future has non `BaseException` set as exception.
        BaseException
            The future's set exception.
        """
    )
    
    
    if __debug__:
        def exception(self):
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
        def exception(self):
            state = self._state

            if state == FUTURE_STATE_FINISHED:
                return self._exception
            
            if state == FUTURE_STATE_CANCELLED:
                raise CancelledError
            
            # still pending
            raise InvalidStateError(self, 'exception')
    
    set_docs(exception,
        """
        Returns the future's exception.
        
        If the future is done, returns it's exception. (Cab be `None`)
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future is not done yet, raises ``InvalidStateError``.
        
        Returns
        -------
        exception : `Any`
        
        Raises
        ------
        CancelledError
            The future is cancelled.
        InvalidStateError
            The futures is not done yet.
        """
    )
    
    def add_done_callback(self, func):
        """
        Adds the given `func` as a callback of the future.
        
        Parameters
        ----------
        `func` : `callable`
            A callback, what is queued up on the respective event loop, when the future is done. These callback should
            accept `1` parameter, the future itself.
            
        Notes
        -----
        If the future is already done, then the newly added callbacks are queued up instantly on the respective
        event loop to be called.
        """
        if self._state == FUTURE_STATE_PENDING:
            self._callbacks.append(func)
        else:
            self._loop.call_soon(func, self)
    
    
    def remove_done_callback(self, func):
        """
        Removes the given `func` from the future's ``._callbacks``.
        
        Parameters
        ----------
        func : `Any`
            The callback to remove.
        
        Returns
        -------
        count : `int`
            The total count of the removed callbacks.
        """
        callbacks = self._callbacks
        count = 0
        index = len(callbacks)
        while index:
            index -= 1
            if callbacks[index] is func:
                del callbacks[index]
                count += 1
        
        return count
    
    
    def set_result(self, result):
        """
        Marks the future as done and set's it's result.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Raises
        ------
        InvalidStateError
            If the future is already done.
        """
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(self, 'set_result')
            
        self._result = result
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
    
    
    def set_result_if_pending(self, result):
        """
        Marks the future as done and set's it's result. Not like ``.set_result``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Returns
        ------
        set_result : `int` (`0`, `1`)
            If the future is already done, returns `0`, else `1`.
        """
        if self._state != FUTURE_STATE_PENDING:
            return 0
        
        self._result = result
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        return 1
    
    
    def set_exception(self, exception):
        """
        Marks the future as done and set's it's exception.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Raises
        ------
        InvalidStateError
            If the future is already done.
        TypeError
            If `StopIteration` is given as `exception`.
        """
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(self, 'set_exception')
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._exception = exception
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
    
    
    def set_exception_if_pending(self, exception):
        """
        Marks the future as done and set's it's exception. Not like ``.set_exception``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Returns
        ------
        set_result : `int` (`0`, `1`)
            If the future is already done, returns `0`, else `1`.
        
        Raises
        ------
        TypeError
            If `StopIteration` is given as `exception`.
        """
        if self._state != FUTURE_STATE_PENDING:
            return 0
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) {self.__class__.__name__}; {self!r}.'
            )
        
        self._exception = exception
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        return 1
    
    
    def __iter__(self):
        """
        Awaits the future till it is done.
        
        This method is a generator. Should be used with `await` expression.
        """
        if self._state == FUTURE_STATE_PENDING:
            self._blocking = True
            yield self
        
        return self.result()
    
    __await__ = __iter__
    
    
    @to_coroutine
    def wait_for_completion(self):
        """
        Awaits the future till it is done, not retrieving it's result.
        
        This method is an awaitable generator.
        
        Notes
        -----
        This method do not protects the future from task cancellation, or from timeout context managers.
        """
        if self._state == FUTURE_STATE_PENDING:
            self._blocking = True
            yield self
    
    
    if __debug__:
        def __del__(self):
            """
            If the future is pending, but it's result was not set, meanwhile anything awaits at it, notifies it.
            
            Also notifies if the future's result was set with ``.set_exception``, or with
            ``.set_exception_if_pending``, and it was not retrieved.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            if not self._loop.running:
                return
            
            state = self._state
            if state == FUTURE_STATE_PENDING:
                if self._callbacks:
                    
                    # ignore being silenced
                    silence_cb = type(self).__silence_cb__
                    for callback in self._callbacks:
                        if callback is silence_cb:
                            return
                    
                    sys.stderr.write(f'{self.__class__.__name__} is not finished, but still pending!\n{self!r}\n')
                return
            
            if state == FUTURE_STATE_FINISHED:
                if (self._exception is not None):
                    self._loop.render_exception_maybe_async(
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
            state = self._state
            if state == FUTURE_STATE_PENDING:
                self._callbacks.append(type(self).__silence_cb__)
                return
            
            if state == FUTURE_STATE_FINISHED:
                self._state = FUTURE_STATE_RETRIEVED
        
        def __silence_cb__(self):
            """
            Callback added to the future, when ``.__silence__`` is called, when the future is still pending.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            if self._state == FUTURE_STATE_FINISHED:
                self._state = FUTURE_STATE_RETRIEVED
    
    
    def cancel_handles(self):
        """
        Cancels the handles (``_HandleCancellerBase``) added as callbacks to the future.
        """
        callbacks = self._callbacks
        if callbacks:
            for index in reversed(range(len(callbacks))):
                callback = callbacks[index]
                if isinstance(callback, _HandleCancellerBase):
                    del callbacks[index]
                    callback.cancel()
    
    
    def clear(self):
        """
        Clears the future, making it reusable.
        """
        self._state = FUTURE_STATE_PENDING
        self._exception = None
        self._result = None
        self.cancel_handles()
        self._blocking = False
    
    
    def sync_wrap(self):
        """
        Wraps the future, so it's result can be retrieved from a sync thread.
        
        Returns
        -------
        future_wrapper : ``FutureSyncWrapper``
            A future awaitable from sync threads.
        """
        return FutureSyncWrapper(self)
    
    
    def async_wrap(self, loop):
        """
        Wraps the future, so it's result can be retrieved from an other async thread.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop, from where the future would be awaited.
        
        Returns
        -------
        future_wrapper : ``FutureAsyncWrapper``
            An awaitable future from the given event loop.
        """
        return FutureAsyncWrapper(self, loop)
