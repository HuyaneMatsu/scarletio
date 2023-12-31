import vampytest

from ..parsing import (
    ACTION_BACKWARDS, ACTION_FORWARD, ACTION_TYPE_LINE_ESCAPE, ACTION_TYPE_NONE, ACTION_TYPE_PARENTHESES_CLOSE_BOX,
    ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, ACTION_TYPE_PARENTHESES_CLOSE_CURVY, ACTION_TYPE_PARENTHESES_OPEN_BOX,
    ACTION_TYPE_PARENTHESES_OPEN_BRACKET, ACTION_TYPE_PARENTHESES_OPEN_CURVY, ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE,
    ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE, ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE, ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
    _merge_actions
)


def _iter_options():
    yield (
        'empty',
        [],
        [],
    )
    
    yield (
        'line escape in middle',
        [
            ACTION_TYPE_LINE_ESCAPE,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
        ],
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
        ],
    )
    
    yield (
        'line escape at end',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_LINE_ESCAPE,
        ],
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_LINE_ESCAPE,
        ],
    )
    
    yield (
        'only ignorable',
        [
            ACTION_TYPE_NONE,
            ACTION_FORWARD,
            ACTION_BACKWARDS,
        ],
        [],
    )
    
    # parentheses
    yield (
        'parentheses : open -> close | bracket',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        [],
    )
    
    yield (
        'parentheses : open -> close | box',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BOX,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
        ],
        [],
    )
    
    yield (
        'parentheses : open -> close | curvy',
        [
            ACTION_TYPE_PARENTHESES_OPEN_CURVY,
            ACTION_TYPE_PARENTHESES_CLOSE_CURVY,
        ],
        [],
    )
    
    yield (
        'parentheses : open -> close | open -> close',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        [],
    )
    yield (
        'parentheses : nested same',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        [],
    )
    
    yield (
        'parentheses : nested different',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_OPEN_BOX,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        [],
    )
    
    yield (
        'parentheses : nested invalid',
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
            ACTION_TYPE_PARENTHESES_OPEN_BOX,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
        [
            ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
            ACTION_TYPE_PARENTHESES_CLOSE_BOX,
            ACTION_TYPE_PARENTHESES_OPEN_BOX,
            ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
        ],
    )

    
    # strings
    yield (
        'string : same type of 2',
        [
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
            ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE,
        ],
        [],
    )
    
    # mixed
    yield (
        'string : mixed; different before',
        [
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
            ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE,
            ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE,
        ],
        [
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
        ],
    )
    
    yield (
        'string : mixed; different after',
        [
            ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE,
            ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE,
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
        ],
        [
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
        ],
    )
    
    yield (
        'string : double after',
        [
            ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE,
            ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE,
            ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
            ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE,
        ],
        [],
    )



@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__merge_actions(case_name, action_stack):
    """
    Tests whether ``_merge_actions`` works as intended.
    
    Parameters
    ----------
    case_name : `str`
        The case's name. For debugging only.
    action_stack : `list<int>`
        Stack of actions to merge.
    
    Returns
    -------
    output : `list<int>`
    """
    action_stack = action_stack.copy()
    _merge_actions(action_stack)
    return action_stack
