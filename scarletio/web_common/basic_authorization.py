__all__ = ('BasicAuthorization', )

from warnings import warn
from binascii import Error as EncodeOrDecodeError
from base64 import b64decode as base64_decode, b64encode as base64_encode
from re import compile as re_compile

from ..utils import RichAttributeErrorBaseType


AUTHORIZATION_HEADER_RP = re_compile('\\s*(.*?)\\s+(.*?)\\s*')
USER_ID_PASSWORD_JOIN_RP = re_compile('(.*?)(?:\\:(.*))?')
BASIC_AUTH_DEFAULT_ENCODING = 'latin1'


class BasicAuthorization(RichAttributeErrorBaseType):
    """
    Http basic authorization implementation.
    
    Attributes
    ----------
    encoding : `str`
        Encoding used to encode the authorization headers.
    
    password : `str`
        Authorization password. Can be empty string.
    
    user_id : `str`
        Authorization login name.
    """
    __slots__ = ('encoding', 'password', 'user_id',)
    
    def __new__(cls, user_id, password = '', *deprecated, encoding = BASIC_AUTH_DEFAULT_ENCODING):
        """
        Creates a new basic auth instance with the given parameters.
        
        Attributes
        ----------
        user_id : `str`
            Authorization user identifier.
        
        password : `str`, Optional
            Authorization password. Can be empty string.
        
        encoding : `str`, Optional (Keyword only)
            Encoding used to encode the authorization headers.
            Defaults to `'latin1'`.
        
        Raises
        ------
        ValueError
            - If `user_id` contains `':'` character.
        TypeError
            - if a parameter's type is invalid.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `encoding` parameter in `{cls.__name__}.__new__` is moved to be '
                    f'keyword only. Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            encoding = deprecated[0]
        
        
        if not isinstance(user_id, str):
            raise TypeError(
                f'`user_id` can be `str`; got {type(user_id).__name__}; user_id = {user_id!r}.'
            )
        
        if not isinstance(password, str):
            raise TypeError(
                f'`password` can be `str`; got {type(password).__name__}; password = {password!r}.'
            )
        
        if ':' in user_id:
            raise ValueError(
                f'`user_id` cannot contain `\':\'`. It is used as a special character. Got user_id = {user_id!r}.'
            )
        
        # Construct
        self = object.__new__(cls)
        self.encoding = encoding
        self.password = password
        self.user_id = user_id
        return self
    
    
    def __repr__(self):
        """Returns the basic authorisation's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # user_id
        repr_parts.append(' user_id = ')
        repr_parts.append(repr(self.user_id))
        
        # password
        password = self.password
        if password:
            repr_parts.append(', password = ')
            repr_parts.append(repr(password))
        
        # encoding
        encoding = self.encoding
        if encoding != BASIC_AUTH_DEFAULT_ENCODING:
            repr_parts.append(', encoding = ')
            repr_parts.append(repr(encoding))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two basic authorisations are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # encoding
        if self.encoding != other.encoding:
            return False
        
        # password
        if self.password != other.password:
            return False
        
        # user_id
        if self.user_id != other.user_id:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the basic authorization's hash value."""
        hash_value = 0
        
        # encoding
        encoding = self.encoding
        if encoding != BASIC_AUTH_DEFAULT_ENCODING:
            hash_value ^= hash(encoding)
        
        # password
        password = self.password
        if password:
            hash_value ^= hash(password)
        
        # user_id
        hash_value ^= hash(self.user_id)
        
        return hash_value
    
    
    @classmethod
    def from_header(cls, authorization_header, *deprecated, encoding = BASIC_AUTH_DEFAULT_ENCODING):
        """
        Creates a new basic auth instance from the given HTTP authorization header value.
        
        Parameters
        ----------
        authorization_header : `str`
            Authorization header value.
        
        encoding : `str` = `BASIC_AUTH_DEFAULT_ENCODING`, Optional (Keyword only)
            Encoding used to encode the authorization headers.
            Defaults to `'latin1'`.
        
        Returns
        -------
        self : `instance<cls>`
        
        Raises
        ------
        ValueError
            If the authorization method is not `'basic'`.
            If cannot parse the authorization headers.
            Cannot decode authorization header.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `encoding` parameter in `{cls.__name__}.__new__` is moved to be '
                    f'keyword only. Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            encoding = deprecated[0]
        
        match = AUTHORIZATION_HEADER_RP.fullmatch(authorization_header)
        if match is None:
            raise ValueError(
                f'Could not parse authorization header; authorization_header = {authorization_header!r}.'
            )
        
        authorization_method, token = match.groups()
        
        authorization_method = authorization_method.casefold()
        if authorization_method != 'basic':
            raise ValueError(
                f'Non basic authorization method; authorization_method = {authorization_method!r}.'
            )
        
        try:
            decoded = base64_decode(token.encode('ascii')).decode(encoding)
        except (EncodeOrDecodeError, UnicodeEncodeError, UnicodeDecodeError) as exception:
            raise ValueError(f'Could not decode token; token ={token!r}') from exception
        
        match = USER_ID_PASSWORD_JOIN_RP.fullmatch(decoded)
        if match is None:
            raise ValueError(f'Could not decode token; token = {token!r};')
        
        user_id, password = match.groups()
        if password is None:
            password = ''
        
        # Construct
        self = object.__new__(cls)
        self.user_id = user_id
        self.password = password
        self.encoding = encoding
        return self
    
    
    def to_header(self):
        """
        Converts the authorization to it's header value.
        
        Returns
        -------
        authorization_header : `str`
        """
        return f'Basic {base64_encode((f"{self.user_id}:{self.password}").encode(self.encoding)).decode(self.encoding)}'
    
    
    @classmethod
    def decode(cls, authorization_header, encoding = BASIC_AUTH_DEFAULT_ENCODING):
        """
        Deprecated and will be removed 2025 August. Please use `.from_header` instead.
        """
        warn(
            (
                f'`{cls.__name__}.decode` has been renamed to `from_header`.'
                f'`.decode` will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return cls.from_header(authorization_header, encoding = encoding)
    
    
    def encode(self):
        """
        Deprecated and will be removed 2025 August. Please use `.to_header` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.encode` has been renamed to `to_header`.'
                f'`.encode` will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return self.to_header()
    
    
    @property
    def username(self):
        """
        Deprecated and will be removed in 2025 August. Please use `.user_id` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.username` has been renamed to `user_id`.'
                f'`.username` will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.user_id
