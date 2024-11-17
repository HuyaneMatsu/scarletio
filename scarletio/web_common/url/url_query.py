__all__ = ()

from datetime import datetime as DateTime
from math import isinf, isnan

from ...utils import MultiValueDictionary, copy_docs, copy_func

from ..quoting import quote, unquote

from .constants import NoneType
from .url_part_base_parsed import URLPartBaseParsed


encode = lambda value: quote(value, safe = '/?:@=', query_string = True)
decode = unquote


def parse_query(query_string, encoded):
    """
    Parses a query string.
    
    Parameters
    ----------
    query_string : `None | str`
        Query string to parse if any.
    
    encoded : `bool`
        Whether the query is encoded.
    
    Returns
    -------
    query : `None | MultiValueDictionary<str, str>`
    """
    if query_string is None:
        return
    
    query = None
    value_length = len(query_string)
    item_end_index = 0
    
    while item_end_index < value_length:
        item_start_index = item_end_index
        
        # Find item end
        item_end_index = query_string.find('&', item_start_index)
        if item_end_index == -1:
            item_end_index = len(query_string)
        
        if item_start_index != item_end_index:
            # Find item middle
            item_middle_index = query_string.find('=', item_start_index, item_end_index)
            if item_middle_index == -1:
                query_key = query_string[item_start_index : item_end_index]
                query_value = ''
            
            else:
                query_key = query_string[item_start_index : item_middle_index]
                query_value = query_string[item_middle_index + 1 : item_end_index]
            
            if encoded:
                query_key = decode(query_key)
                query_value = decode(query_value)
            
            if query is None:
                query = MultiValueDictionary()
            
            query[query_key] = query_value
        
        item_end_index += 1
        continue
    
    return query



def normalize_query(query):
    """
    Normalises the given query.
    
    Parameters
    ----------
    query : `None | str | dict<str, str | int | bool | None | float | DateTime | (list | set)<...>> | (list | set)<(str, ...)>`
        The query to normalize.
    
    Returns
    -------
    normalized_query : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    if query is None:
        normalized_query = None
    
    elif isinstance(query, dict):
        normalized_query = _normalize_query_dict(None, query)
    
    elif isinstance(query, (list, set)):
        normalized_query = _normalize_query_list(None, query)
    
    elif isinstance(query, str):
        normalized_query = parse_query(query, False)
    
    elif isinstance(query, (bytes, bytearray, memoryview)):
        raise TypeError(
            f'Query type cannot be `bytes`, `bytearray` and `memoryview`, got '
            f'{type(query).__name__}; {query!r}.'
        )
    
    else:
        raise TypeError(
            f'Invalid query type: {type(query).__name__}; {query!r}.'
        )
    
    return normalized_query



def _normalize_query_dict(normalized_query, query_dict):
    """
    Normalises a query dict.
    
    Parameters
    ----------
    normalized_query : `None | MultiValueDictionary<str, str>`
        The already normalised query.
    
    query_dict : `dict<str, str | int | bool | None | float | DateTime | (list | set)<...>>`
        The query dict to normalize.
    
    Returns
    -------
    normalized_query : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    for query_key, query_value in query_dict.items():
        normalized_query = _normalize_query_item(normalized_query, query_key, query_value)
    
    return normalized_query


def _normalize_query_list(normalized_query, query_list):
    """
    Normalises a query list..
    
    Parameters
    ----------
    normalized_query : `None | MultiValueDictionary<str, str>`
        The already normalised query.
    
    query_dict : `(list | set)<(str, str | int | bool | None | float | DateTime | (list | set)<...>)>`
        The query list to normalize.
    
    Returns
    -------
    normalized_query : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    for query_key, query_value in query_list:
        normalized_query = _normalize_query_item(normalized_query, query_key, query_value)
    
    return normalized_query


def _normalize_query_item(normalized_query, query_key, query_value):
    """
    Normalises a query item (key-value pair).
    
    Parameters
    ----------
    normalized_query : `None | MultiValueDictionary<str, str>`
        The already normalised query.
    
    query_key : `str`
        Query key.
    
    query_value : `str | int | bool | None | float | DateTime | (list | set)<...>`
        Query value.
    
    Returns
    -------
    normalized_query : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    if isinstance(query_value, str):
        pass
    
    elif isinstance(query_value, bool):
        query_value = 'true' if query_value else 'false'
    
    elif isinstance(query_value, int):
        query_value = str(query_value)
    
    elif isinstance(query_value, NoneType):
        query_value = 'null'
    
    elif isinstance(query_value, DateTime):
        query_value = query_value.isoformat()
    
    elif isinstance(query_value, float):
        if isinf(query_value):
             raise ValueError('`inf` is not a supported query string parameter value.')
        
        if isnan(query_value):
            raise ValueError('`nan` is not a supported query string parameter value.')
        
        query_value = str(query_value)
    
    elif isinstance(query_value, (list, tuple, set)):
        return _normalize_query_item_list(normalized_query, query_key, query_value)
    
    else:
        raise TypeError(
            f'Unexpected value type received when serializing query string, got '
            f'{type(query_value).__name__}; {query_value!r}.'
        )
    
    if (not query_key) and (not query_value):
        return normalized_query
    
    if normalized_query is None:
        normalized_query = MultiValueDictionary()
    
    normalized_query[query_key] = query_value
    return normalized_query


def _normalize_query_item_list(normalized_query, query_key, query_value_list):
    """
    Normalises a query item where the value is a list of more values.
    
    Parameters
    ----------
    normalized_query : `None | MultiValueDictionary<str, str>`
        The already normalised query.
    
    query_key : `str`
        Query key.
    
    query_value : `(list | set)<tr | int | bool | None | float | DateTime | ...>`
        Query value.
    
    Returns
    -------
    normalized_query : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    for query_value in query_value_list:
        normalized_query = _normalize_query_item(normalized_query, query_key, query_value)
    
    return normalized_query


def serialize_query(query, encoded):
    """
    Serialises the given query.
    
    Parameters
    ----------
    query : `None | MultiValueDictionary<str, str>`
        The query to serialise.
    
    encoded : `bool
        Whether the output should be encoded.
    
    Returns
    -------
    query_string : `None | str`
    """
    if (query is None) or (not query):
        return None
    
    query_string_parts = []
    
    # Sort the keys to always get the same output.
    for query_key in sorted(query.keys()):
        if encoded:
            query_key_processed = encode(query_key)
        else:
            query_key_processed = query_key
        
        for query_value in query.get_all(query_key, ()):
            if encoded:
                query_value = encode(query_value)
            
            if query_string_parts:
                query_string_parts.append('&')
            
            query_string_parts.append(query_key_processed)
            query_string_parts.append('=')
            query_string_parts.append(query_value)
    
    return ''.join(query_string_parts)


class URLQuery(URLPartBaseParsed):
    """
    Represents a url's query.
    
    Attributes
    ----------
    _decoded : `None | str`
        Decoded value.
    
    _encoded : `None | str`
        Encoded value.
    
    _flags : `int`
        Bitwise flags representing how the object is constructed.
    
    parsed : `None | tuple<str>`
        The represented path split to parts.
    """
    __slots__ = ()
    
    
    _encode = staticmethod(copy_docs(URLPartBaseParsed._encode)(copy_func(encode)))
    _decode = staticmethod(copy_docs(URLPartBaseParsed._decode)(copy_func(decode)))
    
    
    _parse = staticmethod(copy_docs(URLPartBaseParsed._parse)(copy_func(parse_query)))
    _serialize = staticmethod(copy_docs(URLPartBaseParsed._serialize)(copy_func(serialize_query)))
