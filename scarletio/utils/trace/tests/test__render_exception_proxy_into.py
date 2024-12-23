import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER

from ..expression_parsing import ExpressionInfo
from ..exception_proxy import ExceptionProxyVirtual
from ..exception_representation import ExceptionRepresentationGeneric
from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import render_exception_proxy_into


def _get_input_exception_proxy():
    frame_proxy_0 = FrameProxyVirtual.from_fields(
        file_name = 'orin.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_0.expression_info = ExpressionInfo(frame_proxy_0.expression_key, ['hey', 'sister'], 0, True)

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'okuu.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = ExpressionInfo(frame_proxy_1.expression_key, ['darling'], 0, True)
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    
    representation = 'Exception(\'hey mister\')'
    exception_representation = ExceptionRepresentationGeneric.from_fields(
        representation = representation
    )
    
    return ExceptionProxyVirtual.from_fields(
        exception_representation = exception_representation,
        frame_groups = [frame_group_0],
    )


def _get_expected_output_string():
    return (
        '  File "orin.py", around line 13, in sit\n'
        '    hey\n'
        '    sister\n'
        '  File "okuu.py", line 16, in mind_read\n'
        '    darling\n'
         'Exception(\'hey mister\')\n'
    )


def test__render_exception_proxy_into__no_highlight():
    """
    Tests whether ``render_exception_proxy_into`` works as intended.
    
    Case: No highlight.
    """
    exception_proxy = _get_input_exception_proxy()
    output = render_exception_proxy_into(exception_proxy, None, [])
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__render_exception_proxy_into__with_highlight():
    """
    Tests whether ``render_exception_proxy_into`` works as intended.
    
    Case: With highlight.
    """
    exception_proxy = _get_input_exception_proxy()
    output = render_exception_proxy_into(exception_proxy, DEFAULT_ANSI_HIGHLIGHTER, [])
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    vampytest.assert_true(any('\x1b' in part for part in output))
    
    output_string = ''.join(filter(lambda part: '\x1b' not in part, output))
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )
