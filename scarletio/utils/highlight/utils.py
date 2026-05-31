__all__ = (
    'get_highlight_parse_result', 'get_token_type_and_repr_mode_for_variable',
    'iter_highlight_code_token_types_and_values', 'search_layer_index', 'search_line_end_index_in_tokens',
    'search_line_start_index_in_tokens',
)

from .constants import BUILTIN_CONSTANTS, BUILTIN_EXCEPTIONS, BUILTIN_VARIABLES
from .flags import HIGHLIGHT_PARSER_MASK_DEFAULT
from .parse_result import ParseResult
from .parser_context import HighlightParserContext
from .token_types import (
    TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED,
    TOKEN_TYPE_NUMERIC_FLOAT, TOKEN_TYPE_NUMERIC_INTEGER, TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_UNICODE
)


def iter_highlight_code_token_types_and_values(code):
    """
    Parses the given code and iterates over its token types and values.
    
    This function is an iterable coroutine.
    
    Parameters
    ----------
    code : `str`
        Code to parse.
    
    Yields
    ------
    token_type_and_value : `(int, str)`
    """
    # Note: Parsing line by line will be replaced with global parsing.
    context = HighlightParserContext(code, HIGHLIGHT_PARSER_MASK_DEFAULT)
    context.match()
    
    for token in context.tokens:
        length = token.length
        if not length:
            continue
        
        content_character_index = token.content_character_index
        value = code[content_character_index : content_character_index + length]
        
        yield token.type, value


def get_highlight_parse_result(content):
    """
    Gets highlight parse result for the given code.
    
    Parameters
    ----------
    content : `str`
        Code to parse.
    
    Returns
    -------
    parse_result : ``ParseResult``
    """
    context = HighlightParserContext(content, HIGHLIGHT_PARSER_MASK_DEFAULT)
    context.match()
    return ParseResult(context.layers, context.tokens)


def get_token_type_and_repr_mode_for_variable(variable):
    """
    Gets the token type for the given variable.
    
    Parameters
    ----------
    variable : `object`
        The variable to get token type for.
    
    Returns
    -------
    token_type, use_name : `(int, bool)`
        What token-type should be used for highlighting the given variable & whether the name of the variable should
        be used instead of its representation to show it.
    """
    while True:
        if isinstance(variable, str):
            if (type(variable).__repr__ is str.__repr__):
                token_type = TOKEN_TYPE_STRING_UNICODE
                use_name = False
                break
        
        elif isinstance(variable, bytes):
            if (type(variable).__repr__ is bytes.__repr__):
                token_type = TOKEN_TYPE_STRING_BINARY
                use_name = False
                break
        
        elif isinstance(variable, int) and (not isinstance(variable, bool)):
            if (type(variable).__repr__ is int.__repr__):
                token_type = TOKEN_TYPE_NUMERIC_INTEGER
                use_name = False
                break
        
        elif isinstance(variable, float):
            if (type(variable).__repr__ is float.__repr__):
                token_type = TOKEN_TYPE_NUMERIC_FLOAT
                use_name = False
                break
        
        else:
            try:
                hash(variable)
            except TypeError:
                pass
            
            else:
                if variable in BUILTIN_CONSTANTS:
                    token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT
                    use_name = False
                    break
                
                elif variable in BUILTIN_VARIABLES:
                    token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE
                    use_name = True
                    break
                
                elif variable in BUILTIN_EXCEPTIONS:
                    token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION
                    use_name = True
                    break
        
        if isinstance(variable, type):
            token_type = TOKEN_TYPE_IDENTIFIER_VARIABLE
            use_name = True
            break
        
        token_type = TOKEN_TYPE_NON_SPACE_UNIDENTIFIED
        use_name = False
        break
    
    return token_type, use_name


def search_line_start_index_in_tokens(tokens, line_index):
    """
    Searches line start index in tokens.
    
    Parameters
    ----------
    tokens : ``list<Token>``
        Tokens to search in.
    
    line_index : `int`
        Line index to search for.
    
    Returns
    -------
    index : `int`
    """
    low = 0
    high = len(tokens)
    
    while low < high:
        mid = (low + high) >> 1
        
        if tokens[mid].line_index < line_index:
            low = mid + 1
        else:
            high = mid
    
    return low


def search_line_end_index_in_tokens(tokens, line_index):
    """
    Searches line end index in tokens.
    
    Parameters
    ----------
    tokens : ``list<Token>``
        Tokens to search in.
    
    line_index : `int`
        Line index to search for.
    
    Returns
    -------
    index : `int`
    """
    low = 0
    high = len(tokens)
    
    while low < high:
        mid = (low + high) >> 1
        
        if line_index < tokens[mid].line_index:
            high = mid
        else:
            low = mid + 1
    
    return low


def search_layer_index(layers, token_index):
    """
    Searches the layer index of a token index.
    
    Parameters
    ----------
    layers : ``list<Layer>``
        Layers to search in.
    
    token_index : `int`
        Token index to search for.
    
    Returns
    -------
    index : `int`
    """
    low = 0
    high = len(layers)
    
    while low < high:
        mid = (low + high) >> 1
        
        layer = layers[mid]
        if token_index < layer.token_start_index:
            high = mid
            continue
        
        if token_index > layer.token_end_index:
            low = mid + 1
            continue
        
        index = mid
        break
    
    else:
        index = -1
    
    return index
