from sys import _getframe as get_frame

import vampytest

from ...expression_parsing import ExpressionInfo
from ...tests.helper_create_dummy_expression_info import create_dummy_expression_info

from ..frame_proxy_frame import FrameProxyFrame
from ..frame_proxy_virtual import FrameProxyVirtual
from ..frame_proxy_traceback import FrameProxyTraceback
from ..frame_proxying import convert_frames_to_frame_proxies, get_exception_frames, populate_frame_proxies


def _get_traceback_frame():
    try:
        raise ValueError
    except ValueError as err:
        return err.__traceback__


def _get_call_frame():
    return get_frame()


def _nested_exception():
    raise ValueError


def _get_nested_exception():
    try:
        _nested_exception()
    except ValueError as err:
        return err


def test__convert_frames_to_frame_proxies():
    """
    Tests whether ``convert_frames_to_frame_proxies`` works as intended.
    """
    traceback_frame = _get_traceback_frame()
    call_frame = _get_call_frame()
    frame_proxy = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    output = convert_frames_to_frame_proxies([traceback_frame, call_frame, frame_proxy])
    vampytest.assert_instance(output, list)
    
    vampytest.assert_eq(len(output), 3)
    
    frame = output[0]
    vampytest.assert_instance(frame, FrameProxyTraceback)
    vampytest.assert_is(frame._traceback, traceback_frame)
    
    frame = output[1]
    vampytest.assert_instance(frame, FrameProxyFrame)
    vampytest.assert_is(frame._frame, call_frame)
    
    frame = output[2]
    vampytest.assert_is(frame, frame_proxy)


def test__get_exception_frames():
    """
    Tests whether ``get_exception_frames`` works as intended.
    """
    exception = _get_nested_exception()
    output = get_exception_frames(exception)
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 2)
    
    frame = output[0]
    vampytest.assert_instance(frame, FrameProxyTraceback)
    vampytest.assert_is(frame._traceback, exception.__traceback__)
    
    frame = output[1]
    vampytest.assert_instance(frame, FrameProxyTraceback)
    vampytest.assert_is(frame._traceback, exception.__traceback__.tb_next)


def test__populate_frame_proxies():
    """
    Tests whether ``populate_frame_proxies`` works as intended.
    """
    traceback_frame = FrameProxyTraceback(_get_traceback_frame())
    call_frame = FrameProxyFrame(_get_call_frame())
    frame_proxy = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_proxies = [traceback_frame, call_frame, frame_proxy, frame_proxy]
    
    populate_frame_proxies(frame_proxies)
    
    for frame_proxy in frame_proxies:
        vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo)


def test__populate_frame_proxies__desync():
    """
    Tests whether ``populate_frame_proxies`` works as intended.
    
    Case: Desync while populating.
    """
    frame_proxy = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    expression_info = create_dummy_expression_info(frame_proxy.expression_key, '')
    new_file_name = 'kokoro.py'
    
    def mock_get_expression_info(expression_key):
        nonlocal frame_proxy
        nonlocal expression_info
        nonlocal new_file_name
        vampytest.assert_eq(expression_key, expression_info.key)
        frame_proxy.file_name = new_file_name
        return expression_info
    
    frame_proxies = [frame_proxy]
    
    mocked = vampytest.mock_globals(populate_frame_proxies, get_expression_info = mock_get_expression_info)
    mocked(frame_proxies)
    
    for frame_proxy in frame_proxies:
        vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo)
    
    vampytest.assert_eq(frame_proxy.expression_info.key.file_name, new_file_name)
