__all__ = ('ExpressionInfo', 'get_expression_info')

from .file_info import get_file_info

from ...highlight import search_layer_index, search_line_end_index_in_tokens, search_line_start_index_in_tokens


class ExpressionInfo:
    """
    Represents an expression.
    
    Attributes
    ----------
    expression_character_end_index : `int`
        The character's index where the expression ends at.
    
    expression_character_start_index : `int`
        The character's index where the expression starts at.
    
    expression_line_end_index : `int`
        The line's index where the expression ends.
    
    expression_line_start_index : `int`
        The line's index where the expression starts.
    
    expression_token_end_index : `int`
        The token's index where the expression ends at.
    
    expression_token_start_index : `int`
        The token's index where the expression starts at.
    
    file_info : ``FileInfo``
        The parent file of the expression.
    
    key : ``ExpressionKey``
        The key of the expression.
    
    line : `str`
        The expression's line. The value should be already normalized.
    
    removed_indentation_characters : `int`
        By how much characters the expression should be dedented.
    """
    __slots__ = (
        'expression_character_end_index', 'expression_character_start_index', 'expression_line_end_index',
        'expression_line_start_index', 'expression_token_end_index', 'expression_token_start_index', 'file_info', 'key',
        'line', 'removed_indentation_characters'
    )
    
    def __new__(
        cls,
        key, 
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    ):
        """
        Creates a new expression info.
        
        Parameters
        ----------
        key : ``ExpressionKey``
            The key of the expression.
        
        file_info : ``FileInfo``
            The parent file of the expression.
        
        expression_line_start_index : `int`
            The line's index where the expression starts.
        
        expression_line_end_index : `int`
            The line's index where the expression ends.
        
        expression_character_start_index : `int`
            The character's index where the expression starts at.
        
        expression_character_end_index : `int`
            The character's index where the expression ends at.
        
        expression_token_start_index : `int`
            The token's index where the expression starts at.
        
        expression_token_end_index : `int`
            The token's index where the expression ends at.
        
        removed_indentation_characters : `int`
            By how much characters the expression should be dedented.
        
        line : `str`
            The expression's line. The value should be already normalized.
        """
        self = object.__new__(cls)
        self.key = key
        self.file_info = file_info
        self.expression_line_start_index = expression_line_start_index
        self.expression_line_end_index = expression_line_end_index
        self.expression_character_start_index = expression_character_start_index
        self.expression_character_end_index = expression_character_end_index
        self.expression_token_start_index = expression_token_start_index
        self.expression_token_end_index = expression_token_end_index
        self.removed_indentation_characters = removed_indentation_characters
        self.line = line
        return self
    
    
    def __repr__(self):
        """Returns the expression info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' key = ')
        repr_parts.append(repr(self.key))
        
        # file_info
        repr_parts.append(', file_info = ')
        repr_parts.append(repr(self.file_info))
        
        # expression_line_start_index
        repr_parts.append(', expression_line_start_index = ')
        repr_parts.append(repr(self.expression_line_start_index))
        
        # expression_line_end_index
        repr_parts.append(', expression_line_end_index = ')
        repr_parts.append(repr(self.expression_line_end_index))
        
        # expression_character_start_index
        repr_parts.append(', expression_character_start_index = ')
        repr_parts.append(repr(self.expression_character_start_index))
        
        # expression_character_end_index
        repr_parts.append(', expression_character_end_index = ')
        repr_parts.append(repr(self.expression_character_end_index))
        
        # expression_token_start_index
        repr_parts.append(', expression_token_start_index = ')
        repr_parts.append(repr(self.expression_token_start_index))
        
        # expression_token_end_index
        repr_parts.append(', expression_token_end_index = ')
        repr_parts.append(repr(self.expression_token_end_index))
        
        # removed_indentation_characters
        repr_parts.append(', removed_indentation_characters = ')
        repr_parts.append(repr(self.removed_indentation_characters))
        
        # line
        repr_parts.append(', line = ')
        repr_parts.append(repr(self.line))
        
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
        new.file_info = self.file_info
        new.expression_line_start_index = self.expression_line_start_index
        new.expression_line_end_index = self.expression_line_end_index
        new.expression_character_start_index = self.expression_character_start_index
        new.expression_character_end_index = self.expression_character_end_index
        new.expression_token_start_index = self.expression_token_start_index
        new.expression_token_end_index = self.expression_token_end_index
        new.removed_indentation_characters = self.removed_indentation_characters
        new.line = self.line
        return new
    
    
    @property
    def shift(self):
        if self.expression_character_start_index == self.expression_character_end_index:
            return 0
        
        return self.key.line_index - self.expression_line_start_index
    
    
    @property
    def lines(self):
        return self.line.splitlines()


def get_expression_area(file_name, line_index):
    """
    Gets the expression's area.
    
    Parameters
    ----------
    file_name : `str`
        The file's name to get the expressions for.
    
    line_index : `int`
        The line's index in the file.
    
    Returns
    -------
    area : `(FileInfo, int, int, int, int, int, int)`
    """
    file_info = get_file_info(file_name)
    parse_result = file_info.parse_result
    tokens = parse_result.tokens
    layers = parse_result.layers
    
    expression_line_start_index = line_index
    expression_line_end_index = line_index
    
    expression_token_start_index = search_line_start_index_in_tokens(tokens, line_index)
    expression_token_end_index = search_line_end_index_in_tokens(tokens, line_index)
    
    if expression_token_start_index == expression_token_end_index:
        expression_character_start_index = 0
        expression_character_end_index = 0
    
    else:
        layer_index_start = search_layer_index(layers, expression_token_start_index)
        layer_index_end = search_layer_index(layers, expression_token_end_index)
        if layer_index_start != layer_index_end:
            if layer_index_start != -1:
                expression_line_start_index = tokens[layers[layer_index_start].token_start_index].line_index
                expression_token_start_index = search_line_start_index_in_tokens(tokens, expression_line_start_index)
            
            if (expression_token_end_index != len(tokens)) and (layer_index_end != -1):
                expression_token_end_index = layers[layer_index_end].token_end_index
                expression_line_end_index = tokens[expression_token_end_index].line_index
                expression_token_end_index = search_line_end_index_in_tokens(tokens, expression_line_end_index)
            
        expression_character_start_index = tokens[expression_token_start_index].content_character_index
        if expression_token_end_index == len(tokens):
            expression_character_end_index = len(file_info.content)
        else:
            expression_character_end_index = tokens[expression_token_end_index].content_character_index
    
    return (
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
    )


def normalize_and_dedent_lines(lines):
    """
    Normalises the lines and dedents them.
    
    Parameters
    ----------
    lines : `list<str>`
        The lines to work on.
    
    Returns
    -------
    removed_indentation_characters : `int`
    """
    if not lines:
        return 0
    
    for index in range(len(lines)):
        lines[index] = lines[index].rstrip()
    
    
    do_remove = False
    removed_indentation_characters = 0
    
    for line in lines:
        if not line:
            continue
        
        count = 0
        for character in line:
            if character not in (' ', '\t'):
                break
            
            count += 1
            continue
        
        if count == 0:
            do_remove = False
            removed_indentation_characters = 0
            break
        
        if not do_remove:
            do_remove = True
            removed_indentation_characters = count
            continue
        
        if count < removed_indentation_characters:
            removed_indentation_characters = count
            continue
        
        continue
    
    if do_remove:
        for index in range(len(lines)):
            lines[index] = lines[index][removed_indentation_characters:]
    
    return removed_indentation_characters


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
    (
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
    ) = get_expression_area(expression_key.file_name, expression_key.line_index)
    
    if expression_character_start_index == expression_character_end_index:
        removed_indentation_characters = 0
        line = ''
    else:
        lines = file_info.content[expression_character_start_index : expression_character_end_index].splitlines()
        removed_indentation_characters = normalize_and_dedent_lines(lines)
        line = '\n'.join(lines)
    
    return ExpressionInfo(
        expression_key,
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    )
