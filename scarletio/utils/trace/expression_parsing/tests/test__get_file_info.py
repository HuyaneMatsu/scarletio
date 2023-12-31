from os import stat_result as GetStatsResult

import vampytest

from ..cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE
from ..console_input import add_console_input
from ..line_cache_session import LineCacheSession
from ..file_info import FileInfo, get_file_info


def test__get_file_info__in_cache():
    """
    tests whether ``get_file_info`` works as intended.
    
    Case: File in cache.
    """
    try:
        with LineCacheSession() as cache:
            add_console_input('koishi.py', 'aya\nya')
            
            output = get_file_info('koishi.py')
            vampytest.assert_instance(output, FileInfo)
            vampytest.assert_eq(output.file_name, 'koishi.py')
            vampytest.assert_eq(output.lines, ['aya', 'ya'])
            
            vampytest.assert_eq(len(FILE_INFO_CACHE), 1)
            vampytest.assert_eq(len(cache.memorized_file_infos), 1)
        
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()


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


def test__get_file_info__new_success():
    """
    tests whether ``get_file_info`` works as intended.
    
    Case: Create new successfully.
    """
    try:
        with LineCacheSession() as cache:
            mocked = vampytest.mock_globals(
                get_file_info,
                open = OpenMock,
                get_stats = get_stats_mock,
            )
            
            output = mocked('koishi.py')
            
            vampytest.assert_instance(output, FileInfo)
            vampytest.assert_eq(output.file_name, 'koishi.py')
            vampytest.assert_eq(output.lines, ['aya', 'ya'])
            
            vampytest.assert_eq(len(FILE_INFO_CACHE), 1)
            vampytest.assert_eq(len(cache.memorized_file_infos), 1)
        
    finally:
        CONSOLE_INPUT_CACHE.clear()
        FILE_INFO_CACHE.clear()
