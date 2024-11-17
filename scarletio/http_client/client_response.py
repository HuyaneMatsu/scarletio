__all__ = ()

from codecs import lookup as lookup_encoding
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
from warnings import warn

from ..utils import RichAttributeErrorBaseType, from_json
from ..web_common.headers import CONTENT_TYPE, METHOD_CONNECT, METHOD_HEAD, SET_COOKIE
from ..web_common.multipart import MimeType

from .constants import JSON_RE

try:
    from cchardet import detect as detect_encoding
except ImportError:
    try:
        from chardet import detect as detect_encoding
    except ImportError as err:
        detect_encoding = None


class ClientResponse(RichAttributeErrorBaseType):
    """
    Http response class used by ``HTTPClient``.
    
    Attributes
    ----------
    _released : `bool`
        Whether the connection is released.
    
    body : `None | bytes`
        The received response body. Set as `None` if the response body is not yet received, or if it is empty.
        Not set as non-`None` if the payload was streamed.
    
    closed : `bool`
        Whether the response is closed.
    
    connection : `None | Connection`
        Connection used to receive the request response.
        Set as `None` if the response is ``.close``-d or ``.release``-d.
    
    cookies : `http.cookies.SimpleCookie`
        Received cookies with the response.
    
    history : `None | tuple<ClientResponse>`
        Response history. Set as `tuple` of responses from outside.
    
    loop : ``EventThread``
        The event loop, trough what the request is executed.
    
    method : `str`
        Method of the respective request.
    
    payload_stream : `None | PayloadStream`
        Future used to retrieve the response's body.
        It's result is set, when the respective protocol's reader task finished.
    
    raw_message : `None | RawResponseMessage`
        Raw received http response.
    
    url : ``URL``
        The requested url.
    
    write_body_task : `None | Task<ClientRequest.write_body>`
        Payload writer task of the respective request.
    """
    __slots__ = (
        '_released', 'body', 'closed', 'connection', 'cookies', 'history', 'loop', 'method', 'payload_stream',
        'raw_message', 'url', 'write_body_task' 
    )
       
    def __new__(cls, request, connection):
        """
        Crates a new client response from the given request and connection.
        
        Parameters
        ----------
        request : ``ClientRequest``
            The respective request.
        
        connection : ``Connection``
            The connection used to send the request and receive the response.
        """
        self = object.__new__(cls)
        
        self._released = False
        self.body = None
        self.closed = False
        self.connection = connection
        self.cookies = SimpleCookie()
        self.history = None
        self.loop = request.loop
        self.method = request.method
        self.payload_stream = None
        self.raw_message = None
        self.url = request.original_url
        self.write_body_task = request.write_body_task
        
        return self
    
    
    def __repr__(self):
        """Returns the response's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # url
        repr_parts.append(' url = ')
        repr_parts.append(str(self.url))
        
        # status & reason
        repr_parts.append(', response = ')
        repr_parts.append(repr(f'{self.status!s} {self.reason!s}'))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __del__(self):
        """releases the response if not yet closed."""
        if self.closed:
            return
        
        self._release_connection()
    
    
    @property
    def headers(self):
        """
        Headers of the response. Set when the http response is successfully received.
        
        Returns
        --------
        headers : `None | IgnoreCaseMultiValueDictionary<str, str>`
        """
        message = self.raw_message
        if (message is None):
            return None
        
        return message.headers
    
    
    @property
    def reason(self):
        """
        Returns the server response reason.
        
        Returns
        -------
        reason : `None | str`
        """
        message = self.raw_message
        if (message is None):
            return None
        
        reason = message.reason
        if (reason is not None):
            return reason
        
        return HTTPStatus(message.status).phrase
    
    
    @property
    def status(self):
        """
        Received status code. Returns `0` by default.
        
        Returns
        -------
        status : `int`
        """
        message = self.raw_message
        if (message is None):
            return 0
        
        return message.status
    
    
    async def start_processing(self):
        """
        Starts response processing.
        
        This method is a coroutine.
        """
        try:
            protocol = self.connection.protocol
            self.raw_message = message = await protocol.read_http_response()
            
            if self.method == METHOD_CONNECT:            
                # Do not read anything if we are doing a connect request.
                payload_stream = None
            
            else:
                if self.method == METHOD_HEAD:
                    payload_reader = None
                else:
                    payload_reader = protocol.get_payload_reader_task(message)
                
                if (payload_reader is None):
                    payload_stream = None
                    self._response_eof(None)
                else:
                    payload_stream = protocol.set_payload_reader(payload_reader)
                    payload_stream.add_done_callback(self._response_eof)
                    protocol.handle_payload_stream_abortion()
            
            self.payload_stream = payload_stream
            
            # cookies
            headers = message.headers
            if (headers is not None):
                for header in headers.get_all(SET_COOKIE, ()):
                    try:
                        self.cookies.load(header)
                    except CookieError: # so sad
                        pass
        except:
            self.close()
            raise
    
    
    def _response_eof(self, payload_stream):
        """
        Future callback added to the payload waiter future, to release the used connection.
        
        Parameters
        ----------
        payload_stream : `None | PayloadStream`
            The respective payload stream.
        """
        if self.closed:
            return
        
        connection = self.connection
        if (connection is not None):
            # WebSocket, protocol could be `None`, because connection could be detached.
            if (connection.protocol is not None) and self.raw_message.upgraded:
                return
            
            self._released = True
            self._release_connection()
        
        self.closed = True
        self._clean_up_writer()
    
    
    def _release_connection(self):
        """
        Releases the response's connection.
        
        If the connection type is `close`, closes the protocol as well.
        """
        connection = self.connection
        if connection is None:
            return
        
        raw_message = self.raw_message
        if raw_message is None:
            keep_alive = None
        else:
            keep_alive = raw_message.keep_alive
        
        self.connection = None
        connection.release(keep_alive)
    
    
    def _notify_content(self):
        """
        Called when response reading is cancelled or released.
        Sets `ConnectionError` to the respective protocol if the payload is still reading.
        """
        payload_stream = self.payload_stream
        if (payload_stream is not None):
            connection = self.connection
            if (connection is not None):
                protocol = connection.protocol
                if (protocol is not None):
                    protocol.set_exception(ConnectionError('Connection closed.'))
        
        self._released = True
    
    
    def _clean_up_writer(self):
        """
        Cancels the writer task of the respective request. Called when the response is cancelled or released, or if
        reading the whole response is done.
        """
        write_body_task = self.write_body_task
        if (write_body_task is not None):
            self.write_body_task = None
            write_body_task.cancel()
    
    
    async def read(self):
        """
        Reads the response's body.
        
        This method is a coroutine.
        
        Returns
        -------
        body : `None | bytes`
        """
        payload_stream = self.payload_stream
        if (payload_stream is None):
            body = self.body
        else:
            try:
                self.body = body = await payload_stream
            finally:
                self.payload_stream = None
        
        return body
    
    
    def get_encoding(self):
        """
        Gets the encoding of the response's body.
        
        Returns
        -------
        encoding : `str`
            Defaults to `'utf-8'`.
        """
        headers = self.headers
        if headers is None:
            return 'utf-8'
        
        content_type = headers.get(CONTENT_TYPE, '').casefold()
        mime_type = MimeType(content_type)
        
        encoding = mime_type.parameters.get('charset', None)
        if (encoding is not None):
            try:
                lookup_encoding(encoding)
            except LookupError:
                pass
            else:
                return encoding
        
        # RFC 7159 states that the default encoding is utf-8.
        if (mime_type.type == 'application' and mime_type.sub_type in ('json', 'rdap')):
            return 'utf-8'
        
        # If we cannot detect encoding leave
        if (detect_encoding is None):
            return 'utf-8'
        
        # Can we detect encoding from anything even?
        body = self.body
        if (body is None):
            return 'utf-8'
        
        encoding = detect_encoding(body)['encoding']
        if encoding is None:
            encoding = 'utf-8'
        
        return encoding
    
    
    async def text(self, *deprecated, encoding = None, errors = 'strict'):
        """
        Loads the response's content as text.
        
        This method is a coroutine.
        
        Parameters
        ----------
        encoding : `None`, `str` = `None`, Optional (Keyword only)
            If no encoding is given, then detects it from the payload.
        
        errors : `str` = `'strict'`, Optional (Keyword only)
            May be given to set a different error handling scheme. The default `errors` value is `'strict'`, meaning
            that encoding errors raise a `UnicodeError`. Other possible values are `'ignore'`, `'replace'`,
            `'xmlcharrefreplace'`, `'backslashreplace'` and any other name registered via `codecs.register_error()`.
        
        Returns
        -------
        text : `str`
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `encoding` and `errors` parameters of '
                    f'`{type(self).__name__}.text` are moved to be keyword only. '
                    f'Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            encoding = deprecated[0]
            
            if deprecated_length > 1:
                errors = deprecated[1]
        
        
        body = await self.read()
        if body is None:
            return
        
        if encoding is None:
            encoding = self.get_encoding()
        
        return body.decode(encoding, errors)
    
    
    async def json(self, *deprecated, content_type = None, encoding = None, loader = from_json):
        """
        Loads the response's content as a json.
        
        This method is a coroutine.
        
        Parameters
        ----------
        content_type : `None | str` = `None`, Optional (Keyword only)
            Content type to use instead of the default one.
            Pass it as empty string to disable the check.
        
        encoding : `None | str` = `None`, Optional (Keyword only)
            Encoding to use instead of the response's.
            If not given then will use the response's own encoding.
        
        loader : `callable` = ``from_json``, Optional (Keyword only)
            Json loader. Defaults to json.loads`.
        
        Returns
        -------
        json : `object`
        
        Raises
        ------
        TypeError
            If the response's mime_type do not match.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `encoding`, `loader` and `content_type` parameters of '
                    f'`{type(self).__name__}.json` are moved to be keyword only. '
                    f'Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            encoding = deprecated[0]
            
            if deprecated_length > 1:
                loader = deprecated[1]
            
            if deprecated_length > 2:
                content_type = deprecated[2]
        
        # body
        body = await self.read()
        if body is None:
            return None
        
        
        # content_type
        while True:
            # At this point we should have headers, but in tests we have only `.body`.
            headers = self.headers
            if headers is None:
                break
            
            received_content_type = headers.get(CONTENT_TYPE, '').casefold()
            
            if content_type is None:
                if (JSON_RE.match(received_content_type) is not None):
                    break
            
            else:
                if (content_type in received_content_type):
                    break
            
            raise TypeError(
                f'Attempt to decode JSON with unexpected mime_type: {received_content_type!r}.'
            )
        
        # encoding
        if encoding is None:
            encoding = self.get_encoding()
        
        return loader(body.decode(encoding))
    
    
    def close(self):
        """
        Closes the response and it's connection. The used connection will not be reused after.
        """
        if not self._released:
            self._notify_content()
        
        if self.closed:
            return
        
        self.closed = True
        
        connection = self.connection
        if (connection is not None):
            self.connection = None
            connection.close()
        
        self._clean_up_writer()
    
    
    def release(self):
        """
        Releases the response and it's connection. The used connection might be reused after.
        """
        if not self._released:
            self._notify_content()
        
        if self.closed:
            return
        
        self.closed = True
        
        self._release_connection()
        self._clean_up_writer()
    
    
    @property
    def payload_waiter(self):
        """
        Deprecated and will be removed in 2025 October. Please use `.payload_stream` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.payload_waiter` is deprecated and will be removed in 2025 October. '
                f'Please use `.payload_stream` instead. Note that it is a different type.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
    
        return self.payload_stream
