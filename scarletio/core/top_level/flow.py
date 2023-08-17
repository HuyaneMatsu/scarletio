__all__ = ('run', 'run_coroutine')

from threading import current_thread

from ...utils import ignore_frame

from ..event_loop import EventThread
from ..traps import Task

from .event_loop import _get_event_loop_is_current_thread, _try_detect_event_loop


ignore_frame(__spec__.origin, 'run_coroutine', 'return task.async_wrap(thread)',)
ignore_frame(__spec__.origin, 'run_coroutine', 'return task.sync_wrap().wait()',)


def run(awaitable, timeout = None):
    """
    Runs the given awaitable on an event loop. This function cannot be called from an event loop itself.
    
    Parameters
    ----------
    awaitable : `awaitable`
        The awaitable to run.
    timeout : `None`, `float` = `None`, Optional
        Timeout after the awaitable should be cancelled. Defaults to `None`.
    
    Raises
    ------
    TypeError
        If `awaitable` is not `awaitable`.
    TimeoutError
         If `awaitable` did not finish before the given `timeout` is over.
    RuntimeError
        If called from itself.
    BaseException
        Any exception raised by `awaitable`.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        raise RuntimeError(
            f'`{local_thread.__class__.__name__}.run` should not be called from itself; thread={local_thread!r}.'
        )
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is None):
        stop_event_loop_after = True
        event_loop = EventThread(daemon = True, name = 'scarletio.run', start_later = False)
    else:
        stop_event_loop_after = False
    
    try:
        return event_loop.run(awaitable, timeout = timeout)
    finally:
        if stop_event_loop_after:
            event_loop.stop()


def run_coroutine(coroutine, loop = None):
    """
    Runs the given coroutine concurrently. If the function is called from an event loop, you can await the result
    of the returned task. If not, then it blocks till the task is finished and returns the result of the coroutine.
    
    Parameters
    ----------
    coroutine : `GeneratorType`, `CoroutineType`
        The coroutine to create task from.
    
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to schedule the created task on.
    
    Returns
    -------
    task : ``Task``, ``FutureWrapperAsync``, `object`
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    BaseException
        Any exception raised by `coroutine`.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread(loop)
    
    task = Task(loop, coroutine)
    
    if is_current_thread:
        return task
    
    thread = current_thread()
    if isinstance(thread, EventThread):
        # `.async_wrap` wakes up the event loop
        return task.async_wrap(thread)
    
    loop.wake_up()
    return task.sync_wrap().wait()
