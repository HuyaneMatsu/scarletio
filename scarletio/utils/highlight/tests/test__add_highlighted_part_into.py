import vampytest

from ..ansi import iter_split_ansi_format_codes
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
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, 'koishi')


def test__add_highlighted_part_into__with_highlighter():
    """
    Tests whether ``add_highlighted_part_into`` works as intended.
    
    Case: With highlighter.
    """
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    input_value = 'koishi'
    
    output = add_highlighted_part_into(token_type, input_value, DEFAULT_ANSI_HIGHLIGHTER, [])
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    output_string = ''.join([item[1] for item in iter_split_ansi_format_codes(output_string) if not item[0]])
    vampytest.assert_eq(output_string, 'koishi')
