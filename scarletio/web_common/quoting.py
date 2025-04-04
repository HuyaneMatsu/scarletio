__all__ = ('quote', 'unquote',)

from string import ascii_letters, digits


BINARY_PERCENTAGE_ALLOWED = frozenset((f'%{index:02X}'.encode('ascii') for index in range(256)))
GEN_DELIMITERS = frozenset(':/?#[]@')
SUB_DELIMITERS_WITHOUT_QUOTES = frozenset('!$\'()*,;')
QUERY_STRING_NOT_SAFE = frozenset('+&=')
SUB_DELIMITERS = frozenset((*SUB_DELIMITERS_WITHOUT_QUOTES, *QUERY_STRING_NOT_SAFE))
RESERVED = frozenset((*GEN_DELIMITERS, *SUB_DELIMITERS))
UNRESERVED = frozenset((*ascii_letters, *digits, *'-._~'))
ALLOWED = frozenset((*UNRESERVED, *SUB_DELIMITERS_WITHOUT_QUOTES))

QUOTE_SAFE_MAP = {}
UNQUOTE_UNSAFE_MAP = {}


def iter_nullable_string(string):
    """
    Iterates over the given nullable string.
    
    Parameters
    ----------
    string : `None`, `str`
        The string to iterate trough
    
    Yields
    ------
    element : `str`
    """
    if (string is not None):
        yield from string


def _base_16_char_to_int(char):
    """
    Converts a base-16 character to its integer representation.
    
    Parameters
    ----------
    char : `int`
        Character.
    
    Returns
    -------
    value : `int`
    """
    value = char & 0x7
    if char >= b'0'[0] and char <= b'9'[0]:
        pass
    elif (char >= b'a'[0] and char <= b'f'[0]) or (char >= b'A'[0] and char <= b'F'[0]):
        value += 9
    else:
        raise ValueError(
            f'Unallowed character in percentage: {chr(char)!r}.'
        )
    
    return value


def _int_to_base_16_char(value):
    """
    Converts a base-16 character to its integer representation.
    
    Parameters
    ----------
    value : `int`
        Integer.
    
    Returns
    -------
    char : `int`
    """
    char = 0x30 | value
    
    if value > 9:
        char += 0x27
    
    return char


def quote(value, safe = None, protected = None, query_string = False):
    """
    Http quotes the given `value`.
    
    Parameters
    ----------
    value : `None | str`
        The value to quote.
    
    safe : `None | str` = `None`, Optional
        Additional not percentage encoding safe characters, which should not be contained by potentially percent
        encoded characters.
    
    protected : `None | str` = `None`, Optional
        Additional characters, which should not be percentage encoded.
    
    query_string : `bool` = `False`, Optional
        Whether the `value` is a query string value.
    
    Returns
    -------
    unquoted : `None`, `str`
        The unquoted value. Returns `None` of `value` was given as `None` as well.
    
    Raises
    ------
    TypeError
        If `value` was not given neither as `None`, nor `str`.
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        raise TypeError(
            f'`value` can be `None`, `str`, got {type(value).__name__}; {value!r}.'
        )
    
    if not value:
        return ''
    
    value = value.encode('utf8')
    result = bytearray()
    
    key = (safe, protected, query_string)
    try:
        safe, binary_safe = QUOTE_SAFE_MAP[key]
    except KeyError:
        safe = frozenset((
            *iter_nullable_string(safe),
            *ALLOWED,
            *iter_nullable_string(protected),
            *iter_nullable_string(None if query_string else QUERY_STRING_NOT_SAFE),
        ))
        
        binary_safe = frozenset(ord(char) for char in safe)
        
        QUOTE_SAFE_MAP[key] = (safe, binary_safe)
    
    
    iterator = iter(value)
    for char in iterator:
        if char == b'%'[0]:
            try:
                char_0 = next(iterator)
                char_1 = next(iterator)
            except StopIteration:
                break
            
            joined = (_base_16_char_to_int(char_0) << 4) | _base_16_char_to_int(char_1)
            unquoted = chr(joined)
            
            if ((protected is not None) and (unquoted in protected)) or (unquoted not in safe):
                result.append(b'%'[0])
                result.append(char_0)
                result.append(char_1)
            
            else:
                result.append(joined)
            continue
        
        if query_string:
            if char == b' '[0]:
                result.append(b'+'[0])
                continue
        
        if char in binary_safe:
            result.append(char)
            continue
        
        result.extend((f'%{char:02X}').encode('ascii'))
    
    return result.decode('ascii')


def unquote(value, unsafe = None, query_string = False):
    """
    Http unquotes the given `value`.
    
    Parameters
    ----------
    value : `None`, `str`
        The value to quote.
    
    unsafe : `None`, `str` = `None`, Optional
        Additional not percentage encoding safe characters, which should not be contained by potentially percent
        encoded characters.
    
    query_string : `bool` = `False`, Optional
        Whether the `value` is a query string value.
    
    Returns
    -------
    unquoted : `None`, `str`
        The unquoted value. Returns `None` of `value` was given as `None` as well.
    
    Raises
    ------
    TypeError
        If `value` was not given neither as `None`, nor `str`.
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        raise TypeError(
            f'`value` can be `None`, `str`, got {type(value).__name__}; {value!r}.'
        )
    
    if not value:
        return ''
    
    percentages = None
    result = []
    joined = -1
    
    if (unsafe is not None):
        try:
            unsafe = UNQUOTE_UNSAFE_MAP[unsafe]
        except KeyError:
            unsafe = UNQUOTE_UNSAFE_MAP[unsafe] = frozenset(unsafe)
    
    iterator = iter(value)
    for char in iterator:
        if (percentages is not None):
            try:
                unquoted = percentages.decode('utf8')
            except UnicodeDecodeError:
                pass
            else:
                if query_string and (unquoted in QUERY_STRING_NOT_SAFE):
                    result.append(quote(unquoted, query_string = True))
                elif (unsafe is not None) and (unquoted in unsafe):
                    result.append(quote(unquoted))
                else:
                    result.append(unquoted)
                
                percentages = None
        
        if char == '%':
            try:
                char_0 = next(iterator)
                char_1 = next(iterator)
            except StopIteration:
                break
            
            joined = (_base_16_char_to_int(ord(char_0)) << 4) | _base_16_char_to_int(ord(char_1))
            
            if (percentages is None):
                percentages = bytearray()
            
            percentages.append(joined)
            continue
        
        if (percentages is not None) and (joined != -1):
            result.append('%')
            result.append(char_0)
            result.append(char_1)
            joined = -1
        
        if char == '+':
            if (unsafe is None) or (char not in unsafe):
                char = ' '
            
            result.append(char)
            continue
        
        if (unsafe is not None) and (char in unsafe):
            result.append('%')
            result.append(chr(_int_to_base_16_char(ord(char) >> 4)))
            result.append(chr(_int_to_base_16_char(ord(char) & 0xf)))
            continue
        
        result.append(char)
    
    
    if (percentages is not None):
        try:
            unquoted = percentages.decode('utf8')
        except UnicodeDecodeError:
            if (joined != -1):
                result.append('%')
                result.append(char_0)
                result.append(char_1)
        
        else:
            if query_string and (unquoted in QUERY_STRING_NOT_SAFE):
                result.append(quote(unquoted, query_string = True))
            elif (unsafe is not None) and (unquoted in unsafe):
                result.append(quote(unquoted))
            else:
                result.append(unquoted)
    
    return ''.join(result)
