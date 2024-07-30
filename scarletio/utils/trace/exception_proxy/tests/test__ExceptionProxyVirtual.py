import vampytest

from ...exception_representation import ExceptionRepresentationBase, ExceptionRepresentationGeneric
from ...frame_group import FrameGroup
from ...frame_proxy import FrameProxyBase, FrameProxyTraceback, FrameProxyVirtual

from ..exception_proxy_rich import ExceptionProxyRich
from ..exception_proxy_virtual import ExceptionProxyVirtual


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
    exception_proxy : ``ExceptionProxyVirtual``
        The exception proxy to check.
    """
    vampytest.assert_instance(exception_proxy, ExceptionProxyVirtual)
    vampytest.assert_instance(exception_proxy.exception_representation, ExceptionRepresentationBase, nullable = True)
    vampytest.assert_instance(exception_proxy.frame_groups, list, nullable = True)


def test__ExceptionProxyVirtual__new__with_variables():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: with variables.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    _assert_fields_set(exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(exception_proxy.frame_groups, source_exception_proxy.frame_groups)


def test__ExceptionProxyVirtual__new__without_variables():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: without variables.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = False)
    _assert_fields_set(exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(
        exception_proxy.frame_groups,
        [frame_group.copy_without_variables() for frame_group in source_exception_proxy.frame_groups],
    )


def test__ExceptionProxyVirtual__new__with_to_without():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: with to without.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyVirtual(ExceptionProxyRich(exception), with_variables = True)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = False)
    _assert_fields_set(exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(
        exception_proxy.frame_groups,
        [frame_group.copy_without_variables() for frame_group in source_exception_proxy.frame_groups],
    )


def test__ExceptionProxyVirtual__new__with_to_with():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: with to with.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyVirtual(ExceptionProxyRich(exception), with_variables = True)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    _assert_fields_set(exception_proxy)
    vampytest.assert_is(source_exception_proxy, exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(exception_proxy.frame_groups, source_exception_proxy.frame_groups)


def test__ExceptionProxyVirtual__new__same_type_without_to_without():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: without variables to without variables.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyVirtual(ExceptionProxyRich(exception), with_variables = False)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = False)
    _assert_fields_set(exception_proxy)
    vampytest.assert_is(source_exception_proxy, exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(exception_proxy.frame_groups, source_exception_proxy.frame_groups)


def test__ExceptionProxyVirtual__new__same_type_without_to_with():
    """
    Tests whether ``ExceptionProxyVirtual.__new__`` works as intended.
    
    Case: without variables to with variables.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyVirtual(ExceptionProxyRich(exception), with_variables = False)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    _assert_fields_set(exception_proxy)
    vampytest.assert_is(source_exception_proxy, exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(exception_proxy.frame_groups, source_exception_proxy.frame_groups)


def test__ExceptionProxyVirtual__from_fields__no_fields():
    """
    Tests whether ``ExceptionProxyVirtual.from_fields`` works as intended.
    
    Case: no fields.
    """
    exception_proxy = ExceptionProxyVirtual.from_fields()
    _assert_fields_set(exception_proxy)


def test__ExceptionProxyVirtual__from_fields__all_fields():
    """
    Tests whether ``ExceptionProxyVirtual.from_fields`` works as intended.
    
    Case: all fields.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyVirtual(ExceptionProxyRich(exception), with_variables = True)
    
    exception_proxy = ExceptionProxyVirtual.from_fields(
        exception_representation = source_exception_proxy.exception_representation,
        frame_groups = source_exception_proxy.frame_groups,
    )
    _assert_fields_set(exception_proxy)
    
    vampytest.assert_eq(exception_proxy.exception_representation, source_exception_proxy.exception_representation)
    vampytest.assert_eq(exception_proxy.frame_groups, source_exception_proxy.frame_groups)


def test__ExceptionProxyVirtual__repr():
    """
    Tests whether ``ExceptionProxyVirtual.__repr__`` works as intended.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    output = repr(exception_proxy)
    vampytest.assert_instance(output, str)


def test__ExceptionProxyVirtual__exception_representation():
    """
    Tests whether ``ExceptionProxyVirtual.exception_representation`` works as intended.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    output = exception_proxy.exception_representation
    vampytest.assert_instance(exception_proxy.exception_representation, ExceptionRepresentationBase)
    vampytest.assert_eq(output, ExceptionRepresentationGeneric(ValueError('miau'), None))


def test__ExceptionProxyVirtual__frame_groups():
    """
    Tests whether ``ExceptionProxyVirtual.frame_groups`` works as intended.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    
    output = exception_proxy.frame_groups
    vampytest.assert_instance(output, list, nullable = True)
    vampytest.assert_eq(output, [FrameGroup._create_repeated([FrameProxyTraceback(exception.__traceback__)], 1)])


def test__ExceptionProxyVirtual__eq():
    """
    Tests whether ``ExceptionProxyVirtual.__eq__`` works as intended.
    """
    exception_0 = _create_exception_0()
    source_exception_proxy_0 = ExceptionProxyRich(exception_0)
    exception_proxy_0 = ExceptionProxyVirtual(source_exception_proxy_0)
    
    vampytest.assert_eq(exception_proxy_0, exception_proxy_0)
    vampytest.assert_ne(exception_proxy_0, object())
    
    exception_1 = ValueError()
    source_exception_proxy_1 = ExceptionProxyRich(exception_1)
    exception_proxy_1 = ExceptionProxyVirtual(source_exception_proxy_1)
    
    vampytest.assert_ne(exception_proxy_0, exception_proxy_1)
    

def test__ExceptionProxyVirtual__mod():
    """
    Tests whether ``ExceptionProxyVirtual.__mod__`` and `.__rmod__` works as intended.
    """
    exception_0 = _create_exception_0()
    source_exception_proxy_0 = ExceptionProxyRich(exception_0)
    exception_proxy_0 = ExceptionProxyVirtual(source_exception_proxy_0)
    
    vampytest.assert_true(source_exception_proxy_0 % source_exception_proxy_0)
    
    with vampytest.assert_raises(TypeError):
        source_exception_proxy_0 % object()
    
    with vampytest.assert_raises(TypeError):
        object() % source_exception_proxy_0

    exception_1 = ValueError()
    source_exception_proxy_1 = ExceptionProxyRich(exception_1)
    exception_proxy_1 = ExceptionProxyVirtual(source_exception_proxy_1)
    
    vampytest.assert_false(exception_proxy_0 % exception_proxy_1)


def test__ExceptionProxyVirtual__drop_variables():
    """
    Tests whether ``ExceptionProxyVirtual.drop_variables`` works as intended.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    
    exception_proxy.drop_variables()
    
    vampytest.assert_false(exception_proxy.drop_variables())


def test__ExceptionProxyVirtual__has_variables():
    """
    Tests whether ``ExceptionProxyVirtual.has_variables`` works as intended.
    """
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy, with_variables = True)
    
    output = exception_proxy.has_variables()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__ExceptionProxyVirtual__len():
    """
    Tests whether ``ExceptionProxyVirtual.__len__`` works as intended.
    """
    exception = _create_exception_1()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    output = len(exception_proxy)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)


def test__ExceptionProxyRich__iter_frame_groups():
    """
    Tests whether ``ExceptionProxyRich.iter_frame_groups`` works as intended.
    """
    exception = _create_exception_1()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    output = [*exception_proxy.iter_frame_groups()]
    
    for element in output:
        vampytest.assert_instance(element, FrameGroup)
        
    vampytest.assert_eq(len(output), 1)


def test__ExceptionProxyVirtual__drop_ignored_frames():
    """
    Tests whether ``ExceptionProxyVirtual.drop_ignored_frames`` works as intended.
    """
    def filter(frame):
        return '0' in frame.name
    
    exception = _create_exception_1()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    exception_proxy.drop_ignored_frames(filter = filter)
    
    vampytest.assert_eq(len(exception_proxy), 1)


def test__ExceptionProxyVirtual__drop_ignored_frames__all_in_group():
    """
    Tests whether ``ExceptionProxyVirtual.drop_ignored_frames`` works as intended.
    
    Case: All dropped in a group.
    """
    def filter(frame):
        return False
    
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    exception_proxy.drop_ignored_frames(filter = filter)
    
    vampytest.assert_eq(len(exception_proxy), 0)
    vampytest.assert_is(exception_proxy.frame_groups, None)


def test__ExceptionProxyVirtual__apply_frame_filter():
    """
    Tests whether ``ExceptionProxyVirtual.apply_frame_filter`` works as intended.
    """
    def filter(frame):
        return '0' in frame.name
    
    exception = _create_exception_1()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    exception_proxy.apply_frame_filter(filter = filter)
    
    vampytest.assert_eq(len(exception_proxy), 1)


def test__ExceptionProxyVirtual__apply_frame_filter__all_in_group():
    """
    Tests whether ``ExceptionProxyVirtual.apply_frame_filter`` works as intended.
    
    Case: All dropped in a group.
    """
    def filter(frame):
        return False
    
    exception = _create_exception_0()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    exception_proxy.apply_frame_filter(filter)
    
    vampytest.assert_eq(len(exception_proxy), 0)
    vampytest.assert_is(exception_proxy.frame_groups, None)


def test__ExceptionProxyVirtual__iter_frames_no_repeat():
    """
    Tests whether ``ExceptionProxyVirtual.iter_frames_no_repeat`` works as intended.
    """
    exception = _create_exception_1()
    source_exception_proxy = ExceptionProxyRich(exception)
    exception_proxy = ExceptionProxyVirtual(source_exception_proxy)
    
    output = [*exception_proxy.iter_frames_no_repeat()]
    
    for element in output:
        vampytest.assert_instance(element, FrameProxyBase)
        
    vampytest.assert_eq(len(output), 2)


def test__ExceptionProxyVirtual__iter_frames_no_repeat__multiple_groups():
    """
    Tests whether ``ExceptionProxyVirtual.iter_frames_no_repeat`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_2 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_0)
    frame_group_0.try_add_frame(frame_1)
    frame_group_1 = FrameGroup._create_repeated([frame_2], 2)
    
    exception_proxy = ExceptionProxyVirtual.from_fields(frame_groups = [frame_group_0, frame_group_1])
    
    output = [*exception_proxy.iter_frames_no_repeat()]
    
    for element in output:
        vampytest.assert_instance(element, FrameProxyBase)
        
    vampytest.assert_eq(len(output), 3)
