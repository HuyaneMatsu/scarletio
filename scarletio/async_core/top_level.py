__all__ = ('get_event_loop',)

from threading import current_thread, enumerate as list_threads
from ..utils import WeakItemDictionary
from .event_loop import EventThread


THREAD_TO_EVENT_LOOP_REFERENCE = WeakItemDictionary()

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
    
    try:
        return THREAD_TO_EVENT_LOOP_REFERENCE[local_thread]
    except KeyError:
        pass
    
    for thread in list_threads():
        if isinstance(thread, EventThread):
            if thread.daemon:
                continue
            
            if thread.is_stopped():
                continue
            
            THREAD_TO_EVENT_LOOP_REFERENCE[local_thread] = thread
            return thread
    
    raise RuntimeError(f'No running event loop on {local_thread!r}.')
