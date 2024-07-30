import vampytest

from ...exception_representation import ExceptionRepresentationBase, ExceptionRepresentationGeneric
from ...frame_group import FrameGroup
from ...frame_proxy import FrameProxyBase, FrameProxyTraceback

from ..exception_proxy_rich import ExceptionProxyRich


def _create_exception_0():
    try:
        raise ValueError('miau')
    except ValueError as err:
        return err


def _create_exception_1():
    try:
        raise _create_exception_0()
    except ValueError as err:
        return err


def _assert_fields_set(exception_proxy):
    """
    Asserts whether every fields are set of the exception proxy.
    
    Parameters
    ----------
    exception_proxy : ``ExceptionProxyRich``
        The exception proxy to check.
    """
    vampytest.assert_instance(exception_proxy, ExceptionProxyRich)
    vampytest.assert_instance(exception_proxy.exception_representation, ExceptionRepresentationBase, nullable = True)
    vampytest.assert_instance(exception_proxy.frame_groups, list, nullable = True)


def test__ExceptionProxyRich__new():
    """
    Tests whether ``ExceptionProxyRich.__new__`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    _assert_fields_set(exception_proxy)


def test__ExceptionProxyRich__repr():
    """
    Tests whether ``ExceptionProxyRich.__repr__`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = repr(exception_proxy)
    vampytest.assert_instance(output, str)


def test__ExceptionProxyRich__exception_representation():
    """
    Tests whether ``ExceptionProxyRich.exception_representation`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = exception_proxy.exception_representation
    vampytest.assert_instance(exception_proxy.exception_representation, ExceptionRepresentationBase, nullable = True)
    vampytest.assert_eq(output, ExceptionRepresentationGeneric(ValueError('miau'), None))


def test__ExceptionProxyRich__frame_groups():
    """
    Tests whether ``ExceptionProxyRich.frame_groups`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = exception_proxy.frame_groups
    vampytest.assert_instance(output, list, nullable = True)
    vampytest.assert_eq(output, [FrameGroup._create_repeated([FrameProxyTraceback(exception.__traceback__)], 1)])


def test__ExceptionProxyRich__eq():
    """
    Tests whether ``ExceptionProxyRich.__eq__`` works as intended.
    """
    exception_0 = _create_exception_0()
    exception_proxy_0 = ExceptionProxyRich(exception_0)
    
    vampytest.assert_eq(exception_proxy_0, exception_proxy_0)
    vampytest.assert_ne(exception_proxy_0, object())
    
    exception_1 = ValueError()
    exception_proxy_1 = ExceptionProxyRich(exception_1)
    
    vampytest.assert_ne(exception_proxy_0, exception_proxy_1)
    

def test__ExceptionProxyRich__mod():
    """
    Tests whether ``ExceptionProxyRich.__mod__`` and `.__rmod__` works as intended.
    """
    exception_0 = _create_exception_0()
    exception_proxy_0 = ExceptionProxyRich(exception_0)
    
    vampytest.assert_true(exception_proxy_0 % exception_proxy_0)
    
    with vampytest.assert_raises(TypeError):
        exception_proxy_0 % object()
    
    with vampytest.assert_raises(TypeError):
        object() % exception_proxy_0

    exception_1 = ValueError()
    exception_proxy_1 = ExceptionProxyRich(exception_1)
    
    vampytest.assert_false(exception_proxy_0 % exception_proxy_1)


def test__ExceptionProxyRich__drop_variables():
    """
    Tests whether ``ExceptionProxyRich.drop_variables`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    
    exception_proxy.drop_variables()
    
    vampytest.assert_false(exception_proxy.drop_variables())


def test__ExceptionProxyRich__has_variables():
    """
    Tests whether ``ExceptionProxyRich.has_variables`` works as intended.
    """
    exception = _create_exception_0()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = exception_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__ExceptionProxyRich__len():
    """
    Tests whether ``ExceptionProxyRich.__len__`` works as intended.
    """
    exception = _create_exception_1()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = len(exception_proxy)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)


def test__ExceptionProxyRich__iter_frame_groups():
    """
    Tests whether ``ExceptionProxyRich.iter_frame_groups`` works as intended.
    """
    exception = _create_exception_1()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = [*exception_proxy.iter_frame_groups()]
    
    for element in output:
        vampytest.assert_instance(element, FrameGroup)
        
    vampytest.assert_eq(len(output), 1)


def test__ExceptionProxyRich__drop_ignored_frames():
    """
    Tests whether ``ExceptionProxyRich.drop_ignored_frames`` works as intended.
    """
    def filter(frame):
        return '0' in frame.name
    
    exception = _create_exception_1()
    exception_proxy = ExceptionProxyRich(exception)
    
    exception_proxy.drop_ignored_frames(filter = filter)
    
    vampytest.assert_eq(len(exception_proxy), 1)


def test__ExceptionProxyRich__apply_frame_filter():
    """
    Tests whether ``ExceptionProxyRich.apply_frame_filter`` works as intended.
    """
    def filter(frame):
        return '0' in frame.name
    
    exception = _create_exception_1()
    exception_proxy = ExceptionProxyRich(exception)
    
    exception_proxy.apply_frame_filter(filter)
    
    vampytest.assert_eq(len(exception_proxy), 1)


def test__ExceptionProxyRich__iter_frames_no_repeat():
    """
    Tests whether ``ExceptionProxyRich.iter_frames_no_repeat`` works as intended.
    """
    exception = _create_exception_1()
    exception_proxy = ExceptionProxyRich(exception)
    
    output = [*exception_proxy.iter_frames_no_repeat()]
    
    for element in output:
        vampytest.assert_instance(element, FrameProxyBase)
        
    vampytest.assert_eq(len(output), 2)
