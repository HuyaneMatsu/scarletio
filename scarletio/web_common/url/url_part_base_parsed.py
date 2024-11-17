__all__ = ()

from ...utils import copy_docs

from ..quoting import quote, unquote

from .constants import URL_PART_FLAG_DECODED_SET, URL_PART_FLAG_ENCODED_SET
from .url_part_base import URLPartBase


class URLPartBaseParsed(URLPartBase):
    """
    Represents an url's part that can be parsed.
    
    Attributes
    ----------
    _decoded : `None | str`
        Decoded value.
    
    _encoded : `None | str`
        Encoded value.
    
    _flags : `int`
        Bitwise flags representing how the object is constructed.
    
    parsed : `None | object`
        The parsed value.
    """
    __slots__ = ('parsed',)
    
    def __new__(cls):
        """
        Use either ``.create_from_decoded``, ``.create_from_encoded`` or ``.create_from_parsed`` instead.
        
        Raises
        ------
        RuntimeError
        """
        raise RuntimeError(
            'Use either `.create_from_decoded`, `.create_from_encoded` or `.create_from_parsed` instead.'
        )
    
    
    def __eq__(self, other):
        """Returns whether the two url parts are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # parsed
        if self.parsed != other.parsed:
            return False
        
        return True
    
    
    def _parse(value, encoded):
        """
        Parses the given value.
        
        Parameters
        ----------
        value : `None | str`
            The value to parse.
        
        encoded : `bool`
            Whether an encoded value is passed.
        
        Returns
        -------
        value : `None | object`
        """
        if encoded:
            value = unquote(value)
        
        return value
    
    
    @staticmethod
    def _serialize(value, encoded):
        """
        Serializes the given value.
        
        Parameters
        ----------
        value : `None | object`
            The value serialize.
        
        encoded : `bool`
            Whether an encoded value is requested.
        
        Returns
        -------
        value : `None | str`
        """
        if encoded:
            value = quote(value)
        
        return value
    
    
    @classmethod
    @copy_docs(URLPartBase.create_from_decoded)
    def create_from_decoded(cls, decoded):
        parsed = cls._parse(decoded, False)
        
        self = object.__new__(cls)
        self._decoded = None
        self._encoded = None
        self._flags = 0
        self.parsed = parsed
        return self
    
    
    @classmethod
    @copy_docs(URLPartBase.create_from_encoded)
    def create_from_encoded(cls, encoded):
        parsed = cls._parse(encoded, True)
        
        self = object.__new__(cls)
        self._decoded = None
        self._encoded = None
        self._flags = 0
        self.parsed = parsed
        return self


    @classmethod
    @copy_docs(URLPartBase.create_from_encoded)
    def create_from_parsed(cls, parsed):
        """
        Creates a new url part from a parsed value.
        
        Parameters
        ----------
        parsed : `None | object`
            Parsed value.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self._decoded = None
        self._encoded = None
        self._flags = 0
        self.parsed = parsed
        return self
    
    
    @property
    @copy_docs(URLPartBase.decoded)
    def decoded(self):
        flags = self._flags
        if flags & URL_PART_FLAG_DECODED_SET:
            decoded = self._decoded
        
        else:
            if flags & URL_PART_FLAG_ENCODED_SET:
                decoded = self._decode(self._encoded)
            else:
                decoded = self._serialize(self.parsed, False)
            
            self._decoded = decoded
            self._flags = flags | URL_PART_FLAG_DECODED_SET
        
        return decoded
    
    
    @property
    @copy_docs(URLPartBase.encoded)
    def encoded(self):
        flags = self._flags
        if flags & URL_PART_FLAG_ENCODED_SET:
            encoded = self._encoded
        
        else:
            if flags & URL_PART_FLAG_DECODED_SET:
                encoded = self._encode(self._decoded)
            else:
                encoded = self._serialize(self.parsed, True)
            
            self._encoded = encoded
            self._flags = flags | URL_PART_FLAG_ENCODED_SET
        
        return encoded
