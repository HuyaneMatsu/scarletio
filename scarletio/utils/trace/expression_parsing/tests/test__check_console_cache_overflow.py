import vampytest

from ..cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE
from ..console_input import add_console_input, check_console_cache_overflow


def test__check_console_cache_overflow__under():
    """
    Tests whether ``check_console_cache_overflow`` works as intended.
    
    Case: Within limit.
    """
    try:
        add_console_input('koishi.py', 'aya\nya')
        add_console_input('satori.py', 'aya\nnya')
        
        length_before = len(CONSOLE_INPUT_CACHE)
        
        check_console_cache_overflow()
        
        length_after = len(CONSOLE_INPUT_CACHE)
        vampytest.assert_eq(length_before, length_after)
    
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()


def test__check_console_cache_overflow__over():
    """
    Tests whether ``check_console_cache_overflow`` works as intended.
    
    Case: Out of limit.
    """
    try:
        add_console_input('koishi.py', 'aya\nya')
        add_console_input('satori.py', 'aya\nnya')
        
        length_before = len(CONSOLE_INPUT_CACHE)
        
        mocked = vampytest.mock_globals(check_console_cache_overflow, CONSOLE_INPUT_MAX_SIZE = 10)
        mocked()
        
        length_after = len(CONSOLE_INPUT_CACHE)
        vampytest.assert_ne(length_before, length_after)
        
        vampytest.assert_in('satori.py', CONSOLE_INPUT_CACHE.keys())
        vampytest.assert_not_in('koishi.py', CONSOLE_INPUT_CACHE.keys())
    
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()
