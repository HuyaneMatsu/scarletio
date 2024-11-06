__all__ = ()

from reprlib import repr as short_repr

from ..utils import RichAttributeErrorBaseType, copy_docs, export

from .headers import CONNECTION, CONTENT_ENCODING, KEEP_ALIVE, TRANSFER_ENCODING, UPGRADE
from .helpers import HttpVersion11
from .keep_alive_info import KeepAliveInfo


CACHE_FLAG_UPGRADE_SET = 1 << 0
CACHE_FLAG_UPGRADE_VALUE = 1 << 1

CACHE_FLAG_CHUNKED_SET = 1 << 2
CACHE_FLAG_CHUNKED_VALUE = 1 << 3

CACHE_FLAG_ENCODING_SET = 1 << 4

CACHE_FLAG_KEEP_ALIVE_SET = 1 << 5


class RawMessage(RichAttributeErrorBaseType):
    """
    Base type of ``RawResponseMessage`` and ``RawRequestMessage``.
    
    Attributes
    ----------
    _cache_encoding : `None | str`
        Cache field for ``.encoding`` property.
    
    _cache_flags : `int`
        Cache flags for properties.
    
    _cache_keep_alive : `None | KeepAliveInfo`.
        cache field for ``.keep_alive`` property.
    
    headers : `IgnoreCaseMultiValueDictionary<str, str>`
        The headers of the http message.
    
    version : ``HttpVersion``
        The http version of the response.
    """
    __slots__ = ('_cache_encoding', '_cache_flags', '_cache_keep_alive', 'headers', 'version')
    
    def __new__(cls, version, headers):
        """
        Creates a new raw http message.
        
        Parameters
        ----------
        version : ``HttpVersion``
            The http version of the response.
        
        headers : `IgnoreCaseMultiValueDictionary<str, str>`
            The headers of the http message.
        """
        self = object.__new__(cls)
        self._cache_encoding = None
        self._cache_flags = 0
        self._cache_keep_alive = None
        self.headers = headers
        self.version = version
        return self
    
    
    def __repr__(self):
        """Returns the http messages representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' version = ')
        repr_parts.append(repr(self.version))
        
        self._put_repr_parts_into(repr_parts)
        
        repr_parts.append(', headers = ')
        repr_parts.append(repr(self.headers))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def _put_repr_parts_into(self, repr_parts):
        """
        Appends the embed field's representation parts.
        
        Parameters
        ----------
        repr_parts : `list<str>`
            Representation parts to extend.
        """
        upgraded = self.upgraded
        if upgraded:
            repr_parts.append(', upgraded = ')
            repr_parts.append(repr(upgraded))
        
        chunked = self.chunked
        if chunked:
            repr_parts.append(', chunked = ')
            repr_parts.append(repr(chunked))
        
        keep_alive = self.keep_alive
        if (keep_alive is not None):
            repr_parts.append(', keep_alive = ')
            repr_parts.append(repr(keep_alive))
        
        encoding = self.encoding
        if (encoding is not None):
            repr_parts.append(', encoding = ')
            repr_parts.append(repr(encoding))
    
    
    def _is_equal_same_type(self, other):
        """
        Returns whether self is equal to other. Other must be the same type as well.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other instance.
        
        Returns
        -------
        is_equal : `bool`
        """
        if self.headers != other.headers:
            return False
        
        if self.version != other.version:
            return False
        
        return True
    
    
    def __eq__(self, other):
        """Returns whether the two messages are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self._is_equal_same_type(other)
    
    
    @property
    def upgraded(self):
        """
        A get-set descriptor to access whether the message is upgraded.
        
        Returns
        -------
        upgrade : `bool`
        """
        cache_flags = self._cache_flags
        if cache_flags & CACHE_FLAG_UPGRADE_SET:
            return True if cache_flags & CACHE_FLAG_UPGRADE_VALUE else False
        
        headers = self.headers
        # Also require the `UPGRADE` header to be non-empty.
        if not headers.get(UPGRADE, ''):
            value = False
        
        else:
            try:
                connection = headers[CONNECTION]
            except KeyError:
                value = False
            else:
                value = (connection.casefold() == 'upgrade')
                if value:
                    cache_flags |= CACHE_FLAG_UPGRADE_VALUE
                else:
                    value = False
        
        cache_flags |= CACHE_FLAG_UPGRADE_SET
        self._cache_flags = cache_flags
        
        return value
    
    
    @upgraded.setter
    def upgraded(self, value):
        cache_flags = self._cache_flags
        cache_flags |= CACHE_FLAG_UPGRADE_SET
        
        if value:
            cache_flags |= CACHE_FLAG_UPGRADE_VALUE
        else:
            cache_flags &= ~CACHE_FLAG_UPGRADE_VALUE
        
        self._cache_flags = cache_flags
    
    
    @property
    def chunked(self):
        """
        Returns whether the respective http message' body is chunked.
        
        Returns
        -------
        chunked : `bool`
        """
        cache_flags = self._cache_flags
        if cache_flags & CACHE_FLAG_CHUNKED_SET:
            return True if cache_flags & CACHE_FLAG_CHUNKED_VALUE else False
        
        try:
            transfer_encoding = self.headers[TRANSFER_ENCODING]
        except KeyError:
            value = False
        else:
            value = ('chunked' in transfer_encoding.casefold())
            if value:
                cache_flags |= CACHE_FLAG_CHUNKED_VALUE
        
        cache_flags |= CACHE_FLAG_CHUNKED_SET
        self._cache_flags = cache_flags
        
        return value
    
    
    @chunked.setter
    def chunked(self, value):
        cache_flags = self._cache_flags
        cache_flags |= CACHE_FLAG_CHUNKED_SET
        
        if value:
            cache_flags |= CACHE_FLAG_CHUNKED_VALUE
        else:
            cache_flags &= ~CACHE_FLAG_CHUNKED_VALUE
        
        self._cache_flags = cache_flags
    
    
    @property
    def encoding(self):
        """
        Returns the body encoding set in the http message's header.
        
        Returns
        -------
        encoding : `None | str`
            If no encoding is set, defaults to `None`.
        """
        cache_flags = self._cache_flags
        if cache_flags & CACHE_FLAG_ENCODING_SET:
            return self._cache_encoding
        
        try:
            encoding = self.headers[CONTENT_ENCODING]
        except KeyError:
            encoding = None
        else:
            encoding = encoding.casefold()
        
        self._cache_flags = cache_flags | CACHE_FLAG_ENCODING_SET
        self._cache_encoding = encoding
        return encoding

        
    @encoding.setter
    def encoding(self, value):
        self._cache_flags |= CACHE_FLAG_ENCODING_SET
        self._cache_encoding = value
    
    
    @property
    def keep_alive(self):
        """
        Returns whether the respective http connection is keep-alive.
        
        Returns
        -------
        keep_alive : `bool`
        """
        cache_flags = self._cache_flags
        if cache_flags & CACHE_FLAG_KEEP_ALIVE_SET:
            return self._cache_keep_alive
        
        try:
            connection = self.headers[CONNECTION]
        except KeyError:
            keep_alive_enabled = self.version >= HttpVersion11
        else:
            keep_alive_enabled = ('close' not in connection.casefold())
        
        if keep_alive_enabled:
            keep_alive = KeepAliveInfo.from_header_value(self.headers.get(KEEP_ALIVE))
        else:
            keep_alive = None
        
        self._cache_flags = cache_flags | CACHE_FLAG_KEEP_ALIVE_SET
        self._cache_keep_alive = keep_alive
        
        return keep_alive
    
    
    @keep_alive.setter
    def keep_alive(self, value):
        self._cache_flags |= CACHE_FLAG_KEEP_ALIVE_SET
        self._cache_keep_alive = value


