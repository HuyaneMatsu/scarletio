from types import CodeType, FunctionType

import vampytest

from ...expression_parsing import ExpressionInfo, ExpressionKey

from ..frame_proxy_virtual import FrameProxyVirtual
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


def _assert_fields_set(frame_proxy):
    """
    Asserts whether every fields are set of the given frame proxy.
    
    Parameters
    ----------
    frame_proxy : ``FrameProxyVirtual``
        The frame proxy to check.
    """
    vampytest.assert_instance(frame_proxy, FrameProxyVirtual)
    vampytest.assert_instance(frame_proxy.builtins, dict, nullable = True)
    vampytest.assert_instance(frame_proxy.code, CodeType, nullable = True)
    vampytest.assert_instance(frame_proxy.globals, dict, nullable = True)
    vampytest.assert_instance(frame_proxy.line_index, int)
    vampytest.assert_instance(frame_proxy.instruction_index, int)
    vampytest.assert_instance(frame_proxy.locals, dict, nullable = True)
    vampytest.assert_instance(frame_proxy.tracing_function, FunctionType, nullable = True)
    vampytest.assert_instance(frame_proxy.expression_info, ExpressionInfo, nullable = True)
    vampytest.assert_instance(frame_proxy.file_name, str)
    vampytest.assert_instance(frame_proxy.name, str)


def test__FrameProxyVirtual__new__with_variables():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: with variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyTraceback(traceback_frame)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = True)
    _assert_fields_set(frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, source_frame_proxy.builtins)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, source_frame_proxy.globals)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, source_frame_proxy.locals)
    vampytest.assert_eq(frame_proxy.tracing_function, source_frame_proxy.tracing_function)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__new__without_variables():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: without variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyTraceback(traceback_frame)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = False)
    _assert_fields_set(frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, None)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, None)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, None)
    vampytest.assert_eq(frame_proxy.tracing_function, None)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__new__same_type_with_to_without():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: with variables to without variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyVirtual(FrameProxyTraceback(traceback_frame), with_variables = True)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = False)
    _assert_fields_set(frame_proxy)
    vampytest.assert_is_not(source_frame_proxy, frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, None)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, None)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, None)
    vampytest.assert_eq(frame_proxy.tracing_function, None)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__new__same_type_with_to_with():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: with variables to with variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyVirtual(FrameProxyTraceback(traceback_frame), with_variables = True)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = True)
    _assert_fields_set(frame_proxy)
    vampytest.assert_is(source_frame_proxy, frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, source_frame_proxy.builtins)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, source_frame_proxy.globals)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, source_frame_proxy.locals)
    vampytest.assert_eq(frame_proxy.tracing_function, source_frame_proxy.tracing_function)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__new__same_type_without_to_without():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: without variables to without variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyVirtual(FrameProxyTraceback(traceback_frame), with_variables = False)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = False)
    _assert_fields_set(frame_proxy)
    vampytest.assert_is(source_frame_proxy, frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, None)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, None)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, None)
    vampytest.assert_eq(frame_proxy.tracing_function, None)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__new__same_type_without_to_with():
    """
    Tests whether ``FrameProxyVirtual.__new__`` works as intended.
    
    Case: without variables to with variables.
    """
    traceback_frame = _get_traceback_frame_0()
    
    source_frame_proxy = FrameProxyVirtual(FrameProxyTraceback(traceback_frame), with_variables = False)
    
    frame_proxy = FrameProxyVirtual(source_frame_proxy, with_variables = True)
    _assert_fields_set(frame_proxy)
    vampytest.assert_is(source_frame_proxy, frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, None)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, None)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, None)
    vampytest.assert_eq(frame_proxy.tracing_function, None)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__from_fields__no_fields():
    """
    Tests whether ``FrameProxyVirtual.from_fields`` works as intended.
    
    Case: no fields.
    """
    frame_proxy = FrameProxyVirtual.from_fields()
    _assert_fields_set(frame_proxy)


def test__FrameProxyVirtual__from_fields__all_fields():
    """
    Tests whether ``FrameProxyVirtual.from_fields`` works as intended.
    
    Case: all fields.
    """
    traceback_frame = _get_traceback_frame_0()
    source_frame_proxy = FrameProxyVirtual(FrameProxyTraceback(traceback_frame), with_variables = True)
    
    frame_proxy = FrameProxyVirtual.from_fields(
        builtins = source_frame_proxy.builtins,
        code = source_frame_proxy.code,
        globals = source_frame_proxy.globals,
        line_index = source_frame_proxy.line_index,
        instruction_index = source_frame_proxy.instruction_index,
        locals = source_frame_proxy.locals,
        tracing_function = source_frame_proxy.tracing_function,
        expression_info = source_frame_proxy.expression_info,
        file_name = source_frame_proxy.file_name,
        name = source_frame_proxy.name,
    )
    _assert_fields_set(frame_proxy)
    
    vampytest.assert_eq(frame_proxy.builtins, source_frame_proxy.builtins)
    vampytest.assert_eq(frame_proxy.code, source_frame_proxy.code)
    vampytest.assert_eq(frame_proxy.globals, source_frame_proxy.globals)
    vampytest.assert_eq(frame_proxy.line_index, source_frame_proxy.line_index)
    vampytest.assert_eq(frame_proxy.instruction_index, source_frame_proxy.instruction_index)
    vampytest.assert_eq(frame_proxy.locals, source_frame_proxy.locals)
    vampytest.assert_eq(frame_proxy.tracing_function, source_frame_proxy.tracing_function)
    vampytest.assert_eq(frame_proxy.expression_info, source_frame_proxy.expression_info)
    vampytest.assert_eq(frame_proxy.file_name, source_frame_proxy.file_name)
    vampytest.assert_eq(frame_proxy.name, source_frame_proxy.name)


