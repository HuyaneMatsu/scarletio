__all__ = ('Future',)

import sys
from datetime import datetime as DateTime
from types import MethodType
from warnings import warn

from ...utils import ignore_frame, include, to_coroutine

from ..exceptions import CancelledError, InvalidStateError

from .future_repr import render_callbacks_into, render_result_into, render_state_into
from .future_states import (
    FUTURE_STATE_CANCELLED, FUTURE_STATE_CANCELLING_SELF, FUTURE_STATE_MASK_DONE, FUTURE_STATE_MASK_SILENCED,
    FUTURE_STATE_RESULT_RAISE, FUTURE_STATE_RESULT_RAISE_RETRIEVED, FUTURE_STATE_RESULT_RETURN, FUTURE_STATE_SILENCED
)


FutureWrapperSync = include('FutureWrapperSync')
FutureWrapperAsync = include('FutureWrapperAsync')
write_exception_async = include('write_exception_async')
write_exception_maybe_async = include('write_exception_maybe_async')

ignore_frame(__spec__.origin, 'get_result', 'raise self._result')
ignore_frame(__spec__.origin, 'get_result', 'raise CancelledError')
ignore_frame(__spec__.origin, '__iter__', 'yield self',)
ignore_frame(__spec__.origin, '__iter__', 'return self.get_result()',)


SILENCE_DEPRECATED =  DateTime.utcnow() > DateTime(2023, 11, 12)


def _set_timeout_if_pending(future):
    """
    Sets timeout exception into the future if still pending.
    
    Parameters
    ----------
    future : ``Future``
        The future to set timeout to.
    """
    future.cancel_with(TimeoutError)


