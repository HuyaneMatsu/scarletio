__all__ = ()

import re

from .quoting import quote


_TOKEN_RP = re.compile(r'[-!#$%&\'*+.^_`|~0-9a-zA-Z]+')
_LIST_START_RP = re.compile('[\t ,]*')
_SPACE_RP = re.compile('[\t ]*')
_PROTOCOL_RP = re.compile(r'[-!#$%&\'*+.^_`|~0-9a-zA-Z]+(?:/[-!#$%&\'*+.^_`|~0-9a-zA-Z]+)?')

CHARS = frozenset((chr(i) for i in range(0, 128)))
CONTROLS = frozenset((*(chr(i) for i in range(0, 32)), chr(127)))
SEPARATORS = frozenset(
    ('(', ')', '<', '>', '@', ', ', ';', ':', '\\', '"', '/', '[', ']', '?', '=', '{', '}', ' ', chr(9)),
)
TOKENS = CHARS ^ CONTROLS ^ SEPARATORS

def build_extensions(available_extensions):
    """
    Builds websocket extensions header from the given extension values.
    
    Parameters
    ----------
    available_extensions : `list` of `object`
        Each websocket extension should have the following `4` attributes / methods:
        - `name`: `str`. The extension's name.
        - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
        - `decode` : `callable`. Decoder method, what processes a received websocket frame. Should accept `2`
            parameters: The respective websocket ``Frame``, and the ˙max_size` as `int`, what decides the
            maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
        - `encode` : `callable`. Encoder method, what processes the websocket frames to send. Should accept `1`
            parameter, the respective websocket ``Frame``.
    
    Returns
    -------
    header_value : `str`
    """
    main_parts = []
    sub_parts = []
    
    for available_extension in available_extensions:
        name = available_extension.name
        parameters = available_extension.request_params
        
        sub_parts.append(name)
        for key, value in parameters:
            if value is None:
                sub_parts.append(key)
            else:
                sub_parts.append(f'{key}={value}')
        
        main_parts.append('; '.join(sub_parts))
        sub_parts.clear()
    
    return ', '.join(main_parts)


