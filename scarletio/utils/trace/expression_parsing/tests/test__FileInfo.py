import vampytest

from ..file_info import FileInfo


def test__FileInfo__new():
    """
    Tests whether ``FileInfo.__new__`` works as intended.
    """
    alive = True
    console = False
    file_modification_time = 100.0
    file_name = 'koishi.py'
    file_size = 69
    lines = ['hello', 'hell']
    
    file_info = FileInfo(file_name, file_size, file_modification_time, lines, alive, console)
    
    vampytest.assert_instance(file_info, FileInfo)
    vampytest.assert_instance(file_info.alive, bool)
    vampytest.assert_instance(file_info.console, bool)
    vampytest.assert_instance(file_info.file_modification_time, float)
    vampytest.assert_instance(file_info.file_name, str)
    vampytest.assert_instance(file_info.file_size, int)
    vampytest.assert_instance(file_info.lines, list)
    
    vampytest.assert_eq(file_info.alive, alive)
    vampytest.assert_eq(file_info.console, console)
    vampytest.assert_eq(file_info.file_modification_time, file_modification_time)
    vampytest.assert_eq(file_info.file_name, file_name)
    vampytest.assert_eq(file_info.file_size, file_size)
    vampytest.assert_eq(file_info.lines, lines)


def test__FileInfo__repr():
    """
    Tests whether ``FileInfo.__repr__`` works as intended.
    """
    alive = True
    console = False
    file_modification_time = 100.0
    file_name = 'koishi.py'
    file_size = 69
    lines = ['hello', 'hell']
    
    file_info = FileInfo(file_name, file_size, file_modification_time, lines, alive, console)
    
    output = repr(file_info)
    vampytest.assert_instance(output, str)


def _iter_options__get_line():
    yield -1, (False, '')
    yield 0, (True, 'hello')
    yield 1, (True, 'hell')
    yield 2, (True, 'hecatia')
    yield 3, (False, '')


@vampytest._(vampytest.call_from(_iter_options__get_line()).returning_last())
def test__File_info__get_line(index):
    """
    Tests whether ``FileInfo.get_line`` works as intended.
    
    Parameters
    ----------
    index : `int`
        The line's index.
    
    Returns
    -------
    output : `(bool, str)`
    """
    file_info = FileInfo('koishi.py', 0, 0.0, ['hello', 'hell', 'hecatia'], False, False)
    output = file_info.get_line(index)
    vampytest.assert_instance(output, tuple)
    return output
