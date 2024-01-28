__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType

from .frame_proxy import FrameProxyVirtual
from .repeat_strategies import get_repeat_with_strategy_bot


FRAME_GROUP_TYPE_NONE = 0
FRAME_GROUP_TYPE_SINGLES = 1
FRAME_GROUP_TYPE_REPEAT = 2


class FrameGroup(RichAttributeErrorBaseType):
    """
    Represents grouped frames.
    
    Attributes
    ----------
    frames : `None | list<FrameProxyBase>`
        The grouped up frames.
    repeat_count : `int`
        How much times the wrapped frames are grouped.
    type : `int`
        Information about how the frames are grouped.
    """
    __slots__ = ('frames', 'repeat_count', 'type')
    
    def __new__(cls):
        """
        Creates a new frame group.
        """
        self = object.__new__(cls)
        self.frames = None
        self.type = FRAME_GROUP_TYPE_NONE
        self.repeat_count = 0
        return self
    
    
    @classmethod
    def _create_repeated(cls, frames, repeat_count):
        """
        Creates a repeated frame group.
        
        Parameters
        ----------
        frames : `list<FrameProxyBase>`
            The stored frames by the group.
        repeat_count : `int`
            How much times is the group repeated.
        
        Returns
        -------
        self : ``FrameGroup``
        """
        self = object.__new__(cls)
        self.frames = frames
        self.repeat_count = repeat_count
        self.type = FRAME_GROUP_TYPE_REPEAT
        return self
    
    
    def __eq__(self, other):
        """Returns whether the two frame groups are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_equal(other)
    
    
    def _is_equal(self, other):
        """
        Returns whether the two frame groups are equal.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other instance.
        
        Returns
        -------
        is_equal : `bool`
        """
        if len(self) != len(other):
            return False
        
        for self_frame, other_frame in zip(self.iter_frames(), other.iter_frames()):
            if self_frame != other_frame:
                return False
        
        return True
    
    
    def __mod__(self, other):
        """Returns whether the two frame groups are alike."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def __rmod__(self, other):
        """Returns whether the two frame proxies are alike."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def _is_alike(self, other):
        """
        Returns whether the frame groups are alike.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other instance.
        
        Returns
        -------
        is_alike : `bool`
        """
        if len(self) != len(other):
            return False
        
        for self_frame, other_frame in zip(self.iter_frames(), other.iter_frames()):
            if not (self_frame % other_frame):
                return False
        
        return True
        
    
    def __len__(self):
        """Returns how much frames are in the group."""
        frames = self.frames
        if frames is None:
            return 0
        
        return len(frames) * self.repeat_count
    
    
    def __repr__(self):
        """Returns the frame group's representation."""
        repr_parts = ['<', type(self).__name__]
        
        field_added = False
        
        repeat_count = self.repeat_count
        if repeat_count > 1:
            field_added = True
            repr_parts.append(' repeat_count = ')
            repr_parts.append(repr(repeat_count))
        
        frames = self.frames
        if (frames is not None):
            if field_added:
                repr_parts.append(',')
            
            repr_parts.append(' frames = ')
            repr_parts.append(repr(frames))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __bool__(self):
        """Returns whether the frame group has any elements."""
        return self.type != FRAME_GROUP_TYPE_NONE
    
    
    def iter_frames(self):
        """
        Iterates over the frames of the frame group.
        
        This method is an iterable generator.
        
        Yields
        ------
        frame : ``FrameProxyBase``
        """
        frames = self.frames
        if (frames is not None):
            for index in range(self.repeat_count):
                yield from frames
    
    
    def iter_exhaust_frames(self):
        """
        Iterates over the frames of the frame group, exhausting its own.
        
        This method is an iterable generator.
        
        Yields
        ------
        frame : ``FrameProxyBase``
        """
        try:
            yield from self.iter_frames()
        finally:
            self.clear()
    
    
    def clear(self):
        """
        Clears the frame group.
        """
        self.frames = None
        self.repeat_count = 0
        self.type = FRAME_GROUP_TYPE_NONE
    
    
    def copy(self):
        """
        Copies the frame group.
        
        Returns
        -------
        new : `instance<type<self>>`
        """
        new = object.__new__(type(self))
        frames = self.frames
        if (frames is not None):
            frames = frames.copy()
        new.frames = frames
        new.repeat_count = self.repeat_count
        new.type = self.type
        return new
    
    
    def drop_variables(self):
        """
        Drops the variables of the frame group.
        """
        frames = self.frames
        if (frames is not None):
            self.frames = [FrameProxyVirtual(frame, with_variables = False) for frame in frames]
    
    
    def has_variables(self):
        """
        Returns whether any frames inherited variables on creation.
        
        Returns
        -------
        has_variables : `bool`
        """
        frames = self.frames
        if (frames is not None):
            for frame in frames:
                if frame.has_variables():
                    return True
        
        return False
    
    
    def try_add_frame(self, frame):
        """
        Tries to add the given frame to self. On success returns `True`.
        
        Parameters
        ----------
        frame : ``FrameProxyBase``
            The frame to add.
        
        Returns
        -------
        success : `bool`
        """
        group_type = self.type
        
        if group_type == FRAME_GROUP_TYPE_NONE:
            self.frames = [frame]
            self.repeat_count = 1
            
            if frame.mention_count > 1:
                group_type = FRAME_GROUP_TYPE_REPEAT
            else:
                group_type = FRAME_GROUP_TYPE_SINGLES
            self.type = group_type
            return True
        
        if group_type == FRAME_GROUP_TYPE_SINGLES:
            if frame.mention_count > 1:
                return False
            
            self.frames.append(frame)
            return True
        
        
        if group_type == FRAME_GROUP_TYPE_REPEAT:
            if frame.mention_count <= 1:
                return False
            
            self.frames.append(frame)
            return True
        
        # No more cases
        return False
    
    
    def try_merge(self, other):
        """
        Tries to merge self with an other frame group.
        
        Parameters
        ----------
        other : `instance<cls>`
            The frame group to merge self with.
        
        Returns
        -------
        merged : `bool`
        """
        if (self.repeat_count != 1) or (other.repeat_count != 1):
            return False
        
        self_group_type = self.type
        other_group_type = other.type
        
        # single + single
        if self_group_type == FRAME_GROUP_TYPE_SINGLES and other_group_type == FRAME_GROUP_TYPE_SINGLES:
            should_merge = True
        
        # single + repeat -> short
        elif self_group_type == FRAME_GROUP_TYPE_SINGLES and other_group_type == FRAME_GROUP_TYPE_REPEAT:
            if len(other.frames) <= 2:
                should_merge = True
            else:
                should_merge = False
        
        # repeat + single -> short
        elif self_group_type == FRAME_GROUP_TYPE_REPEAT and other_group_type == FRAME_GROUP_TYPE_SINGLES:
            if len(self.frames) <= 2:
                should_merge = True
            else:
                should_merge = False
        
        # `repeat + repeat` cannot happen
        else:
            should_merge = False
        
        if should_merge:
            self.frames.extend(other.iter_exhaust_frames())
            self.type = FRAME_GROUP_TYPE_SINGLES
        
        return should_merge
    
    
    def iter_separate_repeated(self):
        """
        Iterates over self producing repeated groups.
        
        Yields
        ------
        checked : `bool`
        frame_group : `instance<type<self>>`
        """
        # Yield self if non-repeat or if already processed repeat.
        if self.type != FRAME_GROUP_TYPE_REPEAT or self.repeat_count > 1:
            yield True, self
            return
        
        # Find repeat
        repeat_range = get_repeat_with_strategy_bot(self.frames)
        if repeat_range is None:
            self.type = FRAME_GROUP_TYPE_SINGLES
            yield True, self
            return
        
        start_shift, chunk_size, repeat = repeat_range
        frames = self.frames
        
        # fore part
        if start_shift > 0:
            yield False, self._create_repeated(frames[0 : start_shift], 1)
        
        # mid part
        yield True, self._create_repeated(frames[start_shift : start_shift + chunk_size], repeat)
        
        # last part
        frames_length = len(frames)
        end_shift = start_shift + chunk_size * repeat
        if frames_length > end_shift:
            yield False, self._create_repeated(frames[end_shift : frames_length], 1)
    
    
    def get_last_frame(self):
        """
        Returns the last frame of the frame group.
        
        Returns
        -------
        frame : `None | FrameProxyBase`
        """
        frames = self.frames
        if frames is not None:
            return frames[-1]
