import vampytest

from ..default import DEFAULT_ANSI_HIGHLIGHTER
from ..token_types import TOKEN_TYPE_NUMERIC_FLOAT
from ..utils import add_highlighted_parts_into


def test__add_highlighted_parts_into__no_highlighter():
    """
    Tests whether ``add_highlighted_parts_into`` works as intended.
    
    Case: No highlighter.
    """
    input_value = [
        (TOKEN_TYPE_NUMERIC_FLOAT, 'koishi'),
        (TOKEN_TYPE_NUMERIC_FLOAT, 'satori'),
    ]
    
    output = add_highlighted_parts_into(input_value, None, [])
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 2)
    
    part = output[0]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value[0][1])
    
    part = output[1]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value[1][1])


def test__add_highlighted_parts_into__with_highlighter():
    """
    Tests whether ``add_highlighted_parts_into`` works as intended.
    
    Case: No highlighter.
    """
    input_value = [
        (TOKEN_TYPE_NUMERIC_FLOAT, 'koishi'),
        (TOKEN_TYPE_NUMERIC_FLOAT, 'satori'),
    ]
    
    output = add_highlighted_parts_into(input_value, DEFAULT_ANSI_HIGHLIGHTER, [])
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 6)
    
    part = output[0]
    vampytest.assert_instance(part, str)
    
    part = output[1]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value[0][1])
    
    part = output[2]
    vampytest.assert_instance(part, str)
    
    part = output[3]
    vampytest.assert_instance(part, str)
    
    part = output[4]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value[1][1])

    part = output[5]
    vampytest.assert_instance(part, str)
