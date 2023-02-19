__all__ = ('ScarletExecutor',)

from threading import current_thread
from types import MethodType

from ...utils import WeakReferer, ignore_frame, include

from ..exceptions import CancelledError

from .future import Future


ignore_frame(__spec__.origin, 'get_result', 'raise exception',)
ignore_frame(__spec__.origin, '__iter__', 'yield self',)
ignore_frame(__spec__.origin, '__call__', 'future.get_result()', )

EventThread = include('EventThread')


def _scarlet_executor_callback(parent_reference, future):
    """
    Called as a callback when a waited future or task is finished.
    
    Removes the given `future`'s from the parent's active ones. If the parent Scarlet executor is overloaded with
    tasks, wakes it up.
    
    If the `future` is finished with an exception then propagates it to it's parent to re-raise.
    
    Parameters
    ----------
    parent_reference : ``WeakReferer`` to ``ScarletExecutor``
        Reference to the parent scarlet executor.
    future : ``Future``
        A finished future or task.
    """
    parent = parent_reference()
    if parent is None:
        return
    
    active = parent._active
    
    active.discard(future)
    
    try:
        future.get_result()
    except CancelledError:
        pass
    
    except BaseException as err:
        exception = parent._exception
        if exception is None:
            parent._exception = err
    
    waiter = parent._waiter
    if (waiter is not None):
        waiter.set_result_if_pending(None)


