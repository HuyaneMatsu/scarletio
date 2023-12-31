import vampytest

from ..parsing import (
    ACTION_TYPE_NONE, ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE,
    _try_parse_triple_quote_from_behind
)


def _iter_options():
    line_0 = 'hey = \'\'\''
    line_1 = 'hey = """'
    line_2 = ''
    line_3 = 'hello'
    line_4 = 'hey = \\\'\'\''
    
    yield line_0, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, (6, ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE)
    yield line_1, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, (0, ACTION_TYPE_NONE)
    yield line_0, ACTION_TYPE_NONE, (9, ACTION_TYPE_NONE)
    yield line_1, ACTION_TYPE_NONE, (9, ACTION_TYPE_NONE)
    yield line_2, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, (0, ACTION_TYPE_NONE)
    yield line_2, ACTION_TYPE_NONE, (0, ACTION_TYPE_NONE)
    yield line_3, ACTION_TYPE_NONE, (5, ACTION_TYPE_NONE)
    yield line_3, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, (0, ACTION_TYPE_NONE)
    yield line_4, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, (0, ACTION_TYPE_NONE)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__try_parse_triple_quote_from_behind(line, source_action):
    """
    Tests whether ``_try_parse_triple_quote_from_behind`` works as intended.
    
    Parameters
    ----------
    line : `str`
        Line to parse.
    source_action : `int`
        The last action executed.
    
    Returns
    -------
    output : `(int, int)`
    """
    return _try_parse_triple_quote_from_behind(line, source_action)
