__all__ = ('debug_key',)

import sys, termios, tty
from os import get_blocking, set_blocking
from select import select

from ...tools.keys import KEY_NAMES


def input_once():
    """
    Inputs once from `sys.stdin`.
    
    Returns
    -------
    output : `str`
    """
    input_stream = sys.stdin
    
    input_stream_settings_original = termios.tcgetattr(input_stream)
    input_stream_blocking_original = get_blocking(input_stream.fileno())
    set_blocking(input_stream.fileno(), False)
    tty.setraw(input_stream)
    
    try:
        while True:
            read_file_descriptors, write_file_descriptors, exception_file_descriptors = \
                select([input_stream.fileno()], [], [])
            
            if not read_file_descriptors:
                continue
            
            try:
                content = input_stream.read()
            except (BlockingIOError, InterruptedError):
                continue
            
            if not content:
                continue
            
            return content
    finally:
        termios.tcsetattr(input_stream, termios.TCSADRAIN, input_stream_settings_original)
        set_blocking(input_stream.fileno(), input_stream_blocking_original)


def _escape_character(character):
    """
    Escapes the given character.
    
    Parameters
    ----------
    character : `str`
        The character to escape.
    
    Returns
    -------
    result : `str`
    """
    character_int = ord(character)
    if character_int >= 0x10000 or character_int < 0:
        prefix = '\\U'
        hexadecimal_length = 8
    
    elif character_int >= 0x100:
        prefix = '\\u'
        hexadecimal_length = 4
    
    else:
        prefix = '\\x'
        hexadecimal_length = 2
    
    result = [prefix]
    for index in reversed(range(hexadecimal_length)):
        result.append('0123456789abcdef'[(character_int >> (index << 2)) & 0x0f])
    
    return ''.join(result)


def _escape_string(content):
    """
    Escapes the given string.
    
    Returns
    -------
    escaped : `str`
    """
    return ''.join([_escape_character(character) for character in content])


def _determine_input_name(content):
    """
    Determines the input's content name if its a special character.
    
    Parameters
    ----------
    content : `str`
        Content to get its name of.
    
    Returns
    -------
    name : `str`
    """
    try:
        output = KEY_NAMES[content]
    except KeyError:
        if content.isprintable():
            return content
        
        return _escape_string(content)
    
    return output


def debug_key():
    """
    Prints debug information for a pressed key. Available only on linux.
    """
    if sys.platform != 'linux':
        sys.stdout.write('Linux only.\n')
        return
    
    sys.stdout.write('Please press a key on your keyboard.\n')
    name = _determine_input_name(input_once())
    sys.stdout.write(f'You pressed: {name!s}\n')
