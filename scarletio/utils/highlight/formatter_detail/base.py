__all__ = ('FormatterDetailBase',)

from ...rich_attribute_error import RichAttributeErrorBaseType


class FormatterDetailBase(RichAttributeErrorBaseType):
    """
    Represents a formatter node's detail.
    """
    __slots__ = ()
    
    def __new__(cls):
        """
        Creates a new formatter detail.
        """
        return object.__new__(cls)
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__, '>']
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other"""
        if type(self) is not type(other):
            return NotImplemented
        
        return True
    
    
    def start(self):
        """
        Responsible for starting the highlight.
        
        This function is an iterable generator.
        
        Yields
        ------
        part : `str`
        """
        return
        yield
    
    
    def transform_content(self, content):
        """
        Responsible for transforming the content as applicable.
        
        This function is an iterable generator.
        
        Parameters
        ----------
        content : `str`
            Content to transform.
        
        Yields
        ------
        part : `str`
        """
        yield content
    
    
    def end(self):
        """
        Responsible for ending the highlight.
        
        This function is an iterable generator.
        
        Yields
        ------
        part : `str`
        """
        return
        yield
    
    
    def transition(self, next_detail):
        """
        Responsible for transition the highlight.
        
        This function is an iterable generator.
        
        Parameters
        ----------
        next_detail : `instance<type<self>>`
            The next detail to transition to.
        
        Yields
        ------
        part : `str`
        """
        return
        yield
    
