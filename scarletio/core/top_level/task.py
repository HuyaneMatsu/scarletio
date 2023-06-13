__all__ = ('create_future', 'create_task', 'get_current_task', 'get_tasks')

from ..traps import Future, Task

from .event_loop import _get_event_loop_is_current_thread, get_event_loop


def create_future(loop = None):
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


def create_task(coroutine, loop = None):
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
    task = Task(loop, coroutine)
    if (not is_current_thread):
        loop.wake_up()
    
    return task



def get_current_task(loop = None):
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


def get_tasks(loop = None):
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
