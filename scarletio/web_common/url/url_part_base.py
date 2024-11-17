__all__ = ()

from ...utils import RichAttributeErrorBaseType

from ..quoting import quote, unquote

from .constants import URL_PART_FLAG_DECODED_SET, URL_PART_FLAG_ENCODED_SET


class URLPartBase(RichAttributeErrorBaseType):
    """
    Represents an url's part.
    
    Attributes
    ----------
    _decoded : `None | str`
        Decoded value.
    
    _encoded : `None | str`
        Encoded value.
    
    _flags : `int`
        Bitwise flags representing how the object is constructed.
    """
    __slots__ = ('_decoded', '_encoded', '_flags')
    
    
    def __new__(cls):
        """
        Use either ``.create_from_decoded`` or ``.create_from_encoded`` instead.
        
        Raises
        ------
        RuntimeError
        """
        raise RuntimeError(
            'Use either `.create_from_decoded` or `.create_from_encoded` instead.'
        )
    
    
    def __repr__(self):
        """Returns the url path's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # decoded
        decoded = self.decoded
        if (decoded is not None):
            repr_parts.append(' decoded = ')
            repr_parts.append(repr(decoded))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two url parts are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # decoded
        if self.decoded != other.decoded:
            return False
        
        return True
    
    
    @staticmethod
    def _encode(value):
        """
        Encodes the given value.
        
        Parameters
        ----------
        value : `None | str`
            The value to encode.
        
        Returns
        -------
        value : `None | str`
        """
        return quote(value)
    
    
    @staticmethod
    def _decode(value):
        """
        Decodes the given value.
        
        Parameters
        ----------
        value : `None | str`
            The value decode.
        
        Returns
        -------
        value : `None | str`
        """
        return unquote(value)
    
    
    @classmethod
    def create_from_decoded(cls, decoded):
        """
        Creates a new url part from a decoded value.
        
        Parameters
        ----------
        decoded : `None | str`
            Already decoded value.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self._decoded = decoded
        self._encoded = None
        self._flags = URL_PART_FLAG_DECODED_SET
        return self
    
    
    @classmethod
    def create_from_encoded(cls, encoded):
        """
        Creates a new url part from a encoded value.
        
        Parameters
        ----------
        encoded : `None | str`
            Encoded value.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self._decoded = None
        self._encoded = encoded
        self._flags = URL_PART_FLAG_ENCODED_SET
        return self


    @property
    def decoded(self):
        """
        Returns the part's decoded string representation.
        
        Returns
        -------
        decoded : `None | str`
            Decoded value.
        
        Returns
        -------
        self : `instance<cls>`
        """
        flags = self._flags
        if flags & URL_PART_FLAG_DECODED_SET:
            decoded = self._decoded
        
        else:
            if flags & URL_PART_FLAG_ENCODED_SET:
                decoded = self._decode(self._encoded)
            else:
                decoded = None
            
            self._decoded = decoded
            self._flags = flags | URL_PART_FLAG_DECODED_SET
        
        return decoded
    
    
    @property
    def encoded(self):
        """
        Returns the part's decoded string representation.
        
        Returns
        -------
        decoded : `None | str`
            Decoded value.
        """
        flags = self._flags
        if flags & URL_PART_FLAG_ENCODED_SET:
            encoded = self._encoded
        
        else:
            encoded = self._encode(self.decoded)
            
            self._encoded = encoded
            self._flags = flags | URL_PART_FLAG_ENCODED_SET
        
        return encoded
