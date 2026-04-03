import vampytest

from ..frame_group import FRAME_GROUP_TYPE_NONE, FRAME_GROUP_TYPE_REPEAT, FRAME_GROUP_TYPE_SINGLES, FrameGroup
from ..frame_proxy import FrameProxyBase, FrameProxyVirtual
from ..tests.helper_create_dummy_expression_info import create_dummy_expression_info


def _assert_fields_set(frame_group):
    """
    Asserts whether every fields are set of the given frame group.
    """
    vampytest.assert_instance(frame_group, FrameGroup)
    vampytest.assert_instance(frame_group.frames, list, nullable = True)
    vampytest.assert_instance(frame_group.type, int)
    vampytest.assert_instance(frame_group.repeat_count, int)


def test__FrameGroup__new():
    """
    Tests whether ``FrameGroup.__new__`` works as intended.
    """
    frame_group = FrameGroup()
    _assert_fields_set(frame_group)
    
    vampytest.assert_is(frame_group.frames, None)
    vampytest.assert_eq(frame_group.repeat_count, 0)
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_NONE)


def test__FrameGroup__create_repeated():
    """
    tests whether ``FrameGroup.__create_repeated`` works as intended. 
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    _assert_fields_set(frame_group)
    
    vampytest.assert_eq(frame_group.frames, frame_proxies)
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_REPEAT)
    vampytest.assert_eq(frame_group.repeat_count, repeat_count)


def test__FrameGroup__eq():
    """
    Tests whether ``FrameGroup.__eq__`` works as intended.
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    vampytest.assert_eq(frame_group, frame_group)
    vampytest.assert_ne(frame_group, object())
    
    
    test_fram_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py', locals = {'hey': 'mister'}),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    test_frame_group = FrameGroup._create_repeated(test_fram_proxies, repeat_count)
    vampytest.assert_ne(frame_group, test_frame_group)
    


def test__FrameGroup__mod():
    """
    Tests whether ``FrameGroup.__mod__`` works as intended.
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    vampytest.assert_true(frame_group % frame_group)
    
    with vampytest.assert_raises(TypeError):
        frame_group % object()
    
    
    test_fram_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py', locals = {'hey': 'mister'}),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    test_frame_group = FrameGroup._create_repeated(test_fram_proxies, repeat_count)
    vampytest.assert_true(frame_group % test_frame_group)
    
    test_fram_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'orin.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    test_frame_group = FrameGroup._create_repeated(test_fram_proxies, repeat_count)
    vampytest.assert_false(frame_group % test_frame_group)


def test__FrameGroup__len__empty():
    """
    Tests whether ``FrameGroup.__len__`` works as intended.
    
    Case: Empty.
    """
    frame_group = FrameGroup()
    
    output = len(frame_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


def test__FrameGroup__len__non_repeated():
    """
    Tests whether ``FrameGroup.__len__`` works as intended.
    
    Case: Non-repeated.
    """
    frame_group = FrameGroup()
    frame_group.try_add_frame(FrameProxyVirtual.from_fields(file_name = 'koishi.py'))
    frame_group.try_add_frame(FrameProxyVirtual.from_fields(file_name = 'satori.py'))
    
    output = len(frame_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)


def test__FrameGroup__len__repeated():
    """
    Tests whether ``FrameGroup.__len__`` works as intended.
    
    Case: Repeated.
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = len(frame_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 20)


def test__FrameGroup__bool__empty():
    """
    Tests whether ``FrameGroup.__bool__`` works as intended.
    """
    frame_group = FrameGroup()
    
    output = bool(frame_group)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__FrameGroup__bool__non_repeated():
    """
    Tests whether ``FrameGroup.__bool__`` works as intended.
    
    Case: Non-repeated.
    """
    frame_group = FrameGroup()
    frame_group.try_add_frame(FrameProxyVirtual.from_fields(file_name = 'koishi.py'))
    frame_group.try_add_frame(FrameProxyVirtual.from_fields(file_name = 'satori.py'))
    
    output = bool(frame_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, True)


