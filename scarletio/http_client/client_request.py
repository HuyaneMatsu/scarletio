__all__ = ('ClientRequest',)

from http.cookies import Morsel, SimpleCookie

from ..core import CancelledError, Task
from ..utils import IgnoreCaseMultiValueDictionary, RichAttributeErrorBaseType
from ..web_common.form_data import FormData
from ..web_common.headers import (
    AUTHORIZATION, CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TYPE, COOKIE, HOST, METHOD_CONNECT,
    TRANSFER_ENCODING
)
from ..web_common import BasicAuth
from ..web_common.helpers import is_ipv6_address
from ..web_common.http_stream_writer import HTTPStreamWriter
from ..web_common.multipart import create_payload

from .client_response import ClientResponse
from .connection_key import ConnectionKey
from .constants import DEFAULT_HEADERS
from .request_info import RequestInfo


class ClientRequest(RichAttributeErrorBaseType):
    """
    Http request class used by ``HTTPClient``.
    
    Attributes
    ----------
    auth : `None | BasicAuth`
        Authorization sent with the request.
    
    body : `None | PayloadBase`
        The request's body.
    
    chunked : `bool`
        Whether the request is sent chunked.
    
    compression : `None | str`
        Compression used when sending the request.
    
    headers : ``IgnoreCaseMultiValueDictionary``
        The headers of the request.
    
    loop : ``EventThread``
        The event loop, trough what the request is executed.
    
    method : `str`
        The request's method.
    
    original_url : ``URL``
        The original url, what was asked to request.
    
    proxy_auth : `None | BasicAuth`
        Proxy authorization sent with the request.
    
    proxy_headers : `None | IgnoreCaseMultiValueDictionary`
        Proxy headers to use if applicable.
    
    proxy_url : `None | URL`
        Proxy url to use if applicable.
    
    response : `None | ClientResponse`
        Object representing the received response. Set as `None` till ``.send`` finishes.
    
    ssl_context : `None | SSLContext`
        The connection's ssl type.
    
    ssl_fingerprint : `None | SSLFingerprint`
        Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
    
    url : ``URL``
        The url, what will be requested.
    
    write_body_task : `None | Task<.write_body>`
        Payload writer task, what is present meanwhile the request's payload is sending.
    """
    __slots__ = (
        'auth', 'body', 'chunked', 'compression', 'headers', 'loop', 'method', 'original_url', 'proxy_auth',
        'proxy_headers', 'proxy_url', 'response', 'ssl_context', 'ssl_fingerprint', 'url', 'write_body_task'
    )
    
    def __new__(
        cls,
        loop,
        method,
        url,
        headers,
        data,
        query_string_parameters,
        cookies,
        auth,
        proxy_url,
        proxy_headers,
        proxy_auth,
        ssl_context,
        ssl_fingerprint,
    ):
        """
        Creates a new client request with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop, trough what the request is executed.
        
        method : `str`
            The request's method.
        
        url : ``URL``
            The url to request.
        
        headers : ``IgnoreCaseMultiValueDictionary``
            Headers of the request.
        
        data : `None | bytes-like | io-like | FormData`
            Data to send as the request's body.
        
        query_string_parameters : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`
            Query string parameters.
        
        cookies : `None | dict<str, str | Morsel>`
            Cookies OwO.
        
        auth : `None`, ``BasicAuth``
            Authorization sent with the request.
        
        proxy_url : `None | URL`
            Proxy url to use if applicable.
        
        proxy_headers : `None | IgnoreCaseMultiValueDictionary`
            Proxy headers sent with the request.
        
        proxy_auth : `None | BasicAuth`
            Proxy authorization sent with the request.
        
        ssl_context : `None | SSLContext``
            The connection's ssl type.
        
        ssl_fingerprint : `None | SSLFingerprint`
            Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
        
        Raises
        ------
        TypeError
            - ˙Cannot serialize a field of the given `data`.
        ValueError
            - Host could not be detected from `url`.
            - `compression` and `Content-Encoding` would be set at the same time.
            - `chunked` cannot be set, because `Transfer-Encoding: chunked` is already set.
            - `chunked` cannot be set, because `Content-Length` header is already present.
        RuntimeError
            - If one of `data`'s field's content has unknown content-encoding.
            - If one of `data`'s field's content has unknown content-transfer-encoding.
        """
        if url.host is None:
            raise ValueError('Host could not be detected.')
        
        # Add extra query parameters to the url and remove fragments
        url = url.extend_query(query_string_parameters)
        request_url = url.with_fragment(None)
        
        # Check authorization
        if auth is None:
            # If authorization is given, try to detect from url.
            username = url.user
            password = url.password
            
            if (username is not None) and username:
                if password is None:
                    password = ''
                
                auth = BasicAuth(username, password)
        
        # Store auth in headers is applicable.
        if (auth is not None):
            headers[AUTHORIZATION] = auth.to_header()
        
        for key, value in DEFAULT_HEADERS:
            headers.setdefault(key, value)
        
        # Add host to headers if not present.
        if HOST not in headers:
            location = request_url.raw_host
            if is_ipv6_address(location):
                location = f'[{location}]'
            else:
                location = location.rstrip('.')
            
            if not request_url.is_default_port():
                port = request_url.port
                if (port is not None):
                    location = f'{location}:{port}'
            
            headers[HOST] = location
        
        # Update cookies
        if (cookies is not None) and cookies:
            cookie = SimpleCookie()
            
            cookie_header = headers.pop(COOKIE, '')
            if cookie_header:
                cookie.load(cookie_header)
            
            for key, value in cookies.items():
                if isinstance(key, Morsel):
                    try:
                        morsel_value = value[value.key]
                    except KeyError:
                        morsel_value = Morsel()
                    
                    morsel_value.set(value.key, value.value, value.coded_value)
                    value = morsel_value
                
                cookie[key] = value
            
            headers[COOKIE] = cookie.output(header = '', sep = ';').strip()
        
        # analyze headers & data
        if (data is not None) and (not data):
            data = None
        
        if (data is None):
            chunked = False
            compression = None
            
            # Remove not needed headers when not transferring any data.
            for header_name in (CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TYPE, TRANSFER_ENCODING):
                try:
                    del headers[header_name]
                except KeyError:
                    pass
        
        else:
            # Needed for transfer data checks
            chunked = 'chunked' in headers.get(TRANSFER_ENCODING, '').casefold()
            compression = headers.get(CONTENT_ENCODING, None)
            
            if (compression is not None):
                chunked = True
            
            # form_data
            if isinstance(data, FormData):
                data = data.generate_form()
            else:
                try:
                    data = create_payload(data, {'disposition': None})
                except LookupError:
                    data = FormData.from_fields(data).generate_form()
            
            if not chunked:
                if CONTENT_LENGTH not in headers:
                    size = data.size
                    if size is None:
                        chunked = True
                    else:
                        if CONTENT_LENGTH not in headers:
                            headers[CONTENT_LENGTH] = str(size)
            
            if CONTENT_TYPE not in headers:
                headers[CONTENT_TYPE] = data.content_type
            
            data_headers = data.headers
            if data_headers:
                for key, value in data_headers.items():
                    headers.setdefault(key, value)
            
            # Analyze transfer-encoding header.
            if chunked:
                if CONTENT_LENGTH in headers:
                    raise ValueError(
                        f'Chunked is mutually exclusive with the `{CONTENT_LENGTH!s}` header.'
                    )
                
                # We may have modify `chunked` value since the start, so lets set it again to make sure.
                headers[TRANSFER_ENCODING] = 'chunked'
            
            else:
                if CONTENT_LENGTH not in headers:
                    headers[CONTENT_LENGTH] = '0' if data is None else str(len(data))
        
        # Everything seems correct, create the object.
        self = object.__new__(cls)
        self.auth = auth
        self.body = data
        self.chunked = chunked
        self.compression = compression
        self.headers = headers
        self.loop = loop
        self.method = method
        self.original_url = url
        self.proxy_auth = proxy_auth
        self.proxy_headers = proxy_headers
        self.proxy_url = proxy_url
        self.response = None
        self.ssl_context = ssl_context
        self.ssl_fingerprint = ssl_fingerprint 
        self.url = request_url
        self.write_body_task = None
        
        return self
    
    
    def is_secure(self):
        """
        Returns whether the request is secure.
        
        Returns
        -------
        is_secure : `bool`
        """
        return self.url.scheme in ('https', 'wss')
    
    
    @property
    def connection_key(self):
        """
        Returns the connection key of request.
        
        Returns
        -------
        connection_key : ``ConnectionKey``
        """
        return ConnectionKey(
            self.host,
            self.port,
            self.proxy_auth,
            self.proxy_headers,
            self.proxy_url,
            self.is_secure(),
            self.ssl_context,
            self.ssl_fingerprint,
        )
    
    
    @property
    def request_info(self):
        """
        Returns base information representing the request.
        
        Returns
        -------
        request_info : ``RequestInfo``
        """
        return RequestInfo(
            self.headers,
            self.method,
            self.original_url,
            self.url,
        )
    
    
    @property
    def host(self):
        """
        Returns the request's host.
        
        Returns
        -------
        host : `str`
        """
        return self.url.host
    
    
    @property
    def port(self):
        """
        Returns the request's port.
        
        Returns
        -------
        port : `None | int`
        """
        return self.url.port
    
    
    async def write_body(self, connection):
        """
        Writes the request's body.
        
        This method is a coroutine.
        
        Parameters
        ----------
        writer : ``HTTPStreamWriter``
            Writer used to write the request's body into the connection's transport.
        
        connection : ``Connection``
            Connection of the request with what the payload is sent.
        """
        writer = HTTPStreamWriter(connection.protocol, self.compression, self.chunked)
        
        try:
            body = self.body
            if (body is not None):
                await self.body.write(writer)
        except OSError as exception:
            new_exception = OSError(exception.errno, f'Failed to write request body for {self.url!r}.')
            new_exception.__cause__ = exception
            connection.protocol.set_exception(new_exception)
        
        except GeneratorExit:
            raise
        
        except CancelledError:
            await writer.write_eof()
            raise
        
        except BaseException as exception:
            connection.protocol.set_exception(exception)
            raise
        
        else:
            await writer.write_eof()
        
        finally:
            self.write_body_task = None
    
    
    def begin(self, connection):
        """
        Begins sending the request.
        
        Parameters
        ----------
        connection : ``Connection``
            Connection, what is used to send the request.
        
        Returns
        -------
        response : ``ClientResponse``
        """
        try:
            url = self.url
            if self.method == METHOD_CONNECT:
                path = url.raw_host
                if is_ipv6_address(path):
                    path = f'[{path}]'
                
                port = url.port
                if port is not None:
                    path = f'{path}:{port}'
            
            elif (self.proxy_url is not None) and (not self.is_secure()):
                path = str(url)
            
            else:
                path = url.raw_path
                raw_query_string = url.raw_query_string
                if raw_query_string:
                    path = f'{path}?{raw_query_string}'
            
            # Note: perhaps move `write_http_request` to `HTTPStreamWriter`. 
            connection.protocol.write_http_request(self.method, path, self.headers)
            self.write_body_task = Task(self.loop, self.write_body(connection))
            
            self.response = response = ClientResponse(self, connection)
            
            return response
        
        except:
            connection.close()
            raise
