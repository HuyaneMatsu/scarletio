__all__ = ()

class Token:
    """
    Represents a token parsed by ``HighlightContextBase``.
    
    Attributes
    ----------
    type : `int`
        The token's identifier.
    value : `str`
        The token's value.
    """
    __slots__ = ('type', 'value',)
    
    def __new__(cls, type_, value):
        """
        Creates a new ``Token``.
        
        Parameters
        ----------
        type_ : `int`
            The token's identifier.
        value : `str`
            The token's value.
        """
        self = object.__new__(cls)
        self.type = type_
        self.value = value
        return self
    
    def __repr__(self):
        """Returns the token's representation."""
        return f'{self.__class__.__name__}({self.type}, {self.value!r})'
    
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        if self.type != other.type:
            return False
        
        if self.value != other.value:
            return False
        
        return True
