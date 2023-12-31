import vampytest

from ..cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE
from ..console_input import add_console_input


def _iter_options__empty_input():
    yield None, 'ayaya'
    yield '', 'ayaya'
    yield 'ayaya', None
    yield 'ayaya', ''


@vampytest._(vampytest.call_from(_iter_options__empty_input()))
def test__add_console_input__empty_input(file_name, content):
    """
    tests whether ``add_console_input`` works as intended.
    
    Case: Empty input.
    
    Parameters
    ----------
    file_name : `None | str`
        File name to add the input as.
    content : `None | str`
        Input content to add.
    """
    add_console_input(file_name, content)
    
    vampytest.assert_false(CONSOLE_INPUT_CACHE)
    vampytest.assert_false(FILE_INFO_CACHE)


def test__add_console_input__actual_input():
    """
    tests whether ``add_console_input`` works as intended.
    
    Case: Actual input.
    """
    file_name = 'koishi.py'
    content = 'aya\nya'
    
    try:
        add_console_input(file_name, content)
        
        vampytest.assert_true(CONSOLE_INPUT_CACHE)
        vampytest.assert_true(FILE_INFO_CACHE)
        
        file_info = next(iter(CONSOLE_INPUT_CACHE.values()))
        vampytest.assert_eq(file_info.file_name, file_name)
        vampytest.assert_eq(file_info.lines, content.splitlines())
        
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()
