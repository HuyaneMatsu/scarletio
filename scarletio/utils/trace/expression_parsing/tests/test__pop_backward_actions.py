import vampytest

from ..parsing import (
    ACTION_TYPE_PARENTHESES_CLOSE_BOX, ACTION_TYPE_PARENTHESES_CLOSE_CURVY, ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
    ACTION_TYPE_PARENTHESES_OPEN_CURVY, _pop_backward_actions
)


def _iter_options():
    yield (
        [],
        [],
    )

    yield (
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_CURVY,
        ],
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_CURVY,
        ],
    )
    
    yield (
        [
            ACTION_TYPE_PARENTHESES_CLOSE_CURVY,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_CURVY,
        ],
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_CURVY,
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__pop_backward_actions(action_stack):
    """
    Tests whether ``_pop_backward_actions`` works as intended.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to work on.
    
    Returns
    -------
    
    """
    action_stack = action_stack.copy()
    _pop_backward_actions(action_stack)
    return action_stack