class ScarletExecutor:
    """
    Scarlet executor allows the user to limit parallelly running task amount to a set one. Not that, only those tasks
    count, which are added to the executor with it's ``.add`` method.
    
    If an exception (except ``CancelledError``) occurs in any of the added tasks, then that exception is propagated
    and every other task is cancelled.
    
    Should be used, like:
    
    ```py
    from time import perf_counter
    from hata import ScarletExecutor, sleep
    
    async def showcase():
        start = perf_counter()
        
        async with ScarletExecutor(2) as scarlet:
            for sleep_time in range(10):
                await scarlet.add(sleep(sleep_time))
        
        end = perf_counter()
        print(end-start)
    ```
    
    Running showcase will take at least `25` seconds, because ``ScarletExecutor`` will allow only `2` sleeps to run
    at the same time, like:
    
    +---------------+-------------------------------+-----------------------+
    | Time passed   | Slot 1                        | Slot 2                |
    +===============+===============================+=======================+
    | 0 (s)         | N/A -> sleep(0) -> sleep(2)   | N/A -> sleep(1)       |
    +---------------+-------------------------------+-----------------------+
    | 1 (s)         | sleep(2)                      | sleep(1) -> sleep(3)  |
    +---------------+-------------------------------+-----------------------+
    | 2 (s)         | sleep(2) -> sleep(4)          | sleep(3)              |
    +---------------+-------------------------------+-----------------------+
    | 3 (s)         | sleep(4)                      | sleep(3)              |
    +---------------+-------------------------------+-----------------------+
    | 4 (s)         | sleep(4)                      | sleep(3) -> sleep(5)  |
    +---------------+-------------------------------+-----------------------+
    | 5 (s)         | sleep(4)                      | sleep(5)              |
    +---------------+-------------------------------+-----------------------+
    | 6 (s)         | sleep(4) -> sleep(6)          | sleep(5)              |
    +---------------+-------------------------------+-----------------------+
    | 7 (s)         | sleep(6)                      | sleep(5)              |
    +---------------+-------------------------------+-----------------------+
    | 8 (s)         | sleep(6)                      | sleep(5)              |
    +---------------+-------------------------------+-----------------------+
    | 9 (s)         | sleep(6)                      | sleep(5) -> sleep(7)  |
    +---------------+-------------------------------+-----------------------+
    | 10 (s)        | sleep(6)                      | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 11 (s)        | sleep(6)                      | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 12 (s)        | sleep(6) -> sleep(8)          | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 13 (s)        | sleep(8)                      | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 14 (s)        | sleep(8)                      | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 15 (s)        | sleep(8)                      | sleep(7)              |
    +---------------+-------------------------------+-----------------------+
    | 16 (s)        | sleep(8)                      | sleep(7) -> sleep(9)  |
    +---------------+-------------------------------+-----------------------+
    | 17 (s)        | sleep(8)                      | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 18 (s)        | sleep(8)                      | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 19 (s)        | sleep(8)                      | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 20 (s)        | sleep(8) -> N/A               | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 20 (s)        | N/A                           | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 21 (s)        | N/A                           | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 22 (s)        | N/A                           | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 23 (s)        | N/A                           | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 24 (s)        | N/A                           | sleep(9)              |
    +---------------+-------------------------------+-----------------------+
    | 25 (s)        | N/A                           | sleep(9) -> N/A       |
    +---------------+-------------------------------+-----------------------+
    
    By increasing parallelism to `3`, the showcase will take only `18` seconds to finish:
    
    ```py
    async def showcase():
        start = perf_counter()
        
        async with ScarletExecutor(3) as scarlet:
            for sleep_time in range(10):
                await scarlet.add(sleep(sleep_time))
        
        end = perf_counter()
        print(end - start)
    ```
    
    +---------------+-------------------------------+-----------------------+-----------------------+
    | Time passed   | Slot 1                        | Slot 2                | Slot 3                |
    +===============+===============================+=======================+=======================+
    | 0 (s)         | N/A -> sleep(0) -> sleep(3)   | N/A -> sleep(1)       | N/A -> sleep(2)       |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 1 (s)         | sleep(3)                      | sleep(1) -> sleep(4)  | sleep(2)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 2 (s)         | sleep(3)                      | sleep(4)              | sleep(2) -> sleep(5)  |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 3 (s)         | sleep(3) -> sleep(6)          | sleep(4)              | sleep(5)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 4 (s)         | sleep(6)                      | sleep(4)              | sleep(5)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 5 (s)         | sleep(6)                      | sleep(4) -> sleep(7)  | sleep(5)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 6 (s)         | sleep(6)                      | sleep(7)              | sleep(5)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 7 (s)         | sleep(6)                      | sleep(7)              | sleep(5) -> sleep(8)  |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 8 (s)         | sleep(6)                      | sleep(7)              | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 9 (s)         | sleep(6) -> sleep(9)          | sleep(7)              | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 10 (s)        | sleep(9)                      | sleep(7)              | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 11 (s)        | sleep(9)                      | sleep(7)              | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 12 (s)        | sleep(9)                      | sleep(7) -> N/A       | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 13 (s)        | sleep(9)                      | N/A                   | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 14 (s)        | sleep(9)                      | N/A                   | sleep(8)              |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 15 (s)        | sleep(9)                      | N/A                   | sleep(8) -> N/A       |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 16 (s)        | sleep(9)                      | N/A                   | N/A                   |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 17 (s)        | sleep(9)                      | N/A                   | N/A                   |
    +---------------+-------------------------------+-----------------------+-----------------------+
    | 18 (s)        | sleep(9) -> N/A               | N/A                   | N/A                   |
    +---------------+-------------------------------+-----------------------+-----------------------+
    
    Attributes
    ----------
    _active : `set` of ``Future``
        The already running tasks.
    _callback : `None`, `MethodType`
        Callback set to the parallelly limited tasks.
    _exception : `None`, `BaseException`
        Any exception raised by an added task. ``CancelledError``-s are ignored.
    _limit : `int`
        The maximal amount of parallelism allowed by the Scarlet executor.
    _loop : `None`, ``EventThread``
        The event loop to what the ScarletExecutor is bound to.
    _waiter : `None`, ``Future``
        A future which is used to block the main task's execution if the parallelly running tasks' amount is greater or
        equal to the ``._limit``.
    """
    __slots__ = ('__weakref__', '_active', '_callback', '_exception', '_limit', '_loop', '_waiter', )
    
    def __new__(cls, limit = ...):
        """
        Creates a new Scarlet executor instance.
        
        Parameters
        ----------
        limit : `int`, Optional
            The maximal amount of parallelism allowed by the Scarlet executor. Defaults to `10`.
        
        Raises
        ------
        TypeError
            `size` is not given as `int`.
        ValueError
            `size` is given as non negative `int`.
        """
        if limit is ...:
            limit = 10
        
        else:
            if not isinstance(limit, int):
                raise TypeError(
                    f'`limit` can be `int`, got {limit.__class__.__name__}; {limit!r}.'
                )
            
            if limit < 1:
                raise ValueError(
                    f'`limit` can only be positive, got {limit!r}.'
                )
        
        self = object.__new__(cls)
        self._limit = limit
        
        self._active = set()
        self._loop = None
        self._callback = None
        self._waiter = None
        self._exception = None
        
        return self
    
    
    async def __aenter__(self):
        """
        Enters the scarlet executor.
        
        This method is a coroutine.
        
        Raises
        ------
        RuntimeError
            Called from outside of an ``EventThread``.
        """
        loop = current_thread()
        if not isinstance(loop, EventThread):
            raise RuntimeError(
                f'`{self.__class__.__name__}` used at non `{EventThread.__name__}`, at {loop!r}.'
            )
        
        self._loop = loop
        self._waiter = Future(loop)
        self._callback = MethodType(_scarlet_executor_callback, WeakReferer(self))
        
        return self
    
    
    async def add(self, future):
        """
        Adds a task to the Scarlet executor to execute parallelly with the other added ones. Blocks execution, if the
        amount of added tasks is greater or equal than the set limit.
        
        This method is a coroutine.
        
        Raises
        ------
        RuntimeError
            ``.add`` called when the Scarlet executor is not entered with `async with.`
        CancelledError
            If any of the tasks raised an error, ``CancelledError`` is propagated to quit from the Scarlet executor.
            This exception is catched by ``.__exit__`` and the original exception is reraised.
        """
        callback = self._callback
        if callback is None:
            raise RuntimeError(
                f'Calling `{self.__class__.__name__}.add` when `{self!r}` is not entered.'
            )
        
        future = self._loop.ensure_future(future)
        future.add_done_callback(callback)
        
        active = self._active
        active.add(future)
        
        waiter = self._waiter
        
        if waiter is None:
            waiter = Future(self._loop)
            self._waiter = waiter
        
        else:
            if waiter.is_done():
                if self._exception is None:
                    waiter = Future(self._loop)
                    self._waiter = waiter
                else:
                    raise CancelledError
        
        limit = self._limit
        while len(active) >= limit:
            await waiter
            if (self._exception is not None):
                raise CancelledError
            
            waiter = Future(self._loop)
            self._waiter = waiter
            
            break
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Leaves from the scarlet execution, blocking till all the added tasks are finished.
        
        If any of the added tasks raised an exception, what is not ``CancelledError``, then cancels all of them and
        propagates the given exception.
        
        This method is a coroutine.
        """
        if exc_type is None:
            active = self._active
            
            while active:
                waiter = self._waiter
                if waiter is None:
                    waiter = Future(self._loop)
                    self._waiter = waiter
                
                await waiter
                
                exception = self._exception
                if exception is None:
                    waiter = Future(self._loop)
                    self._waiter = waiter
                    continue
                
                self._callback = None
                
                self._waiter = None
                self._loop = None
                self._exception = None
                
                for future in active:
                    future.cancel()
                
                active.clear()
                
                raise exception
            
            self._callback = None
            
            self._waiter = None
            self._loop = None
            self._exception = None
            return False
        
        active = self._active
        for future in active:
            future.cancel()
        
        active.clear()
        
        exception = self._exception
        
        self._callback = None
        
        self._waiter = None
        self._loop = None
        self._exception = None
        
        if exception is None:
            if exc_type is CancelledError:
                return True
            else:
                return False
        else:
            raise exception

    
    def __repr__(self):
        """Returns the scarlet executor's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
            ' limit = ',
            repr(self._limit),
        ]
        
        if (self._loop is None):
            repr_parts.append(', closed')
        else:
            repr_parts.append(', active = ')
            repr_parts.append(repr(len(self._active)))
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
