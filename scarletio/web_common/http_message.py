__all__ = ()

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
    
    def __init__(self, version, status, reason, headers):
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
        self.version = version
        self.status = status
        self.reason = reason
        self.headers = headers
        self._upgraded = 2


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
    
    def __init__(self, version, method, path, headers):
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
        self.version = version
        self.method = method
        self.path = path
        self.headers = headers
        self._upgraded = 2
