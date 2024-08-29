__all__ = ('SSLFingerprint',)

from hashlib import md5, sha1

from ..utils import RichAttributeErrorBaseType

from .constants import HASH_FUNCTION_BY_DIGEST_LENGTH


class SSLFingerprint(RichAttributeErrorBaseType):
    """
    HTTP fingerprinting can be used to automate information systems and security audits.
    Automated security testing tools can use HTTP fingerprinting to narrow down the set of tests required,
    based on the specific platform or the specific web server being audited.
    
    Attributes
    ----------
    hash_function : `function`
        Hash function used by the fingerprint.
    value : `bytes`
        The fingerprint's value.
    """
    __slots__ = ('hash_function', 'value')
    
    def __new__(cls, value):
        """
        Creates a new fingerprint with the given parameters.
        
        Parameters
        ----------
        value : `bytes`
            SSLFingerprint value.
        
        Raises
        ------
        ValueError
            - If `fingerprint`'s length is not any of the expected ones.
            - If the detected `hash_function` is `md5` / `sha1`.
        """
        value_length = len(value)
        
        try:
            hash_function = HASH_FUNCTION_BY_DIGEST_LENGTH[value_length]
        except KeyError:
            raise ValueError(
                f'`fingerprint` has invalid length, got: value_length = {value_length!r}; value = {value!r}.'
            ) from None
        
        if hash_function is md5 or hash_function is sha1:
            raise ValueError(
                f'`md5` and `sha1` are insecure, use `sha256`. '
                f'Got value_length = {value_length!r}; value = {value!r}; hash_function = {hash_function.__name__}.'
            )
        
        self = object.__new__(cls)
        self.hash_function = hash_function
        self.value = value
        return self
    
    
    def check(self, protocol):
        """
        Checks whether the given protocol's ssl data matches the fingerprint.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            Asynchronous protocol implementation.
        
        Raises
        ------
        ValueError
            If the fingerprint don't match.
        """
        ssl_object = protocol.get_extra_info('ssl_object')
        if ssl_object is None:
            return
        
        certificate = ssl_object.getpeercert(True)
        received_value = self.hash_function(certificate).digest()
        own_value = self.value
        if received_value == own_value:
            return
        
        address = protocol.get_extra_info('peer_name')
        if address is None:
            host = 'unknown'
            port = 'unknown'
        else:
            host = address[0]
            port = str(address[1])
        
        raise ValueError(
            f'The expected fingerprint: {own_value!r} not matches the received; received = {received_value!r}; '
            f'host = {host}; port = {port}.'
        )
    
    
    def __eq__(self, other):
        """Returns whether the two fingerprints are equal.""" 
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value == other.value
    
    
    def __repr__(self):
        """Returns the fingerprint's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' value = ')
        repr_parts.append(repr(self.value))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


    def __hash__(self):
        """Returns the fingerprint's hash value."""
        return hash(self.value)