def test__FrameGroup__bool__repeated():
    """
    Tests whether ``FrameGroup.__bool__`` works as intended.
    
    Case: Repeated.
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = bool(frame_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, True)


def test__FrameGroup__repr__repeated():
    """
    Tests whether ``FrameGroup.__bool__`` works as intended.
    
    Case: Repeated.
    """
    repeat_count = 10
    frame_proxies = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = repr(frame_group)
    vampytest.assert_instance(output, str)


def test__FrameGroup__iter_frames__empty():
    """
    Tests whether ``FrameGroup.iter_frames`` works as intended.
    
    Case: Empty.
    """
    frame_group = FrameGroup()
    
    output = [*frame_group.iter_frames()]
    vampytest.assert_eq(output, [])
    vampytest.assert_is(frame_group.frames, None)


def test__FrameGroup__iter_frames__non_repeated():
    """
    Tests whether ``FrameGroup.iter_frames`` works as intended.
    
    Case: Non-repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    output = [*frame_group.iter_frames()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])


def test__FrameGroup__iter_frames__repeated():
    """
    Tests whether ``FrameGroup.iter_frames`` works as intended.
    
    Case: Repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    repeat_count = 2
    frame_proxies = [frame_proxy_0, frame_proxy_1]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = [*frame_group.iter_frames()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1, frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])


def test__FrameGroup__iter_exhaust_frames__empty():
    """
    Tests whether ``FrameGroup.iter_exhaust_frames`` works as intended.
    
    Case: Empty.
    """
    frame_group = FrameGroup()
    
    output = [*frame_group.iter_exhaust_frames()]
    vampytest.assert_eq(output, [])
    vampytest.assert_is(frame_group.frames, None)


def test__FrameGroup__iter_exhaust_frames__non_repeated():
    """
    Tests whether ``FrameGroup.iter_exhaust_frames`` works as intended.
    
    Case: Non-repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    output = [*frame_group.iter_exhaust_frames()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_is(frame_group.frames, None)


def test__FrameGroup__iter_exhaust_frames__repeated():
    """
    Tests whether ``FrameGroup.iter_exhaust_frames`` works as intended.
    
    Case: Repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    repeat_count = 2
    frame_proxies = [frame_proxy_0, frame_proxy_1]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = [*frame_group.iter_exhaust_frames()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1, frame_proxy_0, frame_proxy_1])
    vampytest.assert_is(frame_group.frames, None)


def test__FrameGroup__iter_exhaust_frames__clear():
    """
    Tests whether ``FrameGroup.clear`` works as intended.
    
    Case: Non-repeated.
    """
    frame_group = FrameGroup()
    frame_group.try_add_frame(FrameProxyVirtual.from_fields(file_name = 'koishi.py'))
    
    frame_group.clear()
    _assert_fields_set(frame_group)
    
    vampytest.assert_is(frame_group.frames, None)
    vampytest.assert_eq(frame_group.repeat_count, 0)
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_NONE)


def test__FrameGroup__try_add_frame__empty_non_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding a single frame to a repeat group.
    """
    frame_group = FrameGroup()
    
    frame = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    output = frame_group.try_add_frame(frame)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group.frames, [frame])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_SINGLES)


def test__FrameGroup__try_add_frame__empty_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding repeat frame to an empty group.
    """
    frame_group = FrameGroup()
    
    frame = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame.expression_info = create_dummy_expression_info(frame.expression_key, '')
    frame.alike_count = 2
    
    output = frame_group.try_add_frame(frame)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group.frames, [frame])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_REPEAT)


def test__FrameGroup__try_add_frame__singles_non_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding single frame to a single group.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)

    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    output = frame_group.try_add_frame(frame_proxy_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_SINGLES)


def test__FrameGroup__try_add_frame__singles_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding repeated frame to a single group.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)

    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, '')
    frame_proxy_1.alike_count = 2
    
    output = frame_group.try_add_frame(frame_proxy_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_SINGLES)


def test__FrameGroup__try_add_frame__repeat_non_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding single frame to a repeat group.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)

    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    output = frame_group.try_add_frame(frame_proxy_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_REPEAT)


def test__FrameGroup__try_add_frame__repeat_repeat():
    """
    Tests whether ``FrameGroup.try_add_frame`` works as intended.
    
    Case: Adding a repeat frame to a repeat group.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)

    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, '')
    frame_proxy_1.alike_count = 2
    
    output = frame_group.try_add_frame(frame_proxy_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.type, FRAME_GROUP_TYPE_REPEAT)


