__all__ = (
    'add_highlighted_part_into', 'add_highlighted_parts_into', 'get_token_type_and_repr_mode_for_variable',
    'iter_highlight_code_lines', 'iter_highlight_code_token_types_and_values'
)

from warnings import warn

from .constants import BUILTIN_CONSTANTS, BUILTIN_EXCEPTIONS, BUILTIN_VARIABLES
from .flags import HIGHLIGHT_PARSER_MASK_DEFAULT
from .highlight_streamer import get_highlight_streamer
from .parser_context import HighlightParserContext
from .token_types import (
    TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED,
    TOKEN_TYPE_NUMERIC_FLOAT, TOKEN_TYPE_NUMERIC_INTEGER, TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_UNICODE
)


def iter_highlight_code_lines(lines, formatter_context):
    """
    Matches the given python code lines and iterates it's formatted representation.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    lines : `list` of `str`
        Lines to format.
    
    formatter_context : ``HighlightFormatterContext``
        Context to use for highlighting.
    
    Yields
    ------
    content : `str`
    """
    warn(
        (
            f'`iter_highlight_code_lines` is deprecated and will be removed 2025 October. '
            f'Please use `iter_highlight_code_token_types_and_values` paired with `get_highlight_streamer` '
            f'instead accordingly. '
        ),
        FutureWarning,
        stacklevel = 2,
    )
    
    code = ''.join(lines)
    context = HighlightParserContext(code, HIGHLIGHT_PARSER_MASK_DEFAULT)
    context.match()
    highlight_streamer = get_highlight_streamer(formatter_context)
    for token in context.tokens:
        location = token.location
        length = location.length
        if not length:
            continue
        
        content_character_index = location.content_character_index
        value = code[content_character_index : content_character_index + length]
        
        yield from highlight_streamer.asend((token.type, value))
    
    yield from highlight_streamer.asend(None)


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
        location = token.location
        length = location.length
        if not length:
            continue
        
        content_character_index = location.content_character_index
        value = code[content_character_index : content_character_index + length]
        
        yield token.type, value


def add_highlighted_part_into(token_type, part, highlighter, into):
    """
    Adds a highlighted part extending the given list of strings.
    
    Parameters
    ----------
    token_type : `int`
        Token type identifier.
    
    part : `str`
        The part to add.
    
    highlighter : ``None | HighlightFormatterContext``
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    warn(
        (
            f'`add_highlighted_part_into` is deprecated and will be removed 2025 October. '
            f'Please use `into.extend(highlight_streamer.asend((token_type, part)))` instead accordingly. '
            f'For more information read `get_highlight_streamer`\'s documentation.'
        ),
        FutureWarning,
        stacklevel = 2,
    )

    if (highlighter is None):
        into.append(part)
    else:
        detail = highlighter.formatter_nodes[token_type].detail
        if (detail is None):
            into.append(part)
        
        else:
            into.extend(detail.start())
            into.extend(detail.transform_content(part))
            into.extend(detail.end())
    
    return into
    

def add_highlighted_parts_into(producer, highlighter, into):
    """
    Iterates over a producer and applies highlighter for each produced item extending the given list of strings with
    them.
    
    Parameters
    ----------
    producer : `iterable<(int, str)>`
        Iterable to produce token_type - part items.
    
    highlighter : ``None | HighlightFormatterContext``
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Yields
    ------
    into : `list<str>`
    """
    warn(
        (
            f'`add_highlighted_parts_into` is deprecated and will be removed 2025 October. '
            f'Please use `for item in producer: into.extend(highlight_streamer.asend(item))` instead accordingly. '
            f'For more information read `get_highlight_streamer`\'s documentation.'
        ),
        FutureWarning,
        stacklevel = 2,
    )
    
    for token_type, part in producer:
        if (highlighter is None):
            into.append(part)
        else:
            detail = highlighter.formatter_nodes[token_type].detail
            if (detail is None):
                into.append(part)
            
            else:
                into.extend(detail.start())
                into.extend(detail.transform_content(part))
                into.extend(detail.end())
    
    return into


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
