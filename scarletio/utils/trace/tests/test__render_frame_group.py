import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER

from ..expression_parsing import ExpressionInfo
from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import _build_frames_repeated_line, render_frame_group_into


def _iter_options__build_frames_repeated_line():
    yield 1, 2, '[Following 1 frame was repeated 2 times]'
    yield 4, 3, '[Following 4 frames were repeated 3 times]'


@vampytest._(vampytest.call_from(_iter_options__build_frames_repeated_line()).returning_last())
def test__build_frames_repeated_line(frame_count, repeat_count):
    """
    Tests whether ``_build_frames_repeated_line`` works as intended.
    
    Parameters
    ----------
    frame_count : `lint`
        The amount of repeated frames.
    repeat_count : `int`
        How much times the frames were repeated.
    
    Returns
    -------
    output : `str`
    """
    output = _build_frames_repeated_line(frame_count, repeat_count)
    vampytest.assert_instance(output, str)
    return output


def _get_input_frame_group():
    frame_proxy_0 = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_0.expression_info = ExpressionInfo(frame_proxy_0.expression_key, ['hey', 'mister'], 0, True)

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = ExpressionInfo(frame_proxy_1.expression_key, ['i love you'], 0, True)
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    return frame_group


def _get_expected_output_string():
    return (
        '  File "koishi.py", around line 13, in sit\n'
        '    hey\n'
        '    mister\n'
        '  File "satori.py", line 16, in mind_read\n'
        '    i love you\n'
    )


def test__render_frame_group_into__no_repeat_no_highlight():
    """
    Tests whether ``render_frame_group_into`` works as intended.
    
    Case: No repeat & no highlight.
    """
    frame_group = _get_input_frame_group()
    output = render_frame_group_into(frame_group, [], None)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__render_frame_group_into__no_repeat_with_highlight():
    """
    Tests whether ``render_frame_group_into`` works as intended.
    
    Case: No repeat & with highlight.
    """
    frame_group = _get_input_frame_group()
    output = render_frame_group_into(frame_group, [], DEFAULT_ANSI_HIGHLIGHTER)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    vampytest.assert_true(any('\x1b' in part for part in output))
    
    output_string = ''.join(filter(lambda part: '\x1b' not in part, output))
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__render_frame_group_into__with_repeat_no_highlight():
    """
    Tests whether ``render_frame_group_into`` works as intended.
    
    Case: With repeat & no highlight.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_0.expression_info = ExpressionInfo(frame_proxy_0.expression_key, ['hey', 'mister'], 0, True)
    frame_proxy_0.expression_info.mention_count = 3

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = ExpressionInfo(frame_proxy_1.expression_key, ['i love you'], 0, True)
    frame_proxy_1.expression_info.mention_count = 3
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    frame_group.repeat_count = 3
    
    output = render_frame_group_into(frame_group, [], None)
    vampytest.assert_instance(output, list)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        (
            '[Following 2 frames were repeated 3 times]\n'
            '  File "koishi.py", around line 13, in sit\n'
            '    hey\n'
            '    mister\n'
            '  File "satori.py", line 16, in mind_read\n'
            '    i love you\n'
            '[End of repeated frames]\n'
        )
    )
