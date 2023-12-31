from sys import _getframe as get_frame
from types import CodeType, FunctionType, FrameType

import vampytest

from ...expression_parsing import ExpressionInfo, ExpressionKey

from ..frame_proxy_frame import FrameProxyFrame


def _get_frame_0():
    return get_frame()


def _get_frame_1():
    return get_frame()


def test__FrameProxyFrame__new():
    """
    Tests whether ``FrameProxyFrame.__new__`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    vampytest.assert_instance(frame_proxy, FrameProxyFrame)
    vampytest.assert_instance(frame_proxy._frame, FrameType)
    vampytest.assert_is(frame_proxy._frame, frame)
    vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo, nullable = True)


def test__FrameProxyFrame__repr():
    """
    Tests whether ``FrameProxyFrame.__repr__`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = repr(frame_proxy)
    vampytest.assert_instance(output, str)


def test__FrameProxyFrame__builtins():
    """
    Tests whether ``FrameProxyFrame.builtins`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.builtins
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, frame.f_builtins)


def test__FrameProxyFrame__globals():
    """
    Tests whether ``FrameProxyFrame.globals`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.globals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, frame.f_globals)


def test__FrameProxyFrame__locals():
    """
    Tests whether ``FrameProxyFrame.locals`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.locals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, frame.f_locals)


def test__FrameProxyFrame__code():
    """
    Tests whether ``FrameProxyFrame.code`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.code
    vampytest.assert_instance(output, CodeType, nullable = True)
    vampytest.assert_eq(output, frame.f_code)


def test__FrameProxyFrame__instruction_index():
    """
    Tests whether ``FrameProxyFrame.instruction_index`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.instruction_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, frame.f_lasti)


def test__FrameProxyFrame__line_index():
    """
    Tests whether ``FrameProxyFrame.line_index`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.line_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, frame.f_lineno - 1)


def test__FrameProxyFrame__tracing_function():
    """
    Tests whether ``FrameProxyFrame.tracing_function`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.tracing_function
    vampytest.assert_instance(output, FunctionType, nullable = True)
    vampytest.assert_eq(output, frame.f_trace)


def test__FrameProxyFrame__file_name():
    """
    Tests whether ``FrameProxyFrame.file_name`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.file_name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, __file__)


def test__FrameProxyFrame__name():
    """
    Tests whether ``FrameProxyFrame.name`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, _get_frame_0.__name__)


def test__FrameProxyFrame__eq():
    """
    Tests whether ``FrameProxyFrame.__eq__`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    vampytest.assert_eq(frame_proxy, frame_proxy)
    vampytest.assert_ne(frame_proxy, object())
    vampytest.assert_ne(frame_proxy, FrameProxyFrame(_get_frame_1()))
    

def test__FrameProxyFrame__mod():
    """
    Tests whether ``FrameProxyFrame.__mod__`` and `.__rmod__` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    vampytest.assert_true(frame_proxy % frame_proxy)
    vampytest.assert_true(frame_proxy % FrameProxyFrame(_get_frame_0()))
    vampytest.assert_false(frame_proxy % FrameProxyFrame(_get_frame_1()))
    
    with vampytest.assert_raises(TypeError):
        frame_proxy % object()
    
    with vampytest.assert_raises(TypeError):
        object() % frame_proxy


def test__FrameProxyFrame__expression_key():
    """
    Tests whether ``FrameProxyFrame.expression_key`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.expression_key
    vampytest.assert_instance(output, ExpressionKey)
    vampytest.assert_eq(
        output,
        ExpressionKey(frame_proxy.file_name, frame_proxy.line_index, frame_proxy.name, frame_proxy.instruction_index),
    )


def test__FrameProxyFrame__has_variables():
    """
    Tests whether ``FrameProxyFrame.has_variables`` works as intended.
    """
    frame = _get_frame_0()
    frame_proxy = FrameProxyFrame(frame)
    
    output = frame_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
