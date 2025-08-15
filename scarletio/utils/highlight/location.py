__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType


class Location(RichAttributeErrorBaseType):
    """
    Represents the location of a token.
    
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
    """
    __slots__ = ('content_character_index', 'length', 'line_character_index', 'line_index')
    
    def __new__(cls, content_character_index, line_index, line_character_index, length):
        """
        Creates a new location.
        
        Parameters
        ----------
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
        return self
    
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return ''.join([
            type(self).__name__, '(',
            repr(self.content_character_index), ', ',
            repr(self.line_index), ', ',
            repr(self.line_character_index), ', ',
            repr(self.length),
            ')',
        ])
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.content_character_index != other.content_character_index:
            return False
        
        if self.line_index != other.line_index:
            return False
        
        if self.line_character_index != other.line_character_index:
            return False
        
        if self.length != other.length:
            return False
        
        return True
