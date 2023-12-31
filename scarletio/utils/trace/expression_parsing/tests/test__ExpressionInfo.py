import vampytest

from ..expression_info import ExpressionInfo
from ..expression_key import ExpressionKey


def _assert_fields_set(expression_info):
    """
    Asserts whether every fields are set of the given expression info.
    
    Parameters
    ----------
    expression_info : ``ExpressionInfo``
        The expression info to test.
    """
    vampytest.assert_instance(expression_info, ExpressionInfo)
    vampytest.assert_instance(expression_info.key, ExpressionKey)
    vampytest.assert_instance(expression_info.line, str)
    vampytest.assert_instance(expression_info.lines, list)
    vampytest.assert_instance(expression_info.shift, int)
    vampytest.assert_instance(expression_info.syntax_valid, bool)
    vampytest.assert_instance(expression_info.mention_count, int)


def test__ExpressionInfo__new():
    """
    Tests whether ``ExpressionInfo.__new__`` works as intended.
    """
    key = ExpressionKey('orin.py', 20, 'koishi', 10)
    lines = ['aya', 'ya']
    shift = 1
    syntax_valid = True
    
    expression_info = ExpressionInfo(key, lines, shift, syntax_valid)
    _assert_fields_set(expression_info)
    
    vampytest.assert_eq(expression_info.key, key)
    vampytest.assert_eq(expression_info.line, 'aya\nya')
    vampytest.assert_eq(expression_info.lines, lines)
    vampytest.assert_eq(expression_info.shift, shift)
    vampytest.assert_eq(expression_info.syntax_valid, syntax_valid)
    vampytest.assert_eq(expression_info.mention_count, 0)


def test__ExpressionInfo__repr():
    """
    Tests whether ``ExpressionInfo.__repr__`` works as intended.
    """
    key = ExpressionKey('orin.py', 20, 'koishi', 10)
    lines = ['aya', 'ya']
    shift = 1
    syntax_valid = True
    
    expression_info = ExpressionInfo(key, lines, shift, syntax_valid)
    
    output = repr(expression_info)
    vampytest.assert_instance(output, str)


def test__ExpressionInfo__copy():
    """
    Tests whether ``ExpressionInfo.copy`` works as intended.
    """
    key = ExpressionKey('orin.py', 20, 'koishi', 10)
    lines = ['aya', 'ya']
    shift = 1
    syntax_valid = True
    
    expression_info = ExpressionInfo(key, lines, shift, syntax_valid)
    copy = expression_info.copy()
    _assert_fields_set(copy)
    vampytest.assert_is_not(copy, expression_info)
    
    vampytest.assert_eq(copy.key, key)
    vampytest.assert_eq(copy.line, 'aya\nya')
    vampytest.assert_eq(copy.lines, lines)
    vampytest.assert_eq(copy.shift, shift)
    vampytest.assert_eq(copy.syntax_valid, syntax_valid)
    vampytest.assert_eq(copy.mention_count, 0)


def test__Expression_info__do_mention():
    """
    Tests whether ``ExpressionInfo.do_mention`` works as intended.
    """
    key = ExpressionKey('orin.py', 20, 'koishi', 10)
    lines = ['aya', 'ya']
    shift = 1
    syntax_valid = True
    
    expression_info = ExpressionInfo(key, lines, shift, syntax_valid)
    
    expression_info.do_mention()
    vampytest.assert_eq(expression_info.mention_count, 1)
    
    expression_info.do_mention()
    vampytest.assert_eq(expression_info.mention_count, 2)
