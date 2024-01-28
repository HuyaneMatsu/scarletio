__all__ = ('ExceptionRepresentationGeneric',)

from ...docs import copy_docs

from .exception_representation_base import ExceptionRepresentationBase
from .representation_helpers import get_exception_representation_generic


class ExceptionRepresentationGeneric(ExceptionRepresentationBase):
    """
    Holds a generic exception's representation.
    
    Attributes
    ----------
    representation : `str`
        The exception's representation.
    """
    __slots__ = ('representation',)
    
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
        representation = get_exception_representation_generic(exception)
        
        self = object.__new__(cls)
        self.representation = representation
        return self
    
    
    @classmethod
    def from_fields(cls, *, representation = ...):
        """
        Creates a new generic exception representation from the given fields.
        
        Parameters
        ----------
        representation : `str`
            The exception's representation.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.representation = '' if representation is ... else representation
        return self
    
    
    @copy_docs(ExceptionRepresentationBase._populate_repr_parts)
    def _populate_repr_parts(self, repr_parts):
        repr_parts.append(' representation = ')
        repr_parts.append(repr(self.representation))
    
    
    @copy_docs(ExceptionRepresentationBase._is_equal)
    def _is_equal(self, other):
        if self.representation != other.representation:
            return False
        
        return True
