__all__ = ('JSONDecodeError', 'from_json', 'to_json')

from json import JSONDecodeError, dumps as dump_to_json, loads as from_json

from .docs import has_docs


@has_docs
def added_json_serializer(obj):
    """
    Default json encoder function for supporting additional object types.
    
    Parameters
    ----------
    obj : `iterable`
    
    Returns
    -------
    result : `Any`
    
    Raises
    ------
    TypeError
        If the given object is not json serializable.
    """
    obj_type = obj.__class__
    if hasattr(obj_type, '__iter__'):
        return list(obj)
    
    raise TypeError(f'Object of type {obj_type.__name__!r} is not JSON serializable.',)


@has_docs
def to_json(data):
    """
    Converts the given object to json.
    
    Parameters
    ----------
    data : `Any`
    
    Returns
    -------
    json : `str`
    
    Raises
    ------
    TypeError
        If the given object is /or contains an object with a non convertible type.
    """
    return dump_to_json(data, separators=(',', ':'), ensure_ascii=True, default=added_json_serializer)
