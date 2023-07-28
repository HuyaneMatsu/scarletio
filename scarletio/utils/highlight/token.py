__all__ = ()

class Token:
    """
    Represents a token parsed by ``HighlightContextBase``.
    
    Attributes
    ----------
    type : `int`
        The token's identifier.
    value : `None`, `str`
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
        value : `None`, `str`
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


def _merge_tokens(tokens, start_index, end_index):
    """
    Merges the tokens inside of the given range.
    
    Parameters
    ----------
    tokens : `list` of ``Token``
        The tokens, which will have it's slice merged.
    start_index : `int`
        The first token's index to merge.
    end_index : `int`
        The last token's index +1 to merge.
    """
    values = []
    
    for token_index in range(start_index, end_index):
        value = tokens[token_index].value
        if (value is not None) and value:
            values.append(value)
    
    value = ''.join(values)
    
    del tokens[start_index + 1 : end_index]
    tokens[start_index].value = value
