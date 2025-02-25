__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType

from .flags import HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING
from .matching import _keep_python_parsing
from .token import Token, _merge_tokens
from .token_types import (
    MERGE_TOKEN_TYPES, TOKEN_TYPE_ALL, TOKEN_TYPE_COMMENT, TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_LINE_BREAK_ESCAPED,
    TOKEN_TYPE_SPACE, TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_PUNCTUATION
)


class HighlightParserContext(RichAttributeErrorBaseType):
    """
    Represents a context of highlighting any content.
    
    Attributes
    ----------
    brace_nesting : `None | list<str>`
        How the braces are nested.
    
    done : `bool`
        Whether processing is done.
    
    flags : `int`
        Flags used to determine how to parse.
    
    line_character_index : `int`
        The index of the character of the processed line.
    
    line_index : `int`
        The index of the line which is processed at the moment.
    
    lines : `list` of `str`
        The lines to highlight.
    
    tokens : `list` of ``Token``
        The generated tokens.
    """
    __slots__ = ('brace_nesting', 'done', 'flags', 'line_character_index', 'line_index', 'lines', 'tokens')
    
    def __new__(cls, lines, flags):
        """
        Creates a new highlight parser context.
        
        Parameters
        ----------
        lines : `list<str>`
            The lines what the highlight context should match.
        
        flags : `int`
            Flags used to determine how to parse.
        """
        self = object.__new__(cls)
        self.brace_nesting = None
        self.done = False
        self.flags = flags
        self.tokens = []
        self.lines = lines
        self.line_index = 0
        self.line_character_index = 0
        
        if not lines:
            self.done = True
        
        return self
    
    
    def get_line_index(self):
        """
        Returns the line's index where the context is at.
        
        Returns
        -------
        line_index : `int`
        """
        return self.line_index
    
    
    def get_line(self):
        """
        Returns the actual line of the context.
        
        Returns
        -------
        line : `str`
        """
        lines = self.lines
        line_index = self.line_index
        if len(lines) <= line_index:
            line = ''
        else:
            line = lines[line_index]
        
        return line
    
    
    def get_line_character_index(self):
        """
        Returns the character index of the context's actual line.
        
        Returns
        -------
        line_character_index : `int`
        """
        return self.line_character_index
    
    
    def set_line_character_index(self, line_character_index):
        """
        Sets the actual line's character index.
        
        Parameters
        ----------
        line_character_index : `int`
            The index to set of the actual line.
            
            Pass it as `-1` to force end the line with linebreak or as `-2` to force it without linebreak.
        """
        lines = self.lines
        line_index = self.line_index
        
        if line_index >= len(lines):
            line = ''
        else:
            line = lines[line_index]
        
        if (line_character_index < 0) or (len(line) <= line_character_index):
            line_index += 1
            
            self.line_index = line_index
            if len(lines) <= line_index:
                self.done = True
            
            self._end_of_line()
            
            line_character_index = 0
        
        self.line_character_index = line_character_index
    
    
    def recheck_done(self):
        """
        Rechecks whether the context is done. Used after exiting a nesting.
        """
        if len(self.lines) <= self.line_index:
            self.done = True
    
    
    def add_token(self, token_type, token_value):
        """
        Adds a token to the context.
        
        Parameters
        ----------
        token_type : `int`
            The token's identifier.
        
        token_value : `None | str`
            The token's value.
        """
        token = Token(token_type, token_value)
        self.tokens.append(token)
        
        if (token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION) and (self.flags & HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING):
            self._track_brace_nesting(token_value)
    
    
    def _track_brace_nesting(self, token_value):
        """
        Parameters
        ----------
        token_value : `None | str`
            The token's value.
        """
        if token_value in ('(', '[', '{'):
            brace_nesting = self.brace_nesting
            if brace_nesting is None:
                brace_nesting = []
                self.brace_nesting = brace_nesting
            
            brace_nesting.append(token_value)
            return
        
        if token_value in (')', ']', '}'):
            brace_nesting = self.brace_nesting
            # Nothing to remove from?
            if brace_nesting is None:
                return
            
            # Find the brace's pair from backwards and remove everything including it
            if token_value == ')':
                token_value = '('
            elif token_value == ']':
                token_value = '['
            else:
                token_value = '{'
            
            for index in reversed(range(len(brace_nesting))):
                if brace_nesting[index] == token_value:
                    break
            
            del brace_nesting[index:]
            
            if not brace_nesting:
                self.brace_nesting = None
            
            return
        
        # no more cases
        return
    
    
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
        self._optimize_tokens()
    
    
    def _optimize_tokens(self):
        tokens = self.tokens
        # Optimize tokens with merging sames into each other if applicable
        same_count = 0
        last_type = TOKEN_TYPE_ALL
        token_index = len(tokens) - 1
        
        while True:
            if token_index < 0:
                if same_count > 1:
                    # Merge tokens
                    _merge_tokens(tokens, 0, same_count)
                break
            
            token = tokens[token_index]
            token_type = token.type
            
            if (token_type not in MERGE_TOKEN_TYPES):
                last_type = token_type
                same_count = 0
                token_index -= 1
                continue
            
            if (last_type == token_type):
                token_index -= 1
                same_count += 1
                continue
            
            if same_count > 1:
                # Merge tokens
                _merge_tokens(tokens, token_index + 1, token_index + same_count + 1)
            
            same_count = 1
            last_type = token_type
            token_index -= 1
            continue
    
    
    def generate_highlighted(self, formatter):
        """
        Generates highlighted content.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        formatter : ``Formatter``
            Formatter to use for formatting content.
        
        Yields
        ------
        content : `str`
            The generated content.
        """
        for token in self.tokens:
            yield from formatter.generate_highlighted(token)
    
    
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
            
            if (token_type == TOKEN_TYPE_SPECIAL_OPERATOR) and (token.value == '\\'):
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
        nester = ParserContextNester(self, self.flags, self.brace_nesting, self.done)
        self.brace_nesting = None
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
    
    previous_brace_nesting : `None | list<str>`
        How the braces are nested.
    
    previous_done : `bool`
        Whether processing is done.
    
    previous_flags : `int`
        Flags used to determine how to parse.
    """
    __slots__ = ('context', 'previous_brace_nesting', 'previous_flags', 'previous_done')
    
    def __new__(cls, context, previous_flags, previous_brace_nesting, previous_done):
        """
        Creates a new parser context nester.
        
        Parameters
        ----------
        context : ``HighlightParserContext``
            The context to use.
        
        previous_flags : `int`
            Flags used to determine how to parse.
        
        previous_brace_nesting : `None | list<str>`
            How the braces are nested.
        
        previous_done : `bool`
            Whether processing is done.
        """
        self = object.__new__(cls)
        self.context = context
        self.previous_brace_nesting = previous_brace_nesting
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
        context.brace_nesting = self.previous_brace_nesting
        context.flags = self.previous_flags
        context.done = self.previous_done
        context.recheck_done()
        return False
