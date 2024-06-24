import vampytest

from ..display_state import _jump_horizontal
from ..terminal_control_commands import create_command_left, create_command_right


def _iter_options():
    yield (
        0,
        0,
        '',
    )
    
    yield (
        10,
        10,
        '',
    )
    
    yield (
        0,
        10,
        create_command_right(10),
    )
    
    yield (
        10,
        0,
        create_command_left(10),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__jump_horizontal(old_index, new_index):
    """
    Tests whether ``_jump_horizontal`` works as intended.
    
    Parameters
    ----------
    old_index : `int`
        Old line index to jump to.
    new_index : `int`
        New line index to jump to.
    
    Returns
    -------
    output : `str`
    """
    write_buffer = []
    _jump_horizontal(write_buffer, old_index, new_index)
    return ''.join(write_buffer)
