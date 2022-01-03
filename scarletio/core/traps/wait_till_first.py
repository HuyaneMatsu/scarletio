__all__ = ('WaitTillFirst',)

from ...utils import set_docs

from ..exceptions import InvalidStateError

from .future import FUTURE_STATE_CANCELLED, FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED, Future


class WaitTillFirst(Future):
    """
    A future subclass, which waits till the first task or future is completed from the given ones. When finished,
    returns the `done` and the `pending` futures.
    
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
    """
    __slots__ = ('_callback', )
    
    def __new__(cls, futures, loop):
        """
        Creates a new ``WaitTillFirst`` object with the given parameters.
        
        Parameters
        ----------
        futures : `iterable` of ``Future``
            The futures from which we will wait on the first to complete.
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        """
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
        ``WaitTillFirst``'s callback put on the future's waited by it.
        
        Attributes
        ----------
        _parent : ``WaitTillFirst``
            The parent future.
        """
        __slots__ = ('_parent',)
        
        def __init__(self, parent):
            """
            Creates a new ``WaitTillFirst`` callback object with the given parent ``WaitTillFirst``.
            
            Parameters
            ----------
            parent : ``WaitTillFirst``
                The parent future.
            """
            self._parent = parent
        
        
        def __call__(self, future):
            """
            The callback, which runs when a waited future is done.
            
            Removes the done future from the parent's `pending` futures and puts it on the `done` ones. Also marks the
            parent ``WaitTillFirst`` as finished.
            
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
            
            parent._mark_as_finished()
    
    
    def _mark_as_finished(self):
        """
        Marks self as finished, ensures it's callbacks, stops other waited futures to go to it's `done` result group
        and removes it's callback from the non-yet-done futures as well.
        """
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        
        callback = self._callback
        callback._parent = None
        
        for future in self._result[1]:
            future.remove_done_callback(callback)
    
    
    @property
    def futures_done(self):
        """
        Returns the already done futures.
        
        Returns
        -------
        done : `set` of ``Future``-s.
        """
        return self._result[0]
    
    
    @property
    def futures_pending(self):
        """
        Returns the yet pending futures.
        
        Returns
        -------
        done : `set` of ``Future``-s.
        """
        return self._result[1]
    
    
    # cancels the future, but every pending one as well.
    if __debug__:
        def cancel(self):
            state = self._state
            if state != FUTURE_STATE_PENDING:
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                
                return 0
                
            self._callback._parent = None
            for future in self._result[1]:
                future.cancel()
            
            self._state = FUTURE_STATE_CANCELLED
            self._loop._schedule_callbacks(self)
            return 1
    
    else:
        def cancel(self):
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            self._callback._parent = None
            for future in self._result[1]:
                future.cancel()
            
            self._state = FUTURE_STATE_CANCELLED
            self._loop._schedule_callbacks(self)
            return 1
    
    set_docs(cancel,
        """
        Cancels the future if it is pending.
        
        By cancelling the main waiter future, the not yet done futures will be also cancelled as well.
        
        Returns
        -------
        cancelled : `int` (`0`, `1`)
            If the future is already done, returns `0`, if it got cancelled, returns `1`.
        
        Notes
        -----
        If `__debug__` is set as `True`, then `.cancel()` also marks the future as retrieved, causing it to not render
        non-retrieved exceptions.
        """
    )
    
    # `is_cancelled` is same as ``Future.is_cancelled``
    # `is_done` is same as ``Future.is_done``
    # `is_pending` is same as ``Future.is_pending``
    # `result` is same as ``Future.result``
    # `exception` is same as ``Future.exception``
    # `add_done_callback` is same as ``Future.add_done_callback``
    # `remove_done_callback` is same as ``Future.remove_done_callback``
    
    
    def set_result(self, result):
        """
        Result waiter future types do not support `.set_result` operation.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Raises
        ------
        RuntimeError
            Waiter futures do not support `.set_result` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_result` operation.'
        )
    
    
    def set_result_if_pending(self, result):
        """
        Result waiter future types do not support `.set_result_if_pending` operation.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Raises
        ------
        RuntimeError
            Waiter futures do not support `.set_result_if_pending` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_result_if_pending` operation.'
        )
    
    
    def set_exception(self, exception):
        """
        Sets an exception as a result of the waiter future.
        
        If `exception` is given as `TimeoutError`, then the waiter will not raise, instead will yield it's `done`
        and `pending` future's current status.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Raises
        ------
        InvalidStateError
            If the task is already done.
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
        
        if type(exception) is not TimeoutError:
            self._exception = exception
        
        self._mark_as_finished()
    
    def set_exception_if_pending(self, exception):
        """
        Sets an exception as a result of the waiter future. Not like ``.set_exception``, this method will not raise
        ``InvalidStateError`` if the future is already done.
        
        If `exception` is given as `TimeoutError`, then the waiter will not raise, instead will yield it's `done`
        and `pending` future's current status.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as the future's exception.
        
        Returns
        ------
        set_result : `int` (`0`, `1`)
            If the future is already done, returns `0`. If `exception` is given as `TimeoutError`, returns `2`, else
            `1`.
        
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
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._mark_as_finished()
        
        if isinstance(exception, TimeoutError):
            return 2
        
        self._exception = exception
        return 1
    
    # `__iter__` is same as ``Future.__iter__``
    # `__await__` is same as ``Future.__await__``
    # if __debug__:
    #    `__del__` is same as ``Future.__del__``
    #    `__silence__` is same as ``Future.__silence__``
    #    `__silence_cb__` is same as ``Future.__silence_cb__``
    # `cancel_handles` is same as ``Future.cancel_handles``
    
    def clear(self):
        """
        Waiter futures do not support `.clear` operation.
        
        Raises
        ------
        RuntimeError
            Waiter futures do not support `.clear` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.clear` operation.'
        )
    
    # `sync_wrap` is same as ``Future.sync_wrap``
    # `async_wrap` is same as ``Future.async_wrap``
