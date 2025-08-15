import vampytest

from ..ansi import ANSITextDecoration, create_ansi_format_code, iter_produce_ansi_format_code


def _iter_options():
    text_decoration = ANSITextDecoration.bold
    color_0 = (100, 136, 156)
    color_1 = (50, 40, 255)
    
    
    yield False, None, None, None, ''
    yield False, None, None, color_1, '\x1b[38;2;50;40;255m'
    yield False, None, color_0, None, '\x1b[48;2;100;136;156m'
    yield False, None, color_0, color_1, '\x1b[48;2;100;136;156;38;2;50;40;255m'
    yield False, text_decoration, None, None, '\x1b[1m'
    yield False, text_decoration, None, color_1, '\x1b[1;38;2;50;40;255m'
    yield False, text_decoration, color_0, None, '\x1b[1;48;2;100;136;156m'
    yield False, text_decoration, color_0, color_1, '\x1b[1;48;2;100;136;156;38;2;50;40;255m'
    
    yield True, None, None, None, '\x1b[0m'
    yield True, None, None, color_1, '\x1b[0;38;2;50;40;255m'
    yield True, None, color_0, None, '\x1b[0;48;2;100;136;156m'
    yield True, None, color_0, color_1, '\x1b[0;48;2;100;136;156;38;2;50;40;255m'
    yield True, text_decoration, None, None, '\x1b[0;1m'
    yield True, text_decoration, None, color_1, '\x1b[0;1;38;2;50;40;255m'
    yield True, text_decoration, color_0, None, '\x1b[0;1;48;2;100;136;156m'
    yield True, text_decoration, color_0, color_1, '\x1b[0;1;48;2;100;136;156;38;2;50;40;255m'
    

@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__create_ansi_format_code(reset, text_decoration, background_color, foreground_color):
    """
    Tests whether ``create_ansi_format_code`` works as intended.
    
    Parameters
    ----------
    reset : `bool` = `False`, Optional
        Whether to reset the previous formatting.
    
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    
    background_color : `None | (int, int, int)` = `None`, Optional
        background color.
    
    foreground_color : `None | (int, int, int)` = `None`, Optional
        Foreground color.
    
    Returns
    -------
    output : `str`
    """
    output = create_ansi_format_code(reset, text_decoration, background_color, foreground_color)
    vampytest.assert_instance(output, str)
    return output


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_produce_ansi_format_code(reset, text_decoration, background_color, foreground_color):
    """
    Tests whether ``iter_produce_ansi_format_code`` works as intended.
    
    Parameters
    ----------
    reset : `bool` = `False`, Optional
        Whether to reset the previous formatting.
    
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    
    background_color : `None | (int, int, int)` = `None`, Optional
        background color.
    
    foreground_color : `None | (int, int, int)` = `None`, Optional
        Foreground color.
    
    Returns
    -------
    output : `str`
    """
    elements = [*iter_produce_ansi_format_code(reset, text_decoration, background_color, foreground_color)]
    
    for element in elements:
        vampytest.assert_instance(element, str)
    
    return ''.join(elements)
