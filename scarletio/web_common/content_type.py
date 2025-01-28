__all__ = ('ContentType', 'ContentTypeParsingError', 'parse_content_type')

from ..utils import MultiValueDictionary, RichAttributeErrorBaseType


WHITE_SPACE = ' \t' # space & horizontal tab
DELIMITERS = (
    ',:;' # field delimiters
    '(){}[]<>\'\"' # Bracket delimiters
    '\\?@=/' # These are also not allowed
)


def _consume_whitespace(string, index, end):
    """
    Consumes all white space (and horizontal tabulator) till hits end of string or any other character.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    Returns
    -------
    index : `int` 
    """
    while True:
        if index >= end:
            break
        
        character = string[index]
        if character not in ' \t':
            break
        
        index += 1
        continue
    
    return index


def _parse_token(string, index, end, disallowed):
    """
    Parses a single token out. Stops when hits the first non-token character.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    disallowed : `None | str`
        Disallowed characters that cannot be part of then token.
    
    Returns
    -------
    index : `int` 
    token : `None | str`
    """
    start = index
    
    while True:
        if index >= end:
            break
        
        character = string[index]
        if (disallowed is not None) and (character in disallowed):
            break
        
        if (character in WHITE_SPACE) or (character in DELIMITERS):
            break
        
        index += 1
        continue
    
    if start >= index:
        token = None
    else:
        token = string[start : index]
    
    return index, token


def _parse_quoted(string, index, end):
    """
    Parses a quoted value. The start of the quoted value should be already consumed.
    Stops when the quote is closed (consuming it) or when we end of string is hit.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    Returns
    -------
    index : `int` 
    token : `None | str`
    expected : `None | str`
    """
    collected = None
    expected = None
    
    last_escape = False
    
    while True:
        if index >= end:
            if last_escape:
                if collected is None:
                    collected = []
                
                collected.append('\\')
            
            expected = '"'
            break
        
        character = string[index]
        
        index += 1
        
        if last_escape:
            last_escape = False
            
            if collected is None:
                collected = []
            
            if character not in '\\"':
                collected.append('\\')
            
            collected.append(character)
        
        else:
            if character == '"':
                break
            
            if character == '\\':
                last_escape = True
            
            else:
                if collected is None:
                    collected = []
                
                collected.append(character)
        
        continue
    
    if collected is None:
        value = None
    else:
        value = ''.join(collected)
    
    return index, value, expected


def _parse_token_with_space_around(string, index, end, disallowed):
    """
    Parses a token. Allows space to be around.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    disallowed : `None | str`
        Disallowed characters that cannot be part of then token.
    
    Returns
    -------
    index : `int` 
    token : `None | str`
    """
    index = _consume_whitespace(string, index, end)
    index, token = _parse_token(string, index, end, disallowed)
    index = _consume_whitespace(string, index, end)
    
    return index, token


def _parse_token_or_quited_with_space_around(string, index, end):
    """
    Parses a token or a quoted value out. Allows space to be around.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    Returns
    -------
    index : `int` 
    token : `None | str`
    expected : `None | str`
    """
    token = None
    expected = None
    
    index = _consume_whitespace(string, index, end)
    if index < end:
        character = string[index]
        if character == '"':
            index += 1
            index, token, expected = _parse_quoted(string, index, end)
        else:
            index, token = _parse_token(string, index, end, None)
    
    index = _consume_whitespace(string, index, end)
    return index, token, expected


def _parse_head(string, index, end):
    """
    Parses a content-type header's head.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    Returns
    -------
    index : `int`
    type_ : `None | str`
    sub_type : `None | str`
    suffix : `None | str`
    expected : `None | str`
    """
    type_ = None
    sub_type = None
    suffix = None
    expected = None
    
    while True:
        if index >= end:
            break
        
        index, type_ = _parse_token_with_space_around(string, index, end, ';/')
        if index >= end:
            break
        
        character = string[index]
        if character == ';':
            index += 1
            break
        
        if character != '/':
            expected = ';/'
            break
        
        index += 1
        index, sub_type = _parse_token_with_space_around(string, index, end, ';+')
        if index >= end:
            break
        
        character = string[index]
        if character == ';':
            index += 1
            break
        
        if character != '+':
            expected = ';+'
            break
        
        index += 1
        index, suffix = _parse_token_with_space_around(string, index, end, ';')
        if index >= end:
            break
        
        character = string[index]
        if character == ';':
            index += 1
            break
        
        expected = ';'
        break
    
    return index, type_, sub_type, suffix, expected


