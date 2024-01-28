__all__ = (
    'AbortHandshake', 'ConnectionClosed', 'ContentEncodingError', 'HttpProcessingError', 'InvalidHandshake',
    'InvalidOrigin', 'InvalidUpgrade', 'PayloadError', 'ProxyError', 'WebSocketProtocolError'
)

class PayloadError(Exception):
    """
    Raised when http payload processing fails.
    """
    pass


class HttpErrorBase(Exception):
    """
    Base type for http exceptions.
    
    Attributes
    ----------
    message : `str`
        Error message.
    """
    __slots__ = ('message',)
    
    def __new__(cls, message = ''):
        self = Exception.__new__(cls, message)
        self.message = message
        return self
    
    __init__ = object.__init__


class InvalidHandshake(HttpErrorBase):
    """
    Raised when websocket handshake fails.
    
    Attributes
    ----------
    message : `str`
        Error message.
    response : `None`, ``ClientResponse``
        Received http answer.
    request : ``RawRequestMessage``
        Received raw http request.
    """
    __slots__ = ('response', 'request')
    
    def __new__(cls, message, *, response = None, request = None):
        self = Exception.__new__(cls, message, response, request)
        self.response = response
        self.message = message
        self.request = request
        return self


class HttpProcessingError(HttpErrorBase):
    """
    Base class for http content specific errors.
    
    Attributes
    ----------
    code : `int`
        Http error code. Defaults to `0`.
    message : `str`
        Error message. Defaults to empty string.
    headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        Respective headers.
    """
    __slots__ = ('code', 'headers')
    
    def __new__(cls, message = '', code = 0, headers = None):
        self = Exception.__new__(cls, message, code, headers)
        self.code = code
        self.headers = headers
        self.message = message
        return self
    
    
    def __repr__(self):
        """Returns the exception's representation."""
        return f'<{type(self).__name__} code = {self.code}, headers = {self.headers!r}, message = {self.message!r}>'


class AbortHandshake(HttpProcessingError):
    """
    Raised when websocket handshake is aborted on server side.
    
    Attributes
    ----------
    code : `int`
        Http error code. Defaults to `0`.
    message : `str`
        Error message. Defaults to empty string.
    headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        Respective headers.
    response : `None`, ``ClientResponse``
        Received http answer.
    request : ``RawRequestMessage``
        Received raw http request.
    """
    __slots__ = InvalidHandshake.__slots__
    
    def __new__(cls, message = '', code = 0, headers = None, *, response = None, request = None):
        self = Exception.__new__(cls, message, code, headers, response, request)
        self.response = response
        self.message = message
        self.request = request
        self.code = code
        self.headers = headers
        return self


class ProxyError(HttpProcessingError):
    """
    Raised when a proxy request responds with status other than "200 OK".
    
    Attributes
    ----------
    code : `int`
        Http error code. Defaults to `0`.
    message : `str`
        Error message. Defaults to empty string.
    headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        Respective headers.
    """
    __slots__ = ()


class InvalidOrigin(InvalidHandshake):
    """
    Raised when a websocket handshake received invalid origin header.
    """
    __slots__ = ()


class InvalidUpgrade(InvalidHandshake):
    """
    Raised when a websocket was not correctly upgraded.
    """
    __slots__ = ()


class ContentEncodingError(HttpProcessingError, PayloadError):
    """
    Raised when http content decoding fails.
    
    Attributes
    ----------
    code : `int`
        Http error code. Defaults to `0`.
    message : `str`
        Error message. Defaults to empty string.
    headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`) items
        Respective headers.
    """
    __slots__ = ()
    
    def __new__(cls, message = 'Bad Request', headers = None):
        return HttpProcessingError.__new__(cls, message, 400, headers)


CLOSE_REASONS = {
    1000: 'OK',
    1001: 'going away',
    1002: 'protocol error',
    1003: 'unsupported type',
    1004: '`reserved`',
    1005: 'no status code (internal)',
    1006: 'connection closed abnormally (internal)',
    1007: 'invalid data',
    1008: 'policy violation',
    1009: 'message too big',
    1010: 'extension required',
    1011: 'unexpected error',
    1013: 'Try again later',
    1014: 'Bad gateway',
    1015: 'TLS failure (internal)',
}

def get_close_reason(code):
    """
    Gets close for any websocket close code.
    
    Parameters
    ----------
    code : `int`
        Web socket close code.
    
    Returns
    -------
    reason : `str`
    """
    try:
        close_reason = CLOSE_REASONS[code]
    except KeyError:
        if code < 1000:
            close_reason = '`unused`'
        elif code < 2000:
            close_reason = '`reserved`'
        elif code < 3000:
            close_reason = '`reserved for extensions`'
        elif code < 4000:
            close_reason = '`registered`'
        elif code < 5000:
            close_reason = '`private use`'
        else:
            close_reason = '`unknown`'
    
    return close_reason


class ConnectionClosed(Exception):
    """
    Connection closed exception raised when a websocket is closed.
    
    Attributes
    ----------
    code : `int`
        Web socket close code.
    exception : `None`, `BaseException`
        Source exception if applicable.
    reason : `None or `str`
        Web socket close reason if any.
    """
    __slots__ = ('_reason', 'code', 'exception')
    
    def __new__(cls, code, exception, reason = None):
        """
        Creates a new ``ConnectionClosed`` exception from the given parameters.
        
        Parameters
        ----------
        code : `int`
            The websocket close code.
        exception : `None`, `BaseException`
            Source exception if applicable.
        reason : `None`, `str` = `None`, Optional
            Web socket close reason if any.
        """
        self = Exception.__new__(cls, code, exception, reason)
        self.code = code
        self.exception = exception
        self._reason = reason
        return self
    
    
    __init__ = object.__init__
    
    
    @property
    def reason(self):
        """
        Returns the websocket close reason.
        
        Returns
        -------
        reason : `str`
        """
        reason = self._reason
        if (reason is None):
            reason = get_close_reason(self.code)
            self._reason = reason
        
        return reason
    
    
    def __repr__(self):
        """Returns the exception's representation."""
        return f'<{type(self).__name__}, code = {self.code!r}, reason = {self.reason!r}, exception = {self.exception!r}>'
    
    
    __str__ = __repr__


class WebSocketProtocolError(Exception):
    """
    Exception raised by websocket when receiving invalid payload.
    """
    __slots__ = ()
    __init__ = object.__init__
