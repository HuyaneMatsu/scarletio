__all__ = ('ExpressionKey',)


class ExpressionKey:
    """
    Key used to represent an expression.
    
    Attributes
    ----------
    file_name : `str`
        The file name the expression is located at.
    instruction_index : `int`
        The instruction's index used for identification.
    line_index : `int`
        The line's identifier where the expression is at.
    name : `str`
        The function's name the expression is at.
    """
    __slots__ = ('file_name', 'instruction_index', 'line_index', 'name')
    
    def __new__(cls, file_name, line_index, name, instruction_index):
        """
        Creates a new expression key.
        
        Parameters
        ----------
        file_name : `str`
            The file name the expression is located at.
        line_index : `int`
            The line's identifier where the expression is at.
        name : `str`
            The function's name the expression is at.
        instruction_index : `int`
            The instruction's index used for identification.
        """
        self = object.__new__(cls)
        self.file_name = file_name
        self.instruction_index = instruction_index
        self.line_index = line_index
        self.name = name
        return self
    
    
    def __repr__(self):
        """Returns the expression key's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' file_name = ')
        repr_parts.append(repr(self.file_name))
        
        repr_parts.append(', line_index = ')
        repr_parts.append(repr(self.line_index))
        
        repr_parts.append(', name = ')
        repr_parts.append(repr(self.name))
        
        repr_parts.append(', instruction_index = ')
        repr_parts.append(repr(self.instruction_index))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two expression keys are equal."""
        if type(self) is not type(other):
            return False
        
        if self.file_name != other.file_name:
            return False
        
        if self.instruction_index != other.instruction_index:
            return False
        
        if self.line_index != other.line_index:
            return False
        
        if self.name != other.name:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the expression key's hash value."""
        hash_value = 0
        hash_value ^= hash(self.file_name)
        hash_value ^= self.instruction_index
        hash_value ^= self.line_index << 16
        hash_value ^= hash(self.name)
        return hash_value
