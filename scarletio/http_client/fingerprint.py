__all__ = ()

from hashlib import md5, sha1, sha256


HASH_FUNCTION_BY_DIGEST_LENGTH = {
    16: md5,
    20: sha1,
    32: sha256,
}

class Fingerprint:
    """
    HTTP fingerprinting can be used to automate information systems and security audits. Automated security testing
    tools can use HTTP fingerprinting to narrow down the set of tests required, based on the specific platform or the
    specific web server being audited.
    
    Attributes
    ----------
    fingerprint : `bytes`
        The fingerprint's value.
    hash_function : `function`
        Hash function used by the fingerprint.
    
    Class Attributes
    ----------------
    HASH_FUNCTION_BY_DIGEST_LENGTH : `dict` of (`int`, `function`) items
        `fingerprint`'s length - `hash-function` relation mapping.
    """
    __slots__ = ('fingerprint', 'hash_function',)
    
    def __new__(cls, fingerprint):
        """
        Creates a new ``Fingerprint`` with the given parameters.
        
        Parameters
        ----------
        fingerprint : `bytes`
            Fingerprint value.
        
        Raises
        ------
        ValueError
            - If `fingerprint`'s length is not any of the expected ones.
            - If the detected `hash_function` is `md5` / `sha1`.
        """
        fingerprint_length = len(fingerprint)
        
        try:
            hash_function = HASH_FUNCTION_BY_DIGEST_LENGTH[fingerprint_length]
        except KeyError:
            raise ValueError(
                f'`fingerprint` has invalid length, got {fingerprint_length!r}, {fingerprint!r}.'
            ) from None
        
        if hash_function is md5 or hash_function is sha1:
            raise ValueError(
                '`md5` and `sha1` are insecure and not supported, use `sha256`.'
            )
        
        self = object.__new__(cls)
        self.hash_function = hash_function
        self.fingerprint = fingerprint
        return self
    
    
    def check(self, protocol):
        """
        Checks whether the given protocol's ssl data matches the fingerprint.
        
        Parameters
        ----------
        protocol : `object`
            Asynchronous protocol implementation.
        
        Raises
        ------
        ValueError
            If the fingerprint don't match.
        """
        if protocol.get_extra_info('ssl_context') is None:
            return
        
        ssl_object = protocol.get_extra_info('ssl_object')
        cert = ssl_object.getpeercert(binary_form = True)
        received = self.hash_function(cert).digest()
        fingerprint = self.fingerprint
        if received == fingerprint:
            return
            
        host, port, *_ = protocol.get_extra_info('peer_name')
        
        raise ValueError(
            f'The expected fingerprint: {fingerprint!r} not matches the received; received = {received!r}; '
            f'host = {host!r}; port = {port!r}.'
        )
