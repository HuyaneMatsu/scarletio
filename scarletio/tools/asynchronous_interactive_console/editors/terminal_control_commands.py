__all__ = ()

from ....utils import create_ansi_format_code


COMMAND_DOWN = '\n'
COMMAND_UP = '\u001b[F'
# COMMAND_START_LINE = '\u001b[1000D'
COMMAND_START_LINE = '\r'
COMMAND_FORMAT_RESET = create_ansi_format_code()


COMMAND_CLEAR_SCREEN_FROM_CURSOR = '\u001b[0J'
COMMAND_CLEAR_SCREEN_TILL_CURSOR = '\u001b[1J'
COMMAND_CLEAR_SCREEN_WHOLE = '\u001b[2J'

COMMAND_CLEAR_LINE_FROM_CURSOR = '\u001b[0K'
COMMAND_CLEAR_LINE_TILL_CURSOR = '\u001b[1K'
COMMAND_CLEAR_LINE_WHOLE = '\u001b[2K'


def is_command(part):
    """
    Returns whether the given part is an ansi command.
    Designed for general color commands and not for various.
    
    Parameters
    ----------
    part : `str`
        the part to check.
    
    Returns
    -------
    is_ansi_command : `bool`
    """
    return part.startswith('\u001b[')


def create_command_up(amount):
    """
    Creates a command that moves the cursor up.
    
    Parameters
    ----------
    amount : `str`
        The amount to move the cursor by.
    
    Returns
    -------
    command : `str`
    """
    if amount <= 0:
        return ''
    
    return f'\u001b[{amount}A'


def create_command_down(amount):
    """
    Creates a command that moves the cursor down.
    
    Parameters
    ----------
    position : `str`
        The amount to move the cursor by.
    
    Parameters
    ----------
    amount : `str`
        The amount to move the cursor by.
    """
    if amount <= 0:
        return ''
    
    if amount == 1:
        return COMMAND_DOWN
    
    return f'\u001b[{amount}B'


def create_command_right(amount):
    """
    Creates a command that moves the cursor right.
    
    Parameters
    ----------
    amount : `str`
        The amount to move the cursor by.
    
    Returns
    -------
    command : `str`
    """
    if amount <= 0:
        return ''
    
    return f'\u001b[{amount}C'


def create_command_left(amount):
    """
    Creates a command that moves the cursor left.
    
    Parameters
    ----------
    amount : `str`
        The amount to move the cursor by.
    
    Returns
    -------
    command : `str`
    """
    if amount <= 0:
        return ''
    
    return f'\u001b[{amount}D'
