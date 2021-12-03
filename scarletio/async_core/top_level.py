__all__ = ('create_event_loop', 'create_future', 'create_task', 'get_event_loop', 'run',)

from threading import current_thread, enumerate as list_threads

from ..utils import WeakItemDictionary
from .event_loop import EventThread
from .traps import Task, Future

THREAD_TO_EVENT_LOOP_REFERENCE = WeakItemDictionary()


def _try_detect_event_loop(local_thread):
    """
    Tries to detect the event loop, what should be used from the current thread.
    
    Returns
    -------
    event_loop : `None` or ``EventThread``
    """
    try:
        thread = THREAD_TO_EVENT_LOOP_REFERENCE[local_thread]
    except KeyError:
        pass
    else:
        if not thread.is_stopped():
            return thread
    
    for thread in list_threads():
        if not isinstance(thread, EventThread):
            continue
        
        if thread.daemon:
            continue
        
        if thread.is_stopped():
            continue
        
        THREAD_TO_EVENT_LOOP_REFERENCE[local_thread] = thread
        return thread


def _get_event_loop_is_current_thread():
    """
    Gets the local event loop if applicable and whether it is indeed the current thread or nah.
    
    Used by other top level functions.
    
    Returns
    -------
    event_loop : ``EventThread``
        The local event loop.
    is_current_thread : `bool`
        Whether the event loop is teh current thread.
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        return local_thread, True
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is not None):
        return event_loop, False
    
    raise RuntimeError(f'No running event loop on {local_thread!r}.')


def get_event_loop():
    """
    Gets the local event loop if applicable. If not raises `RuntimeError`.
    
    Returns
    -------
    event_loop : ``EventThread``
        The local event loop.
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        return local_thread
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is not None):
        return event_loop
    
    raise RuntimeError(f'No running event loop on {local_thread!r}.')


def create_event_loop(**kwargs):
    """
    Creates a new event loop.
    
    Parameters
    ----------
    **kwargs : Keyword parameters
        Parameters to create the event loop with.
    
    Other parameters
    ----------------
    daemon : `bool`, Optional (Keyword only)
        Whether the event loop should be daemon. Defaults to `False`
    name : `None` or `str`, Optional (Keyword only)
        The event loop's name. Defaults ot `None`.
    start_later : `bool`, Optional (Keyword only)
        Whether the event loop should be started only later. Defaults to `True`
    keep_executor_count : `int`, Optional (Keyword only)
        The minimal amount of executors, what the event thread should keep alive. Defaults to `1`.

    Returns
    -------
    event_loop : ``EventThread``
    """
    return EventThread(**kwargs)


def create_task(coroutine):
    """
    Creates a task on the local event loop.
    
    Parameters
    ----------
    coroutine : `GeneratorType` or `CoroutineType`
        The coroutine to create task from.
    
    Returns
    -------
    task : ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread()
    task = Task(coroutine, loop)
    if (not is_current_thread):
        loop.wake_up()
    
    return task


def create_future():
    """
    Creates s future bound to teh local event loop.
    
    Returns
    -------
    task : ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread()
    future = Future(loop)
    if (not is_current_thread):
        loop.wake_up()
    
    return future


def run(awaitable, timeout=None):
    """
    Runs the given awaitable on an event loop. This function cannot be called from an event loop itself.
    
    Parameters
    ----------
    awaitable : `awaitable`
        The awaitable to run.
    timeout : `None` or `float`, Optional
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
        raise RuntimeError(f'`{local_thread.__class__.__name__}.run` should not be called from itself.')
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is None):
        stop_event_loop_after = True
        event_loop = EventThread(daemon=True, name='scarletio.run', start_later=False)
    else:
        stop_event_loop_after = False
    
    try:
        return event_loop.run(awaitable, timeout=timeout)
    finally:
        if stop_event_loop_after:
            event_loop.stop()
