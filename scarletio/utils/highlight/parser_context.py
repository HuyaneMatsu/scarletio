__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType

from .location import Location
from .matching import _keep_python_parsing
from .token import Token
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_LINE_BREAK_ESCAPED, TOKEN_TYPE_SPACE,
    TOKEN_TYPE_SPECIAL_OPERATOR,
    TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN, TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN,
    TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN,
    TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE, TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE,
    TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE
)


def _is_open_brace(token_type):
    """
    Returns whether the given token is an open token.
    
    Parameters
    ----------
    token_type : `int`
        Token type.
    
    Returns
    -------
    is_open_token : `bool`
    """
    return (
        (token_type == TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN) or 
        (token_type == TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN) or 
        (token_type == TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN) or 
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN) or 
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN) or
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN)
    )


def _is_close_brace(token_type):
    """
    Returns whether the given token is an close token.
    
    Parameters
    ----------
    token_type : `int`
        Token type.
    
    Returns
    -------
    is_close_token : `bool`
    """
    return (
        (token_type == TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE) or 
        (token_type == TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE) or 
        (token_type == TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE) or 
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE) or 
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE) or
        (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE)
    )


def _swap_open_brace_token_type(token_type):
    """
    Swaps the given open token to an close token.
    
    Parameters
    ----------
    token_type : `int`
        Token type.
    
    Returns
    -------
    cose_token : `int`
    """
    # Find the brace's pair from backwards and remove everything including it
    if token_type == TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN:
        token_type = TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE
    elif token_type == TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN:
        token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE
    elif token_type == TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN:
        token_type = TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE
    elif token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN:
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE
    elif token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN:
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE
    else:
        # token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE
    
    return token_type


def _swap_close_brace_token_type(token_type):
    """
    Swaps the given close token to an open token.
    
    Parameters
    ----------
    token_type : `int`
        Token type.
    
    Returns
    -------
    open_token : `int`
    """
    if token_type == TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE:
        token_type = TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN
    elif token_type == TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE:
        token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
    elif token_type == TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE:
        token_type = TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN
    elif token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE:
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN
    elif token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE:
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN
    else:
        # token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN
    
    return token_type


def _is_barrier_token(token_type):
    """
    Returns whether the given token type is a barrier token (has its own parser that will close itself).
    
    Parameters
    ----------
    token_type : `int`
        Token type.
    
    Returns
    -------
    is_barrier_token : `bool`
    """
    return (
        (token_type == TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN) or 
        (token_type == TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN) or 
        (token_type == TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN)
    )


