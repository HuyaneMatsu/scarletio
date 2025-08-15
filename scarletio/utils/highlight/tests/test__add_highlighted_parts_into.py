import vampytest

from ..ansi import iter_split_ansi_format_codes
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
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, 'koishisatori')


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
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    output_string = ''.join([item[1] for item in iter_split_ansi_format_codes(output_string) if not item[0]])
    vampytest.assert_eq(output_string, 'koishisatori')
