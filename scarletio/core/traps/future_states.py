__all__ = ()

from ...utils import export


FUTURE_STATE_RESULT_RETURN = 1 << 0
FUTURE_STATE_RESULT_RAISE = 1 << 1
FUTURE_STATE_RESULT_RAISE_RETRIEVED = 1 << 2

FUTURE_STATE_CANCELLING_SELF = 1 << 3
FUTURE_STATE_CANCELLED = 1 << 4

FUTURE_STATE_DESTROYED = 1 << 5
FUTURE_STATE_SILENCED = 1 << 6


FUTURE_STATE_MASK_RESULT = (
    FUTURE_STATE_RESULT_RETURN |
    FUTURE_STATE_RESULT_RAISE
)

FUTURE_STATE_MASK_DONE = (
    FUTURE_STATE_RESULT_RETURN |
    FUTURE_STATE_RESULT_RAISE |
    FUTURE_STATE_CANCELLED |
    FUTURE_STATE_DESTROYED
)

FUTURE_STATE_MASK_SILENCED = (
    FUTURE_STATE_RESULT_RETURN |
    FUTURE_STATE_RESULT_RAISE_RETRIEVED |
    FUTURE_STATE_CANCELLED |
    FUTURE_STATE_DESTROYED |
    FUTURE_STATE_SILENCED
)


DONE_MASK_AND_NAME_PAIRS = (
    (FUTURE_STATE_CANCELLED, 'cancelled'),
    (FUTURE_STATE_RESULT_RETURN, 'result~return'),
    (FUTURE_STATE_RESULT_RAISE_RETRIEVED, 'result~raise~retrieved'),
    (FUTURE_STATE_RESULT_RAISE, 'result~raise'),
    (FUTURE_STATE_DESTROYED, 'destroyed'),
)


@export
def get_future_state_name(state):
    """
    Gets the future's state's name.
    
    A future can have multiple states at once. They are separated with a comma.
    
    Parameters
    ----------
    state : `int`
        Future state flags.
    
    Returns
    -------
    state_name : `str`
    """
    return ''.join(render_future_state_name_into([], state))


def _add_first_state_name_from(into, field_added, state, mask_name_pairs):
    """
    Adds the first state name of the given ones that matches.
    
    Parameters
    ----------
    into : `list<str>`
        List to render the state into.
    field_added : `bool`
        Whether there were a field added already.
    state : `int`
        Future state flags.
    mask_name_pairs : `tuple<(int, str)>
        Mask and name pairs.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    for mask, name in mask_name_pairs:
        if state & mask:
            _add_state_name(into, field_added, name)
            field_added = True
            break
    
    return into, field_added


def _add_state_name(into, field_added, name):
    """
    Adds a single state name.
    
    Parameters
    ----------
    into : `list<str>`
        List to render the state into.
    field_added : `bool`
        Whether there were a field added already.
    name : `str`
        the state's name.

    Returns
    -------
    into : `list<str>`
    """
    if field_added:
        into.append(', ')
    into.append(name)
    return into


def render_future_state_name_into(into, state):
    """
    Renders the future's state into the given container.
    
    A future can have multiple states at once. They are separated with a comma.
    
    Parameters
    ----------
    into : `list<str>`
        List to render the state into.
    state : `int`
        Future state flags.
    
    Returns
    -------
    into : `list<str>`
        List to render the state into.
    """
    field_added = False
    
    if state & FUTURE_STATE_MASK_DONE:
        into, field_added = _add_first_state_name_from(into, field_added, state, DONE_MASK_AND_NAME_PAIRS)
    else:
        into = _add_state_name(into, field_added, 'pending')
        field_added = True
        
        if state & FUTURE_STATE_CANCELLING_SELF and not (state & FUTURE_STATE_CANCELLED):
            into = _add_state_name(into, field_added, 'cancelling~self')
            field_added = True
    
    if state & FUTURE_STATE_SILENCED:
        into = _add_state_name(into, field_added, 'silenced')
        
    return into