def test__FrameGroup__try_merge__single_with_short_repeat():
    """
    Tests whether ``FrameGroup.try_merge`` works as intended.
    
    Case: Merging single with short repeat.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, '')
    frame_proxy_1.alike_count = 2
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)

    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_1)
    
    output = frame_group_0.try_merge(frame_group_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group_0.frames, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group_0.type, FRAME_GROUP_TYPE_SINGLES)
    
    vampytest.assert_eq(frame_group_1.frames, None)
    vampytest.assert_eq(frame_group_1.type, FRAME_GROUP_TYPE_NONE)


def test__FrameGroup__try_merge__single_with_single():
    """
    Tests whether ``FrameGroup.try_merge`` works as intended.
    
    Case: Merging single with single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)

    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_1)
    
    output = frame_group_0.try_merge(frame_group_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group_0.frames, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group_0.type, FRAME_GROUP_TYPE_SINGLES)
    
    vampytest.assert_eq(frame_group_1.frames, None)
    vampytest.assert_eq(frame_group_1.type, FRAME_GROUP_TYPE_NONE)


def test__FrameGroup__try_merge__short_repeat_with_singles():
    """
    Tests whether ``FrameGroup.try_merge`` works as intended.
    
    Case: Merging short repeat with single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)

    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_1)
    
    output = frame_group_0.try_merge(frame_group_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    
    vampytest.assert_eq(frame_group_0.frames, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group_0.type, FRAME_GROUP_TYPE_SINGLES)
    
    vampytest.assert_eq(frame_group_1.frames, None)
    vampytest.assert_eq(frame_group_1.type, FRAME_GROUP_TYPE_NONE)


def test__FrameGroup__try_merge__single_with_long_repeat():
    """
    Tests whether ``FrameGroup.try_merge`` works as intended.
    
    Case: Merging single with long repeat.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_1.expression_key, '')
    frame_proxy_1.alike_count = 3
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)

    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_1)
    frame_group_1.try_add_frame(frame_proxy_1)
    frame_group_1.try_add_frame(frame_proxy_1)
    
    output = frame_group_0.try_merge(frame_group_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    
    vampytest.assert_eq(frame_group_0.frames, [frame_proxy_0])
    vampytest.assert_eq(frame_group_0.type, FRAME_GROUP_TYPE_SINGLES)
    
    vampytest.assert_eq(frame_group_1.frames, [frame_proxy_1, frame_proxy_1, frame_proxy_1])
    vampytest.assert_eq(frame_group_1.type, FRAME_GROUP_TYPE_REPEAT)


def test__FrameGroup__try_merge__long_repeat_with_singles():
    """
    Tests whether ``FrameGroup.try_merge`` works as intended.
    
    Case: Merging long repeat with single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 3
    
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_0)
    
    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_1)
    
    output = frame_group_0.try_merge(frame_group_1)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    
    vampytest.assert_eq(frame_group_0.frames, [frame_proxy_0, frame_proxy_0, frame_proxy_0])
    vampytest.assert_eq(frame_group_0.type, FRAME_GROUP_TYPE_REPEAT)
    
    vampytest.assert_eq(frame_group_1.frames, [frame_proxy_1])
    vampytest.assert_eq(frame_group_1.type, FRAME_GROUP_TYPE_SINGLES)


def test__FrameGroup__copy():
    """
    Tests whether ``FrameGroup.copy`` works as intended.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 3
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_0)
    
    copy = frame_group.copy()
    _assert_fields_set(copy)
    vampytest.assert_is_not(copy, frame_group)    
    vampytest.assert_true(copy % frame_group)


def test__FrameGroup__iter_separate_repeated__single():
    """
    Tests whether ``FrameGroup.iter_separate_repeated`` works as intended.
    
    Case: Single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')

    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    
    output = [*frame_group_0.copy().iter_separate_repeated()]
    vampytest.assert_eq(len(output), 1)
        
    checked, frame_group = output[0]
    vampytest.assert_eq(checked, True)
    vampytest.assert_true(frame_group % frame_group_0)


def test__FrameGroup__iter_separate_repeated__repeat_no_pattern():
    """
    Tests whether ``FrameGroup.iter_separate_repeated`` works as intended.
    
    Case: Single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_1.alike_count = 2

    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    
    output = [*frame_group_0.copy().iter_separate_repeated()]
    vampytest.assert_eq(len(output), 1)
        
    checked, frame_group = output[0]
    vampytest.assert_eq(checked, True)
    vampytest.assert_true(frame_group % frame_group_0)


