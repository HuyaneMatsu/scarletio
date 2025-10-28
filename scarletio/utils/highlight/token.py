__all__ = ('Token',)

from ..rich_attribute_error import RichAttributeErrorBaseType


class Token(RichAttributeErrorBaseType):
    """
    Represents a token parsed by the highlighter.
    
    Attributes
    ----------
    content_character_index : `int`
        Where the token starts in the content.
    
    length : `int`
        The length of the represented slice.
    
    line_character_index : `int`
        The character index inside of the current line.
    
    line_index : `int`
        The current line's index.
    
    type : `int`
        The token's identifier.
    """
    __slots__ = ('content_character_index', 'length', 'line_character_index', 'line_index', 'type')
    
    def __new__(cls, token_type, content_character_index, line_index, line_character_index, length):
        """
        Creates a new token.
        
        Parameters
        ----------
        token_type : `int`
            The token's identifier.
            
        content_character_index : `int`
            Where the token starts in the content.
        
        line_index : `int`
            The current line's index.
        
        line_character_index : `int`
            The character index inside of the current line.
        
        length : `int`
            The length of the represented slice.
        """
        self = object.__new__(cls)
        self.content_character_index = content_character_index
        self.length = length
        self.line_character_index = line_character_index
        self.line_index = line_index
        self.type = token_type
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # type
        repr_parts.append(' type = ')
        repr_parts.append(repr(self.type))
        
        # content_character_index
        repr_parts.append(', content_character_index = ')
        repr_parts.append(repr(self.content_character_index))
        
        # line_index
        repr_parts.append(', line_index = ')
        repr_parts.append(repr(self.line_index))
        
        # line_character_index
        repr_parts.append(', line_character_index = ')
        repr_parts.append(repr(self.line_character_index))
        
        # length
        repr_parts.append(', length = ')
        repr_parts.append(repr(self.length))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # type
        if self.type != other.type:
            return False
        
        # content_character_index
        if self.content_character_index != other.content_character_index:
            return False
        
        # line_index
        if self.line_index != other.line_index:
            return False
        
        # line_character_index
        if self.line_character_index != other.line_character_index:
            return False
        
        # length
        if self.length != other.length:
            return False
        
        return True
