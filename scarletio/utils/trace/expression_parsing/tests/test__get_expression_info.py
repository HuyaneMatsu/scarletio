import vampytest

from ..expression_info import ExpressionInfo, get_expression_info
from ..expression_key import ExpressionKey
from ..line_cache_session import LineCacheSession


"""
def a(
    koishi = None,
):
"""


def test__get_expression_info():
    """
    Tests whether ``get_expression_info`` works as intended.
    """
    expression_key = ExpressionKey(__file__, 8, '<module>', 6)
    
    with LineCacheSession():
        expression_info = get_expression_info(expression_key)
    
    vampytest.assert_instance(expression_info, ExpressionInfo)
    vampytest.assert_eq(expression_info.key, expression_key)
    vampytest.assert_eq(expression_info.line, 'def a(\n    koishi = None,\n):')
    vampytest.assert_eq(expression_info.lines, ['def a(', '    koishi = None,', '):'])
    vampytest.assert_eq(expression_info.shift, 0)
    vampytest.assert_eq(expression_info.syntax_valid, True)
