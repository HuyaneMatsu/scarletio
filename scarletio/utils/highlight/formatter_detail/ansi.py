__all__ = ('FormatterDetailANSI',)

from ...docs import copy_docs

from ..ansi import iter_produce_ansi_format_code

from .base import FormatterDetailBase


class FormatterDetailANSI(FormatterDetailBase):
    """
    Represents a formatter node's detail. Specialized for outputting highlights using ansi escape codes.
    
    Attributes
    ----------
    background_color : `None | (int, int, int)` = `None`, Optional
        background color.
    
    foreground_color : `None | (int, int, int)` = `None`, Optional
        Foreground color.
    
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    """
    __slots__ = ('background_color', 'foreground_color', 'text_decoration')
    
    def __new__(cls, text_decoration = None, background_color = None, foreground_color = None):
        """
        Creates a new ansi formatter detail.
        
        Parameters
        ----------
        text_decoration : `None | int` = `None`, Optional
            Text decoration.
        
        background_color : `None | (int, int, int)` = `None`, Optional
            background color.
        
        foreground_color : `None | (int, int, int)` = `None`, Optional
            Foreground color.
        """
        self = object.__new__(cls)
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.text_decoration = text_decoration
        return self
    
    
    @copy_docs(FormatterDetailBase.__repr__)
    def __repr__(self):
        repr_parts = ['<', type(self).__name__]
        
        field_added = False
        
        # background_color
        background_color = self.background_color
        if (background_color is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' background_color = ')
            repr_parts.append(repr(background_color))
        
        # foreground_color
        foreground_color = self.foreground_color
        if (foreground_color is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' foreground_color = ')
            repr_parts.append(repr(foreground_color))
        
        # text_decoration
        text_decoration = self.text_decoration
        if (text_decoration is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' text_decoration = ')
            repr_parts.append(repr(text_decoration))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
        

    @copy_docs(FormatterDetailBase.__eq__)
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        # background_color
        if self.background_color != other.background_color:
            return False
        
        # foreground_color
        if self.foreground_color != other.foreground_color:
            return False
        
        # text_decoration
        if self.text_decoration != other.text_decoration:
            return False
        
        return True
    
    
    @copy_docs(FormatterDetailBase.start)
    def start(self):
        yield from iter_produce_ansi_format_code(
            False, self.text_decoration, self.background_color, self.foreground_color
        )
    
    
    @copy_docs(FormatterDetailBase.end)
    def end(self):
        yield from iter_produce_ansi_format_code(True, None, None, None)
    
    
    @copy_docs(FormatterDetailBase.transition)
    def transition(self, next_detail):
        self_background_color = self.background_color
        other_background_color = next_detail.background_color
        
        self_foreground_color = self.foreground_color
        other_foreground_color = next_detail.foreground_color
        
        self_text_decoration = self.text_decoration
        other_text_decoration = next_detail.text_decoration
        
        # Anything reset in new?
        if (
            ((self_background_color is not None) and (other_background_color is None)) or
            ((self_foreground_color is not None) and (other_foreground_color is None)) or
            ((self_text_decoration is not None) and (other_text_decoration is None))
        ):
            yield from iter_produce_ansi_format_code(
                True, other_text_decoration, other_background_color, other_foreground_color
            )
            return
        
        if self_background_color == other_background_color:
            other_background_color = None
        
        if self_foreground_color == other_foreground_color:
            other_foreground_color = None
        
        if self_text_decoration == other_text_decoration:
            other_text_decoration = None
        
        # Is new different?
        if (
            (other_background_color is not None) or
            (other_foreground_color is not None) or
            (other_text_decoration is not None)
        ):
            yield from iter_produce_ansi_format_code(
                False, other_text_decoration, other_background_color, other_foreground_color
            )
            return
