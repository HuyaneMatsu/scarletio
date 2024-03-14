__all__ = ()

import codecs, re
from http.cookies import CookieError, SimpleCookie

from ..core import Task
from ..utils import from_json
from ..web_common.headers import CONNECTION, CONTENT_TYPE, METHOD_HEAD, SET_COOKIE
from ..web_common.helpers import HttpVersion10
from ..web_common.multipart import MimeType


try:
    import cchardet as chardet
except ImportError:
    try:
        import chardet
    except ImportError as err:
        chardet = None

JSON_RE = re.compile(r'^application/(?:[\w.+-]+?\+)?json')


class ClientResponse:
    """
    Http response class used by ``HTTPClient``.
    
    Attributes
    ----------
    _released : `bool`
        Whether the connection is released.
    body : `None`, `bytes`
        The received response body. Set as `None` if the response body is not yet received, or if it is empty.
    closed : `bool`
        Whether the response is closed.
    connection : `None`, ``Connection``
        Connection used to receive the request response. Set as `None` if the response is ``.close``-d or
        ``.release``-d.
    payload_waiter : `None`, ``Future``
        Future used to retrieve the response's body. It's result is set, when the respective protocol's reader task
        finished.
    cookies : `http.cookies.SimpleCookie`
        Received cookies with the response.
    headers : `None`, ``IgnoreCaseMultiValueDictionary``
        Headers of the response. Set when the http response is successfully received.
    history : `None`, `tuple` of ``ClientResponse``
        Response history. Set as `tuple` of responses from outside.
    loop : ``EventThread``
        The event loop, trough what the request is executed.
    method : `str`
        Method of the respective request.
    status : `int`
        Received status code. Set as `0` by default.
    url : ``URL``
        The requested url.
    writer : ``Task`` of ``ClientRequest.write_bytes``
        Payload writer task of the respective request.
    raw_message : `None`, ``RawResponseMessage``
        Raw received http response.
    """
    __slots__ = (
        '_released', 'body', 'closed', 'connection', 'payload_waiter', 'cookies', 'headers', 'history', 'loop',
        'method', 'status', 'url', 'writer', 'raw_message'
    )
       
    def __new__(cls, request, connection):
        """
        Crates a new ``ClientResponse`` from the given request and connection.
        
        Parameters
        ----------
        request : ``ClientRequest``
            The respective request.
        connection : ``Connection``
            The connection used to send the request and receive the response.
        """
        self = object.__new__(cls)
        self.loop = request.loop
        self.method = request.method
        self.url = request.original_url
        
        self.writer = request.writer
        self.closed = False
        self.cookies = SimpleCookie()
        self._released = False
        
        self.body = None
        self.status = 0
        self.payload_waiter = None
        self.headers = None
        self.connection = connection
        
        self.raw_message = None
        self.history = None  # will be added later
        
        return self
    
    
    @property
    def reason(self):
        """
        Returns the server response reason.
        
        Returns
        -------
        reason : `None`, `str`
        """
        message = self.raw_message
        if (message is not None):
            reason = message.reason
            if (reason is not None):
                return reason.decode()
    
    
    def __del__(self):
        """releases the response if not yet closed."""
        if self.closed:
            return
        
        self._release_connection()
    
    
    def __repr__(self):
        """Returns the response's representation."""
        ascii_encodable_url = str(self.url)
        
        return f'<{self.__class__.__name__}({ascii_encodable_url}) [{self.status} {self.reason!r}]>'
    
    
    async def start(self):
        """
        Starts response processing.
        
        This method is a coroutine.
        
        Returns
        -------
        self : ``ClientResponse``
        """
        try:
            protocol = self.connection.protocol
            
            payload_waiter = protocol.set_payload_reader(protocol._read_http_response())
            self.raw_message = message = await payload_waiter
            
            if self.method == METHOD_HEAD:
                payload_reader = None
            else:
                payload_reader = protocol.get_payload_reader_task(message)
            
            if (payload_reader is None):
                payload_waiter = None
                self._response_eof(None)
            else:
                payload_waiter = protocol.set_payload_reader(payload_reader)
                protocol.handle_payload_waiter_cancellation()
                payload_waiter.add_done_callback(self._response_eof)
            
            # response status
            self.status = message.status
            # headers
            self.headers = message.headers
            # OwO
            self.payload_waiter = payload_waiter
            
            # cookies
            for header in self.headers.get_all(SET_COOKIE, ()):
                try:
                    self.cookies.load(header)
                except CookieError: # so sad
                    pass
        except:
            self.close()
            raise
        
        return self
    
    
    def _response_eof(self, future):
        """
        Future callback added to the payload waiter future, to release the used connection.
        
        Parameters
        ----------
        future : ``Future``
            ``.payload_waiter`` future.
        """
        if self.closed:
            return
        
        self.payload_waiter = None
        
        connection = self.connection
        if (connection is not None):
            # WebSocket, protocol could be `None`, because connection could be detached.
            if (connection.protocol is not None) and self.raw_message.upgraded:
                return
            
            self._release_connection()
        
        self.closed = True
        self._cleanup_writer()
    
    
    def _release_connection(self):
        """
        Releases the response's connection.
        
        If the connection type is "close", closes the protocol as well.
        """
        connection = self.connection
        if connection is None:
            return
        
        headers = self.headers
        if (headers is None):
            connection_type = None
        else:
            connection_type = headers.get(CONNECTION, None)
        
        if (
            (self.raw_message.version <= HttpVersion10) if
            (connection_type is None) else
            (connection_type.lower() == 'close')
        ):
            connection.close()
        else:
            connection.release()
        self.connection = None
    
    
    def _notify_content(self):
        """
        Called when response reading is cancelled or released. Sets `ConnectionError` to the respective protocol if
        the payload is still reading.
        """
        payload_waiter = self.payload_waiter
        if (payload_waiter is not None):
            connection = self.connection
            if (connection is not None):
                connection.protocol.set_exception(ConnectionError('Connection closed.'))
        
        self._released = True
    
    
    def _cleanup_writer(self):
        """
        Cancels the writer task of the respective request. Called when the response is cancelled or released, or if
        reading the whole response is done.
        """
        writer = self.writer
        if (writer is not None):
            self.writer = None
            writer.cancel()
    
    
    async def read(self):
        """
        Reads the response's body.
        
        This method is a coroutine.
        
        Returns
        -------
        body : `bytes`
        """
        payload_waiter = self.payload_waiter
        if (payload_waiter is None):
            body = self.body
        else:
            try:
                self.body = body = await payload_waiter
            finally:
                self.payload_waiter = None
        
        return body
    
    
    def get_encoding(self):
        """
        Gets the encoding of the response's body.
        
        Returns
        -------
        encoding : `str`
            Defaults to `'utf-8'`.
        """
        content_type = self.headers.get(CONTENT_TYPE, '').lower()
        mime_type = MimeType(content_type)
        
        encoding = mime_type.parameters.get('charset', None)
        if encoding is not None:
            try:
                codecs.lookup(encoding)
            except LookupError:
                encoding = None
        
        if encoding is None:
            if mime_type.type == 'application' and mime_type.sub_type == 'json':
                encoding = 'utf-8' # RFC 7159 states that the default encoding is UTF-8.
            else:
                if chardet is None:
                    encoding = 'utf-8'
                else:
                    encoding = chardet.detect(self.body)['encoding']
        
        if not encoding:
            encoding = 'utf-8'
        
        return encoding
    
    
    async def text(self, encoding = None, errors = 'strict'):
        """
        Loads the response's content as text.
        
        This method is a coroutine.
        
        Parameters
        ----------
        encoding : `None`, `str` = `None`, Optional
            If no encoding is given, then detects it from the payload-
        errors : `str` = `'strict'`, Optional
            May be given to set a different error handling scheme. The default `errors` value is `'strict'`, meaning
            that encoding errors raise a `UnicodeError`. Other possible values are `'ignore'`, `'replace'`,
            `'xmlcharrefreplace'`, `'backslashreplace'` and any other name registered via `codecs.register_error()`.
        
        Returns
        -------
        text : `str`
        """
        body = await self.read()
        if body is None:
            return
        
        if encoding is None:
            encoding = self.get_encoding()
        
        return body.decode(encoding, errors)
    
    
    async def json(self, encoding = None, loader = from_json, content_type = None):
        """
        Loads the response's content as a json.
        
        This method is a coroutine.
        
        Parameters
        ----------
        encoding : None`, `str` = `None`, Optional
            Encoding to use instead of the response's. If given as `None` (so by default), then will use the response's
            own encoding.
        loader : `callable` = ``from_json``, Optional
            Json loader. Defaults to json.loads`.
        content_type : `None`, `str` = `None`, Optional
            Content type to use instead of the default one. Defaults to `'application/json'`.
        
        Returns
        -------
        json : `object`
        
        Raises
        ------
        TypeError
            If the response's mime_type do not match.
        """
        body = await self.read()
        if body is None:
            return
        
        if content_type is not None:
            received_content_type = self.headers.get(CONTENT_TYPE, '').lower()
            
            if (
                (JSON_RE.match(received_content_type) is None)
                     if (content_type is None) else
                (content_type not in received_content_type)
            ):
                raise TypeError(
                    f'Attempt to decode JSON with unexpected mime_type: {received_content_type!r}.'
                )
        
        stripped = body.strip()
        if not stripped:
            return None
        
        if encoding is None:
            encoding = self.get_encoding()
        
        return loader(stripped.decode(encoding))
    
    
    async def __aenter__(self):
        """
        Enters the client response as an asynchronous context manager.
        
        This method is a coroutine.
        """
        return self
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Releases the response if not yet closed.
        
        This method is a coroutine.
        """
        self.release()
        return False
    
    
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
        
        self._cleanup_writer()
    
    
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
        self._cleanup_writer()
