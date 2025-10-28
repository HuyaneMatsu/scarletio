import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER, get_highlight_streamer, iter_split_ansi_format_codes

from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import _build_frames_repeated_line, produce_frame_group
from ..tests.helper_create_dummy_expression_info import create_dummy_expression_info


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
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, 'hey\nmister')

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, 'i love you')
    
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


def test__produce_frame_group__no_repeat_no_highlight():
    """
    Tests whether ``produce_frame_group`` works as intended.
    
    Case: No repeat & no highlight.
    """
    frame_group = _get_input_frame_group()
    highlight_streamer = get_highlight_streamer(None)
    output = []
    for item in produce_frame_group(frame_group):
        output.extend(highlight_streamer.asend(item))
        
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__produce_frame_group__no_repeat_with_highlight():
    """
    Tests whether ``produce_frame_group`` works as intended.
    
    Case: No repeat & with highlight.
    """
    frame_group = _get_input_frame_group()
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = []
    for item in produce_frame_group(frame_group):
        output.extend(highlight_streamer.asend(item))
        
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    vampytest.assert_true(any(item[0] for item in split))
    
    output_string = ''.join([item[1] for item in split if not item[0]])
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__produce_frame_group__with_repeat_no_highlight():
    """
    Tests whether ``produce_frame_group`` works as intended.
    
    Case: With repeat & no highlight.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, 'hey\nmister')
    frame_proxy_0.alike_count = 3

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, 'i love you')
    frame_proxy_1.alike_count = 3
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    frame_group.repeat_count = 3
    
    highlight_streamer = get_highlight_streamer(None)
    output = []
    for item in produce_frame_group(frame_group):
        output.extend(highlight_streamer.asend(item))
        
    output.extend(highlight_streamer.asend(None))
    
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