def _parse_parameter(string, index, end):
    """
    Parses a single parameter out. If ends with a semi colon, consumes it as well.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    index : `int`
        The index where to start the parsing.
    
    end : `int`
        The end where to stop parsing.
    
    Returns
    -------
    index : `int`
    type_ : `None | str`
    sub_type : `None | str`
    suffix : `None | str`
    expected : `None | str`
    """
    key = None
    value = None
    expected = None
    
    while True:
        if index >= end:
            break
        
        index, key = _parse_token_with_space_around(string, index, end, ';=')
        if index >= end:
            break
        
        character = string[index]
        if character == ';':
            index += 1
            break
        
        if character != '=':
            expected = ';='
            break
        
        index += 1
        index, value, expected = _parse_token_or_quited_with_space_around(string, index, end)
        if index >= end:
            break
        
        if string[index] == ';':
            index += 1
            break
        
        expected = ';'
        break
    
    return index, key, value, expected


def _parse_content_type(string):
    """
    Parses the given content-type header value.
    
    Parameters
    ----------
    string : `str`
        The string to parse.
    
    Returns
    -------
    type_ : `None | str`
    sub_type : `None | str`
    suffix : `None | str`
    parameters : `None | MultiValueDictionary<str, str>`
    expected : `None | str`
    """
    index = 0
    end = len(string)
    
    parameters = None
    
    index, type_, sub_type, suffix, expected = _parse_head(string, index, end)
    
    # type, sub_type, suffix are case in-sensitive
    if (type_ is not None):
        type_ = type_.casefold()
    
    if (sub_type is not None):
        sub_type = sub_type.casefold()
    
    if (suffix is not None):
        suffix = suffix.casefold()
    
    # Convert `*` head to `*/*`
    if (type_ == '*') and (sub_type is None):
        sub_type = '*'
    
    if (expected is None) and (index < end):
        while True:
            index, key, value, expected = _parse_parameter(string, index, end)
            
            # do we have an item?
            if (key is not None) or (value is not None):
                # key must be set & must is case in-sensitive
                if (key is None):
                    key = ''
                else:
                    key = key.casefold()
                
                # value must be set
                if (value is None):
                    value = ''
                
                if (parameters is None):
                    parameters = MultiValueDictionary()
                
                parameters[key] = value
            
            if (expected is not None):
                break
            
            if (index >= end):
                break
    
    if (expected is None):
        error = None
    else:
        error = (string, index, expected)
    
    return type_, sub_type, suffix, parameters, error


def parse_content_type(string):
    """
    Parses the given content-type header value. `None` allowed.
    
    Parameters
    ----------
    string : `None | str`
        The string to parse.
    
    Returns
    -------
    content_type : ``ContentType``
    content_type_parsing_error : `None | ContentTypeParsingError`
    """
    if (string is None) or (not string):
        content_type = ContentType.create_empty()
        content_type_parsing_error = None
    
    else:
        type_, sub_type, suffix, parameters, error = _parse_content_type(string)
        content_type = ContentType(type_, sub_type, suffix, parameters)
        if (error is None):
            content_type_parsing_error = None
        
        else:
            content_type_parsing_error = ContentTypeParsingError(*error)
        
    return content_type, content_type_parsing_error


