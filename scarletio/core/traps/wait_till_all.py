__all__ = ('WaitTillAll',)

from .wait_till_first import WaitTillFirst


class WaitTillAll(WaitTillFirst):
    """
    A future subclass, which waits till all the given tasks or futures become done. When finished, returns the `done`
    and the `pending` futures.
    
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
    __slots__ = ()
    # `__new__` is same as ``WaitTillFirst.__new__``
    # `__repr__` is same as ``Future.__repr__``

    class _wait_callback:
        """
        ``WaitTillAll``'s callback put on the future's waited by it.
        
        Attributes
        ----------
        _parent : ``WaitTillAll``
            The parent future.
        """
        __slots__ = ('_parent',)
        
        def __init__(self, parent):
            """
            Creates a new ``WaitTillAll`` callback object with the given parent ``WaitTillAll``.
            
            Parameters
            ----------
            parent : ``WaitTillAll``
                The parent future.
            """
            self._parent = parent
            
        def __call__(self, future):
            """
            The callback, which runs when a waited future is done.
            
            Removes the done future from the parent's `pending` futures and puts it on the `done` ones. If there is no
            more future to wait for, marks the parent ``WaitTillAll`` as finished as well.
            
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
            
            if pending:
                return
            
            parent._mark_as_finished()
    
    # `futures_done` is same as ``WaitTillFirst.futures_done``
    # `futures_pending` is same as ``WaitTillFirst.futures_pending``
    # `cancel` is same as ``WaitTillFirst.cancel``
    # `is_cancelled` is same as ``Future.is_cancelled``
    # `is_done` is same as ``Future.is_done``
    # `is_pending` is same as ``Future.is_pending``
    # `result` is same as ``Future.result``
    # `exception` is same as ``Future.exception``
    # `add_done_callback` is same as ``Future.add_done_callback``
    # `remove_done_callback` is same as ``Future.remove_done_callback``
    # `set_result` is same as ``WaitTillFirst.set_result``
    # `set_result_if_pending` is same as ``WaitTillFirst.set_result_if_pending``
    # `set_exception` is same as ``WaitTillFirst.set_exception``
    # `set_exception_if_pending` is same as ``WaitTillFirst.set_exception_if_pending``
    # `__iter__` is same as ``Future.__iter__``
    # `__await__` is same as ``Future.__await__``
    # if __debug__:
    #    `__del__` is same as ``Future.__del__``
    #    `__silence__` is same as ``Future.__silence__``
    #    `__silence_cb__` is same as ``Future.__silence_cb__``
    # `cancel_handles` is same as ``Future.cancel_handles``
    # `clear` is same as ``WaitTillFirst.clear``
    # `sleep` is same as ``WaitTillFirst.clear``
    # `sync_wrap` is same as ``Future.cancel_handles``
    # `async_wrap` is same as ``Future.cancel_handles``
