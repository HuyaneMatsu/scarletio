import vampytest

from ..file_info import FileInfo

from ....highlight import ParseResult, get_highlight_parse_result


def _assert_fields_set(file_info):
    """
    Asserts whether the file info has all of its fields set.
    
    Parameters
    ----------
    file_info : ``FileInfo``
        The instance to check.
    """
    vampytest.assert_instance(file_info, FileInfo)
    vampytest.assert_instance(file_info.alive, bool)
    vampytest.assert_instance(file_info.console, bool)
    vampytest.assert_instance(file_info.content, str)
    vampytest.assert_instance(file_info.file_modification_time, float)
    vampytest.assert_instance(file_info.file_name, str)
    vampytest.assert_instance(file_info.file_size, int)
    vampytest.assert_instance(file_info.parse_result, ParseResult)


def test__FileInfo__new():
    """
    Tests whether ``FileInfo.__new__`` works as intended.
    """
    alive = True
    console = False
    file_modification_time = 100.0
    file_name = 'koishi.py'
    file_size = 69
    content = 'hello\nhell'
    parse_result = get_highlight_parse_result(content)
    
    file_info = FileInfo(file_name, file_size, file_modification_time, content, parse_result, alive, console)
    _assert_fields_set(file_info)
    
    vampytest.assert_eq(file_info.alive, alive)
    vampytest.assert_eq(file_info.console, console)
    vampytest.assert_eq(file_info.content, content)
    vampytest.assert_eq(file_info.file_modification_time, file_modification_time)
    vampytest.assert_eq(file_info.file_name, file_name)
    vampytest.assert_eq(file_info.file_size, file_size)
    vampytest.assert_eq(file_info.parse_result, parse_result)


def test__FileInfo__repr():
    """
    Tests whether ``FileInfo.__repr__`` works as intended.
    """
    alive = True
    console = False
    file_modification_time = 100.0
    file_name = 'koishi.py'
    file_size = 69
    content = 'hello\nhell'
    parse_result = get_highlight_parse_result(content)
    
    file_info = FileInfo(file_name, file_size, file_modification_time, content, parse_result, alive, console)
    
    output = repr(file_info)
    vampytest.assert_instance(output, str)


def _iter_options__get_token_index_range_for_line_index():
    yield -1, (0, 0)
    yield 0, (0, 2)
    yield 1, (2, 4)
    yield 2, (4, 5)
    yield 3, (5, 5)


@vampytest._(vampytest.call_from(_iter_options__get_token_index_range_for_line_index()).returning_last())
def test__File_info__get_token_index_range_for_line_index(index):
    """
    Tests whether ``FileInfo.get_token_index_range_for_line_index`` works as intended.
    
    Parameters
    ----------
    index : `int`
        The line's index.
    
    Returns
    -------
    output : `(int, int)`
    """
    content = 'hello\nhell\nhecatia'
    parse_result = get_highlight_parse_result(content)
    
    file_info = FileInfo('koishi.py', 0, 0.0, content, parse_result, False, False)
    
    output = file_info.get_token_index_range_for_line_index(index)
    vampytest.assert_instance(output, tuple)
    return output