@export
class RawResponseMessage(RawMessage):
    """
    Represents a raw http response message.
    
    Attributes
    ----------
    _cache_encoding : `None | str`
        Cache field for ``.encoding`` property.
    
    _cache_flags : `int`
        Cache flags for properties.
    
    _cache_keep_alive : `None | KeepAliveInfo`.
        cache field for ``.keep_alive`` property.
    
    headers : `IgnoreCaseMultiValueDictionary<str, str>`
        The headers of the http message.
    
    reason : `None | str`
        Reason included with the response.
    
    status : `int`
        The response's status.
    
    version : ``HttpVersion``
        The http version of the response.
    """
    __slots__ = ('status', 'reason',)
    
    def __new__(cls, version, status, reason, headers):
        """
        Creates a new raw response message with the given parameters.
        
        Parameters
        ----------
        version : ``HttpVersion``
            The http version of the response.
        
        status : `int`
            The response's status.
        
        reason : `None | str`
            Reason included with the response.
        
        headers : `IgnoreCaseMultiValueDictionary<str, str>`
            The headers of the http message.
        """
        self = RawMessage.__new__(cls, version, headers)
        
        self.reason = reason
        self.status = status
        
        return self


    @copy_docs(RawMessage._put_repr_parts_into)
    def _put_repr_parts_into(self, repr_parts):
        repr_parts.append(' status = ')
        repr_parts.append(repr(self.status))
        
        reason = self.reason
        if reason is not None:
            repr_parts.append(', reason = ')
            repr_parts.append(short_repr(reason))
        
        RawMessage._put_repr_parts_into(self, repr_parts)
    
    
    @copy_docs(RawMessage._is_equal_same_type)
    def _is_equal_same_type(self, other):
        if not RawMessage._is_equal_same_type(self, other):
            return False
        
        if self.reason != other.reason:
            return False
        
        if self.status != other.status:
            return False
        
        return True


