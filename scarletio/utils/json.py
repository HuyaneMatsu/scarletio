__all__ = ('JSONDecodeError', 'from_json', 'to_json')

from enum import Enum
from json import JSONDecodeError, dumps as dump_to_json, loads as from_json

from .docs import has_docs


@has_docs
def added_json_serializer(obj):
    """
    Default json encoder function for supporting additional object types.
    
    Parameters
    ----------
    obj : `iterable`, `Enum`
        The value to json serialize.
    
    Returns
    -------
    result : `object`
    
    Raises
    ------
    TypeError
        If the given object is not json serializable.
    """
    if hasattr(obj, '__iter__'):
        return list(obj)
    
    if isinstance(obj, Enum):
        return obj.value
    
    raise TypeError(f'Object of type {obj.__class__.__name__!r} is not JSON serializable, got {obj!r}')


@has_docs
def to_json(data):
    """
    Converts the given object to json.
    
    Parameters
    ----------
    data : `object`
    
    Returns
    -------
    json : `str`
    
    Raises
    ------
    TypeError
        If the given object is /or contains an object with a non convertible type.
    """
    return dump_to_json(data, separators = (',', ':'), ensure_ascii = True, default = added_json_serializer)
