__all__ = ()

from ...utils import copy_docs, copy_func

from ..quoting import quote, unquote

from .url_part_base_parsed import URLPartBaseParsed


encode = lambda value: quote(value, safe = '@:', protected = '/')
decode = unquote


def normalize_path_parts(parts):
    """
    Normalises the given parts.
    
    Parameters
    ----------
    parts : `list<str>`
        The parts to normalize.
    
    Returns
    -------
    parts : `None | list<str>`
        The normalized parts.
    """
    if parts is None:
        return None

    parts_length = len(parts)
    deleted_count = 0
    
    # Remove single dot parts. If the last is dot set it as empty string instead.
    index = 0
    while index < parts_length:
        part = parts[index]
        if part != '.':
            index += 1
            continue
        
        if index and index == parts_length - 1:
            parts[index] = ''
            index += 1
        else:
            del parts[index]
            parts_length -= 1
            deleted_count += 1
    
    # Remove double dot parts.
    to_delete = 0
    
    for index in reversed(range(parts_length)):
        part = parts[index]
        if part == '..':
            to_delete += 1
            continue
        
        if not to_delete:
            continue
        
        to_delete -= 1
        del parts[index]
        del parts[index]
        deleted_count += 2
        parts_length -= 2
        
    
    while to_delete:
        to_delete -= 1
        del parts[0]
        deleted_count += 1
        parts_length -= 1
        
    if deleted_count and (parts_length == 1) and (not parts[0]):
        del parts[0]
        parts_length = 0
    
    if (parts_length == 0):
        parts = None
    
    return parts


class URLPath(URLPartBaseParsed):
    """
    Represents a url's path.
    
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
    
    
    @staticmethod
    @copy_docs(URLPartBaseParsed._parse)
    def _parse(value, encoded):
        if (value is not None):
            if not value:
                return None
            
            if value.startswith('/'):
                value = value[1:]
            
            parts = [(decode(part) if encoded else part) for part in value.split('/')]
            if not parts[0]:
                del parts[0]
            
            parts = normalize_path_parts(parts)
            if (parts is not None):
                return tuple(parts)
    
    
    @staticmethod
    @copy_docs(URLPartBaseParsed._serialize)
    def _serialize(value, encoded):
        if (value is not None):
            built = []
            
            if not value:
                built.append('/')
            
            else:
                for part in value:
                    if encoded:
                        part = encode(part)
                
                    built.append('/')
                    built.append(part)
            
            return ''.join(built)
