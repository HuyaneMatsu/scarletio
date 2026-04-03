from types import CodeType, FunctionType, TracebackType

import vampytest

from ...expression_parsing import ExpressionInfo, ExpressionKey

from ..frame_proxy_traceback import FrameProxyTraceback


def _get_traceback_frame_0():
    try:
        raise ValueError()
    except ValueError as e:
        return e.__traceback__


def _get_traceback_frame_1():
    try:
        raise KeyError()
    except KeyError as e:
        return e.__traceback__


def test__FrameProxyTraceback__new():
    """
    Tests whether ``FrameProxyTraceback.__new__`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    vampytest.assert_instance(frame_proxy, FrameProxyTraceback)
    vampytest.assert_instance(frame_proxy._traceback, TracebackType)
    vampytest.assert_is(frame_proxy._traceback, traceback_frame)
    vampytest.assert_instance(frame_proxy.alike_count, int)
    vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo, nullable = True)


def test__FrameProxyTraceback__repr():
    """
    Tests whether ``FrameProxyTraceback.__repr__`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = repr(frame_proxy)
    vampytest.assert_instance(output, str)


def test__FrameProxyTraceback__builtins():
    """
    Tests whether ``FrameProxyTraceback.builtins`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.builtins
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_builtins)


def test__FrameProxyTraceback__globals():
    """
    Tests whether ``FrameProxyTraceback.globals`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.globals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_globals)


def test__FrameProxyTraceback__locals():
    """
    Tests whether ``FrameProxyTraceback.locals`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.locals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_locals)


def test__FrameProxyTraceback__code():
    """
    Tests whether ``FrameProxyTraceback.code`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.code
    vampytest.assert_instance(output, CodeType, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_code)


def test__FrameProxyTraceback__instruction_index():
    """
    Tests whether ``FrameProxyTraceback.instruction_index`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.instruction_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_lasti)


def test__FrameProxyTraceback__line_index():
    """
    Tests whether ``FrameProxyTraceback.line_index`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.line_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_lineno - 1)


def test__FrameProxyTraceback__tracing_function():
    """
    Tests whether ``FrameProxyTraceback.tracing_function`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.tracing_function
    vampytest.assert_instance(output, FunctionType, nullable = True)
    vampytest.assert_eq(output, traceback_frame.tb_frame.f_trace)


def test__FrameProxyTraceback__file_name():
    """
    Tests whether ``FrameProxyTraceback.file_name`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.file_name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, __file__)


def test__FrameProxyTraceback__name():
    """
    Tests whether ``FrameProxyTraceback.name`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, _get_traceback_frame_0.__name__)


def test__FrameProxyTraceback__eq():
    """
    Tests whether ``FrameProxyTraceback.__eq__`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    vampytest.assert_eq(frame_proxy, frame_proxy)
    vampytest.assert_ne(frame_proxy, object())
    vampytest.assert_ne(frame_proxy, FrameProxyTraceback(_get_traceback_frame_1()))
    

def test__FrameProxyTraceback__mod():
    """
    Tests whether ``FrameProxyTraceback.__mod__`` and `.__rmod__` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    vampytest.assert_true(frame_proxy % frame_proxy)
    vampytest.assert_true(frame_proxy % FrameProxyTraceback(_get_traceback_frame_0()))
    vampytest.assert_false(frame_proxy % FrameProxyTraceback(_get_traceback_frame_1()))
    
    with vampytest.assert_raises(TypeError):
        frame_proxy % object()
    
    with vampytest.assert_raises(TypeError):
        object() % frame_proxy


def test__FrameProxyTraceback__expression_key():
    """
    Tests whether ``FrameProxyTraceback.expression_key`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.expression_key
    vampytest.assert_instance(output, ExpressionKey)
    vampytest.assert_eq(
        output,
        ExpressionKey(frame_proxy.file_name, frame_proxy.line_index, frame_proxy.name, frame_proxy.instruction_index),
    )


def test__FrameProxyTraceback__has_variables():
    """
    Tests whether ``FrameProxyTraceback.has_variables`` works as intended.
    """
    traceback_frame = _get_traceback_frame_0()
    frame_proxy = FrameProxyTraceback(traceback_frame)
    
    output = frame_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
