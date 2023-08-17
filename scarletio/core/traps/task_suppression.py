__all__ = ('skip_poll_cycle', 'skip_ready_cycle', 'sleep')

from ...utils import include, to_coroutine

from .future import Future
from .handle_cancellers import _SleepHandleCanceller


EventThread = include('EventThread')
get_event_loop = include('get_event_loop')


@to_coroutine
def skip_ready_cycle():
    """
    Skips a ready cycle.
    
    This function is an awaitable generator.
    """
    yield


async def skip_poll_cycle(loop = None):
    """
    Skips a full poll cycle.
    
    This function is a coroutine.
    
    Parameters
    ----------
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to skip poll cycle on.
    """
    if loop is None:
        loop = get_event_loop()
    
    future = Future(loop)
    loop.call_at(0.0, Future.set_result_if_pending, future, None)
    await future


def sleep(delay, loop = None):
    """
    Suspends the current task, allowing other tasks to run.
    
    Parameters
    ----------
    delay : `float`
        The time to block sleep in seconds.
    loop : `None`, ``EventThread`` = `None`, Optional
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
        loop = get_event_loop()
    
    future = Future(loop)
    if delay <= 0.:
        future.set_result(None)
        return future
    
    callback = object.__new__(_SleepHandleCanceller)
    handle = loop.call_after(delay, callback, future)
    if handle is None:
        raise RuntimeError(
            f'`sleep` was called inside of a stopped loop; loop={loop!r}.'
        )
    
    future._callbacks.append(callback)
    callback._handle = handle
    return future
