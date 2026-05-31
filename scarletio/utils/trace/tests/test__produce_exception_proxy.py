import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER, get_highlight_streamer, iter_split_ansi_format_codes

from ..exception_proxy import ExceptionProxyVirtual
from ..exception_representation import ExceptionRepresentationGeneric
from ..frame_group import FrameGroup
from ..frame_proxy import FrameProxyVirtual
from ..rendering import produce_exception_proxy
from ..tests.helper_create_dummy_expression_info import create_dummy_expression_info


def _get_input_exception_proxy():
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
    
    representation = 'Exception(\'hey mister\')'
    exception_representation = ExceptionRepresentationGeneric.from_fields(
        representation = representation
    )
    
    return ExceptionProxyVirtual.from_fields(
        exception_representation = exception_representation,
        frame_groups = [frame_group_0],
    )


EXPECTED_OUTPUT_STRING = (
    '    File "orin.py", around line 13, in sit\n'
    '        11   |\n'
    '        12   |\n'
    '        13 >>> hey\n'
    '        14   ~ sister\n'
    '        15   |\n'
    '    File "okuu.py", line 16, in mind_read\n'
    '        14   |\n'
    '        15   |\n'
    '        16 >>> darling\n'
    '        17   |\n'
    'Exception(\'hey mister\')\n'
)


@vampytest.returning(EXPECTED_OUTPUT_STRING)
def test__produce_exception_proxy__no_highlight():
    """
    Tests whether ``produce_exception_proxy`` works as intended.
    
    Case: No highlight.
    
    Returns
    -------
    output : `str`
    """
    exception_proxy = _get_input_exception_proxy()
    highlight_streamer = get_highlight_streamer(None)
    output = []
    for item in produce_exception_proxy(exception_proxy):
        output.extend(highlight_streamer.asend(item))
    
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return ''.join(output)


@vampytest.returning(EXPECTED_OUTPUT_STRING)
def test__produce_exception_proxy__with_highlight():
    """
    Tests whether ``produce_exception_proxy`` works as intended.
    
    Case: With highlight.
    
    Returns
    -------
    output : `str`
    """
    exception_proxy = _get_input_exception_proxy()
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = []
    for item in produce_exception_proxy(exception_proxy):
        output.extend(highlight_streamer.asend(item))
    
    output.extend(highlight_streamer.asend(None))
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    vampytest.assert_true(any(item[0] for item in split))
    
    return ''.join([item[1] for item in split if not item[0]])
