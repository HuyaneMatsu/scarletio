__all__ = ('ExceptionProxyBase',)

from ..exception_representation import ExceptionRepresentationBase
from ..frame_grouping import normalize_frame_groups


class ExceptionProxyBase:
    """
    Base type for exception proxies.
    """
    __slots__ = ()
    
    def __new__(cls):
        """
        Creates a new exception proxy.
        """
        return object.__new__(cls)
    
    
    @property
    def exception_representation(self):
        """
        Returns the exception's representation.
        
        Returns
        -------
        exception_representation : `None | ExceptionRepresentationBase`
        """
        return None
    
    
    @property
    def frame_groups(self):
        """
        Returns the exception's grouped frames.
        
        Returns
        -------
        frame_groups : `None | list<FrameGroup>`
        """
        return None
    
    
    @frame_groups.setter
    def frame_groups(self, value):
        if (value is not None):
            raise RuntimeError('Cannot set attribute to non-default.')
    
    
    def __repr__(self):
        """Returns the exception proxy's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # exception_representation
        exception_representation = self.exception_representation
        if (exception_representation is not None):
            repr_parts.append(' exception_representation = ')
            repr_parts.append(repr(exception_representation))
            
            field_added = True
        else:
            field_added = False
        
        # frame_groups
        frame_groups = self.frame_groups
        if (frame_groups is not None):
            if field_added:
                repr_parts.append(',')
            repr_parts.append(' frame_groups = ')
            repr_parts.append(repr(frame_groups))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two exception proxies are equal."""
        if not isinstance(other, ExceptionProxyBase):
            return NotImplemented
        
        return self._is_equal(other)
    
    
    def __len__(self):
        """Returns the amount of frames in the exception proxy."""
        return sum(len(frame_group) for frame_group in self.iter_frame_groups())
    
    
    def _is_equal(self, other):
        """
        Returns whether the two exception proxies are equal.
        
        Parameters
        ----------
        other : ``ExceptionProxyBase``
            The other instance.
        
        Returns
        -------
        is_equal : `bool`
        """
        if self.exception_representation != other.exception_representation:
            return False
        
        if self.frame_groups != other.frame_groups:
            return False
        
        return True
    
    
    def __mod__(self, other):
        """Returns whether the two exception proxies are alike."""
        if not isinstance(other, ExceptionProxyBase):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def __rmod__(self, other):
        """Returns whether the two exception proxies are alike."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def _is_alike(self, other):
        """
        Returns whether the exception proxies are alike.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other instance.
        
        Returns
        -------
        is_alike : `bool`
        """
        # exception_representation
        if self.exception_representation != other.exception_representation:
            return False
        
        # frame_groups
        if len(self) != len(other):
            return False
        
        for self_frame_group, other_frame_group in zip(self.iter_frame_groups(), other.iter_frame_groups()):
            if not (self_frame_group % other_frame_group):
                return False
        
        return True
    
    
    def drop_variables(self):
        """
        Drops the variables of the exception representation.
        """
        for frame_group in self.iter_frame_groups():
            frame_group.drop_variables()
    
    
    def has_variables(self):
        """
        Returns whether any frame group inherited variables on creation.
        
        Returns
        -------
        has_variables : `bool`
        """
        for frame_group in self.iter_frame_groups():
            if frame_group.has_variables():
                return True
        
        return False
    
    
    def iter_frame_groups(self):
        """
        Iterates over the frame groups of the exception proxy.
        
        This method is an iterable generator.
        
        Yields
        ------
        frame_group : ``FrameGroup``
        """
        frame_groups = self.frame_groups
        if (frame_groups is not None):
            yield from frame_groups
    
    
    def drop_ignored_frames(self, *, filter = None):
        """
        Drops the frames that should be ignored.
        
        Parameters
        ----------
        filter : `None | callable` = `None`, Optional (Keyword only)
            Additional filter to check whether a frame should be shown.
        """
        for frame_group in self.iter_frame_groups():
            frame_group.drop_ignored_frames(filter = filter)
        
        self.frame_groups = normalize_frame_groups(self.frame_groups)
    
    
    def apply_frame_filter(self, filter):
        """
        Keeps the frames that pass the given `filter`.
        
        Parameters
        ----------
        filter : `callable`
            Filter to check whether a frame should be kept.
        """
        for frame_group in self.iter_frame_groups():
            frame_group.apply_frame_filter(filter)
        
        self.frame_groups = normalize_frame_groups(self.frame_groups)
    
    
    def iter_frames_no_repeat(self):
        """
        Iterates over the frames of the exception proxy without repeating repeated blocks.
        It may still happen that non-unique frames are yielded.
        
        This method is an iterable generator.
        
        Yields
        ------
        frame : ``FrameProxyBase``
        """
        for frame_group in self.iter_frame_groups():
            yield from frame_group.iter_frames_no_repeat()
