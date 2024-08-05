import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER

from ..expression_parsing import ExpressionInfo
from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import render_frame_groups_into


def _get_input_frame_groups():
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
    
    frame_proxy_2 = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_2.expression_info = ExpressionInfo(frame_proxy_2.expression_key, ['hey', 'mister'], 0, True)
    frame_proxy_2.alike_count = 3

    frame_proxy_3 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_3.expression_info = ExpressionInfo(frame_proxy_3.expression_key, ['i love you'], 0, True)
    frame_proxy_3.alike_count = 3
    
    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_2)
    frame_group_1.try_add_frame(frame_proxy_3)
    frame_group_1.repeat_count = 3
    
    return [frame_group_0, frame_group_1]


def _get_expected_output_string():
    return (
        '  File "orin.py", around line 13, in sit\n'
        '    hey\n'
        '    sister\n'
        '  File "okuu.py", line 16, in mind_read\n'
        '    darling\n'
        '[Following 2 frames were repeated 3 times]\n'
        '  File "koishi.py", around line 13, in sit\n'
        '    hey\n'
        '    mister\n'
        '  File "satori.py", line 16, in mind_read\n'
        '    i love you\n'
        '[End of repeated frames]\n'
    )


def test__render_frame_groups_into__no_highlight():
    """
    Tests whether ``render_frame_groups_into`` works as intended.
    
    Case: No highlight.
    """
    frame_groups = _get_input_frame_groups()
    output = render_frame_groups_into(frame_groups, [], None)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__render_frame_groups_into__with_highlight():
    """
    Tests whether ``render_frame_groups_into`` works as intended.
    
    Case: With highlight.
    """
    frame_groups = _get_input_frame_groups()
    output = render_frame_groups_into(frame_groups, [], DEFAULT_ANSI_HIGHLIGHTER)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    vampytest.assert_true(any('\x1b' in part for part in output))
    
    output_string = ''.join(filter(lambda part: '\x1b' not in part, output))
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__render_frame_groups_into__no_frame_groups():
    """
    Tests whether ``render_frame_groups_into`` works as intended.
    
    Case: No frame groups.
    """
    output = render_frame_groups_into(None, [], None)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, '')
