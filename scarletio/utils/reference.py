__all__ = ('Reference',)

from .rich_attribute_error import RichAttributeErrorBaseType


class Reference(RichAttributeErrorBaseType):
    """
    Can be used to store a immutable.
    
    Parameters
    ----------
    value : `object`
        The stored value.
    """
    __slots__ = ('value',)
    
    def __new__(cls, value):
        """
        Creates a new reference with the given value.
        
        Parameters
        ----------
        value : `object`
            The value to store.
        """
        self = object.__new__(cls)
        self.value = value
        return self
    
    
    def __eq__(self, other):
        """Returns whether the two references store the same value."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value == other.value
    
    
    def __repr__(self):
        """Returns the reference's representation"""
        return f'<{self.__class__.__name__} to {self.value!r}>'
