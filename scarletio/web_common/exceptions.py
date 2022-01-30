__all__ = (
    'AbortHandshake', 'ConnectionClosed', 'ContentEncodingError', 'HttpProcessingError', 'InvalidHandshake',
    'InvalidOrigin', 'InvalidUpgrade', 'PayloadError', 'ProxyError', 'WebSocketProtocolError'
)

class PayloadError(Exception):
    """
    Raised when http payload processing fails.
    """
    pass


class InvalidHandshake(Exception):
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
    def __init__(self, message, *, response=None, request=None):
        self.response = response
        self.message = message
        self.request = request
        Exception.__init__(self, message)


class HttpProcessingError(Exception):
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
    def __init__(self, message='', code=0, headers=None):
        self.code = code
        self.headers = headers
        self.message = message
        
        Exception.__init__(self, f'HTTP {code}, message={message!r}, headers={headers!r}')


class AbortHandshake(HttpProcessingError, InvalidHandshake):
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
    def __init__(self, message='', code=0, headers=None, *, response=None, request=None):
        self.response = response
        self.message = message
        self.request = request
        self.code = code
        self.headers = headers
        
        Exception.__init__(self, f'HTTP {code}, message={message!r}, headers={headers!r}')


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
    pass


class InvalidOrigin(InvalidHandshake):
    """
    Raised when a websocket handshake received invalid origin header.
    """
    pass


class InvalidUpgrade(InvalidHandshake):
    """
    Raised when a websocket was not correctly upgraded.
    """
    pass


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
    def __init__(self, message='Bad Request', headers=None):
        HttpProcessingError.__init__(self, message, 400, headers)


CLOSE_REASONS = {
    1000: 'OK',
    1001: 'going away',
    1002: 'protocol error',
    1003: 'unsupported type',
    1004: '`reserved`',
    1005: 'no status code [internal]',
    1006: 'connection closed abnormally [internal]',
    1007: 'invalid data',
    1008: 'policy violation',
    1009: 'message too big',
    1010: 'extension required',
    1011: 'unexpected error',
    1013: 'Try again later',
    1014: 'Bad gateway',
    1015: 'TLS failure [internal]',
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
    
    def __init__(self, code, exception, reason=None):
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
        self.code = code
        self.exception = exception
        self._reason = reason
        Exception.__init__(self)
    
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
        
        return reason
    
    def __repr__(self):
        """Returns the exception's representation."""
        return f'<{self.__class__.__name__}, code={self.code!r}, reason={self.reason!r}, exception={self.exception!r}>'
    
    __str__ = __repr__


class WebSocketProtocolError(Exception):
    """
    Exception raised by websocket when receiving invalid payload.
    """
    pass