class HighlightParserContext(RichAttributeErrorBaseType):
    """
    Represents a context of highlighting any content.
    
    Attributes
    ----------
    brace_nesting : `None | list<int>`
        How the braces are nested.
    
    content : `str`
        The content that the higher context should match.
    
    content_character_index : `int`
        The character's index from the start.
    
    content_length : `int`
        The content's length.
    
    done : `bool`
        Whether processing is done.
    
    flags : `int`
        Flags used to determine how to parse.
    
    line_character_index : `int`
        The index of the character of the processed line.
    
    line_index : `int`
        The index of the line which is processed at the moment.
    
    tokens : ``list<Token>``
        The generated tokens.
    """
    __slots__ = (
        'brace_nesting', 'content', 'content_character_index', 'content_length',  'done', 'flags',
        'line_character_index', 'line_index', 'tokens'
    )
    
    def __new__(cls, content, flags):
        """
        Creates a new highlight parser context.
        
        Parameters
        ----------
        content : `str`
            The content that the higher context should match.
        
        flags : `int`
            Flags used to determine how to parse.
        """
        self = object.__new__(cls)
        self.brace_nesting = None
        self.content = content
        self.content_character_index = 0
        self.content_length = content_length = len(content)
        self.done = False if content_length else True
        self.flags = flags
        self.tokens = []
        self.line_index = 0
        self.line_character_index = 0
        return self
    
    
    def recheck_done(self):
        """
        Rechecks whether the context is done. Used after exiting a nesting.
        """
        if self.content_character_index >= self.content_length:
            self.done = True
    
    
    def add_token(self, token_type, token_length):
        """
        Adds a token to the context.
        
        Parameters
        ----------
        token_type : `int`
            The token's identifier.
        
        token_length : `int`
            The length of the token.
        """
        content_character_index = self.content_character_index
        line_index = self.line_index
        line_character_index = self.line_character_index
        
        if (token_type == TOKEN_TYPE_LINE_BREAK):
            self.line_index = line_index + 1
            self.line_character_index = 0
            self._end_of_line()
        
        else:
            if _is_open_brace(token_type):
                brace_nesting = self.brace_nesting
                if brace_nesting is None:
                    brace_nesting = []
                    self.brace_nesting = brace_nesting
                
                brace_nesting.append(token_type)
            
            elif _is_close_brace(token_type):
                brace_nesting = self.brace_nesting
                
                open_brace_token = _swap_close_brace_token_type(token_type)
                if (brace_nesting is None):
                    open_found = False
                else:
                    while brace_nesting:
                        last_open_brace_type = brace_nesting[-1]
                        if (last_open_brace_type == open_brace_token):
                            del brace_nesting[-1]
                            open_found = True
                            break
                        
                        if _is_barrier_token(last_open_brace_type):
                            open_found = True
                            break
                            
                        self.tokens.append(Token(
                            _swap_open_brace_token_type(last_open_brace_type),
                            Location(content_character_index, line_index, line_character_index, 0),
                        ))
                        del brace_nesting[-1]
                    
                    else:
                        open_found = False
                
                if not open_found:
                    self.tokens.append(Token(
                        open_brace_token,
                        Location(content_character_index, line_index, line_character_index, 0),
                    ))
                
                if not brace_nesting:
                    self.brace_nesting = None
            
            self.line_character_index = line_character_index + token_length
        
         
        self.content_character_index = content_character_index + token_length
        self.tokens.append(Token(
            token_type,
            Location(content_character_index, line_index, line_character_index, token_length),
        ))
        
        if self.content_character_index >= self.content_length:
            self.done = True
            brace_nesting = self.brace_nesting
            if (brace_nesting is not None):
                while brace_nesting:
                    last_open_brace_type = brace_nesting[-1]
                    if _is_barrier_token(last_open_brace_type):
                        break
                    
                    self.tokens.append(Token(
                        _swap_open_brace_token_type(last_open_brace_type),
                        Location(content_character_index, line_index, line_character_index, 0),
                    ))
                    del brace_nesting[-1]
                
                if not brace_nesting:
                    self.brace_nesting = None
    
    
    def get_last_related_token(self):
        """
        Gets the last token of the highlight context.
        
        Returns
        -------
        token : ``Token``, `None`
            The token if there is any added.
        """
        tokens = self.tokens
        
        for token in reversed(tokens):
            token_type = token.type
            
            if token_type == TOKEN_TYPE_LINE_BREAK_ESCAPED:
                continue
            
            if token_type == TOKEN_TYPE_SPACE:
                continue
            
            if token_type == TOKEN_TYPE_COMMENT:
                continue
            
            break
        else:
            token = None
        
        return token
    
    
    def match(self):
        """
        Matches the content of the context.
        """
        _keep_python_parsing(self)
    
    
    def _end_of_line(self):
        """
        Adds a linebreak token to the context.
        """
        tokens = self.tokens
        if not tokens:
            return
        
        # Turns out there is no reversed i-slice
        for index in range(len(tokens) - (1 + (tokens[-1].type == TOKEN_TYPE_LINE_BREAK)), -1, -1):
            token = tokens[index]
            token_type = token.type
            if token_type == TOKEN_TYPE_LINE_BREAK:
                continue
            
            if token_type == TOKEN_TYPE_SPACE:
                continue
            
            if token_type == TOKEN_TYPE_COMMENT:
                continue
            
            if (
                (token_type == TOKEN_TYPE_SPECIAL_OPERATOR) and
                (token.location.length == 1) and
                (self.content[token.location.content_character_index] == '\\')
            ):
                token.type = TOKEN_TYPE_LINE_BREAK_ESCAPED
            
            break
    
    
    def enter(self, flags):
        """
        Enters the context manager nesting it.
        
        flags : `int`
            New flags to use.
        
        Returns
        -------
        nester : ``ParserContextNester``
        """
        nester = ParserContextNester(self, self.flags, self.done)
        self.flags = flags
        return nester


class ParserContextNester(RichAttributeErrorBaseType):
    """
    Nester of a parser context that stores its previous configurations and on exit reverts them.
    Allowing the user to start a new context with different flags without actually starting a new context.
    
    Attributes
    ----------
    context : ``HighlightParserContext``
        The context to use.
    
    previous_done : `bool`
        Whether processing is done.
    
    previous_flags : `int`
        Flags used to determine how to parse.
    """
    __slots__ = ('context', 'previous_flags', 'previous_done')
    
    def __new__(cls, context, previous_flags, previous_done):
        """
        Creates a new parser context nester.
        
        Parameters
        ----------
        context : ``HighlightParserContext``
            The context to use.
        
        previous_flags : `int`
            Flags used to determine how to parse.
        
        previous_done : `bool`
            Whether processing is done.
        """
        self = object.__new__(cls)
        self.context = context
        self.previous_done = previous_done
        self.previous_flags = previous_flags
        return self
    
    
    def __enter__(self):
        """
        Enters the context manager.
        
        Returns
        -------
        self : `self`
        """
        return self
    
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Exits the context manager.
        
        Parameters
        ----------
        exception_type : `None | type<BaseException>`
            The occurred exception's type if any.
        
        exception_value : `None | BaseException`
            The occurred exception if any.
        
        exception_traceback : `None | TracebackType`
            the exception's traceback if any.
        
        Returns
        -------
        captured : `bool`
            Whether the exception was captured.
        """
        context = self.context
        context.flags = self.previous_flags
        context.done = self.previous_done
        context.recheck_done()
        return False
