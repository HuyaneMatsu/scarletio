__all__ = ('create_event_loop', 'get_event_loop', 'get_or_create_event_loop', 'set_event_loop')

from threading import current_thread, enumerate as list_threads

from ...utils import WeakItemDictionary, export

from ..event_loop import EventThread


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
    
    Parameters
    ----------
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


def _maybe_set_event_loop(event_loop):
    """
    Sets the event loop linked to the current thread if possible.
    
    Parameters
    ----------
    event_loop : ``EventThread``
        The event loop to set.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        return
    
    linked_event_loop = _try_detect_event_loop(local_thread)
    if (linked_event_loop is not None):
        return
    
    THREAD_TO_EVENT_LOOP_REFERENCE[local_thread] = event_loop


def create_event_loop(**keyword_parameters):
    """
    Creates a new event loop.
    
    Parameters
    ----------
    **keyword_parameters : Keyword parameters
        Parameters to create the event loop with.
    
    Other Parameters
    ----------------
    daemon : `bool` = `False`, Optional (Keyword only)
        Whether the event loop should be daemon.
    name : `None`, `str` = `None`, Optional (Keyword only)
        The event loop's name.
    start_later : `bool` = `True`, Optional (Keyword only)
        Whether the event loop should be started only later.

    Returns
    -------
    event_loop : ``EventThread``
    """
    event_loop = EventThread(**keyword_parameters)
    _maybe_set_event_loop(event_loop)
    return event_loop


def get_or_create_event_loop(**keyword_parameters):
    """
    Gets the local event loop if applicable. If not creates a new one.
    
    Parameters
    ----------
    **keyword_parameters : Keyword parameters
        Parameters to create the event loop with.
    
    Other Parameters
    ----------------
    daemon : `bool` = `False`, Optional (Keyword only)
        Whether the event loop should be daemon.
    name : `None`, `str` = `None`, Optional (Keyword only)
        The event loop's name.
    start_later : `bool` = `True`, Optional (Keyword only)
        Whether the event loop should be started only later.

    Returns
    -------
    event_loop : ``EventThread``
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        return local_thread
    
    event_loop = _try_detect_event_loop(local_thread)
    if (event_loop is not None):
        return event_loop
    
    event_loop = EventThread(**keyword_parameters)
    THREAD_TO_EVENT_LOOP_REFERENCE[local_thread] = event_loop
    return event_loop
