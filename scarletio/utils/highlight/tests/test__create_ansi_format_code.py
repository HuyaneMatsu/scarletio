import vampytest

from ..ansi import AnsiTextDecoration, create_ansi_format_code


def _iter_options():
    text_decoration = AnsiTextDecoration.bold
    color_0 = (100, 136, 156)
    color_1 = (50, 40, 255)
    
    
    yield None, None, None, '\x1b[0m'
    yield None, None, color_1, '\x1b[38;2;50;40;255m'
    yield None, color_0, None, '\x1b[48;2;100;136;156m'
    yield None, color_0, color_1, '\x1b[48;2;100;136;156;38;2;50;40;255m'
    yield text_decoration, None, None, '\x1b[1m'
    yield text_decoration, None, color_1, '\x1b[1;38;2;50;40;255m'
    yield text_decoration, color_0, None, '\x1b[1;48;2;100;136;156m'
    yield text_decoration, color_0, color_1, '\x1b[1;48;2;100;136;156;38;2;50;40;255m'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__create_ansi_format_code(text_decoration, background_color, foreground_color):
    output = create_ansi_format_code(text_decoration, background_color, foreground_color)
    vampytest.assert_instance(output, str)
    return output
