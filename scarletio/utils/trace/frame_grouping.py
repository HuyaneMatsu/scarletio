__all__ = ()

from .expression_parsing import ExpressionInfo
from .frame_group import FrameGroup


def group_frames(frames):
    """
    Groups frames into frame groups and then normalises them into non-repeat and repeat sequences.
    
    Parameters
    ----------
    frames : `list<FrameGroupFrame>`
        The frames to group.
    
    Returns
    -------
    frame_groups : `None | list<FrameGroup>`
        The created frame groups.
    """
    # note: frames may be an empty list.
    if not frames:
        return None
    
    _count_alikes(frames)
    frame_groups = _group_frames_to_frame_groups(frames)
    frame_groups = _merge_frame_groups(frame_groups)
    frame_groups = _separate_repeats_in_frame_groups(frame_groups)
    frame_groups = _merge_frame_groups(frame_groups)
    return frame_groups


def _group_frames_to_frame_groups(frames):
    """
    Groups the frames to frame groups depending how much times a frame's expression is mentioned.
    
    Parameters
    ----------
    frames : `list<FrameGroupFrame>`
        The frames to group.
    
    Returns
    -------
    frame_groups : `list<FrameGroup>`
    """
    frame_group = FrameGroup()
    frame_groups = []
    
    for frame in frames:
        if not frame_group.try_add_frame(frame):
            frame_groups.append(frame_group)
            frame_group = FrameGroup()
            frame_group.try_add_frame(frame)
    
    if frame_group:
        frame_groups.append(frame_group)
    
    return frame_groups


def _merge_frame_groups(frame_groups):
    """
    Merges the given frame groups to produce bigger non-repeat frame groups.
    Call it after creating frame groups to merge too short to be repeated frame groups into single mention groups.
    Call also after separating repeats to merge the cut down non-repeat parts.
    
    Parameters
    ----------
    frame_groups : `list<frameGroup>`
        The frame groups to merge.
    
    Returns
    -------
    frame_groups : `list<FrameGroup>`
    """
    outcome = []
    frame_group_0 = None
    
    for frame_group_1 in frame_groups:
        if (frame_group_0 is not None) and frame_group_0.try_merge(frame_group_1):
            continue
        
        frame_group_0 = frame_group_1
        outcome.append(frame_group_0)
        continue
    
    return outcome


def _separate_repeats_in_frame_groups(frame_groups):
    """
    Separates the repeated parts down. Each frame may produce `itself` or `before - middle (repeated) - after` parts.
    Repeat separating is then again applied to the `before` and `after` parts till every frame group is either
    marked as single-mention or repeat.
    
    Using a flattened algorithm to avoid recursion.
    
    Parameters
    ----------
    frame_groups : `list<frameGroup>`
        The frame groups to merge.
    
    Returns
    -------
    frame_groups : `list<FrameGroup>`
    """
    frame_groups_to_do = [(False, frame_group) for frame_group in reversed(frame_groups)]
    frame_groups = []
    
    while frame_groups_to_do:
        checked, frame_group = frame_groups_to_do.pop()
        if checked:
            frame_groups.append(frame_group)
        else:
            # cant assign it in order normally, so we reverse add it
            frame_groups_to_do.extend(reversed([*frame_group.iter_separate_repeated()]))
    
    return frame_groups


def _count_alikes(frames):
    """
    Counts how much alike frames there are.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase>`
        A list of frame proxies to create expression info for.
    """
    # Collect
    expressions = {}
    
    for frame in frames:
        expression_key = frame.expression_key
        
        try:
            alike_frames = expressions[expression_key]
        except KeyError:
            alike_frames = []
            expressions[expression_key] = alike_frames
        
        alike_frames.append(frame)
    
    # count
    for alike_frames in expressions.values():
        alike_count = len(alike_frames)
        for frame in alike_frames:
            frame.alike_count = alike_count


def normalize_frame_groups(frame_groups):
    """
    Normalises the given frame groups removing the empty ones.
    
    Parameters
    ----------
    frame_groups : `None | list<frameGroup>`
        The frame groups to merge.
    
    Returns
    -------
    frame_groups : `None | list<FrameGroup>`
    """
    if frame_groups is None:
        return None
    
    outcome = None
    
    for frame_group in frame_groups:
        if not frame_group:
            continue
        
        if outcome is None:
            outcome = []
        
        outcome.append(frame_group)
    
    return outcome
