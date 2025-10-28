__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType


class Layer(RichAttributeErrorBaseType):
    """
    Represents a layer.
    
    Attributes
    ----------
    layer_outer_index : `int`
        The index of the outer layer.
    
    token_end_index : ``None | Token``
        The ending token's index of the layer.
    
    token_start_index : ``Token``
        The starting token's index of the layer.
    """
    __slots__ = ('layer_outer_index', 'token_end_index', 'token_start_index',)
    
    def __new__(cls, layer_outer_index, token_start_index, token_end_index):
        """
        Creates a new layer.
        
        Parameters
        ----------
        layer_outer_index : `int`
            The index of the outer layer.
        
        token_start_index : `int`
            The starting token's index of the layer.
        
        token_end_index : `int`
            The ending token's index of the layer.
        """
        self = object.__new__(cls)
        self.layer_outer_index = layer_outer_index
        self.token_end_index = token_end_index
        self.token_start_index = token_start_index
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # layer_outer_index
        repr_parts.append(' layer_outer_index = ')
        repr_parts.append(repr(self.layer_outer_index))
        
        # token_start_index
        repr_parts.append(', token_start_index = ')
        repr_parts.append(repr(self.token_start_index))
        
        # token_end_index
        repr_parts.append(', token_end_index = ')
        repr_parts.append(repr(self.token_end_index))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # layer_outer_index
        if self.layer_outer_index != other.layer_outer_index:
            return False
        
        # token_start_index
        if self.token_start_index != other.token_start_index:
            return False
        
        # token_end_index
        if self.token_end_index != other.token_end_index:
            return False
        
        return True