def test__FrameGroup__iter_separate_repeated__repeat_with_pattern():
    """
    Tests whether ``FrameGroup.iter_separate_repeated`` works as intended.
    
    Case: Single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_1.alike_count = 2

    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    
    output = [*frame_group_0.copy().iter_separate_repeated()]
    vampytest.assert_eq(len(output), 1)
        
    checked, frame_group = output[0]
    vampytest.assert_eq(checked, True)
    vampytest.assert_true(frame_group % FrameGroup._create_repeated([frame_proxy_0, frame_proxy_1], 2))


def test__FrameGroup__iter_separate_repeated__repeat_with_pattern_between():
    """
    Tests whether ``FrameGroup.iter_separate_repeated`` works as intended.
    
    Case: Single.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_0.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_0.alike_count = 2
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_1.alike_count = 2
    frame_proxy_2 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_proxy_2.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_2.alike_count = 2
    frame_proxy_3 = FrameProxyVirtual.from_fields(file_name = 'okuu.py')
    frame_proxy_3.expression_info = create_dummy_expression_info(frame_proxy_0.expression_key, '')
    frame_proxy_3.alike_count = 2

    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_proxy_2)
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    frame_group_0.try_add_frame(frame_proxy_0)
    frame_group_0.try_add_frame(frame_proxy_1)
    frame_group_0.try_add_frame(frame_proxy_3)
    
    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_proxy_2)
    
    frame_group_2 = FrameGroup()
    frame_group_2.try_add_frame(frame_proxy_3)
    
    output = [*frame_group_0.copy().iter_separate_repeated()]
    vampytest.assert_eq(len(output), 3)
    
    checked, frame_group = output[0]
    vampytest.assert_eq(checked, False)
    vampytest.assert_true(frame_group % frame_group_1)

    checked, frame_group = output[1]
    vampytest.assert_eq(checked, True)
    vampytest.assert_true(frame_group % FrameGroup._create_repeated([frame_proxy_0, frame_proxy_1], 2))

    checked, frame_group = output[2]
    vampytest.assert_eq(checked, False)
    vampytest.assert_true(frame_group % frame_group_2)


def test__FrameGroup__drop_variables__no_frames():
    """
    Tests whether ``FrameGroup.drop_variables`` works as intended.
    
    Case: No frames.
    """
    frame_group = FrameGroup()
    frame_group_expected = FrameGroup()
    
    frame_group.drop_variables()
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__drop_variables__with_frames():
    """
    Tests whether ``FrameGroup.drop_variables`` works as intended.
    
    Case: has frames.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py', locals = {'hey': 'mister'})
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_2 = FrameProxyVirtual.from_fields(file_name = 'koishi.py', locals = {'hey': 'mister'})
    frame_proxy_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_2)
    
    frame_group_expected = FrameGroup()
    frame_group_expected.try_add_frame(frame_proxy_1)
    frame_group_expected.try_add_frame(frame_proxy_3)
    
    frame_group.drop_variables()
    vampytest.assert_eq(frame_group, frame_group_expected)


def _iter_options__has_variables():
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py', locals = {'hey': 'mister'})
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_2 = FrameProxyVirtual.from_fields(file_name = 'koishi.py', locals = {'hey': 'mister'})
    frame_proxy_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    # no variables (no frames)
    frame_group = FrameGroup()
    yield frame_group, False
    
    # variables
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_2)
    yield frame_group, True
    
    # no variables
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_1)
    frame_group.try_add_frame(frame_proxy_3)
    yield frame_group, False
    
    # mixed
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    yield frame_group, True


@vampytest._(vampytest.call_from(_iter_options__has_variables()).returning_last())
def test__FrameGroup__has_variables(frame_group):
    """
    Tests whether ``FrameGroup.has_variables`` works as intended.
    
    Parameters
    ----------
    frame_group : ``FrameGroup``
        The frame group to test.
    
    Returns
    -------
    output : `bool`
    """
    output = frame_group.has_variables()
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__get_last_frame():
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py', locals = {'hey': 'mister'})
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    frame_group = FrameGroup()
    yield frame_group, None
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    yield frame_group, frame_proxy_0
    
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    yield frame_group, frame_proxy_1
    

@vampytest._(vampytest.call_from(_iter_options__get_last_frame()).returning_last())
def test__FrameGroup__get_last_frame(frame_group):
    """
    Tests whether ``FrameGroup.get_last_frame`` works as intended.
    
    Parameters
    ----------
    frame_group : ``FrameGroup``
        The frame group to test.
    
    Returns
    -------
    output : `None | FrameProxyBase`
    """
    output = frame_group.get_last_frame()
    vampytest.assert_instance(output, FrameProxyBase, nullable = True)
    return output


def test__FrameGroup__copy_without_variables():
    """
    Tests whether ``FrameGroup.copy_without_variables`` works as intended.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py', locals = {'hey': 'mister'})
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_2 = FrameProxyVirtual.from_fields(file_name = 'koishi.py', locals = {'hey': 'mister'})
    frame_proxy_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_2)
    
    frame_group_expected = FrameGroup()
    frame_group_expected.try_add_frame(frame_proxy_1)
    frame_group_expected.try_add_frame(frame_proxy_3)
    
    copy = frame_group.copy_without_variables()
    _assert_fields_set(copy)
    vampytest.assert_is_not(copy, frame_group)
    
    vampytest.assert_eq(copy, frame_group_expected)