def parse_extensions(header_value):
    """
    Parses extension header.
    
    Parameters
    ----------
    header_value : `str`
        Received extension header.

    Returns
    -------
    result : `list` of `tuple` (`str`, `list` of `tuple` (`str`, `str`))
        The parsed out extensions as `name` - `parameters` pairs. The `parameters` are in `list` storing
        `key` - `value` pairs.
    
    Raises
    ------
    ValueError
        Extension header value is incorrect.
    """
    result = []
    limit = len(header_value)
    index = 0
    
    check_start = True
    
    while True:
        # parse till 1st element
        matched = _LIST_START_RP.match(header_value, index)
        index = matched.end()
        
        # are we at the end?
        if index == limit:
            return result
        
        # now lets parse the extension's name
        matched = _TOKEN_RP.match(header_value, index)
        if matched is None:
            raise ValueError(
                f'Expected extension name since index {index!r}, got {header_value!r}.'
            )
        
        name = matched.group(0)
        index = matched.end()
        
        # nice, we have a name, we can make our item now!
        sub_parts = []
        result.append((name, sub_parts,),)
        
        # should we parse a sublist?
        while True:
            
            # after half item we skip this part
            if check_start:
                # are we at the end?
                if index == limit:
                    return result
                
                # lets parse till next character
                matched = _SPACE_RP.match(header_value, index)
                index = matched.end()
                
                # are we at the end?
                if index == limit:
                    return result
                
                # no sublist?
                if header_value[index] == ',':
                    index += 1
                    break

                # invalid character
                if header_value[index] != ';':
                    raise ValueError(
                        f'Expected \';\' at index {index!r}, got {header_value!r}.'
                    )
                
                # we have a sublist
                index += 1
                
            else:
                check_start = True
            
            # parse space
            matched = _SPACE_RP.match(header_value, index)
            index = matched.end()
            
            # are we at the end?
            if index == limit:
                break
            
            # lets parse the key now
            matched = _TOKEN_RP.match(header_value, index)
            if matched is None:
                raise ValueError(
                    f'Expected parameter name since index {index!r}, got {header_value!r}.'
                )
            
            key = matched.group(0)
            index = matched.end()
            
            # are we at the end?
            if index == limit:
                sub_parts.append((key, None,),)
                break
            
            # parse space
            matched = _SPACE_RP.match(header_value, index)
            index = matched.end()
            
            # are we at the end?
            if index == limit:
                sub_parts.append((key, None,),)
                break

            #is it a full item or a half?
            
            #next extension
            if header_value[index] == ',':
                sub_parts.append((key, None,),)
                index += 1
                break

            # next item
            if header_value[index] == ';':
                sub_parts.append((key, None,),)
                index += 1
                check_start = False
                continue

            #invalid character
            if header_value[index] != '=':
                raise ValueError(
                    f'Expected \',\' or \';\' or \'=\' at index {index!r}, got {header_value!r}.'
                )
            
            index += 1
            
            # parse space
            matched = _SPACE_RP.match(header_value, index)
            index = matched.end()
            
            # are we at the end?
            if index == limit:
                raise ValueError(
                    f'Expected a parameter value, but string ended, got {header_value!r}.'
                )
            
            # is it '"stuff"' ?
            if header_value[index] == '"':
                index += 1
                
                # are we at the end?
                if index == limit:
                    raise ValueError(
                        f'Expected a parameter value, but string ended, got {header_value!r}.'
                    )
                
                matched = _TOKEN_RP.match(header_value, index)
                if matched is None:
                    raise ValueError(
                        f'Expected parameter value since index {index!r}, got {header_value!r}'
                    )
                
                value = matched.group(0)
                index = matched.end()
                
                # are we at the end? or did we finish the string normally?
                if index == limit or header_value[index] != '"':
                    raise ValueError(
                        f'Expected a \'"\' after starting a value with \'"\', got {header_value!r}.'
                    )
                index += 1
            
            # is it 'stuff' ?
            else:
                matched = _TOKEN_RP.match(header_value, index)
                if matched is None:
                    raise ValueError(
                        f'Expected parameter value since index {index!r}, got {header_value!r}.'
                    )
                value = matched.group(0)
                index = matched.end()
            
            # we got a full item
            sub_parts.append((key, value,),)


def parse_connections(header_value):
    """
    Parses subprotocol or connection headers.
    
    Parameters
    ----------
    header_value : `str`
        Received subprotocol or connection header.
    
    Returns
    -------
    result : `list` of `str`
        The parsed subprotocol or connection headers.
    
    Raises
    ------
    ValueError
        Subprotocol or connection header value is incorrect.
    """
    result = []
    limit = len(header_value)
    index = 0
    
    while True:
        #parse till 1st element
        matched = _LIST_START_RP.match(header_value, index)
        index = matched.end()
        
        #are we at the end?
        if index == limit:
            return result
        
        #now lets parse the upgrade's name
        matched = _TOKEN_RP.match(header_value, index)
        if matched is None:
            raise ValueError(
                f'Expected upgrade type since index {index!r}, got {header_value!r}.'
            )
        
        name = matched.group(0)
        index = matched.end()

        #nice
        result.append(name)
        
        #are we at the end?
        if index == limit:
            return result

        #lets parse till next character
        matched = _SPACE_RP.match(header_value, index)
        index = matched.end()

        #are we at the end?
        if index == limit:
            return result
    
        #no sublist?
        if header_value[index] == ',':
            index += 1
            continue
        
        raise ValueError(
            f'Expected \',\' at index {index!r}, got {header_value!r}.'
        )


