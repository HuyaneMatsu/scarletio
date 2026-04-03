import vampytest

from ..display_state import _get_line_line_count_same_or_increased


def _iter_options():
    yield 0, 10, 1
    yield 1, 10, 1
    yield 10, 10, 1
    yield 11, 10, 2


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_line_line_count_same_or_increased(line_length, content_width):
    """
    Tests whether ``_get_line_line_count_same_or_increased`` works as intended.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    
    Returns
    -------
    output : `int`
    """
    output = _get_line_line_count_same_or_increased(line_length, content_width)
    
    vampytest.assert_instance(output, int)
    
    return output