def test__FrameGroup__drop_ignored_frames():
    """
    Tests whether ``FrameGroup.drop_ignored_frames`` works as intended.
    
    Case: No frames.
    """
    frame_group = FrameGroup()
    frame_group_expected = FrameGroup()
    
    frame_group.drop_ignored_frames()
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__drop_ignored_frames__with_frames():
    """
    Tests whether ``FrameGroup.drop_ignored_frames`` works as intended.
    
    Case: has frames.
    """
    def filter(frame):
        return frame.file_name == 'satori.py'
    
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    frame_group_expected = FrameGroup()
    frame_group_expected.try_add_frame(frame_proxy_0)
    
    frame_group.drop_ignored_frames(filter = filter)
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__drop_ignored_frames__with_frames_to_no_frames():
    """
    Tests whether ``FrameGroup.drop_ignored_frames`` works as intended.
    
    Case: has frames to has no frames.
    """
    def filter(frame):
        return False
    
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    frame_group_expected = FrameGroup()
    
    frame_group.drop_ignored_frames(filter = filter)
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__apply_frame_filter():
    """
    Tests whether ``FrameGroup.apply_frame_filter`` works as intended.
    
    Case: No frames.
    """
    def filter(frame):
        return True
    
    frame_group = FrameGroup()
    frame_group_expected = FrameGroup()
    
    frame_group.apply_frame_filter(filter)
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__apply_frame_filter__with_frames():
    """
    Tests whether ``FrameGroup.apply_frame_filter`` works as intended.
    
    Case: has frames.
    """
    def filter(frame):
        return frame.file_name == 'satori.py'
    
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    frame_group_expected = FrameGroup()
    frame_group_expected.try_add_frame(frame_proxy_0)
    
    frame_group.apply_frame_filter(filter)
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__apply_frame_filter__with_frames_to_no_frames():
    """
    Tests whether ``FrameGroup.apply_frame_filter`` works as intended.
    
    Case: has frames to has no frames.
    """
    def filter(frame):
        return False
    
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    frame_group_expected = FrameGroup()
    
    frame_group.apply_frame_filter(filter)
    vampytest.assert_eq(frame_group, frame_group_expected)


def test__FrameGroup__iter_frames_no_repeat__empty():
    """
    Tests whether ``FrameGroup.iter_frames_no_repeat`` works as intended.
    
    Case: Empty.
    """
    frame_group = FrameGroup()
    
    output = [*frame_group.iter_frames_no_repeat()]
    vampytest.assert_eq(output, [])
    vampytest.assert_is(frame_group.frames, None)


def test__FrameGroup__iter_frames_no_repeat__non_repeated():
    """
    Tests whether ``FrameGroup.iter_frames_no_repeat`` works as intended.
    
    Case: Non-repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_group = FrameGroup()
    frame_group.try_add_frame(frame_proxy_0)
    frame_group.try_add_frame(frame_proxy_1)
    
    output = [*frame_group.iter_frames_no_repeat()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])


def test__FrameGroup__iter_frames_no_repeat__repeated():
    """
    Tests whether ``FrameGroup.iter_frames_no_repeat`` works as intended.
    
    Case: Repeated.
    """
    frame_proxy_0 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_proxy_1 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    
    repeat_count = 2
    frame_proxies = [frame_proxy_0, frame_proxy_1]
    
    frame_group = FrameGroup._create_repeated(frame_proxies, repeat_count)
    
    output = [*frame_group.iter_frames_no_repeat()]
    vampytest.assert_eq(output, [frame_proxy_0, frame_proxy_1])
    vampytest.assert_eq(frame_group.frames, [frame_proxy_0, frame_proxy_1])
