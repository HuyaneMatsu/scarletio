__all__ = ('WaitContinuously', )

from ...utils import ignore_frame

from ..exceptions import CancelledError, InvalidStateError

from .future import FUTURE_STATE_CANCELLED, FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED
from .wait_till_first import WaitTillFirst


ignore_frame(__spec__.origin, 'result', 'raise exception',)

class WaitContinuously(WaitTillFirst):
    """
    A future subclass, which allows waiting for future or task results continuously, yielding `1` result, when awaited.
    
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
    _result : `tuple` (`set` of ``Future``, `set` of ``Future``)
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
    
    _callback : ``._wait_callback``
        Callback added to the waited futures.
    _last_done : `None`, ``Future``
        The last done future or task of the ``WaitContinuously``.
    """
    __slots__ = ('_last_done',)
    
    def __new__(cls, futures, loop):
        """
        Creates a new ``WaitContinuously`` from the given `futures` bound to the given `loop`.
        
        Parameters
        ----------
        futures : `None`, `iterable` of ``Future``
            The futures from which the ``WaitContinuously`` will yield the done ones. Can be given as `None`.
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        """
        if (futures is None):
            pending = set()
        else:
            pending = set(futures)
        
        done = set()
        
        self = object.__new__(cls)
        self._loop = loop
        
        callback = cls._wait_callback(self)
        self._callback = callback
        
        self._result = (done, pending)
        self._exception = None
        
        self._callbacks = []
        self._blocking = False
        
        self._last_done = None
        
        if pending:
            try:
                for future in pending:
                    future.add_done_callback(callback)
            finally:
                self._state = FUTURE_STATE_PENDING
        else:
            self._state = FUTURE_STATE_FINISHED
        
        return self
    
    # `__repr__` is same as ``Future.__repr__``
    
    class _wait_callback:
        """
        ``WaitContinuously``'s callback put on the future's waited by it.
        
        Attributes
        ----------
        _parent : ``WaitContinuously``
            The parent future.
        """
        __slots__ = ('_parent',)
        
        def __init__(self, parent):
            """
            Creates a new ``WaitContinuously`` callback object with the given parent ``WaitContinuously``.
            
            Parameters
            ----------
            parent : ``WaitContinuously``
                The parent future.
            """
            self._parent = parent
        
        def __call__(self, future):
            """
            The callback, which runs when a waited future is done.
            
            Removes the done future from the parent's `pending` futures and puts it on the `done` ones. Also marks the
            parent ``WaitContinuously`` as finished if it is pending.
            
            Parameters
            ----------
            future : ``Future``
                A done waited future.
            """
            parent = self._parent
            if parent is None:
                return
            
            done, pending = parent._result
            
            pending.remove(future)
            done.add(future)
            
            if parent._state == FUTURE_STATE_PENDING:
                parent._state = FUTURE_STATE_FINISHED
                parent._last_done = future
                parent._loop._schedule_callbacks(parent)
    
    def add(self, future):
        """
        Adds a new future to the ``WaitContinuously`` to wait for.
        
        Parameters
        ----------
        future : ``Future``
            A task or future to the ``WaitContinuously`` to wait for.
        
        Raises
        ------
        RuntimeError
            If the ``WaitContinuously`` has exception set, or if it is cancelled already. At this case the
            added `future` is cancelled instantly.
        """
        state = self._state
        if state == FUTURE_STATE_PENDING:
            if future.is_done():
                self._result[0].add(future)
                self._state = FUTURE_STATE_FINISHED
                self._loop._schedule_callbacks(self)
                self._last_done = future
                return
            
            pending = self._result[1]
            pending_count = len(pending)
            pending.add(future)
            if pending_count != pending:
                future.add_done_callback(self._callback)
            
            return
        
        if state == FUTURE_STATE_FINISHED:
            exception = self._exception
            if (exception is not None):
                future.cancel()
                raise RuntimeError(
                    f'`{self.__class__.__name__}.add` called, when `{self.__class__.__name__}` is already '
                    f'finished with an exception; exception={exception!r}.'
                ) from exception
            
            if future.is_done():
                self._result[0].add(future)
                return
            
            pending = self._result[1]
            pending_count = len(pending)
            pending.add(future)
            if pending_count != len(pending):
                future.add_done_callback(self._callback)
            
            self._state = FUTURE_STATE_PENDING
            return
        
        if __debug__:
            if state == FUTURE_STATE_RETRIEVED:
                exception = self._exception
                if (exception is not None):
                    future.cancel()
                    raise RuntimeError(
                        f'`{self.__class__.__name__}.add` called, when `{self.__class__.__name__}` is already '
                        f'finished with an exception; exception={exception!r}.'
                    ) from exception
                
                if future.is_done():
                    self._result[0].append(future)
                    self._state = FUTURE_STATE_FINISHED
                    return
                
                pending = self._result[1]
                pending_count = len(pending)
                pending.add(future)
                if pending_count != len(pending):
                    future.add_done_callback(self._callback)
                
                self._state = FUTURE_STATE_PENDING
                return
        
        future.cancel()
        
        raise RuntimeError(
            f'`{self.__class__.__name__}.add` called, when `{self.__class__.__name__}` is already '
           f'cancelled; self={self!r}.'
        )
    
    def _mark_as_finished(self):
        """
        Marks self as finished, ensures it's callbacks, and cancels all the added futures.
        """
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        
        self._callback._parent = None
        
        done, pending = self._result
        # silence them
        if __debug__:
            for future in done:
                future.cancel()
        
        callback = self._callback
        callback._parent = None
        
        while pending:
            future = pending.pop()
            future.remove_done_callback(callback)
            future.cancel()
            done.add(future)
    
    # `futures_done` same as ``WaitTillFirst.futures_done``
    # `futures_pending` same as ``WaitTillFirst.futures_pending``
    
    def cancel(self):
        """
        Cancels the ``WaitContinuously``.
        
        By calling it, also cancels all the waited futures as well.
        
        Returns
        -------
        cancelled : `int` (`0`, `1`)
            If the future is already done, returns `0`, if it got cancelled, returns `1`-
        
        Notes
        -----
        If `__debug__` is set as `True`, then `.cancel()` also marks the future and all the waited-done futures as well
        as retrieved, causing them to not render non-retrieved exceptions.
        """
        state = self._state
        if state == FUTURE_STATE_CANCELLED:
            return 0
        
        if (self._exception is not None):
            if __debug__:
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                    return 0
                
                if state == FUTURE_STATE_RETRIEVED:
                    return 0
            
            else:
                if state == FUTURE_STATE_FINISHED:
                    return 0
        
        done, pending = self._result
        # silence them
        if __debug__:
            for future in done:
                future.cancel()
        
        callback = self._callback
        callback._parent = None
        
        while pending:
            future = pending.pop()
            future.remove_done_callback(callback)
            future.cancel()
            done.add(future)
        
        if state == FUTURE_STATE_PENDING:
            self._loop._schedule_callbacks(self)
            self._state = FUTURE_STATE_CANCELLED
        else:
            if __debug__:
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
            
        return 1
    
    # `is_cancelled` is same as ``Future.is_cancelled``
    # `is_done` is same as ``Future.is_done``
    # `is_pending` is same as ``Future.is_pending``
    
    def result(self):
        """
        Returns the last done future.
        
        Returns
        -------
        last_done : `None`, ``Future``.
            The last future, what finished. Defaults to `None`.
        
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
        
        if state == FUTURE_STATE_FINISHED:
            if __debug__:
                self._state = FUTURE_STATE_RETRIEVED
            
            exception = self._exception
            if (exception is not None):
                raise exception
            
            return self._last_done
        
        if __debug__:
            if state == FUTURE_STATE_RETRIEVED:
                exception = self._exception
                if (exception is not None):
                    raise exception
                
                return self._last_done
        
        if state == FUTURE_STATE_CANCELLED:
            raise CancelledError
        
        # still pending
        raise InvalidStateError(self, 'result')
    
    def reset(self):
        """
        Resets the future if applicable enabling it to yield the next done future.
        
        Returns
        -------
        reset : `int` (`0`, `1`, `2`, `3`)
            - Returns `0` if the future is unable to reset. For example, there is an exception set to it, or it is
                cancelled.
            - If the future has nothing more to await on, returns `1`.
            - If there are futures to wait for, and there is no other done yet, returns `2`.
            - If there are futures to wait for, and there is at least one already other done, returns `3`.
        """
        state = self._state
        if state == FUTURE_STATE_FINISHED:
            if (self._exception is not None):
                return 0
            
            done, pending = self._result
            if done:
                last_done = self._last_done
                if (last_done is not None):
                    try:
                        done.remove(last_done)
                    except KeyError:
                        pass
            
            if done:
                self._last_done = done.pop()
                return 3
            
            if pending:
                self._state = FUTURE_STATE_PENDING
                return 2
            
            return 1
        
        if __debug__:
            if state == FUTURE_STATE_RETRIEVED:
                if (self._exception is not None):
                    return 0
                
                done, pending = self._result
                last_done = self._last_done
                if (last_done is not None):
                    try:
                        done.remove(last_done)
                    except KeyError:
                        pass
                
                if done:
                    self._state = FUTURE_STATE_FINISHED
                    self._last_done = done.pop()
                    return 3
                
                if pending:
                    self._state = FUTURE_STATE_PENDING
                    return 2
                
                return 1
        
        if state == FUTURE_STATE_PENDING:
            if self._result[1]:
                return 2
            
            return 1
        
        # cancelled
        return 0
    
    # `exception` is same as ``Future.exception``
    # `add_done_callback` is same as ``Future.add_done_callback``
    # `remove_done_callback` is same as ``Future.remove_done_callback``
    # `set_result` is same as ``WaitTillFirst.set_result``
    # `set_result_if_pending` is same as ``WaitTillFirst.set_result_if_pending``
    
    def set_exception(self, exception):
        """
        Marks the future as done and set's it's exception. If the exception is `TimeoutError`, then will not cancel it,
        but it will yield it's next result as `None` instead.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Raises
        ------
        InvalidStateError
            If the future is already done by being cancelled, or it has exception set.
        TypeError
            If `StopIteration` is given as `exception`.
        """
        state = self._state
        if (state == FUTURE_STATE_CANCELLED) or ((state >= FUTURE_STATE_FINISHED) and (self._exception is not None)):
            raise InvalidStateError(self, 'set_exception')
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        if isinstance(exception, TimeoutError):
            self._state = FUTURE_STATE_FINISHED
            self._last_done = None
            self._loop._schedule_callbacks(self)
        else:
            self._mark_as_finished()
            self._exception = exception
    
    def set_exception_if_pending(self, exception):
        """
        Marks the future as done and set's it's exception. If the exception is `TimeoutError`, then will not cancel it,
        but it will yield it's next result as `None` instead. Not like ``.set_exception``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Returns
        ------
        set_result : `int` (`0`, `1`, `2`)
            If the future is already done, returns `0`. If `exception` is given as `TimeoutError`, returns `2`, else
            `1`.
        
        Raises
        ------
        TypeError
            If `StopIteration` is given as `exception`.
        """
        state = self._state
        if (state == FUTURE_STATE_CANCELLED) or ((state >= FUTURE_STATE_FINISHED) and (self._exception is not None)):
            return 0
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        if isinstance(exception, TimeoutError):
            self._state = FUTURE_STATE_FINISHED
            self._last_done = None
            self._loop._schedule_callbacks(self)
            return 2
        
        self._mark_as_finished()
        self._exception = exception
        return 1
    
    # `__iter__` is same as ``Future.__iter__``
    # `__await__` is same as ``Future.__await__``
    # if __debug__:
    #    `__del__` is same as ``Future.__del__``
    #    `__silence__` is same as ``Future.__silence__``
    #    `__silence_cb__` is same as ``Future.__silence_cb__``
    # `cancel_handles` is same as ``Future.cancel_handles``
    # `clear` same as ``WaitTilLFirst.clear``
    # `sync_wrap` is same as ``Future.sync_wrap``
    # `async_wrap` is same as ``Future.async_wrap``
