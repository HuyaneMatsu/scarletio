__all__ = ()

from ...utils import copy_docs

from ..quoting import quote, unquote

from .url_part_base import URLPartBase


class URLFragment(URLPartBase):
    """
    Represents a url's fragment.
    
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
        return quote(value, safe = '?/:@#')
    
    
    @staticmethod
    @copy_docs(URLPartBase._decode)
    def _decode(value):
        return unquote(value)
