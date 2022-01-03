__all__ = ('ResultGatheringFuture',)

import reprlib

from ...utils.trace import format_callback

from ..exceptions import InvalidStateError

from .future import FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, Future


class ResultGatheringFuture(Future):
    """
    A Future subclass, which yields after it's result was set a set amount of times with ``.set_result``, or with
    ``.set_result_if_pending``, or till an exception is set to with ``.set_exception``, or with
    ``.set_exception_if_pending``.
    
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
    _result : `list` of `Any`
        The results of the future.
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
        
        Note, that states are checked by memory address and not by equality. Also ``FUTURE_STATE_RETRIEVED`` is used
        only if `__debug__` is set as `True`.
    _count : `int`
        The amount, how much times the future's result need to be set, because it will yield.
    """
    __slots__ = ('_count',)
    
    def __new__(cls, loop, count):
        """
        Creates a new ``ResultGatheringFuture`` object bound to the given `loop`, which will be marked as done, only if `count`
        results are set to it with ``.set_result``, or with ``.set_result_if_pending``.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        count : `int`
            The amount of times, the future's result need to be set, because becoming done.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._count = count
        self._state = FUTURE_STATE_PENDING
        
        self._result = []
        self._exception = None
        
        self._callbacks = []
        self._blocking = False
        
        return self
    
    
    def __repr__(self):
        """Returns the gatherer's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ']
        
        state = self._state
        repr_parts.append(state)
        
        if state >= FUTURE_STATE_FINISHED:
            exception = self._exception
            if exception is None:
                results = self._result
                for index, result in enumerate(results):
                    repr_parts.append(f', result[')
                    repr_parts.append(repr(index))
                    repr_parts.append(']=')
                    repr_parts.append(reprlib.repr(result))
                
                repr_parts.append(', needed=')
                repr_parts.append(str(self._count - len(results)))
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
    
    
    def set_result(self, result):
        """
        Sets the future result, and if it waits for no more results, marks it as done as well.
        
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
        
        results = self._result
        results.append(result)
        if self._count != len(results):
            return
        
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)


    def set_result_if_pending(self, result):
        """
        Sets the future result, and if it waits for no more results, marks it as done as well. Not like
        ``.set_result``, this method will not raise ``InvalidStateError`` if the future is already done.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Returns
        ------
        set_result : `int` (`0`, `1`, `2`)
            If the future is already done, returns `0`. If the future's result was successfully set, returns `1`,
            meanwhile if the future was marked as done as well, returns `2`.
        """
        if self._state != FUTURE_STATE_PENDING:
            return 0
        
        results = self._result
        results.append(result)
        if self._count != len(results):
            return 1
            
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        return 2
    
    
    def clear(self):
        """
        Clears the future making it reusable.
        """
        self._state = FUTURE_STATE_PENDING
        self._exception = None
        self._result.clear()
        self.cancel_handles()
        self._blocking = False

