import vampytest

from .....utils.highlight import DEFAULT_ANSI_HIGHLIGHTER, iter_split_ansi_format_codes

from ..display_state import iter_highlighted_buffer_parts

def _iter_options():
    yield ['def miau:', '    pass'], None, ('def miau:\n    pass', False)
    yield ['def miau:', '    pass'], DEFAULT_ANSI_HIGHLIGHTER, ('def miau:\n    pass', True)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_highlighted_buffer_parts(buffer, highlighter):
    """
    Tests whether ``iter_highlighted_buffer_parts`` works as intended.
    
    Parameters
    ----------
    buffer : `list` of `str`
        Line buffer.
    highlighter : ``None | HighlightFormatterContext``
        The highlighter to use.
    
    Returns
    -------
    output : `str`
    contains_highlight : `bool`
    """
    output = [*iter_highlighted_buffer_parts(buffer, highlighter)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    
    return (
        ''.join([item[1] for item in split if not item[0]]),
        any(item[0] for item in split),
    )
