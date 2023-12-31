from types import CodeType, FunctionType

import vampytest

from ...expression_parsing import ExpressionInfo, ExpressionKey

from ..frame_proxy_base import FrameProxyBase


def test__FrameProxyBase__new():
    """
    Tests whether ``FrameProxyBase.__new__`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    vampytest.assert_instance(frame_proxy, FrameProxyBase)
    vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo, nullable = True)


def test__FrameProxyBase__repr():
    """
    Tests whether ``FrameProxyBase.__repr__`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = repr(frame_proxy)
    vampytest.assert_instance(output, str)


def test__FrameProxyBase__builtins():
    """
    Tests whether ``FrameProxyBase.builtins`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.builtins
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, None)


def test__FrameProxyBase__globals():
    """
    Tests whether ``FrameProxyBase.globals`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.globals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, None)


def test__FrameProxyBase__locals():
    """
    Tests whether ``FrameProxyBase.locals`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.locals
    vampytest.assert_instance(output, dict, nullable = True)
    vampytest.assert_eq(output, None)


def test__FrameProxyBase__code():
    """
    Tests whether ``FrameProxyBase.code`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.code
    vampytest.assert_instance(output, CodeType, nullable = True)
    vampytest.assert_eq(output, None)


def test__FrameProxyBase__instruction_index():
    """
    Tests whether ``FrameProxyBase.instruction_index`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.instruction_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, 0)


def test__FrameProxyBase__line_index():
    """
    Tests whether ``FrameProxyBase.line_index`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.line_index
    vampytest.assert_instance(output, int, nullable = True)
    vampytest.assert_eq(output, 0)


def test__FrameProxyBase__tracing_function():
    """
    Tests whether ``FrameProxyBase.tracing_function`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.tracing_function
    vampytest.assert_instance(output, FunctionType, nullable = True)
    vampytest.assert_eq(output, None)


def test__FrameProxyBase__file_name():
    """
    Tests whether ``FrameProxyBase.file_name`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.file_name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, '')


def test__FrameProxyBase__name():
    """
    Tests whether ``FrameProxyBase.name`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.name
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, '')


def test__FrameProxyBase__eq():
    """
    Tests whether ``FrameProxyBase.__eq__`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    vampytest.assert_eq(frame_proxy, frame_proxy)
    vampytest.assert_ne(frame_proxy, object())
    

def test__FrameProxyBase__mod():
    """
    Tests whether ``FrameProxyBase.__mod__`` and `.__rmod__` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    vampytest.assert_true(frame_proxy % frame_proxy)
    
    with vampytest.assert_raises(TypeError):
        frame_proxy % object()
    
    with vampytest.assert_raises(TypeError):
        object() % frame_proxy


def test__FrameProxyBase__expression_key():
    """
    Tests whether ``FrameProxyBase.expression_key`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.expression_key
    vampytest.assert_instance(output, ExpressionKey)
    vampytest.assert_eq(
        output,
        ExpressionKey('', 0, '', 0),
    )


def test__FrameProxyBase__has_variables():
    """
    Tests whether ``FrameProxyBase.has_variables`` works as intended.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__FrameProxyBase__lines__no_expression():
    """
    Tests whether ``FrameProxyBase.lines`` works as intended.
    
    Case: No expression set.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.lines
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(output, [])


def test__FrameProxyBase__lines__with_expression():
    """
    Tests whether ``FrameProxyBase.lines`` works as intended.
    
    Case: expression set.
    """
    frame_proxy = FrameProxyBase()
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, ['hey', 'mister'], 0, True)
    
    output = frame_proxy.lines
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(output, ['hey', 'mister'])


def test__FrameProxyBase__mention_count__no_expression():
    """
    Tests whether ``FrameProxyBase.mention_count`` works as intended.
    
    Case: No expression set.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.mention_count
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


def test__FrameProxyBase__mention_count__with_expression():
    """
    Tests whether ``FrameProxyBase.mention_count`` works as intended.
    
    Case: expression set.
    """
    frame_proxy = FrameProxyBase()
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, ['hey', 'mister'], 0, True)
    frame_proxy.expression_info.do_mention()
    
    output = frame_proxy.mention_count
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)


def test__FrameProxyBase__line__no_expression():
    """
    Tests whether ``FrameProxyBase.line`` works as intended.
    
    Case: No expression set.
    """
    frame_proxy = FrameProxyBase()
    
    output = frame_proxy.line
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, '')


def test__FrameProxyBase__line__with_expression():
    """
    Tests whether ``FrameProxyBase.line`` works as intended.
    
    Case: expression set.
    """
    frame_proxy = FrameProxyBase()
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, ['hey', 'mister'], 0, True)
    
    output = frame_proxy.line
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, 'hey\nmister')
