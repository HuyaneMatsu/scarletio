__all__ = ()

from ..docs import copy_docs
from ..export_include import export

from .matching import PYTHON_PARSERS, PYTHON_PARSERS_FORMAT_STRING, _try_match_till_format_string_expression
from .token import Token, _merge_tokens
from .token_types import (
    MERGE_TOKEN_TYPES, TOKEN_TYPE_ALL, TOKEN_TYPE_COMMENT, TOKEN_TYPE_LINEBREAK, TOKEN_TYPE_LINEBREAK_ESCAPED,
    TOKEN_TYPE_SPACE, TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_PUNCTUATION, TOKEN_TYPE_STRING_UNICODE_FORMAT,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK
)


class HighlightParserContextBase:
    """
    Base class for highlighting.
    
    Attributes
    ----------
    done : `bool`
        Whether processing is done.
    tokens : `list` of ``Token``
        The generated tokens.
    """
    __slots__ = ('done', 'tokens',)
    
    def __new__(cls):
        """
        Creates a new ``HighlightParserContextBase``.
        """
        return object.__new__(cls)
    
    
    def get_line_index(self):
        """
        Returns the line's index where the context is at.
        
        Returns
        -------
        line_index : `int`
        """
        return 0
    
    
    def get_line(self):
        """
        Returns the actual line of the context.
        
        Returns
        -------
        line : `str`
        """
        return ''
    
    
    def get_line_character_index(self):
        """
        Returns the character index of the context's actual line.
        
        Returns
        -------
        line_character_index : `int`
        """
        return 0
    
    
    def set_line_character_index(self, line_character_index):
        """
        Sets the actual line's character index.
        
        Parameters
        ----------
        line_character_index : `int`
            The index to set of the actual line.
            
            Pass it as `-1` to force end the line with linebreak or as `-2` to force it without linebreak.
        """
        pass
    
    
    def add_token(self, token_type, token_value):
        """
        Adds a token to the context.
        
        Parameters
        ----------
        token_type : `int`
            The token's identifier.
        token_value : `None`, `str`
            The token's value.
        """
        token = Token(token_type, token_value)
        self.tokens.append(token)
    
    
    def add_tokens(self, tokens):
        """
        Adds tokens to the context.
        
        Parameters
        ----------
        tokens : `list` of ``Token``
            The tokens to add.
        """
        self.tokens.extend(tokens)
    
    
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
            
            if token_type == TOKEN_TYPE_LINEBREAK_ESCAPED:
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
        pass
    
    
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
        return
        yield
    
    
    def _end_of_line(self):
        """
        Adds a linebreak token to the context.
        """
        tokens = self.tokens
        
        for token in reversed(tokens):
            token_type = token.type
            if token_type == TOKEN_TYPE_SPACE:
                continue
            
            if token_type == TOKEN_TYPE_COMMENT:
                continue
            
            if (token_type == TOKEN_TYPE_SPECIAL_OPERATOR) and (token.value == '\\'):
                token.type = TOKEN_TYPE_LINEBREAK_ESCAPED
            
            break


class HighlightParserContext(HighlightParserContextBase):
    """
    Represents a context of highlighting any content.
    
    Attributes
    ----------
    done : `bool`
        Whether processing is done.
    tokens : `list` of ``Token``
        The generated tokens.
    line_character_index : `int`
        The index of the character of the processed line.
    line_index : `int`
        The index of the line which is processed at the moment.
    lines : `list` of `str`
        The lines to highlight.
    """
    __slots__ = ('line_character_index', 'line_index', 'lines')
    
    def __new__(cls, lines):
        """
        Creates a new ``HighlightParserContext``.
        
        Parameters
        ----------
        lines : `list` of `str`
            The lines what the highlight context should match.
        """
        lines = [line for line in lines if line]
        
        if len(lines) == 0:
            done = True
        else:
            done = False
        
        self = object.__new__(cls)
        
        self.lines = lines
        self.line_index = 0
        self.line_character_index = 0
        self.done = done
        self.tokens = []
        
        return self
    
    
    @copy_docs(HighlightParserContextBase.get_line_index)
    def get_line_index(self):
        return self.line_index
    
    
    @copy_docs(HighlightParserContextBase.get_line)
    def get_line(self):
        lines = self.lines
        line_index = self.line_index
        if len(lines) <= line_index:
            line = ''
        else:
            line = lines[line_index]
        
        return line
    
    
    @copy_docs(HighlightParserContextBase.get_line_character_index)
    def get_line_character_index(self):
        return self.line_character_index
    
    
    @copy_docs(HighlightParserContextBase.set_line_character_index)
    def set_line_character_index(self, line_character_index):
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
            
            if line_character_index != -2:
                self._end_of_line()
            
            line_character_index = 0
        
        self.line_character_index = line_character_index
    
    
    @copy_docs(HighlightParserContextBase.match)
    def match(self):
        while not self.done:
            for parser in PYTHON_PARSERS:
                if parser(self):
                    break
        
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
    
    
    @copy_docs(HighlightParserContextBase.generate_highlighted)
    def generate_highlighted(self, formatter):
        for token in self.tokens:
            yield from formatter.generate_highlighted(token)



