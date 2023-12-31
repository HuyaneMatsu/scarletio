__all__ = ('ExpressionInfo', 'get_expression_info')

from .parsing import get_expression_lines


class ExpressionInfo:
    """
    Represents an expression.
    
    Attributes
    ----------
    key : ``ExpressionKey``
        The key of the expression.
    line : `str`
        The joined lines of the expression.
    lines : `list<str>`
        The parsed lines.
    mention_count : `int`
        How much times the expression info is mentioned.
    shift : `int`
        How much the expression is shifted.
    syntax_valid : `bool`
        Whether the syntax is valid.
    """
    __slots__ = ('key', 'line', 'lines', 'mention_count', 'shift', 'syntax_valid')
    
    def __new__(cls, key, lines, shift, syntax_valid):
        """
        Creates a new expression info.
        
        Parameters
        ----------
        key : ``ExpressionKey``
            The key of the expression.
        lines : `list<str>`
            The parsed lines.
        shift : `int`
            How much the expression is shifted.
        syntax_valid : `bool`
            Whether the syntax is valid.
        """
        line = '\n'.join(lines)
        self = object.__new__(cls)
        self.key = key
        self.line = line
        self.lines = lines
        self.mention_count = 0
        self.shift = shift
        self.syntax_valid = syntax_valid
        return self
    
    
    def __repr__(self):
        """Returns the expression info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' key = ')
        repr_parts.append(repr(self.key))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def copy(self):
        """
        Copies the expression info.
        
        Returns
        -------
        new : `instance<type<self>>`
        """
        new = object.__new__(type(self))
        new.key = self.key
        new.line = self.line
        new.lines = self.lines.copy()
        new.mention_count = 0
        new.shift = self.shift
        new.syntax_valid = self.syntax_valid
        return new
    
    
    def do_mention(self):
        """
        Mentions the expression info.
        """
        self.mention_count += 1


def get_expression_info(expression_key):
    """
    Gets expression info for the given expression key.
    
    Parameters
    ----------
    expression_key : ``ExpressionKey``
        Expression key to get the info for.
    
    Returns
    -------
    expression_info : ``ExpressionInfo``
        The retrieved expression info.
    """
    lines, shift, syntax_valid = get_expression_lines(expression_key.file_name, expression_key.line_index)
    return ExpressionInfo(expression_key, lines, shift, syntax_valid)
