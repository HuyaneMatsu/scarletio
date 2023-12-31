import vampytest

from ..parsing import (
    ACTION_TYPE_NONE, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
    ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE, ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE, _parse_forward_next_action
)


def _iter_options():
    line_0 = 'a = hello(there)'
    line_1 = 'hello))'
    line_2 = '+ \'there\' # nothing'
    line_3 = ')'
    
    yield line_0, 0, len(line_0), ACTION_TYPE_NONE, (10, ACTION_TYPE_PARENTHESES_OPEN_BRACKET)
    yield line_0, 10, len(line_0), ACTION_TYPE_PARENTHESES_OPEN_BRACKET, (16, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET)
    yield line_0, 16, len(line_0), ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, (16, ACTION_TYPE_NONE)
    
    yield line_1, 0, len(line_1), ACTION_TYPE_NONE, (6, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET)
    yield line_1, 6, len(line_1), ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, (7, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET)
    yield line_1, 7, len(line_1), ACTION_TYPE_PARENTHESES_CLOSE_BRACKET, (7, ACTION_TYPE_NONE)
    
    yield line_2, 0, len(line_2), ACTION_TYPE_NONE, (3, ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE)
    yield line_2, 3, len(line_2), ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE, (9, ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE)
    yield line_2, 9, len(line_2), ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE, (19, ACTION_TYPE_NONE)
    yield line_2, 0, 2, ACTION_TYPE_NONE, (2, ACTION_TYPE_NONE)
    
    yield line_3, 0, len(line_3), ACTION_TYPE_PARENTHESES_OPEN_BRACKET, (1, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_forward_next_action(line, index, length, source_action):
    """
    Tests whether ``_parse_forward_next_action`` works as intended.
    
    Parameters
    ----------
    line : `str`
        The line to parse from.
    index : `int`
        The index to start parsing at.
    length : `int`
        The index to parse till.
    source_action : `int`
        The previous action.
    
    Returns
    -------
    output : `(int, int)`
    """
    return _parse_forward_next_action(line, index, length, source_action)