@export
class FormatStringParserContext(HighlightParserContextBase):
    """
    Highlighter used to highlight format strings.
    
    Attributes
    ----------
    done : `bool`
        Whether processing is done.
    tokens : `list` of ``Token``
        The generated tokens.
    brace_level : `int`
        The internal brace level to un-match before entering a string.
    in_code : `bool`
        Whether we are parsing format code.
    line : `str`
        The internal content of the format string.
    line_character_index : `int`
        The index of the character of the processed line.
    """
    __slots__ = ('brace_level', 'in_code', 'line', 'line_character_index', )
    
    def __new__(cls, line):
        """
        Creates a new ``FormatStringParserContext``.
        
        Parameters
        ----------
        line : `str`
            A format string's internal content to highlight.
        """
        if len(line) == 0:
            done = True
        else:
            done = False
        
        self = object.__new__(cls)
        
        self.line = line
        self.done = done
        self.tokens = []
        self.line_character_index = 0
        self.brace_level = 0
        self.in_code = False
        
        return self
    
    
    @copy_docs(HighlightParserContextBase.get_line)
    def get_line(self):
        return self.line
    
    
    @copy_docs(HighlightParserContextBase.get_line_character_index)
    def get_line_character_index(self):
        return self.line_character_index
    
    
    @copy_docs(HighlightParserContextBase.set_line_character_index)
    def set_line_character_index(self, line_character_index):
        line = self.line
        
        if (line_character_index < 0) or (len(line) <= line_character_index):
            line_character_index = 0
            self.done = True
        
        self.line_character_index = line_character_index
    
    
    @copy_docs(HighlightParserContextBase.add_token)
    def add_token(self, token_type, token_value):
        if token_type == TOKEN_TYPE_LINEBREAK:
            self._end_of_line()
        
        # Check braces and such ~ Nya!
        elif token_type == TOKEN_TYPE_STRING_UNICODE_FORMAT:
            if self.in_code:
                token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE
        
        elif token_type == TOKEN_TYPE_SPECIAL_PUNCTUATION and (token_value is not None):
            brace_level = self.brace_level
            if token_value == '{':
                if brace_level == self.in_code:
                    token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK
                
                brace_level += 1
                self.brace_level = brace_level
            
            elif token_value == '}':
                if brace_level == 0:
                    # Random `}`- may be added as well, so if we are outside of f string internal, leave it alone.
                    token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT
                else:
                    in_code = self.in_code
                    if brace_level <= in_code + 1:
                        token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK
                        if (brace_level == 1) and in_code:
                            self.in_code = False
                    
                    brace_level -= 1
                    self.brace_level = brace_level
            
            elif token_value == ':':
                if (self.brace_level == 1) and (not self.in_code):
                    self.in_code = True
                    token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK
        
        HighlightParserContextBase.add_token(self, token_type, token_value)
    
    
    @copy_docs(HighlightParserContextBase.match)
    def match(self):
        while True:
            if self.done:
                break
            
            if (self.brace_level == self.in_code):
                _try_match_till_format_string_expression(self)
            else:
                while True:
                    for parser in PYTHON_PARSERS_FORMAT_STRING:
                        if parser(self):
                            break
                    
                    # Need goto!
                    if self.done:
                        break
                    
                    # Need goto!
                    if self.brace_level == self.in_code:
                        break
