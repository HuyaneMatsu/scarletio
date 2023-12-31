import vampytest

from ..parsing import (
    ACTION_TYPE_PARENTHESES_CLOSE_BOX, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
    ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, _is_syntax_valid
)


def _iter_options():
    yield (
        [],
        True,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
        ],
        True,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
        ],
        True,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        True,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        True,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
        ],
        False,
    )
    yield (
        [
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
        ],
        True,
    )
    yield (
        [
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
        ],
        False,
    )
    yield (
        [
            ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE,
        ],
        True,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_syntax_valid(action_stack):
    """
    Tests whether ``_is_syntax_valid`` works as intended.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to read the syntax from.
    
    Returns
    -------
    output : `bool`
    """
    return _is_syntax_valid(action_stack)
