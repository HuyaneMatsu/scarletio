import vampytest

from ..terminal_control_commands import COMMAND_DOWN, create_command_down


def _iter_options():
    yield -10, ''
    yield -1, ''
    yield 0, ''
    yield 1, COMMAND_DOWN
    yield 10, f'\u001b[{10}B'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__create_command_down(part):
    """
    Tests whether ``create_command_down`` works as intended.
    
    Parameters
    ----------
    amount : `str`
        The amount to move the cursor by.
    
    Returns
    -------
    output : `bool`
    """
    output = create_command_down(part)
    vampytest.assert_instance(output, str)
    return output
