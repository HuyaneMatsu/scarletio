import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER

from ..expression_parsing import ExpressionInfo
from ..frame_proxy import FrameProxyVirtual
from ..rendering import render_frame_into


def _get_input_frame():
    frame_proxy = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, ['hey', 'mister'], 0, True)
    return frame_proxy
    

def _get_expected_output_string():
    return (
        '  File "koishi.py", around line 13, in sit\n'
        '    hey\n'
        '    mister\n'
    )


def test__render_frame_into__no_highlighter():
    """
    Tests whether ``render_frame_into`` works as intended.
    
    Case: No highlighter.
    """
    frame_proxy = _get_input_frame()
    output = render_frame_into(frame_proxy, [], None)
    
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, _get_expected_output_string())


def test__render_frame_into__with_highlighter():
    """
    Tests whether ``render_frame_into`` works as intended.
    
    Case: With highlighter.
    """
    frame_proxy = _get_input_frame()
    output = render_frame_into(frame_proxy, [], DEFAULT_ANSI_HIGHLIGHTER)
    
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    vampytest.assert_true(any('\x1b' in part for part in output))
    
    output_string = ''.join(filter(lambda part: '\x1b' not in part, output))
    vampytest.assert_eq(output_string, _get_expected_output_string())
