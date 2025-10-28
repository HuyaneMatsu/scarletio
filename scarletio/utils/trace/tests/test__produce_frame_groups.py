import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER, get_highlight_streamer, iter_split_ansi_format_codes

from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import produce_frame_groups
from ..tests.helper_create_dummy_expression_info import create_dummy_expression_info


def _get_input_frame_groups():
    frame_proxy_0 = FrameProxyVirtual.from_fields(
        file_name = 'orin.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, 'hey\nsister')

    frame_proxy_1 = FrameProxyVirtual.from_fields(
        file_name = 'okuu.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, 'darling')
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    
    frame_proxy_2 = FrameProxyVirtual.from_fields(
        file_name = 'koishi.py', line_index = 12, name = 'sit', instruction_index = 6
    )
    frame_proxy_2.expression_info = create_dummy_expression_info(frame_proxy_2.expression_key, 'hey\nmister')
    frame_proxy_2.alike_count = 3

    frame_proxy_3 = FrameProxyVirtual.from_fields(
        file_name = 'satori.py', line_index = 15, name = 'mind_read', instruction_index = 6
    )
    frame_proxy_3.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, 'i love you')
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


def test__produce_frame_groups__no_highlight():
    """
    Tests whether ``produce_frame_groups`` works as intended.
    
    Case: No highlight.
    """
    frame_groups = _get_input_frame_groups()
    highlight_streamer = get_highlight_streamer(None)
    output = []
    for item in produce_frame_groups(frame_groups):
        output.extend(highlight_streamer.asend(item))
    
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(
        output_string,
        _get_expected_output_string(),
    )


def test__produce_frame_groups__with_highlight():
    """
    Tests whether ``produce_frame_groups`` works as intended.
    
    Case: With highlight.
    """
    frame_groups = _get_input_frame_groups()
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = []
    for item in produce_frame_groups(frame_groups):
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


def test__produce_frame_groups__no_frame_groups():
    """
    Tests whether ``produce_frame_groups`` works as intended.
    
    Case: No frame groups.
    """
    frame_groups = None
    highlight_streamer = get_highlight_streamer(None)
    output = []
    for item in produce_frame_groups(frame_groups):
        output.extend(highlight_streamer.asend(item))
    
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, '')
