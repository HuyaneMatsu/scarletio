__all__ = ()

from ...utils import copy_docs

from .url_part_base import URLPartBase


class URLHostPart(URLPartBase):
    """
    Represents a url's host's part..
    
    Attributes
    ----------
    _decoded : `None | str`
        Decoded value.
    
    _encoded : `None | str`
        Encoded value.
    
    _flags : `int`
        Bitwise flags representing how the object is constructed.
    """
    __slots__ = ()
    
    @staticmethod
    @copy_docs(URLPartBase._encode)
    def _encode(value):
        if (value is not None):
            try:
                value.encode('ascii')
            except UnicodeEncodeError:
                value = value.encode('idna').decode('ascii')
            
        return value
    
    
    @staticmethod
    @copy_docs(URLPartBase._decode)
    def _decode(value):
        if (value is not None):
            try:
                value = value.encode('ascii').decode('idna')
            except UnicodeEncodeError:
                pass
        
        return value
