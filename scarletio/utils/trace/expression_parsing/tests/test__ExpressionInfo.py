import vampytest

from ....highlight import get_highlight_parse_result

from ..expression_info import ExpressionInfo
from ..expression_key import ExpressionKey
from ..file_info import FileInfo


def _assert_fields_set(expression_info):
    """
    Asserts whether every fields are set of the given expression info.
    
    Parameters
    ----------
    expression_info : ``ExpressionInfo``
        The expression info to test.
    """
    vampytest.assert_instance(expression_info, ExpressionInfo)
    vampytest.assert_instance(expression_info.expression_character_end_index, int)
    vampytest.assert_instance(expression_info.expression_character_start_index, int)
    vampytest.assert_instance(expression_info.expression_line_end_index, int)
    vampytest.assert_instance(expression_info.expression_line_start_index, int)
    vampytest.assert_instance(expression_info.expression_token_end_index, int)
    vampytest.assert_instance(expression_info.expression_token_start_index, int)
    vampytest.assert_instance(expression_info.file_info, FileInfo)
    vampytest.assert_instance(expression_info.key, ExpressionKey)
    vampytest.assert_instance(expression_info.line, str)
    vampytest.assert_instance(expression_info.removed_indentation_characters, int)


def test__ExpressionInfo__new():
    """
    Tests whether ``ExpressionInfo.__new__`` works as intended.
    """
    key = ExpressionKey('orin.py', 1, 'koishi', 0)
    content = 'hello\nhell\nhecatia'
    parse_result = get_highlight_parse_result(content)
    removed_indentation_characters = 0
    line = 'hell'
    
    file_info = FileInfo('orin.py', 0, 0.0, content, parse_result, False, False)
    
    expression_line_start_index = 1
    expression_line_end_index = 2
    expression_character_start_index = 4
    expression_character_end_index = 5
    expression_token_start_index = 3
    expression_token_end_index = 4
    
    expression_info = ExpressionInfo(
        key,
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    )
    
    _assert_fields_set(expression_info)
    
    vampytest.assert_eq(expression_info.key, key)
    vampytest.assert_eq(expression_info.file_info, file_info)
    vampytest.assert_eq(expression_info.expression_line_start_index, expression_line_start_index)
    vampytest.assert_eq(expression_info.expression_line_end_index, expression_line_end_index)
    vampytest.assert_eq(expression_info.expression_character_start_index, expression_character_start_index)
    vampytest.assert_eq(expression_info.expression_character_end_index, expression_character_end_index)
    vampytest.assert_eq(expression_info.expression_token_start_index, expression_token_start_index)
    vampytest.assert_eq(expression_info.expression_token_end_index, expression_token_end_index)
    vampytest.assert_eq(expression_info.removed_indentation_characters, removed_indentation_characters)
    vampytest.assert_eq(expression_info.line, line)


def test__ExpressionInfo__repr():
    """
    Tests whether ``ExpressionInfo.__repr__`` works as intended.
    """
    key = ExpressionKey('orin.py', 1, 'koishi', 0)
    content = 'hello\nhell\nhecatia'
    parse_result = get_highlight_parse_result(content)
    removed_indentation_characters = 0
    line = 'hell'
    
    file_info = FileInfo('orin.py', 0, 0.0, content, parse_result, False, False)
    
    expression_line_start_index = 1
    expression_line_end_index = 2
    expression_character_start_index = 4
    expression_character_end_index = 5
    expression_token_start_index = 3
    expression_token_end_index = 4
    
    expression_info = ExpressionInfo(
        key,
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    )
    
    output = repr(expression_info)
    vampytest.assert_instance(output, str)


def test__ExpressionInfo__copy():
    """
    Tests whether ``ExpressionInfo.copy`` works as intended.
    """
    key = ExpressionKey('orin.py', 1, 'koishi', 0)
    content = 'hello\nhell\nhecatia'
    parse_result = get_highlight_parse_result(content)
    removed_indentation_characters = 0
    line = 'hell'
    
    file_info = FileInfo('orin.py', 0, 0.0, content, parse_result, False, False)
    
    expression_line_start_index = 1
    expression_line_end_index = 2
    expression_character_start_index = 4
    expression_character_end_index = 5
    expression_token_start_index = 3
    expression_token_end_index = 4
    
    expression_info = ExpressionInfo(
        key,
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    )
    copy = expression_info.copy()
    _assert_fields_set(copy)
    vampytest.assert_is_not(copy, expression_info)
    
    
    vampytest.assert_eq(copy.key, key)
    vampytest.assert_eq(copy.file_info, file_info)
    vampytest.assert_eq(copy.expression_line_start_index, expression_line_start_index)
    vampytest.assert_eq(copy.expression_line_end_index, expression_line_end_index)
    vampytest.assert_eq(copy.expression_character_start_index, expression_character_start_index)
    vampytest.assert_eq(copy.expression_character_end_index, expression_character_end_index)
    vampytest.assert_eq(copy.expression_token_start_index, expression_token_start_index)
    vampytest.assert_eq(copy.expression_token_end_index, expression_token_end_index)
    vampytest.assert_eq(copy.removed_indentation_characters, removed_indentation_characters)
    vampytest.assert_eq(copy.line, line)
