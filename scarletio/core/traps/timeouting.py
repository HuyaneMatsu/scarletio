__all__ = ('repeat_timeout',)

from threading import current_thread

from ...utils import include

from ..exceptions import CancelledError
from ..time import LOOP_TIME

from .task import Task


EventThread = include('EventThread')


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
    _handle : `None`, ``TimerHandle``
        The handle to cancel when the loop is over.
    _last_set : `float`
        The last time when we repeated the timeout. Set as monotonic time. Defaults to `0.0` if was not set.
    _loop : ``EventThread``
        The current event loop.
    _task : ``Task``
        The currently running task.
    _timed_out : `bool`
        Whether the timeout occurred.
    _timeout : `float`
        The time to drop `TimeoutError` after.
    """
    __slots__ = ('_exception', '_handle', '_last_set', '_loop', '_task', '_timed_out', '_timeout')
    
    def __new__(cls, timeout):
        """
        Creates a new repeated timeouter.
        
        Parameters
        ----------
        timeout : `float`
            The time to drop `TimeoutError` after.
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
        self._handle = thread.call_after(timeout, self)
        self._timed_out = None
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
    
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Exists the repeated timeout, dropping `TimeoutError` when cancelled."""
        handle = self._handle
        if (handle is not None):
            self._handle = None
            handle.cancel()
        
        if exception_type is CancelledError and self._timed_out:
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
            self._timed_out = True
            self._task.cancel()
        
        self._handle = handle
