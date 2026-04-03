import vampytest

from ..future_states import (
    FUTURE_STATE_CANCELLED, FUTURE_STATE_CANCELLING_SELF, FUTURE_STATE_RESULT_RAISE,
    FUTURE_STATE_RESULT_RAISE_RETRIEVED, FUTURE_STATE_RESULT_RETURN, FUTURE_STATE_SILENCED, get_future_state_name,
    render_future_state_name_into
)


def _iter_options():
    yield 0, 'pending'
    yield FUTURE_STATE_RESULT_RETURN, 'result~return'
    yield FUTURE_STATE_CANCELLING_SELF, 'pending, cancelling~self'
    yield FUTURE_STATE_RESULT_RETURN | FUTURE_STATE_CANCELLING_SELF, 'result~return'
    yield FUTURE_STATE_RESULT_RAISE, 'result~raise'
    yield FUTURE_STATE_RESULT_RAISE | FUTURE_STATE_RESULT_RAISE_RETRIEVED, 'result~raise~retrieved'
    yield FUTURE_STATE_RESULT_RETURN | FUTURE_STATE_SILENCED, 'result~return, silenced'
    yield FUTURE_STATE_CANCELLING_SELF | FUTURE_STATE_SILENCED, 'pending, cancelling~self, silenced'
    yield FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE, 'cancelled'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_future_state_name(state):
    """
    Tests whether ``get_future_state_name`` works as intended.
    
    Parameters
    ----------
    state : `int`
        The state to get its name of.
    
    Returns
    -------
    output : `str`
    """
    return get_future_state_name(state)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__render_future_state_name_into(state):
    """
    Tests whether ``render_future_state_name_into`` works as intended.
    
    Parameters
    ----------
    state : `int`
        The state render its name of.
    
    Returns
    -------
    output : `str`
    """
    return ''.join(render_future_state_name_into([], state))