def test__FrameProxyVirtual__repr():
    """
    Tests whether ``FrameProxyVirtual.__repr__`` works as intended.
    """
    source_frame_proxy = FrameProxyTraceback( _get_traceback_frame_0())
    frame_proxy = FrameProxyVirtual(source_frame_proxy)
    
    output = repr(frame_proxy)
    vampytest.assert_instance(output, str)


def test__FrameProxyVirtual__has_variables__yes():
    """
    Tests whether ``FrameProxyVirtual.has_variables`` works as intended.
    
    Case: Yes.
    """
    frame_proxy = FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0()), with_variables = True)
    output = frame_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__FrameProxyVirtual__has_variables__no():
    """
    Tests whether ``FrameProxyVirtual.has_variables`` works as intended.
    
    Case: Nope.
    """
    frame_proxy = FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0()), with_variables = False)
    output = frame_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__FrameProxyVirtual__eq():
    """
    Tests whether ``FrameProxyVirtual.__eq__`` works as intended.
    """
    frame_proxy = FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0()))
    
    vampytest.assert_eq(frame_proxy, frame_proxy)
    vampytest.assert_ne(frame_proxy, object())
    vampytest.assert_ne(frame_proxy, FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_1())))


def test__FrameProxyVirtual__eq__extended():
    """
    Tests whether ``FrameProxyVirtual.__eq__`` works as intended.
    
    Case: Extended.
    """
    test_frame_proxy = FrameProxyTraceback(_get_traceback_frame_0())
    
    keyword_parameters = {
        'builtins': test_frame_proxy.builtins,
        'code': test_frame_proxy.code,
        'globals': test_frame_proxy.globals,
        'line_index': test_frame_proxy.line_index,
        'instruction_index': test_frame_proxy.instruction_index,
        'locals': test_frame_proxy.locals,
        'tracing_function': test_frame_proxy.tracing_function,
    }
    
    for field_name, field_value in (
        ('builtins', None),
        ('code', None),
        ('globals', None),
        ('line_index', -1),
        ('instruction_index', -1),
        ('locals', None),
        ('tracing_function', lambda v: None),
    ):
        frame_proxy = FrameProxyVirtual.from_fields(**{**keyword_parameters, field_name: field_value})
        vampytest.assert_ne(frame_proxy, test_frame_proxy)


def test__FrameProxyVirtual__mod():
    """
    Tests whether ``FrameProxyVirtual.__mod__`` and `.__rmod__` works as intended.
    """
    frame_proxy = FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0()))
    
    vampytest.assert_true(frame_proxy % frame_proxy)
    vampytest.assert_true(frame_proxy % FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0())))
    vampytest.assert_false(frame_proxy % FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_1())))
    
    with vampytest.assert_raises(TypeError):
        frame_proxy % object()
    
    with vampytest.assert_raises(TypeError):
        object() % frame_proxy


def test__FrameProxyVirtual__mod__extended():
    """
    Tests whether ``FrameProxyVirtual.__mod__`` works as intended.
    
    Case: Extended.
    """
    test_frame_proxy = FrameProxyTraceback(_get_traceback_frame_0())
    
    keyword_parameters = {
        'code': test_frame_proxy.code,
        'line_index': test_frame_proxy.line_index,
        'instruction_index': test_frame_proxy.instruction_index,
    }
    
    for field_name, field_value in (
        ('code', None),
        ('line_index', -1),
        ('instruction_index', -1),
    ):
        frame_proxy = FrameProxyVirtual.from_fields(**{**keyword_parameters, field_name: field_value})
        vampytest.assert_false(frame_proxy % test_frame_proxy)


def test__FrameProxyVirtual__expression_key():
    """
    Tests whether ``FrameProxyVirtual.expression_key`` works as intended.
    """
    frame_proxy = FrameProxyVirtual(FrameProxyTraceback(_get_traceback_frame_0()))
    
    output = frame_proxy.expression_key
    vampytest.assert_eq(
        output,
        ExpressionKey(frame_proxy.file_name, frame_proxy.line_index, frame_proxy.name, frame_proxy.instruction_index),
    )