@export
class RawRequestMessage(RawMessage):
    """
    Represents a raw http request message.
    
    Attributes
    ----------
    _cache_encoding : `None | str`
        Cache field for ``.encoding`` property.
    
    _cache_flags : `int`
        Cache flags for properties.
    
    _cache_keep_alive : `None | KeepAliveInfo`.
        cache field for ``.keep_alive`` property.
    
    headers : `IgnoreCaseMultiValueDictionary<str, str>`
        The headers of the http message.
    
    method : `str`
        The request's method.
    
    path : `str`
        The requested path.
    
    version : ``HttpVersion``
        The http version of the response.
    """
    __slots__ = ('method', 'path')
    
    def __new__(cls, version, method, path, headers):
        """
        Creates a new ``RawRequestMessage`` with the given parameters.
        
        Parameters
        ----------
        version : ``HttpVersion``
            The http version of the response.
        
        method : `str`
            The request's method.
        
        path : `str`
            The requested path.
        
        headers : `IgnoreCaseMultiValueDictionary<str, str>`
            The headers of the http message.
        """
        self = RawMessage.__new__(cls, version, headers)
        
        self.method = method
        self.path = path
        
        return self
    
    
    @copy_docs(RawMessage._put_repr_parts_into)
    def _put_repr_parts_into(self, repr_parts):
        
        repr_parts.append(', method = ')
        repr_parts.append(repr(self.method))
        
        path = self.path
        if (path is not None):
            repr_parts.append(', path = ')
            repr_parts.append(repr(path))
        
        RawMessage._put_repr_parts_into(self, repr_parts)
    
    
    @copy_docs(RawMessage._is_equal_same_type)
    def _is_equal_same_type(self, other):
        if not RawMessage._is_equal_same_type(self, other):
            return False
        
        if self.method != other.method:
            return False
        
        if self.path != other.path:
            return False
        
        return True
