from os import terminal_size as TerminalSize

import vampytest

from ..display_state import CONTINUOUS_LINE_POSTFIX, get_new_content_width


def _iter_options():
    prefix_length = 7
    continuous_line_postfix_length = len(CONTINUOUS_LINE_POSTFIX)
    
    yield prefix_length, 50, 50 - prefix_length - continuous_line_postfix_length
    yield prefix_length, 100, 100 - prefix_length - continuous_line_postfix_length  


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_new_content_width(prefix_length, terminal_width):
    """
    Tests whether ``get_new_content_width`` works as intended.
    
    Parameters
    ----------
    prefix_length : `int`
        Prefix length used for calculations of content width.
    terminal_width : `int`
        The terminal's width to return.
    
    Returns
    -------
    output : `int`
    """
    def get_terminal_size_mock():
        nonlocal terminal_width
        return TerminalSize((terminal_width, 0))
    
    mocked = vampytest.mock_globals(
        get_new_content_width,
        get_terminal_size = get_terminal_size_mock,
    )
    
    
    output = mocked(prefix_length)
    
    vampytest.assert_instance(output, int)
    
    return output
