__all__ = ('quote', 'unquote',)

from string import ascii_letters, ascii_lowercase, digits


BINARY_ASCII_LOWERCASE = frozenset(ascii_lowercase.encode('ascii'))
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


def quote(value, safe = None, protected = None, query_string = False):
    """
    Http quotes the given `value`.
    
    Parameters
    ----------
    value : `None`, `str`
        The value to quote.
    safe : `None`, `str` = `None`, Optional
        Additional not percentage encoding safe characters, which should not be contained by potentially percent
        encoded characters.
    protected : `None`, `str` = `None`, Optional
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
            f'`value` can be `None`, `str`, got {value.__class__.__name__}; {value!r}.'
        )
    
    if not value:
        return ''
    
    value = value.encode('utf8')
    result = bytearray()
    percentage = None
    
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
    
    
    for char in value:
        if (percentage is not None):
            if char in BINARY_ASCII_LOWERCASE:
                char -= 32
            
            percentage.append(char)
            if len(percentage) == 3:
                percentage = bytes(percentage)
                try:
                    unquoted = chr(int(percentage[1:].decode('ascii'), base = 16))
                except ValueError as err:
                    raise ValueError(
                        f'Unallowed percentage: {percentage!r}; value = {value!r}.'
                    ) from err
                
                if (protected is not None) and (unquoted in protected):
                    result.extend(percentage)
                elif unquoted in safe:
                    result.append(ord(unquoted))
                else:
                    result.extend(percentage)
                
                percentage = None
            
            continue
            
        if char == b'%'[0]:
            percentage = bytearray()
            percentage.append(char)
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
            f'`value` can be `None`, `str`, got {value.__class__.__name__}; {value!r}.'
        )
    
    if not value:
        return ''
    
    percentage = None
    last_percentage = ''
    percentages = bytearray()
    result = []
    
    if (unsafe is not None):
        try:
            unsafe = UNQUOTE_UNSAFE_MAP[unsafe]
        except KeyError:
            unsafe = UNQUOTE_UNSAFE_MAP[unsafe] = frozenset(unsafe)
    
    for char in value:
        if (percentage is not None):
            percentage += char
            if len(percentage) == 3:
                percentages.append(int(percentage[1:], base = 16))
                last_percentage = percentage
                percentage = None
            continue
        
        if percentages:
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
                percentages.clear()
        
        if char == '%':
            percentage = char
            continue
        
        if percentages:
            result.append(last_percentage)  # %F8ab
            last_percentage = ''
        
        if char == '+':
            if (unsafe is None) or (char not in unsafe):
                char = ' '
            
            result.append(char)
            continue
        
        if (unsafe is not None) and (char in unsafe):
            result.append('%')
            result.extend(ord(char).__format__('X'))
            continue
        
        result.append(char)
    
    if percentages:
        try:
            unquoted = percentages.decode('utf8')
        except UnicodeDecodeError:
            result.append(last_percentage)  # %F8
        else:
            if query_string and (unquoted in QUERY_STRING_NOT_SAFE):
                result.append(quote(unquoted, query_string = True))
            elif (unsafe is not None) and (unquoted in unsafe):
                result.append(quote(unquoted))
            else:
                result.append(unquoted)
    
    return ''.join(result)