class ContentTypeParsingError(RichAttributeErrorBaseType):
    """
    Returned when a content-type could not been fully parsed.
    Contains information to identify error location.
    
    Attributes
    ----------
    expected : `str`
        A string of the expected characters.
    
    index : `int`
        The position where the unexpected character is.
    
    string : `str`
        The string where the error occurred.
    """
    __slots__ = ('expected', 'index', 'string')
    
    def __new__(cls, string, index, expected):
        """
        Creates a new content type parsing error.
        
        Parameters
        ----------
        string : `str`
            The string where the error occurred.
        
        index : `int`
            The position where the unexpected character is.
        
        expected : `str`
            A string of the expected characters.
        """
        self = object.__new__(cls)
        self.expected = expected
        self.index = index
        self.string = string
        return self
    
    
    def __repr__ (self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # string
        repr_parts.append(' string = ')
        repr_parts.append(repr(self.string))
        
        # index
        repr_parts.append(', index = ')
        repr_parts.append(repr(self.index))
        
        # expected
        repr_parts.append(', expected = ')
        repr_parts.append(repr(self.expected))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # string
        if self.string != other.string:
            return False
        
        # index
        if self.index != other.index:
            return False
        
        # expected
        if self.expected != other.expected:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns hash(self)."""
        hash_value = 0
        
        # string
        hash_value ^= hash(self.string)
        
        # index
        hash_value ^= self.index
        
        # expected
        hash_value ^= hash(self.expected)
        
        return hash_value


class ContentType(RichAttributeErrorBaseType):
    """
    A content type, media type, or MIME type represents can be used to identify a data's type and format.
    
    Attributes
    ----------
    parameters : `MultiValueDictionary<str, str>`
        Additional parameters describing the content's format.
    
    sub_type : `None | str`
        Usually consists of the media format.
    
    suffix : `None | str`
        Augmentation for the content to additionally specify its underlying  structure.
    
    type : `None | str`
        The board use of the media type.
    """
    __slots__ = ('parameters', 'sub_type', 'suffix', 'type')
    
    def __new__(cls, type_, sub_type, suffix, parameters):
        """
        Creates a content type with the given parameters.
        
        Parameters
        ----------
        type_ : `None | str`
            The board use of the media type.
        
        sub_type : `None | str`
            Usually consists of the media format.
        
        suffix : `None | str`
            Augmentation for the content to additionally specify its underlying  structure.
        
        parameters : `MultiValueDictionary<str, str>`
            Additional parameters describing the content's format.
        """
        self = object.__new__(cls)
        self.parameters = parameters
        self.sub_type = sub_type
        self.suffix = suffix
        self.type = type_
        return self
    
    
    @classmethod
    def create_empty(cls):
        """
        Creates an empty content type.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.parameters = None
        self.sub_type = None
        self.suffix = None
        self.type = None
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # type_
        type_ = self.type
        if (type_ is None):
            field_added = False
        
        else:
            field_added = True
            
            repr_parts.append(' type = ')
            repr_parts.append(repr(type_))
        
        # sub_type
        sub_type = self.sub_type
        if (sub_type is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' sub_type = ')
            repr_parts.append(repr(sub_type))
        
        # suffix
        suffix = self.suffix
        if (suffix is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' suffix = ')
            repr_parts.append(repr(suffix))
        
        # parameters
        parameters = self.parameters
        if (parameters is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' parameters = ')
            repr_parts.append(repr(parameters))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
        
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # type
        if self.type != other.type:
            return False
        
        # sub_type
        if self.sub_type != other.sub_type:
            return False
        
        # suffix
        if self.suffix != other.suffix:
            return False
        
        # parameters
        if self.parameters != other.parameters:
            return False
        
        return True
    
    
    def __hash__(self, other):
        """Returns hash(self)."""
        hash_value = 0
        
        # type
        type_ = self.type
        if (type_ is not None):
            hash_value ^= hash(type_)
        
        # sub_type
        sub_type = self.sub_type
        if (sub_type is not None) and (sub_type != '*'):
            hash_value ^= hash(sub_type)
        
        # suffix
        suffix = self.suffix
        if (suffix is not None):
            hash_value ^= hash(suffix)
        
        # parameters
        parameters = self.parameters
        if (parameters is not None):
            for key in sorted(parameters.keys()):
                value_hash = 0
                for value in parameters.get_all(key):
                    value_hash ^= hash(value)
                
                hash_value ^= (hash(key) & value_hash)
        
        return hash_value
    
    
    def get_parameter(self, key, default = None):
        """
        Returns the parameter of the content type for the given key.
        
        Parameters
        ----------
        key : `str`
            Key to return the value for.
        
        default : `object` = `None`
            Default value to return if value is missing.
        
        Returns
        -------
        value : `str | default`
        """
        parameters = self.parameters
        if parameters is None:
            return default
        
        return parameters.get(key, default)
