import vampytest

from ..display_state import _get_line_line_count


def _iter_options():
    yield 0, 80, 80, 4, 1
    yield 2, 80, 80, 4, 1
    yield 100, 100, 50, 7, 2
    yield 200, 100, 50, 7, 6
    yield 180, 100, 70, 7, 4
    yield 199, 100, 70, 7, 4
    yield 198, 100, 70, 7, 4
    yield 150, 100, 70, 7, 3
    yield 170, 100, 70, 7, 3


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_line_line_count(line_length, content_width, new_content_width, prefix_length):
    """
    Tests whether ``_get_line_line_count`` works as intended.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `int`
    """
    output = _get_line_line_count(line_length, content_width, new_content_width, prefix_length)
    
    vampytest.assert_instance(output, int)
    
    return output
