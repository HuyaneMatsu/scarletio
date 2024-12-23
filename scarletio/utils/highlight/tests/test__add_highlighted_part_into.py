import vampytest

from ..default import DEFAULT_ANSI_HIGHLIGHTER
from ..token_types import TOKEN_TYPE_NUMERIC_FLOAT
from ..utils import add_highlighted_part_into


def test__add_highlighted_part_into__no_highlighter():
    """
    Tests whether ``add_highlighted_part_into`` works as intended.
    
    Case: No highlighter.
    """
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    input_value = 'koishi'
    
    output = add_highlighted_part_into(token_type, input_value, None, [])
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 1)
    
    part = output[0]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value)


def test__add_highlighted_part_into__with_highlighter():
    """
    Tests whether ``add_highlighted_part_into`` works as intended.
    
    Case: With highlighter.
    """
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    input_value = 'koishi'
    
    output = add_highlighted_part_into(token_type, input_value, DEFAULT_ANSI_HIGHLIGHTER, [])
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 3)
    
    part = output[0]
    vampytest.assert_instance(part, str)
    
    part = output[1]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value)

    part = output[2]
    vampytest.assert_instance(part, str)
