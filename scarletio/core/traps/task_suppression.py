__all__ = ('skip_ready_cycle', 'sleep')

from threading import current_thread

from ...utils import to_coroutine, include

from .future import Future
from .handle_cancellers import _SleepHandleCanceller

EventThread = include('EventThread')


@to_coroutine
def skip_ready_cycle():
    """
    Skips a ready cycle.
    
    This function is a coroutine.
    """
    yield


def sleep(delay, loop=None):
    """
    Suspends the current task, allowing other tasks to run.
    
    Parameters
    ----------
    delay : `float`
        The time to block sleep in seconds.
    loop : `None` or ``EventThread``, Optional
        The event loop to which the returned `future` will be bound to. If not given, or given as `None`, then the
        current event loop will be used.
    
    Returns
    -------
    future : ``Future``
        Future, what can be awaited, to suspend a task.
    
    Raises
    ------
    RuntimeError
        The given or the local event loop is already stopped.
    """
    if loop is None:
        loop = current_thread()
        if not isinstance(loop, EventThread):
            raise RuntimeError(f'`sleep` called without passing `loop` parameter from a non {EventThread.__name__}: '
                f'{loop!r}.')
    
    future = Future(loop)
    if delay <= 0.:
        future.set_result(None)
        return future
    
    callback = object.__new__(_SleepHandleCanceller)
    handle = loop.call_later(delay, callback, future)
    if handle is None:
        raise RuntimeError(f'`sleep` was called with future with a stopped loop {loop!r}')
    
    future._callbacks.append(callback)
    callback._handle = handle
    return future

