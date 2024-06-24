import vampytest

from ..display_state import _get_line_cursor_index


def _iter_options():
    yield 80, 0, 8, 8
    yield 80, 1, 8, 9
    yield 80, 80, 8, 88
    yield 80, 81, 8, 9


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_line_cursor_index(content_width, cursor_index, prefix_length):
    """
    Tests whether ``_get_line_cursor_index`` works as intended.
    
    Parameters
    ----------
    content_width : `int`
        The content field's width.
    cursor_index : `int`
        The cursors index on the current line.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `int`
    """
    output = _get_line_cursor_index(content_width, cursor_index, prefix_length)
    
    vampytest.assert_instance(output, int)
    
    return output
