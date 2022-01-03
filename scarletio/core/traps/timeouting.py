__all__ = ('future_or_timeout', 'repeat_timeout',)

from threading import current_thread

from ...utils import include

from ..exceptions import CancelledError
from ..time import LOOP_TIME

from .handle_cancellers import _TimeoutHandleCanceller
from .task import Task


EventThread = include('EventThread')

def future_or_timeout(future, timeout):
    """
    If the given ``Future`` is not done till the given `timeout` occurs, set `TimeoutError` as it's exception.
    
    Parameters
    ----------
    future : ``Future``
        The future to set the timeout to.
    timeout : `float`
        The time after the given `future`'s exception is set as `TimeoutError`.
    
    Raises
    ------
    RuntimeError
        The future's event loop is already stopped.
    
    Notes
    -----
    For futures, which wait for more results and exceptions like ``Gatherer``, `TimeoutError` gives only 1 result,
    rigging it's results. This is not the case of ``FutureWM``, because that stops when the first exception is received.
    
    If `future_or_timeout` is used on ``WaitTillFirst``, ``WaitTillAll`` or on ``WaitTillAll``, then they stop
    collecting their result at the point, when the timeout occurs and they yield their actual result at that point
    without any specific exception.
    
    At the case of ``WaitContinuously``, when the timeout occurs the next yielded result will be `None` instead of a
    ``Future``.
    """
    loop = future._loop
    callback = _TimeoutHandleCanceller()
    handle = loop.call_later(timeout, callback, future)
    if handle is None:
        raise RuntimeError(
            f'`future_or_timeout` was called on future with a stopped loop; loop={loop!r}.'
        )
    
    callback._handle = handle
    future.add_done_callback(callback)


class repeat_timeout:
    """
    Repeats timeout on the code executed within a context of a for loop.
    
    The timeout it re-set with each iteration.
    
    The main difference between ``repeat_timeout` and ``future_or_timeout`` is, that this only renews the timeout if
    expired, saving a lot of resources on fast running loops compared to their timeout duration.
    
    Usage
    -----
    ```py
    try:
        with repeat_timeout(10.0) as loop:
            for _ in loop:
                await my_task(...)
    except TimeoutError:
        # my_task(...) did not complete within timeout.
    ```
    
    Attributes
    ----------
    _exception : `None`, ``CancelledError``
        The dropped exception to the task.
    _handle : `None`, ``TimerHandle``
        The handle to cancel when the loop is over.
    _last_set : `float`
        The last time when we repeated the timeout. Set as monotonic time. Defaults to `0.0` if was not set.
    _loop : ``EventThread``
        The current event loop.
    _task : ``Task``
        The currently running task.
    _timeout : `float`
        The time to drop `TimeoutError` after.
    """
    __slots__ = ('_exception', '_handle', '_last_set', '_loop', '_task', '_timeout')
    
    def __new__(cls, timeout):
        """
        Creates a new repeated timeouter.
        
        Parameters
        ----------
        timeout : `float`
            The time to drop `TimeoutException` after.
        """
        thread = current_thread()
        if not isinstance(thread, EventThread):
            raise RuntimeError(
                f'`repeat_timeout used outside of `{EventThread.__name__}`, at {thread!r}.'
            )
        
        task = thread.current_task
        if task is None:
            raise RuntimeError(
                f'`repeat_timeout` used outside of a `{Task.__name__}`.'
            )
        
        self = object.__new__(cls)
        self._last_set = 0.0
        self._loop = thread
        self._task = task
        self._timeout = timeout
        self._handle = thread.call_later(timeout, self)
        self._exception = None
        return self
    
    
    def __iter__(self):
        """Iterating a timeout handler returns itself."""
        return self
    
    
    def __next__(self):
        """Called when the timeout handler does a loop, resetting its timeout."""
        self._last_set = LOOP_TIME()
    
    
    def __enter__(self):
        """Entering a timeout handler returns itself."""
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exists the repeated timeout, dropping `TimeoutError` when cancelled."""
        handle = self._handle
        if (handle is not None):
            self._handle = None
            handle.cancel()
        
        exception = self._exception
        if (exception is not None) and (self._task._exception is exception):
            raise TimeoutError from None
        
        return False
    
    
    def __call__(self):
        """
        Checks whether the repeat timeout handler timed out.
        """
        last_set = self._last_set
        if last_set:
            self._last_set = 0.0
            handle = self._loop.call_at(last_set + self._timeout, self)
        else:
            handle = None
            exception = CancelledError()
            self._exception = exception
            self._task.set_exception_if_pending(exception)
        
        self._handle = handle
