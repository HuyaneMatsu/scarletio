from os import stat_result as GetStatsResult

import vampytest

from ..cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE, LINE_INFO_CACHE
from ..console_input import add_console_input
from ..line_cache_session import LineCacheSession
from ..line_info import get_file_line


def test__get_file_line__in_cache():
    """
    tests whether ``get_file_line`` works as intended.
    
    Case: File in cache.
    """
    CONSOLE_INPUT_CACHE.clear()
    FILE_INFO_CACHE.clear()
    LINE_INFO_CACHE.clear()
    
    try:
        with LineCacheSession() as cache:
            add_console_input('koishi.py', 'aya\nya')
            
            output = get_file_line('koishi.py', 1)
            vampytest.assert_instance(output, tuple)
            vampytest.assert_eq(output, (True, 'ya'))
            
            vampytest.assert_eq(len(FILE_INFO_CACHE), 1)
            vampytest.assert_eq(len(LINE_INFO_CACHE), 1)
        
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()
        LINE_INFO_CACHE.clear()


class OpenMock:
    def __new__(cls, file_name, mode):
        self = object.__new__(cls)
        self.file_name = file_name
        self.mode = mode
        return self
    
    
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False
    
    def read(self):
        return 'aya\nya'


def get_stats_mock(file_name):
    return GetStatsResult([0, 0, 0, 0, 0, 0, 100, 0.0, 100.0, 0.0])


def test__get_file_line__new_success():
    """
    tests whether ``get_file_line`` works as intended.
    
    Case: Create new successfully.
    """
    CONSOLE_INPUT_CACHE.clear()
    FILE_INFO_CACHE.clear()
    LINE_INFO_CACHE.clear()

    try:
        with LineCacheSession() as cache:
            mocked = vampytest.mock_globals(
                get_file_line,
                2,
                open = OpenMock,
                get_stats = get_stats_mock,
            )
            
            output = mocked('koishi.py', 1)
            
            vampytest.assert_instance(output, tuple)
            vampytest.assert_eq(output, (True, 'ya'))
            
            vampytest.assert_eq(len(FILE_INFO_CACHE), 1)
            vampytest.assert_eq(len(LINE_INFO_CACHE), 1)
        
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()
        LINE_INFO_CACHE.clear()
