import vampytest

from ..expression_key import ExpressionKey


def test__ExpressionKey__new():
    """
    Tests whether ``ExpressionKey.__new__`` works as intended.
    """
    file_name = 'orin.py'
    instruction_index = 20
    line_index = 19
    name = 'koishi'
    
    expression_key = ExpressionKey(
        file_name,
        line_index,
        name,
        instruction_index,
    )
    
    vampytest.assert_instance(expression_key, ExpressionKey)
    vampytest.assert_instance(expression_key.file_name, str)
    vampytest.assert_instance(expression_key.instruction_index, int)
    vampytest.assert_instance(expression_key.line_index, int)
    vampytest.assert_instance(expression_key.name, str)
    
    vampytest.assert_eq(expression_key.file_name, file_name)
    vampytest.assert_eq(expression_key.instruction_index, instruction_index)
    vampytest.assert_eq(expression_key.line_index, line_index)
    vampytest.assert_eq(expression_key.name, name)


def test__ExpressionKey__repr():
    """
    Tests whether ``ExpressionKey.__repr__`` works as intended.
    """
    file_name = 'orin.py'
    instruction_index = 20
    line_index = 19
    name = 'koishi'
    
    expression_key = ExpressionKey(
        file_name,
        line_index,
        name,
        instruction_index,
    )
    
    output = repr(expression_key)
    vampytest.assert_instance(output, str)


def test__ExpressionKey__hash():
    """
    Tests whether ``ExpressionKey.__hash__`` works as intended.
    """
    file_name = 'orin.py'
    instruction_index = 20
    line_index = 19
    name = 'koishi'
    
    expression_key = ExpressionKey(
        file_name,
        line_index,
        name,
        instruction_index,
    )
    
    output = hash(expression_key)
    vampytest.assert_instance(output, int)


def test__ExpressionKey__eq():
    """
    Tests whether ``ExpressionKey.__eq__`` works as intended.
    """
    file_name = 'orin.py'
    instruction_index = 20
    line_index = 19
    name = 'koishi'
    
    keyword_parameters = {
        'file_name': file_name,
        'instruction_index': instruction_index,
        'line_index': line_index,
        'name': name,
    }
    
    expression_key = ExpressionKey(**keyword_parameters)
    vampytest.assert_eq(expression_key, expression_key)
    vampytest.assert_ne(expression_key, object())
    
    for field_name, field_value in (
        ('file_name', 'okuu.py'),
        ('instruction_index', 2),
        ('line_index', 15),
        ('name', 'satori'),
    ):
        test_expression_key = ExpressionKey(**{**keyword_parameters, field_name: field_value})
        vampytest.assert_ne(expression_key, test_expression_key)
