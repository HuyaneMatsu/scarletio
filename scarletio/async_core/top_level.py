__all__ = ('create_future', 'create_task', 'get_event_loop',)

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
