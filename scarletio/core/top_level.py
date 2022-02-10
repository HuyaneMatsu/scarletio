__all__ = (
    'create_event_loop', 'create_future', 'create_task', 'get_current_task', 'get_event_loop', 'get_tasks', 'run',
    'run_coroutine', 'set_event_loop'
)

from threading import current_thread, enumerate as list_threads

from ..utils import WeakItemDictionary, export

from .event_loop import EventThread
from .traps import Future, Task


THREAD_TO_EVENT_LOOP_REFERENCE = WeakItemDictionary()


def _try_detect_event_loop(local_thread):
    """
    Tries to detect the event loop, what should be used from the current thread.
    
    Returns
    -------
    event_loop : `None`, ``EventThread``
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


def _get_event_loop_is_current_thread(loop):
    """
    Gets the local event loop if applicable and whether it is indeed the current thread or nah.
    
    Used by other top level functions.
    
    Parameters
    ----------
    loop : `None`, ``EventLoop``
        Optional event loop to use instead of auto-detecting.
    
    Returns
    -------
    event_loop : ``EventThread``
        The local event loop.
    is_current_thread : `bool`
        Whether the event loop is the current thread.
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    local_thread = current_thread()
    if (loop is not None):
        return loop, (loop is local_thread)
    
    if isinstance(local_thread, EventThread):
        return local_thread, True
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is not None):
        return event_loop, False
    
    raise RuntimeError(
        f'No running event loop for {local_thread!r}.'
    )


@export
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
    
    raise RuntimeError(
        f'No running event loop for {local_thread!r}.'
    )


def set_event_loop(event_loop):
    """
    Sets the given event loop to be linked to the current thread.
    
    Can be used to force update event loop resolution of ``get_event_loop`` for the current thread.
    
    Returns
    -------
    event_loop : ``EventThread``
        The event loop to set.
    
    Raises
    ------
    RuntimeError
        Cannot set event loop from an event loop.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        raise RuntimeError(
            f'Cannot set event loop from an event loop. Current event loop: {local_thread!r} ;got: {event_loop!r}.'
        )
    
    THREAD_TO_EVENT_LOOP_REFERENCE[local_thread] = event_loop


def create_event_loop(**kwargs):
    """
    Creates a new event loop.
    
    Parameters
    ----------
    **kwargs : Keyword parameters
        Parameters to create the event loop with.
    
    Other parameters
    ----------------
    daemon : `bool` = `False`, Optional (Keyword only)
        Whether the event loop should be daemon.
    name : `None`, `str` = `None`, Optional (Keyword only)
        The event loop's name.
    start_later : `bool` = `True`, Optional (Keyword only)
        Whether the event loop should be started only later.
    keep_executor_count : `int` = `1`, Optional (Keyword only)
        The minimal amount of executors, what the event thread should keep alive.

    Returns
    -------
    event_loop : ``EventThread``
    """
    return EventThread(**kwargs)


def create_task(coroutine, loop=None):
    """
    Creates a task on the local event loop.
    
    Parameters
    ----------
    coroutine : `GeneratorType`, `CoroutineType`
        The coroutine to create task from.
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to schedule the created task on.
    
    Returns
    -------
    task : ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread(loop)
    task = Task(coroutine, loop)
    if (not is_current_thread):
        loop.wake_up()
    
    return task


def create_future(loop=None):
    """
    Creates s future bound to the local event loop.
    
    Parameters
    ----------
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to create bound future to.
    
    Returns
    -------
    task : ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread(loop)
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
        event_loop = EventThread(daemon=True, name='scarletio.run', start_later=False)
    else:
        stop_event_loop_after = False
    
    try:
        return event_loop.run(awaitable, timeout=timeout)
    finally:
        if stop_event_loop_after:
            event_loop.stop()


def get_current_task(loop=None):
    """
    Returns the currently executed task.
    
    Parameters
    ----------
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to get the current task of.
    
    Returns
    -------
    task : `None`, ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    if loop is None:
        loop = get_event_loop()
    
    return loop.current_task


def get_tasks(loop=None):
    """
    Returns the pending tasks.
    
    Parameters
    ----------
    loop : `None`, ``EventThread`` = `None`, Optional
        The event loop to get the pending tasks
    
    Returns
    -------
    task : `None`, ``Task``
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    if loop is None:
        loop = get_event_loop()
    
    return loop.get_tasks()


def run_coroutine(coroutine, loop=None):
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
    task : ``Task``, ``FutureAsyncWrapper``, `Any`
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    BaseException
        Any exception raised by `coroutine`.
    """
    loop, is_current_thread = _get_event_loop_is_current_thread(loop)
    
    task = Task(coroutine, loop)
    
    if is_current_thread:
        return task
    
    thread = current_thread()
    if isinstance(thread, EventThread):
        # `.async_wrap` wakes up the event loop
        return task.async_wrap(thread)
    
    loop.wake_up()
    return task.sync_wrap().wait()
