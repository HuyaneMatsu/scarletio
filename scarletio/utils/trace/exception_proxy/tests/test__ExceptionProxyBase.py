import vampytest

from ...exception_representation import ExceptionRepresentationBase
from ...frame_group import FrameGroup
from ...frame_proxy import FrameProxyBase, FrameProxyVirtual

from ..exception_proxy_base import ExceptionProxyBase


def _assert_fields_set(exception_proxy):
    """
    Asserts whether every fields are set of the exception proxy.
    
    Parameters
    ----------
    exception_proxy : ``ExceptionProxyBase``
        The exception proxy to check.
    """
    vampytest.assert_instance(exception_proxy, ExceptionProxyBase)


def test__ExceptionProxyBase__new():
    """
    Tests whether ``ExceptionProxyBase.__new__`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    _assert_fields_set(exception_proxy)


def test__ExceptionProxyBase__repr():
    """
    Tests whether ``ExceptionProxyBase.__repr__`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = repr(exception_proxy)
    vampytest.assert_instance(output, str)


def test__ExceptionProxyBase__exception_representation():
    """
    Tests whether ``ExceptionProxyBase.exception_representation`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = exception_proxy.exception_representation
    vampytest.assert_instance(output, ExceptionRepresentationBase, nullable = True)
    vampytest.assert_eq(output, None)


def test__ExceptionProxyBase__frame_groups():
    """
    Tests whether ``ExceptionProxyBase.frame_groups`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = exception_proxy.frame_groups
    vampytest.assert_instance(output, list, nullable = True)
    vampytest.assert_eq(output, None)


def test__ExceptionProxyBase__frame_groups__set_default():
    """
    Tests whether ``ExceptionProxyBase.frame_groups`` works as intended.
    
    Case: setting default.
    """
    exception_proxy = ExceptionProxyBase()
    
    exception_proxy.frame_groups = None


def test__ExceptionProxyBase__frame_groups__set_non_default():
    """
    Tests whether ``ExceptionProxyBase.frame_groups`` works as intended.
    
    Case: setting non-default.
    """
    exception_proxy = ExceptionProxyBase()
    
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_0)
    
    with vampytest.assert_raises(RuntimeError):
        exception_proxy.frame_groups = [frame_group]


def test__ExceptionProxyBase__eq():
    """
    Tests whether ``ExceptionProxyBase.__eq__`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    vampytest.assert_eq(exception_proxy, exception_proxy)
    vampytest.assert_ne(exception_proxy, object())
    

def test__ExceptionProxyBase__mod():
    """
    Tests whether ``ExceptionProxyBase.__mod__`` and `.__rmod__` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    vampytest.assert_true(exception_proxy % exception_proxy)
    
    with vampytest.assert_raises(TypeError):
        exception_proxy % object()
    
    with vampytest.assert_raises(TypeError):
        object() % exception_proxy


def test__ExceptionProxyBase__drop_variables():
    """
    Tests whether ``ExceptionProxyBase.drop_variables`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    exception_proxy.drop_variables()
    
    vampytest.assert_false(exception_proxy.drop_variables())


def test__ExceptionProxyBase__has_variables():
    """
    Tests whether ``ExceptionProxyBase.has_variables`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = exception_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__ExceptionProxyBase__len():
    """
    Tests whether ``ExceptionProxyBase.__len__`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = len(exception_proxy)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


def test__ExceptionProxyBase__iter_frame_groups():
    """
    Tests whether ``ExceptionProxyBase.iter_frame_groups`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = [*exception_proxy.iter_frame_groups()]
    
    for element in output:
        vampytest.assert_instance(element, FrameGroup)
        
    vampytest.assert_eq(len(output), 0)


def test__ExceptionProxyBase__drop_ignored_frames():
    """
    Tests whether ``ExceptionProxyBase.drop_ignored_frames`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    exception_proxy.drop_ignored_frames()
    
    vampytest.assert_eq(len(exception_proxy), 0)


def test__ExceptionProxyBase__apply_frame_filter():
    """
    Tests whether ``ExceptionProxyBase.apply_frame_filter`` works as intended.
    """
    def filter(frame):
        return True
    
    exception_proxy = ExceptionProxyBase()
    
    exception_proxy.apply_frame_filter(filter)
    
    vampytest.assert_eq(len(exception_proxy), 0)


def test__ExceptionProxyBase__iter_frames_no_repeat():
    """
    Tests whether ``ExceptionProxyBase.iter_frames_no_repeat`` works as intended.
    """
    exception_proxy = ExceptionProxyBase()
    
    output = [*exception_proxy.iter_frames_no_repeat()]
    
    for element in output:
        vampytest.assert_instance(element, FrameProxyBase)
        
    vampytest.assert_eq(len(output), 0)
