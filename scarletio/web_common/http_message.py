__all__ = ()

import reprlib

from ..utils import copy_docs

from .headers import CONNECTION, CONTENT_ENCODING, TRANSFER_ENCODING


class RawMessage:
    """
    Base class of ``RawResponseMessage`` and ``RawRequestMessage``.
    
    Attributes
    ----------
    _upgraded : `int`
        Whether the connection is upgraded.
        
        Is only set when the ``.upgraded`` property is accessed as `0`, `1`. Till is set as `2`.
    headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        The headers of the http message.
    """
    __slots__ = ('_upgraded', 'headers', )
    
    def __new__(cls, headers):
        """
        Creates a new raw http message.
        
        Parameters
        ----------
        headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
            The headers of the http message.
        """
        self = object.__new__(cls)
        self._upgraded = 2
        self.headers = headers
        return self
    
    
    @property
    def upgraded(self):
        """
        A get-set descriptor to access whether the message is upgraded. On first access the upgrade state is detected
        from the headers.
        """
        upgraded = self._upgraded
        if upgraded == 2:
            try:
                connection = self.headers[CONNECTION]
            except KeyError:
                upgraded = 0
            else:
                upgraded = (connection.lower() == 'upgrade')
            
            self._upgraded = upgraded
        
        return upgraded
    
    
    @upgraded.setter
    def upgraded(self, value):
        self._upgraded = value
    
    
    @property
    def chunked(self):
        """
        Returns whether the respective http message' body is chunked.
        
        Returns
        -------
        chunked : `bool`
        """
        try:
            transfer_encoding = self.headers[TRANSFER_ENCODING]
        except KeyError:
            return False
        
        return ('chunked' in transfer_encoding.lower())
    
    
    @property
    def encoding(self):
        """
        Returns the body encoding set in the http message's header.
        
        Returns
        -------
        encoding : `None`, `str`
            If no encoding is set, defaults to `None`.
        """
        try:
            encoding = self.headers[CONTENT_ENCODING]
        except KeyError:
            encoding = None
        else:
            encoding = encoding.lower()
        
        return encoding
    
    
    def _cursed_repr_builder(self):
        """
        Helper for ``__repr__`` function.
        
        This method is an iterable generator.
        
        Yields
        ------
        repr_parts : `list` of `str`
        
        Usage
        -----
        ```py
        for repr_parts in self._cursed_repr_builder():
            repr_parts.append(', your fields')
        
        return ''.join(repr_parts)
        ```
        """
        repr_parts = ['<', self.__class__.__name__]
        
        yield repr_parts
        
        repr_parts.append(' headers = ')
        repr_parts.append(repr(self.headers))
        
        repr_parts.append(', upgraded = ')
        repr_parts.append(repr(self.upgraded))
        
        repr_parts.append(', chunked = ')
        repr_parts.append(repr(self.chunked))
        
        encoding = self.encoding
        if (encoding is not None):
            repr_parts.append(', encoding = ')
            repr_parts.append(repr(encoding))
        
        repr_parts.append('>')
    
    
    def __repr__(self):
        """Returns the http messages representation."""
        for repr_parts in self._cursed_repr_builder():
            pass
        
        return ''.join(repr_parts)


class RawResponseMessage(RawMessage):
    """
    Represents a raw http response message.
    
    Attributes
    ----------
    _upgraded : `int`
        Whether the connection is upgraded.
        
        Is only set when the ``.upgraded`` property is accessed as `0`, `1`. Till is set as `2`.
    headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        The headers of the http message.
    version : ``HttpVersion``
        The http version of the response.
    status : `int`
        The response's status.
    reason : `bytes`
        Reason included with the response. Might be empty.
    """
    __slots__ = ('version', 'status', 'reason',)
    
    def __new__(cls, version, status, reason, headers):
        """
        Creates a new ``RawResponseMessage`` with the given parameters.
        
        Parameters
        ----------
        version : ``HttpVersion``
            The http version of the response.
        status : `int`
            The response's status.
        reason : `bytes`
            Reason included with the response. Might be empty.
        headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
            The headers of the http message.
        """
        self = RawMessage.__new__(cls, headers)
        
        self.version = version
        self.status = status
        self.reason = reason
        
        return self


    @copy_docs(RawMessage._cursed_repr_builder)
    def _cursed_repr_builder(self):
        for repr_parts in RawMessage._cursed_repr_builder(self):
            
            repr_parts.append(', version = ')
            repr_parts.append(repr(self.version))
            
            repr_parts.append(', status = ')
            repr_parts.append(repr(self.status))
            
            reason = self.reason
            if reason:
                repr_parts.append(', reason = ')
                repr_parts.append(reprlib.repr(self.reason))
            
            yield repr_parts


class RawRequestMessage(RawMessage):
    """
    Represents a raw http request message.
    
    Attributes
    ----------
    _upgraded : `int`
        Whether the connection is upgraded.
        
        Is only set when the ``.upgraded`` property is accessed as `0`, `1`. Till is set as `2`.
    headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        The headers of the http message.
    version : ``HttpVersion``
        The http version of the response.
    method : `int`
        The request's method.
    path : `str`
        The requested path.
    """
    __slots__ = ('version', 'method', 'path',)
    
    def __new__(cls, version, method, path, headers):
        """
        Creates a new ``RawRequestMessage`` with the given parameters.
        
        Parameters
        ----------
        version : ``HttpVersion``
            The http version of the response.
        method : `int`
            The request's method.
        path : `str`
            The requested path.
        headers : ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
            The headers of the http message.
        """
        self = RawMessage.__new__(cls, headers)
        
        self.version = version
        self.method = method
        self.path = path
        
        return self
    
    
    @copy_docs(RawMessage._cursed_repr_builder)
    def _cursed_repr_builder(self):
        for repr_parts in RawMessage._cursed_repr_builder(self):
            
            repr_parts.append(', version = ')
            repr_parts.append(repr(self.version))
            
            repr_parts.append(', method = ')
            repr_parts.append(repr(self.method))
            
            path = self.path
            if path:
                repr_parts.append(', path = ')
                repr_parts.append(repr(path))
            
            yield repr_parts
