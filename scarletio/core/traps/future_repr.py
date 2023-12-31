__all__ = ()

from reprlib import repr as short_repr

from ...utils import include
from ...utils.trace.formatters import format_callback, format_coroutine

from ..exceptions import CancelledError

from .future_states import FUTURE_STATE_CANCELLED, FUTURE_STATE_RESULT_RAISE, FUTURE_STATE_RESULT_RETURN
from .future_states import render_future_state_name_into


# Defines helpers for future __repr__ methods.

Task = include('Task')


EXCEPTION_REPR_LENGTH_MAX = 80


def get_exception_short_representation(exception):
    """
    Gets the exception's representation. If it is too long builds a shorter one instead.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to get representation of.
    
    Returns
    -------
    exception_representation : `str`
    """
    exception_representation = repr(exception)
    if (len(exception_representation) > EXCEPTION_REPR_LENGTH_MAX) or ('\n' in exception_representation):
        exception_representation = f'<{exception.__class__.__name__} ...>'
    
    return exception_representation


def render_callbacks_into(into, field_added, callbacks):
    """
    Renders future callbacks' representation into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    callbacks : `None | list<callable>`
        The callbacks to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    if callbacks is None:
        limit = 0
    else:
        limit = len(callbacks)
    
    if limit:
        if field_added:
            into.append(',')
        else:
            field_added = True
        
        into.append(' callbacks = [')
        index = 0
        while True:
            callback = callbacks[index]
            into.append(format_callback(callback))
            index += 1
            if index == limit:
                break
            
            into.append(', ')
            continue
        
        into.append(']')
    
    return into, field_added


def render_state_into(into, field_added, state):
    """
    Renders future state into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    state : `int`
        The state of the future stored as a bitwise flags.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    if field_added:
        into.append(',')
    else:
        field_added = True
    
    into.append(' state = ')
    into = render_future_state_name_into(into, state)
        
    return into, field_added


def render_result_into(into, field_added, state, result):
    """
    Renders future result into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    state : `int`
        The state of the future stored as a bitwise flags.
    result : `object`
        Future result.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    # Use goto
    while True:
        if (state & FUTURE_STATE_RESULT_RETURN):
            field_name = 'result'
            field_repr_getter = short_repr
            break
        
        elif (state & FUTURE_STATE_CANCELLED):
            if (result is not None) and ((not isinstance(result, CancelledError)) or result.args):
                field_name = 'cancellation_exception'
                field_repr_getter = get_exception_short_representation
                break
        
        elif (state & FUTURE_STATE_RESULT_RAISE):
            field_name = 'exception'
            field_repr_getter = get_exception_short_representation
            break
        
        field_name = None
        field_repr_getter = None
        break
    
    if (field_name is not None):
        if field_added:
            into.append(',')
        else:
            field_added = True
        
        into.append(' ')
        into.append(field_name)
        into.append(' = ')
        into.append(field_repr_getter(result))
    
    return into, field_added


def render_coroutine_into(into, field_added, coroutine):
    """
    Renders task coroutine into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    coroutine : `CoroutineType`, `GeneratorType`
        The coroutine to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    if field_added:
        into.append(',')
    else:
        field_added = True
    
    into.append(' coroutine = ')
    into.append(format_coroutine(coroutine))
    return into, field_added


def render_waits_into(into, field_added, future):
    """
    Renders waiter future into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    future : `None`, ``Future``
        The waited future.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    if (future is not None):
        if field_added:
            into.append(',')
        else:
            field_added = True
        
        into.append(' waits = ')
        
        if isinstance(future, Task):
            into.append('<')
            into.append(future.__class__.__name__)
            into.append(' coroutine = ')
            into.append(future.qualname)
            into.append(', ...>')
        
        else:
            into.append(repr(future))
    
    return into, field_added


def render_future_into(into, field_added, future):
    """
    Renders wrapped future into the given container.
    
    Parameters
    ----------
    into : `list<str>`
        The container to render into.
    field_added : `bool`
        Whether any fields were added already.
    future : ``Future``
        The wrapped future.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    if field_added:
        into.append(',')
    else:
        field_added = True
    
    into.append(' future = <')
    into.append(future.__class__.__name__)
    into.append(' ...>')
    
    return into, field_added