def build_subprotocols(subprotocols):
    """
    Builds websocket subprotocol headers from the given subprotocol values.
    
    Parameters
    ----------
    subprotocols : `list` of `str`
        A list of supported subprotocols.
    
    Returns
    -------
    header_value : `str`
    """
    return ', '.join(subprotocols)


parse_subprotocols = parse_connections # yes, these are the same


def parse_upgrades(header_value):
    """
    Parses upgrade headers.
    
    Parameters
    ----------
    header_value : `str`
        Received upgrade header.
    
    Returns
    -------
    result : `list` of `str`
        The parsed upgrade headers.
    
    Raises
    ------
    ValueError
        Upgrade header value is incorrect.
    """
    result = []
    limit = len(header_value)
    index = 0
    
    while True:
        # parse till 1st element
        matched = _LIST_START_RP.match(header_value, index)
        index = matched.end()
        
        # are we at the end?
        if index == limit:
            return result
        
        # now lets parse the upgrade's name
        matched = _PROTOCOL_RP.match(header_value, index)
        if matched is None:
            raise ValueError(
                f'Expected upgrade type since index {index!r}, got {header_value!r}.'
            )
        name = matched.group(0)
        index = matched.end()
        
        # nice
        result.append(name)
        
        # are we at the end?
        if index == limit:
            return result
        
        # lets parse till next character
        matched = _SPACE_RP.match(header_value, index)
        index = matched.end()
        
        # are we at the end?
        if index == limit:
            return result
        
        # no sublist?
        if header_value[index] == ',':
            index += 1
            continue
        
        raise ValueError(
            f'Expected \',\' at index {index!r}, got {header_value!r}.'
        )


USASCII_ESCAPABLE_RP = re.compile('[^\\041\\043-\\133\\135-\\176]')
USASCII_CHARACTERS = {'\t', *(chr(index) for index in range(0x20, 0x7F))}


def _escape_matched(match):
    """
    Escapes the matched value.
    
    Parameters
    ----------
    match : `re.Match`
        Regex match.
    
    Returns
    -------
    escaped : `str`
    """
    return '\\' + match.group(0)


def _try_usascii_escape(value):
    """
    If the content is `7-bit` (or `usascii`) it escapes it, so there is no need to quote.
    
    Parameters
    ----------
    value : `str`
        Value to escape.
    
    Returns
    -------
    escaped : `bool`
    value : `str`
    """
    if not (USASCII_CHARACTERS > {*value}):
        return False, value
    return True, USASCII_ESCAPABLE_RP.sub(_escape_matched, value)


def build_content_disposition_header(disposition_type, parameters, quote_fields):
    """
    Creates Content-Disposition header value.
    
    Parameters
    ----------
    disposition_type : `str`
        Disposition type. Can be one of following: `'inline'`, `'attachment'`, '`form-data`'.
    parameters : `dict` of (`str`, `str`) items
        Disposition parameters.
    quote_fields : `bool`
        Whether field values should be quoted.
    
    Returns
    -------
    output : `str`
    """
    if (not disposition_type) or not (TOKENS > {*disposition_type}):
        raise ValueError(
            f'Bad content disposition type {disposition_type!r}.'
        )
    
    if not parameters:
        return disposition_type
    
    parameter_parts = [disposition_type]
    for key, value in parameters.items():
        if key == 'file_name':
            key = 'filename'
        
        if (not key) or (not (TOKENS > {*key})):
            raise ValueError(
                f'Bad content disposition parameter {key!r} = {value!r}.'
            )
        
        if quote_fields:
            escaped, value = _try_usascii_escape(value)
            if escaped:
                value = f'"{value!s}"'
            else:
                key = key + '*'
                value = quote(value)
                value = f'utf-8\'\'{value!s}'
        else:
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            value = f'"{value!s}"'
        
        parameter_parts.append('; ')
        
        parameter_parts.append(key)
        parameter_parts.append('=')
        parameter_parts.append(value)
    
    return ''.join(parameter_parts)
