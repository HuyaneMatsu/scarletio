__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType


class Token(RichAttributeErrorBaseType):
    """
    Represents a token parsed by the highlighter.
    
    Attributes
    ----------
    location : ``Location``
        The token's value.
    
    type : `int`
        The token's identifier.
    """
    __slots__ = ('location', 'type')
    
    def __new__(cls, token_type, location):
        """
        Creates a new token.
        
        Parameters
        ----------
        token_type : `int`
            The token's identifier.
        
        location : ``Location``
            The token's location.
        """
        self = object.__new__(cls)
        self.type = token_type
        self.location = location
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return ''.join([
            type(self).__name__, '(',
            repr(self.type), ', ',
            repr(self.location),
            ')',
        ])
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.type != other.type:
            return False
        
        if self.location != other.location:
            return False
        
        return True
