__all__ = ('ExceptionRepresentationBase',)


class ExceptionRepresentationBase:
    """
    Holds an exception's representation.
    """
    __slots__ = ()
    
    def __new__(cls, exception, frame):
        """
        Creates a new exception representation.
        
        Parameters
        ----------
        exception : `BaseException`
            Exception to represent.
        frame : `None | FrameProxyBase`
            The frame the exception is raised from.
        """
        return object.__new__(cls)
    
    
    @classmethod
    def from_fields(cls):
        """
        Creates a new exception representation from the given fields.
        
        Returns
        -------
        self : `instance<cls>`
        """
        return object.__new__(cls)
    
    
    def __repr__(self):
        """Returns the exception representation's representation."""
        repr_parts = ['<', type(self).__name__]
        
        self._populate_repr_parts(repr_parts)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def _populate_repr_parts(self, repr_parts):
        """
        Helper for ``.__repr__`` to populate its parts with type specific information.
        
        Parameters
        ----------
        repr_parts : `list<str>`
            The representation parts to populate.
        """
        pass
    
    
    def __eq__(self, other):
        """Returns whether the two exception representations are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_equal(other)
    
    
    def _is_equal(self, other):
        """
        Returns whether the two exception representations are equal.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other instance. Must be same type as `self`.
        
        Returns
        -------
        is_equal : `bool`
        """
        return True
