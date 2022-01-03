__all__ = ('Gatherer',)

from ...utils import ignore_frame, is_awaitable

from ..exceptions import InvalidStateError

from .future import FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING
from .result_gathering_future import ResultGatheringFuture


ignore_frame(__spec__.origin, '__call__', 'raise exception',)
ignore_frame(__spec__.origin, '__call__', 'future.result()',)

class GathererElement:
    """
    An element of a ``Gatherer`` results.
    
    Attributes
    ----------
    result : `Any`
        The result of a gathered future.
    exception : `None`, `BaseException`
        The exception of a gathered exception.
    """
    __slots__ = ('exception', 'result',)
    
    def __init__(self, result, exception):
        """
        Creates a new ``GathererElement`` with the given parameters.
        
        Parameters
        ----------
        result : `Any`
            The result of a gathered future.
        exception : `None`, `BaseException`
            The exception of a gathered exception.
        """
        self.result = result
        self.exception = exception
    
    
    def __call__(self):
        """
        Returns a gathered future's result or raises it's exception.
        
        Returns
        -------
        result : `Any`
            A gathered future's result.
        
        Raises
        ------
        BaseException
            A gathered future's exception.
        """
        exception = self.exception
        if exception is None:
            return self.result
        raise exception


class GathererCallback:
    """
    Callback of ``Gatherer`` to set a waited future's result or exception to itself.
    
    Attributes
    ----------
    _parent : ``Gatherer``
        The gathering future
    """
    __slots__ = ('_parent',)
    
    def __init__(self, parent):
        """
        Creates a new gathering future callback.
        
        Parameters
        ----------
        parent : ``Gatherer``
            The gathering future
        """
        self._parent = parent
    
    def __call__(self, future):
        """
        Sets a result of an exception to the parent gatherer future.
        
        Parameters
        ----------
        future : ``Future``
            A waited future.
        """
        parent = self._parent
        try:
            result = future.result()
        except BaseException as err:
            parent.set_exception_if_pending(err)
        else:
            parent.set_result_if_pending(result)


class Gatherer(ResultGatheringFuture):
    """
    A ``Future`` subclass to gather more future's results and their exceptions.
    
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
    _result : `list` of ``GathererElement``
        The already gathered future's results.
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
    _count : `int`
        The amount, for how much future's result the gatherer waits.
    """
    __slots__ = ()
    
    def __new__(cls, loop, coroutines_or_futures):
        """
        Creates a new gatherer bound to the given `loop`, waiting for the given `coroutines_or_futures`-s results.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop to what the created future will be bound to.
        coroutines_or_futures : `iterable` of `awaitable`
            Awaitables, which result will be gathered.
        
        Raises
        ------
        TypeError
            Any of the given `coroutines_or_futures` is not awaitable.
        """
        awaitables = set()
        for awaitable in coroutines_or_futures:
            if not is_awaitable(awaitable):
                raise TypeError(
                    f'Cannot await on {awaitable.__class__.__name__}; {awaitable!r}.'
                )
            awaitables.add(awaitable)
        
        self = object.__new__(cls)
        self._loop = loop
        self._count = len(awaitables)
        
        self._result = []
        self._exception = None
        
        self._callbacks = []
        self._blocking = False
        
        if awaitables:
            self._state = FUTURE_STATE_PENDING
            
            callback = GathererCallback(self)
            
            for awaitable in awaitables:
                task = loop.ensure_future(awaitable)
                task.add_done_callback(callback)
        else:
            self._state = FUTURE_STATE_FINISHED
        
        return self
    
    
    def set_result(self, result):
        """
        Sets a result to the gatherer. if all the expected results of the gatherer are retrieved already, marks it as
        done as well.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Raises
        ------
        InvalidStateError
            If the gatherer is already done.
        """
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(self, 'set_result')
        
        results = self._result
        results.append(GathererElement(result, None))
        if self._count != len(results):
            return
        
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
    
    
    def set_result_if_pending(self, result):
        """
        Sets a result to the gatherer. If all the expected results of the gatherer are retrieved already, marks it as
        done as well. Not like ``.set_result``, this method will not raise ``InvalidStateError`` if the future is
        already done.
        
        Parameters
        ----------
        result : `Any`
            The object to set as result.
        
        Returns
        ------
        set_result : `int` (`0`, `1`, `2`)
            If the gatherer is already done, returns `0`. If the gatherer's result was successfully set, returns `1`,
            meanwhile if the gatherer was marked as done as well, returns `2`.
        """
        if self._state != FUTURE_STATE_PENDING:
            return 0
        
        results = self._result
        results.append(GathererElement(result, None))
        if self._count != len(results):
            return 2
        
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        return 1
    
    
    def set_exception(self, exception):
        """
        Sets an exception to the gatherer. If all the expected results of the gatherer are retrieved already, marks it
        as done as well.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as a result of the gatherer.
        
        Raises
        ------
        InvalidStateError
            If the gatherer is already done.
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
        
        results = self._result
        results.append(GathererElement(None, exception))
        if self._count != len(results):
            return
        
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
    
    
    def set_exception_if_pending(self, exception):
        """
        Sets an exception to the gatherer. If all the expected results of the gatherer are retrieved already, marks it
        as done as well. Not like ``.set_exception``, this method will not raise ``InvalidStateError`` if the future is
        already done.
        
        Parameters
        ----------
        exception : `BaseException`
            The exception to set as a result of the gatherer.
        
        Returns
        ------
        set_result : `int` (`0`, `1`, `2`)
            If the gatherer is already done, returns `0`. If the exception was set successfully as a gatherer result,
            returns `1`, meanwhile if the gatherer was marked as done as well, returns `2`.
        
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
        
        results = self._result
        results.append(GathererElement(None, exception))
        if self._count != len(results):
            return 1
        
        self._state = FUTURE_STATE_FINISHED
        self._loop._schedule_callbacks(self)
        return 2
