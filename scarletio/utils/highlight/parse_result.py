__all__ = ('ParseResult',)

from ..rich_attribute_error import RichAttributeErrorBaseType


class ParseResult(RichAttributeErrorBaseType):
    """
    Representation of parsed code.
    
    Attributes
    ----------
    layers : ``list<Layer>``
        The generated layers.
    
    tokens : ``list<Token>``
        The generated tokens.
    """
    __slots__ = ('layers', 'tokens')
    
    def __new__(cls, layers, tokens):
        """
        Creates a new parse result.
        
        Parameters
        ----------
        layers : ``list<Layer>``
            The generated layers.
        
        tokens : ``list<Token>``
            The generated tokens.
        """
        self = object.__new__(cls)
        self.layers = layers
        self.tokens = tokens
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<']
        
        # layers
        repr_parts.append(' layers = ')
        repr_parts.append(repr(self.layers))
        
        # tokens
        repr_parts.append(' tokens = ')
        repr_parts.append(repr(self.tokens))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __iter__(self):
        """Unpacks the parse result."""
        yield self.layers
        yield self.tokens
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.layers != other.layers:
            return False
        
        if self.tokens != other.tokens:
            return False
        
        return True
    