def _cancel_handle_callback(handle, future):
    """
    Callback added to the future to cancel a handle.
    
    Parameters
    ----------
    handle : ``Handle``
        The handle to cancel.
    future : ``Future``
        The completed future.
    """
    handle.cancel()


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
    
    _loop : ``EventThread``
        The loop to what the created future is bound.
    
    _result : `None`, `object`
        The result of the future. Defaults to `None`.
    
    _state : `int`
        The state of the future stored as a bitwise flags.
    """
    __slots__ = ('_blocking', '_callbacks', '_loop', '_result', '_state')
    
    def __new__(cls, loop):
        """
        Creates a new ``Future`` object bound to the given `loop`.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        """
        self = object.__new__(cls)
        self._blocking = False
        self._callbacks = []
        self._loop = loop
        self._result = None
        self._state = 0
        return self
    
    
    def __repr__(self):
        """Returns the future's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        state = self._state
        repr_parts, field_added = render_state_into(repr_parts, False, state)
        repr_parts, field_added = render_result_into(repr_parts, field_added, state, self._result)
        repr_parts, field_added = render_callbacks_into(repr_parts, field_added, self._callbacks)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def cancel(self):
        """
        Cancels the future if it is pending.
        
        Returns
        -------
        result : `int` (`0`, `1`)
            If the future is already done, returns `0`, if it got cancelled, returns `1`.
        """
        state = self._state
        
        if state & FUTURE_STATE_MASK_DONE:
            state |= FUTURE_STATE_SILENCED
            result = 0
        else:
            state |= FUTURE_STATE_CANCELLED
            result = 1
            self._loop._schedule_callbacks(self)
        
        self._state = state
        return result
    
    
    def cancel_with(self, exception):
        """
        Cancels the future with a custom exception.
        
        Returns
        -------
        result : `int` (`0`, `1`)
            If the future is already done, returns `0`, if it got cancelled, returns `1`.
        """
        state = self._state
        
        if state & FUTURE_STATE_MASK_DONE:
            state |= FUTURE_STATE_SILENCED
            result = 0
        
        else:
            if isinstance(exception, type):
                exception = exception()
            
            if isinstance(exception, StopIteration):
                raise TypeError(
                    f'{exception!r} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
                )
            
            state |= FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE
            self._result = exception
            self._loop._schedule_callbacks(self)
            result = 1
        
        self._state = state
        return result
        
    
    def silence(self):
        """
        Silences cleanup warnings of the future.
        
        When a task is cancelled these warnings are also silenced.
        """
        self._state |= FUTURE_STATE_SILENCED
    
    
    def is_silenced(self):
        """
        Returns whether clean up warning are silenced of the future.
        
        Also returns `True` if it is in a state without possible cleanup warning.
        
        Returns
        -------
        is_silenced : `bool`
        """
        return True if self._state & FUTURE_STATE_MASK_SILENCED else False
    
    
    def is_cancelling(self):
        """
        Returns whether the future is currently being cancelled.
        
        Returns
        -------
        is_cancelling : `bool`
        """
        state = self._state
        # Cancelling flag might not cleared when the future is already done.
        if state & FUTURE_STATE_MASK_DONE:
            return False
        
        return True if state & FUTURE_STATE_CANCELLING_SELF else False
    
    
    def is_cancelled(self):
        """
        Returns whether the future is cancelled.
        
        Returns
        -------
        is_cancelled : `bool`
        """
        return True if self._state & FUTURE_STATE_CANCELLED else False
    
    
    def is_done(self):
        """
        Returns whether the future is done.
        
        Returns
        -------
        is_done : `bool`
        """
        return True if self._state & FUTURE_STATE_MASK_DONE else False
    
        
    def is_pending(self):
        """
        Returns whether the future is pending.
        
        Returns
        -------
        pending : `bool`
        """
        return False if self._state & FUTURE_STATE_MASK_DONE else True
    
    
    def get_result(self):
        """
        Returns the result of the future.
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future has exception set with `.set_exception`, `.set_exception_if_pending` successfully, then raises
        the given exception.
        
        If the future has result set with `.set_result`, `.set_result_if_pending` successfully, then returns the
        given object.
        
        If the future is not done yet, or is destroyed, raises ``InvalidStateError``.
        
        Returns
        -------
        result : `object`
        
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
        state = self._state
        
        if state & FUTURE_STATE_RESULT_RETURN:
            return self._result
        
        if state & FUTURE_STATE_RESULT_RAISE:
            self._state = state | FUTURE_STATE_RESULT_RAISE_RETRIEVED
            raise self._result
        
        if state & FUTURE_STATE_CANCELLED:
            raise CancelledError
        
        # still pending or destroyed
        raise InvalidStateError(self, 'get_result')
    
    
    def get_exception(self):
        """
        Returns the future's exception.
        
        If the future is done, returns it's exception. (Cab be `None`)
        
        If the future is cancelled, returns ``CancelledError``.
        
        If the future is not done yet, or is destroyed, raises ``InvalidStateError``.
        
        Returns
        -------
        exception : `None`, `BaseException`
        
        Raises
        ------
        InvalidStateError
            The futures is not done yet.
        """
        state = self._state
        
        if state & FUTURE_STATE_RESULT_RETURN:
            return None
        
        if state & FUTURE_STATE_RESULT_RAISE:
            self._state = state | FUTURE_STATE_RESULT_RAISE_RETRIEVED
            return self._result
        
        if state & FUTURE_STATE_CANCELLED:
            return CancelledError()
        
        # still pending
        raise InvalidStateError(self, 'get_exception')
    
    
    def get_cancellation_exception(self):
        """
        Returns the exception with what the future was cancelled with. This is usually ``CancelledError``.
        
        Returns `None` if it was not yet cancelled.
        
        Returns
        -------
        exception : `None`, `BaseException`
        """
        if not (self._state & FUTURE_STATE_CANCELLED):
            return None
        
        result = self._result
        if (result is not None):
            return result
        
        return CancelledError()
    
    
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
        if self._state & FUTURE_STATE_MASK_DONE:
            self._loop.call_soon(func, self)
        else:
            self._callbacks.append(func)
    
    
    def remove_done_callback(self, func):
        """
        Removes the given `func` from the future's ``._callbacks``.
        
        Parameters
        ----------
        func : `object`
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
        result : `object`
            The object to set as result.
        
        Raises
        ------
        InvalidStateError
            If the future is already done.
        """
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            raise InvalidStateError(self, 'set_result')
            
        self._result = result
        self._state = state | FUTURE_STATE_RESULT_RETURN
        self._loop._schedule_callbacks(self)
    
    
    def set_result_if_pending(self, result):
        """
        Marks the future as done and set's it's result. Not like ``.set_result``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        result : `object`
            The object to set as result.
        
        Returns
        ------
        set_result : `int` (`0`, `1`)
            If the future is already done, returns `0`, else `1`.
        """
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            return 0
        
        self._result = result
        self._state = state | FUTURE_STATE_RESULT_RETURN
        self._loop._schedule_callbacks(self)
        return 1
    
    
    def set_exception(self, exception):
        """
        Marks the future as done and set's it's exception.
        
        Parameters
        ----------
        exception : `BaseException`, `type<BaseException>`
            The exception to set as the future's exception.
        
        Raises
        ------
        InvalidStateError
            If the future is already done.
        TypeError
            If `StopIteration` is given as `exception`.
        """
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            raise InvalidStateError(self, 'set_exception')
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception!r} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._result = exception
        self._state = state | FUTURE_STATE_RESULT_RAISE
        self._loop._schedule_callbacks(self)
    
    
    def set_exception_if_pending(self, exception):
        """
        Marks the future as done and set's it's exception. Not like ``.set_exception``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        exception : `BaseException`, `type<BaseException>`
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
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            return 0
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception!r} cannot be raised to a(n) {self.__class__.__name__}; {self!r}.'
            )
        
        self._result = exception
        self._state = state | FUTURE_STATE_RESULT_RAISE
        self._loop._schedule_callbacks(self)
        return 1
    
    
    def __iter__(self):
        """
        Awaits the future till it is done.
        
        This method is a generator. Should be used with `await` expression.
        """
        if not (self._state & FUTURE_STATE_MASK_DONE):
            self._blocking = True
            yield self
        
        return self.get_result()
    
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
        if not (self._state & FUTURE_STATE_MASK_DONE):
            self._blocking = True
            yield self
    
    
    def __del__(self):
        """
        If the future is pending, but it's result was not set, meanwhile anything awaits at it, notifies it.
        
        Also notifies if the future's result was set with ``.set_exception``, or with
        ``.set_exception_if_pending``, and it was not retrieved.
        """
        if not self._loop.running:
            return
        
        state = self._state
        # Do not notify if we have any silenced state
        if state & FUTURE_STATE_MASK_SILENCED:
            return
        
        # If we are not done, btu have callbacks, we want to notify
        if not (state & FUTURE_STATE_MASK_DONE):
            if self._callbacks:
                sys.stderr.write(
                    f'{self.__class__.__name__} is not finished, but still pending: {self!r}\n',
                )
                sys.stderr.flush()
            
            return
        
        # Notify un-retrieved exceptions
        if state & FUTURE_STATE_RESULT_RAISE:
            write_exception_maybe_async(
                self._result,
                f'{self.__class__.__name__} exception was never retrieved: {self!r}\n',
            )
            return
    
    
    def sync_wrap(self):
        """
        Wraps the future, so it's result can be retrieved from a sync thread.
        
        Returns
        -------
        future_wrapper : ``FutureWrapperSync``
            A future awaitable from sync threads.
        """
        return FutureWrapperSync(self)
    
    
    def async_wrap(self, loop):
        """
        Wraps the future, so it's result can be retrieved from an other async thread.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop, from where the future would be awaited.
        
        Returns
        -------
        future_wrapper : ``FutureWrapperAsync``
            An awaitable future from the given event loop.
        """
        return FutureWrapperAsync(self, loop)
    
    
    def apply_timeout(self, timeout):
        """
        Applies timeout to the future. After the timeout duration passed on seconds propagates a `TimeoutError` if the
        future is still pending.
        
        timeout : `float`
            The time after the given `future`'s exception is set as `TimeoutError`.
        
        Returns
        -------
        timeout_applied : `int`
            Returns `1` if timeout was applied. `0` if the future is already finished.
        """
        if timeout <= 0.0:
            return self.cancel_with(TimeoutError)
        
        else:
            if self.is_done():
                return 0
            
            handle = self._loop.call_after(timeout, _set_timeout_if_pending, self)
            if (handle is not None):
                self.add_done_callback(MethodType(_cancel_handle_callback, handle))
        
        return 1
    
    
    def iter_callbacks(self):
        """
        Iterates over the future's callbacks.
        
        This method is an iterable generator.
        
        Yields
        ------
        callback : `object`
        """
        callbacks = self._callbacks
        if (callbacks is not None):
            yield from callbacks
    
    
    # Deprecations
    
    
    def cancelled(self):
        warn(
            (
                f'`{self.__class__.__name__}.cancelled` is deprecated and will be removed in 2023 November. '
                f'Please use `.is_cancelled()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_cancelled()
    
    
    def pending(self):
        warn(
            (
                f'`{self.__class__.__name__}.pending` is deprecated and will be removed in 2023 November. '
                f'Please use `.is_pending()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_pending()
    
    
    def done(self):
        warn(
            (
                f'`{self.__class__.__name__}.done` is deprecated and will be removed in 2023 November. '
                f'Please use `.is_done()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_done()
    
    
    @property
    def result(self):
        warn(
            (
                f'`{self.__class__.__name__}.result` is deprecated and will be removed in 2023 November. '
                f'Use `.get_result()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.get_result
    
    
    @property
    def exception(self):
        warn(
            (
                f'`{self.__class__.__name__}.exception` is deprecated and will be removed in 2023 November. '
                f'Use `.get_exception()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.get_exception
    
    
    if __debug__:
        def __silence__(self):
            """
            Silences the future's `__del__`, so it will not notify if it would.
            
            Deprecated and will be removed in 2024 February.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            if SILENCE_DEPRECATED:
                warn(
                    (
                        f'`{self.__class__.__name__}.__silence__` is deprecated and will be removed in 2024 february.'
                        f'Please use `.silence()` instead.'
                    ),
                    FutureWarning,
                    stacklevel = 2,
                )
            
            self.silence()
    
    
    @property
    def _exception(self):
        """
        Deprecated and will be removed in 2024 february.
        """
        warn(
            f'`{self.__class__.__name__}._exception` is deprecated and will be removed in 2024 february.',
            FutureWarning,
            stacklevel = 2,
        )
        
        if self._state & FUTURE_STATE_RESULT_RAISE:
            return self._result
