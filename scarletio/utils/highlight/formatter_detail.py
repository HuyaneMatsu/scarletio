__all__ = ()

from html import escape as html_escape

from .token_types import TOKEN_TYPE_LINEBREAK


class FormatterDetail:
    """
    Represents a formatter node's detail.
    
    Attributes
    ----------
    details : `object`
        Additional details to pass to the ``.formatter_generator_function``.
    formatter_generator_function : ``GeneratorFunction``
        Generator function which
    """
    __slots__ = ('details', 'formatter_generator_function')
    
    def __new__(cls, formatter_generator_function, details):
        """
        Creates a new formatter detail.
        
        Parameters
        ----------
        formatter_generator_function : ``GeneratorFunction``
            Generator function which
        details : `object`
            Additional details to pass to the ``.formatter_generator_function``.
        """
        self = object.__new__(cls)
        self.details = details
        self.formatter_generator_function = formatter_generator_function
        return self
    
    
    def __repr__(self):
        """Returns the formatter detail's representation."""
        return f'{self.__class__.__name__}({self.formatter_generator_function!r}, {self.details!r})'
    
    
    def __call__(self, token):
        """
        Generates highlighted content from the given token.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        token : ``Token``
            The token to generate it's highlighted version.
        
        Yields
        ------
        content : `str`
        """
        yield from self.formatter_generator_function(self.details, token)
    
    
    def __eq__(self, other):
        """Returns whether the two formatter details are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.details != other.details:
            return False
        
        if self.formatter_generator_function is not other.formatter_generator_function:
            return False
        
        return True


def formatter_html(html_class, token):
    """
    Html highlight text formatter.
    
    Parameters
    ----------
    html_class : `None`, `str`
        The html class to format the string as.
    token : ``Token``
        The token to generate it's highlighted version.
        
    Yields
    ------
    content : `str`
    """
    token_type = token.type
    if (token_type == TOKEN_TYPE_LINEBREAK):
        yield '<br>'
        return
    
    token_value = token.value
    if (token_value is None):
        return
    
    if (html_class is not None):
        yield '<span class="'
        yield html_class
        yield '">'
    
    yield html_escape(token_value)
    
    if (html_class is not None):
        yield '</span>'


def formatter_ansi_code(format_and_reset_code, token):
    """
    Ansi highlight text formatter.
    
    Parameters
    ----------
    format_and_reset_code : `None`, `tuple` (`str`, `str`)
        Ansi format code and reset code.
    token : ``Token``
        The token to generate it's highlighted version.
        
    Yields
    ------
    content : `str`
    """
    token_value = token.value
    if (token_value is None):
        return
    
    if format_and_reset_code is None:
        yield token_value
        return
    
    starter, ender = format_and_reset_code
    yield starter
    yield token_value
    yield ender
    return
