import vampytest

from ..expression_parsing import ExpressionInfo
from ..frame_group import FrameGroup
from ..frame_grouping import (
    _count_alikes, _group_frames_to_frame_groups, _merge_frame_groups, _separate_repeats_in_frame_groups, group_frames,
    normalize_frame_groups
)
from ..frame_proxy import FrameProxyVirtual


def test__group_frames__no_frames():
    """
    Tests whether ``group_frames`` works as intended.
    
    Case: no frames given.
    """
    output = group_frames([])
    
    vampytest.assert_is(output, None)


def test__group_frames():
    """
    Tests whether ``group_frames`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_0.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_0.alike_count = 3

    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_1.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_1.alike_count = 2

    frame_2 = FrameProxyVirtual.from_fields(file_name = 'okuu.py')
    frame_2.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_2.alike_count = 1
    
    frame_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_3.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_3.alike_count = 1
    
    frames = [
        frame_0,
        frame_0,
        frame_0,
        frame_1,
        frame_2,
        frame_3,
    ]
    
    output = group_frames(frames)
    
    vampytest.assert_eq(
        output,
        [
            FrameGroup._create_repeated([frame_0], 3),
            FrameGroup._create_repeated([frame_1, frame_2, frame_3], 1)
        ],
    )


def test__group_frames_to_frame_groups():
    """
    tests whether ``_group_frames_to_frame_groups`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_0.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_0.alike_count = 3

    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_1.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_1.alike_count = 2

    frame_2 = FrameProxyVirtual.from_fields(file_name = 'okuu.py')
    frame_2.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_2.alike_count = 1
    
    frame_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_3.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_3.alike_count = 1
    

    frames = [
        frame_0,
        frame_0,
        frame_0,
        frame_1,
        frame_2,
        frame_3,
    ]
    
    output = _group_frames_to_frame_groups(frames)
    
    vampytest.assert_eq(
        output,
        [
            FrameGroup._create_repeated([frame_0, frame_0, frame_0, frame_1], 1),
            FrameGroup._create_repeated([frame_2, frame_3], 1)
        ],
    )
    

def test__merge_frame_groups():
    """
    tests whether ``_merge_frame_groups`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_0.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_0.alike_count = 3

    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_1.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_1.alike_count = 2

    frame_2 = FrameProxyVirtual.from_fields(file_name = 'okuu.py')
    frame_2.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_2.alike_count = 1
    
    frame_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_3.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_3.alike_count = 1
    
    
    frame_group_0 = FrameGroup._create_repeated([frame_0], 3)
    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_1)
    frame_group_2 = FrameGroup()
    frame_group_2.try_add_frame(frame_2)
    frame_group_2.try_add_frame(frame_3)
    
    
    output = _merge_frame_groups([frame_group_0, frame_group_1, frame_group_2])
    
    vampytest.assert_eq(
        output,
        [
            FrameGroup._create_repeated([frame_0], 3),
            FrameGroup._create_repeated([frame_1, frame_2, frame_3], 1)
        ],
    )
    

def test__separate_repeats_in_frame_groups():
    """
    tests whether ``_separate_repeats_in_frame_groups`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_0.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_0.alike_count = 3

    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_1.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_1.alike_count = 2

    frame_2 = FrameProxyVirtual.from_fields(file_name = 'okuu.py')
    frame_2.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_2.alike_count = 1
    
    frame_3 = FrameProxyVirtual.from_fields(file_name = 'koishi.py')
    frame_3.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_3.alike_count = 2
    
    frame_4 = FrameProxyVirtual.from_fields(file_name = 'reisen.py')
    frame_4.expression_info = ExpressionInfo(frame_4.expression_key, [], 0, True)
    frame_4.alike_count = 2

    frame_5 = FrameProxyVirtual.from_fields(file_name = 'tewi.py')
    frame_5.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_5.alike_count = 1
    
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_2)
    
    frame_group_1 = FrameGroup._create_repeated(
        [frame_1, frame_0, frame_0, frame_0, frame_3, frame_4, frame_3, frame_4],
        1,
    )
    
    frame_group_2 = FrameGroup()
    frame_group_2.try_add_frame(frame_5)
    
    
    output = _separate_repeats_in_frame_groups([frame_group_0, frame_group_1, frame_group_2])
    
    vampytest.assert_eq(
        output,
        [
            FrameGroup._create_repeated([frame_2], 1),
            FrameGroup._create_repeated([frame_1], 1),
            FrameGroup._create_repeated([frame_0], 3),
            FrameGroup._create_repeated([frame_3, frame_4], 2),
            FrameGroup._create_repeated([frame_5], 1),
        ],
    )


def test__normalize_frame_groups__none():
    """
    Tests whether ``normalize_frame_groups`` works as intended.
    
    Case: none given.
    """
    output = group_frames(None)
    
    vampytest.assert_is(output, None)


def test__normalize_frame_groups__no_valuable_frame_groups():
    """
    Tests whether ``normalize_frame_groups`` works as intended.
    
    Case: no valuable frame groups given.
    """
    frame_group_0 = FrameGroup()
    frame_group_1 = FrameGroup()
    
    output = normalize_frame_groups([frame_group_0, frame_group_1])
    
    vampytest.assert_is(output, None)


def test__normalize_frame_groups__valuable_frame_groups():
    """
    Tests whether ``normalize_frame_groups`` works as intended.
    
    Case: valuable frame groups given.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_0.expression_info = ExpressionInfo(frame_0.expression_key, [], 0, True)
    frame_0.alike_count = 1

    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_1.expression_info = ExpressionInfo(frame_1.expression_key, [], 0, True)
    frame_1.alike_count = 2
    
    frame_group_0 = FrameGroup()
    frame_group_0.try_add_frame(frame_0)
    frame_group_1 = FrameGroup()
    frame_group_1.try_add_frame(frame_1)
    
    output = normalize_frame_groups([frame_group_0, frame_group_1])
    
    vampytest.assert_eq(output, [frame_group_0, frame_group_1])


def test__count_alikes():
    """
    Tests whether ``_count_alikes`` works as intended.
    """
    frame_0 = FrameProxyVirtual.from_fields(file_name = 'satori.py')
    frame_1 = FrameProxyVirtual.from_fields(file_name = 'orin.py')
    frame_2 = FrameProxyVirtual.from_fields(file_name = 'satori.py')

    _count_alikes([frame_0, frame_1, frame_2])
    
    vampytest.assert_eq(frame_0.alike_count, 2)
    vampytest.assert_eq(frame_1.alike_count, 1)
    vampytest.assert_eq(frame_2.alike_count, 2)
