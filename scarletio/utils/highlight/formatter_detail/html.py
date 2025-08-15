__all__ = ('FormatterDetailHTML',)

from html import escape as html_escape

from ...docs import copy_docs

from .base import FormatterDetailBase


class FormatterDetailHTML(FormatterDetailBase):
    """
    Represents a formatter node's detail. Specialized for outputting highlights in html.
    
    Attributes
    ----------
    html_class : `int`
        Html class to use.
    """
    __slots__ = ('html_class',)
    
    def __new__(cls, html_class):
        """
        Creates a new html formatter detail.
        
        Parameters
        ----------
        html_class : `int`
            Html class to use.
        """
        self = object.__new__(cls)
        self.html_class = html_class
        return self
    
    
    @copy_docs(FormatterDetailBase.__repr__)
    def __repr__(self):
        repr_parts = ['<', type(self).__name__]
        
        # html_class
        repr_parts.append(' html_class = ')
        repr_parts.append(repr(self.html_class))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
        

    @copy_docs(FormatterDetailBase.__eq__)
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        # html_class
        if self.html_class != other.html_class:
            return False
        
        return True
    
    
    @copy_docs(FormatterDetailBase.start)
    def start(self):
        html_class = self.html_class
        if (html_class is not None):
            yield '<span class="'
            yield html_class
            yield '">'
    
    
    @copy_docs(FormatterDetailBase.transform_content)
    def transform_content(self, content):
        yield '<br>' if content == '\n' else html_escape(content)
        
    
    @copy_docs(FormatterDetailBase.end)
    def end(self):
        html_class = self.html_class
        if (html_class is not None):
            yield '</span>'
    
    
    @copy_docs(FormatterDetailBase.transition)
    def transition(self, next_detail):
        if self.html_class != next_detail.html_class:
            yield from self.end()
            yield from next_detail.start()
