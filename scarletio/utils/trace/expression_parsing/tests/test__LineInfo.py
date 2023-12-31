from os import stat_result as GetStatsResult

import vampytest

from ..cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE
from ..file_info import FileInfo
from ..line_info import LineInfo


def test__LineInfo__new():
    """
    Tests ``LineInfo.__new__`` works as intended.
    """
    file_modification_time = 12.6
    file_name = 'koishi.py'
    file_size = 56
    hit = True
    index = 2
    line = 'if ayaya:'
    
    line_info = LineInfo(file_name, file_size, file_modification_time, line, index, hit)
    
    vampytest.assert_instance(line_info, LineInfo)
    vampytest.assert_instance(line_info.file_modification_time, float)
    vampytest.assert_instance(line_info.file_name, str)
    vampytest.assert_instance(line_info.file_size, int)
    vampytest.assert_instance(line_info.hit, bool)
    vampytest.assert_instance(line_info.index, int)
    vampytest.assert_instance(line_info.line, str)
    
    vampytest.assert_eq(line_info.file_modification_time, file_modification_time)
    vampytest.assert_eq(line_info.file_name, file_name)
    vampytest.assert_eq(line_info.file_size, file_size)
    vampytest.assert_eq(line_info.hit, hit)
    vampytest.assert_eq(line_info.index, index)
    vampytest.assert_eq(line_info.line, line)


def test__LineInfo__repr():
    """
    Tests ``LineInfo.__new__`` works as intended.
    """
    file_modification_time = 12.6
    file_name = 'koishi.py'
    file_size = 56
    hit = True
    index = 2
    line = 'if ayaya:'
    
    line_info = LineInfo(file_name, file_size, file_modification_time, line, index, hit)
    output = repr(line_info)
    vampytest.assert_instance(output, str)


def _iter_options__is_up_to_date():
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], True, False),
        LineInfo('koishi.py', 100, 100.0, 'hell', 1, True),
        None,
        True,
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], True, False),
        LineInfo('koishi.py', 100, 50.0, 'hell', 1, True),
        None,
        False,
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], True, False),
        LineInfo('koishi.py', 50, 100.0, 'hell', 1, True),
        None,
        False,
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, [], False, False),
        LineInfo('koishi.py', 50, 50.0, 'hell', 1, True),
        None,
        True,
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, [], False, True),
        LineInfo('koishi.py', 50, 50.0, 'hell', 1, True),
        None,
        True,
    )
    yield (
        None,
        LineInfo('koishi.py', 100, 100.0, 'hell', 1, True),
        None,
        False,
    )
    yield (
        None,
        LineInfo('koishi.py', 100, 100.0, 'hell', 1, True),
        GetStatsResult([0, 0, 0, 0, 0, 0, 100, 0.0, 100.0, 0.0]),
        True,
    )
    yield (
        None,
        LineInfo('koishi.py', 100, 100.0, 'hell', 1, True),
        GetStatsResult([0, 0, 0, 0, 0, 0, 50, 0.0, 100.0, 0.0]),
        False,
    )
    yield (
        None,
        LineInfo('koishi.py', 100, 100.0, 'hell', 1, True),
        GetStatsResult([0, 0, 0, 0, 0, 0, 100, 0.0, 50.0, 0.0]),
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__is_up_to_date()).returning_last())
def test__LineInfo__is_up_to_date(file_info, line_info, return_stats):
    """
    Tests whether ``LineInfo.is_up_to_date`` works as intended.
    
    Parameters
    ----------
    file_info : `None | FileInfo`
        File info to use.
    line_info : ``LineInfo``
        Line info to use.
    return_stats : `None | GetStatsResult`
        Stats to return if requested.
    
    Returns
    -------
    output : `bool`
    """
    def get_stats_mock(file_name):
        nonlocal return_stats
        if return_stats is None:
            return GetStatsResult([0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0])
        
        return return_stats
    
    
    mocked = vampytest.mock_globals(type(line_info).is_up_to_date, get_stats = get_stats_mock)
    
    
    try:
        if (file_info is not None):
            FILE_INFO_CACHE[file_info.file_name] = file_info
        
        output = mocked(line_info)
        
        if (file_info is not None) and file_info.console:
            vampytest.assert_eq([*CONSOLE_INPUT_CACHE.items()], [(file_info.file_name, file_info)])
        
        vampytest.assert_instance(output, bool)
        return output
        
    finally:
        if (file_info is not None):
            try:
               del FILE_INFO_CACHE[file_info.file_name]
            except KeyError:
                pass
            
            try:
                del CONSOLE_INPUT_CACHE[file_info.file_name]
            except KeyError:
                pass


def _iter_options__update():
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], True, False),
        LineInfo('koishi.py', 100, 100.0, 'satori', 1, True),
        'hell',
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], False, False),
        LineInfo('koishi.py', 100, 100.0, 'satori', 1, True),
        'satori',
    )


@vampytest._(vampytest.call_from(_iter_options__update()).returning_last())
def test__LineInfo__update(file_info, line_info):
    """
    Tests whether ``LineInfo.update`` works as intended.
    
    Parameters
    ----------
    file_info : ``FileInfo``
        File info to use.
    line_info : ``LineInfo``
        Line info to use.
    
    Returns
    -------
    line : `bool`
    """
    try:
        FILE_INFO_CACHE[file_info.file_name] = file_info
        
        line_info.update()
        line = line_info.line
        vampytest.assert_instance(line, str)
        return line
        
    finally:
        try:
           del FILE_INFO_CACHE[file_info.file_name]
        except KeyError:
            pass


def _iter_options__get():
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], True, False),
        LineInfo('koishi.py', 100, 100.0, 'satori', 1, True),
        (True, 'satori'),
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hell'], False, False),
        LineInfo('koishi.py', 100, 100.0, 'satori', 1, True),
        (True, 'satori'),
    )
    yield (
        FileInfo('koishi.py', 100, 100.0, ['hello', 'hecatia'], True, False),
        LineInfo('koishi.py', 50, 50.0, 'satori', 1, True),
        (True, 'hecatia'),
    )


@vampytest._(vampytest.call_from(_iter_options__get()).returning_last())
def test__LineInfo__get(file_info, line_info):
    """
    Tests whether ``LineInfo.get`` works as intended.
    
    Parameters
    ----------
    file_info : ``FileInfo``
        File info to use.
    line_info : ``LineInfo``
        Line info to use.
    
    Returns
    -------
    line : `(bool, str)`
    """
    try:
        FILE_INFO_CACHE[file_info.file_name] = file_info
        
        output = line_info.get()
        vampytest.assert_instance(output, tuple)
        return output
        
    finally:
        try:
           del FILE_INFO_CACHE[file_info.file_name]
        except KeyError:
            pass
