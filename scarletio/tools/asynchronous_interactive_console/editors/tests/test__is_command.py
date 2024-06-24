import vampytest

from .....utils import create_ansi_format_code

from ..terminal_control_commands import is_command


def _iter_options():
    yield create_ansi_format_code(), True
    yield create_ansi_format_code(background_color = (100, 100, 100)), True
    yield 'miau', False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_command(part):
    """
    Tests whether ``is_command`` works as intended.
    
    Parameters
    ----------
    part : `str`
        the part to check.
    
    Returns
    -------
    output : `bool`
    """
    output = is_command(part)
    vampytest.assert_instance(output, bool)
    return output
