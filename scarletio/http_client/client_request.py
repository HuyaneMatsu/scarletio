__all__ = ('ClientRequest',)

from http.cookies import Morsel, SimpleCookie

from ..core import CancelledError, Task
from ..utils import IgnoreCaseMultiValueDictionary
from ..web_common.form_data import FormData
from ..web_common.headers import (
    ACCEPT, ACCEPT_ENCODING, AUTHORIZATION, CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TYPE, COOKIE, HOST,
    METHOD_CONNECT, METHOD_POST_ALL, TRANSFER_ENCODING
)
from ..web_common.helpers import BasicAuth
from ..web_common.http_stream_writer import HTTPStreamWriter
from ..web_common.multipart import create_payload

from .client_response import ClientResponse
from .connection_key import ConnectionKey
from .request_info import RequestInfo


DEFAULT_HEADERS = (
    (ACCEPT, '*/*'),
    (ACCEPT_ENCODING, 'gzip, deflate'),
)

class ClientRequest:
    """
    Http request class used by ``HTTPClient``.
    
    Attributes
    ----------
    auth : `None`, ``BasicAuth``
        Authorization sent with the request.
    body : `None`, ``PayloadBase``
        The request's body.
    chunked : `bool`
        Whether the request is sent chunked.
    compression : `None`, `str`
        Compression used when sending the request.
    headers : `IgnoreCaseMultiValueDictionary`
        The headers of the request.
    loop : ``EventThread``
        The event loop, trough what the request is executed.
    method : `str`
        The request's method.
    original_url : ``URL``
        The original url, what was asked to request.
    proxy_auth : `None`, ``BasicAuth``
        Proxy authorization sent with the request.
    proxy_url : `None`, ``URL``
        Proxy url to use if applicable.
    response : `None`, ``ClientResponse``
        Object representing the received response. Set as `None` till ``.send`` finishes.
    ssl : `None` `None`, ``SSLContext``, `bool`, ``Fingerprint``
        The connection's ssl type.
    url : ``URL``
        The url, what will be requested.
    writer : `None`, ``Task`` of ``.write_bytes``
        Payload writer task, what is present meanwhile the request's payload is sending.
    """
    __slots__ = (
        'auth', 'body', 'chunked', 'compression', 'headers', 'loop', 'method', 'original_url', 'proxy_auth',
        'proxy_url', 'response', 'ssl', 'url', 'writer'
    )
    
    def __new__(cls, loop, method, url, headers, data, params, cookies, auth, proxy_url, proxy_auth, ssl):
        """
        Creates a new ``ClientRequest`` with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop, trough what the request is executed.
        method : `str`
            The request's method.
        url : ``URL``
            The url to request.
        headers : `None`, `dict`, ``IgnoreCaseMultiValueDictionary``
            Headers of the request.
        data : `None`, `bytes-like`, `io-like`, ``FormData`
            Data to send as the request's body.
        params : `dict` of (`str`, (`str`, `int`, `float`, `bool`)) items
            Query string parameters.
        cookies : `None`, ``CookieJar``
            Cookies OwO.
        auth : `None`, ``BasicAuth``
            Authorization sent with the request.
        proxy_url : `None`, ``URL``
            Proxy url to use if applicable.
        proxy_auth : `None`, ``BasicAuth``
            Proxy authorization sent with the request.
        ssl : `None` `None`, ``SSLContext``, `bool`, ``Fingerprint``
            The connection's ssl type.
        
        Raises
        ------
        TypeError
            - `proxy_auth`'s type is incorrect.
            - ˙Cannot serialize a field of the given `data`.
        ValueError
            - Host could not be detected from `url`.
            - The `proxy_url`'s scheme is not `http`.
            - `compression` and `Content-Encoding` would be set at the same time.
            - `chunked` cannot be set, because `Transfer-Encoding: chunked` is already set.
            - `chunked` cannot be set, because `Content-Length` header is already present.
        RuntimeError
            - If one of `data`'s field's content has unknown content-encoding.
            - If one of `data`'s field's content has unknown content-transfer-encoding.
        """
        # Convert headers
        headers = IgnoreCaseMultiValueDictionary(headers)
        
        # Add extra query parameters to the url and remove fragments
        url = url.extend_query(params)
        request_url = url.with_fragment(None)
        
        if not url.host:
            raise ValueError('Host could not be detected.')
        
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
            headers[AUTHORIZATION] = auth.encode()
        
        for key, value in DEFAULT_HEADERS:
            headers.setdefault(key, value)
        
        # Add host to headers if not present.
        if HOST not in headers:
            netloc = request_url.raw_host
            if not request_url.is_default_port():
                netloc = f'{netloc}:{request_url.port}'
            
            headers[HOST] = netloc
        
        # Update cookies
        if (cookies is not None) and cookies:
            cookie = SimpleCookie()
            if COOKIE in headers:
                cookie.load(headers.get(COOKIE, ''))
                del headers[COOKIE]
            
            for key, value in cookies.items():
                if isinstance(key, Morsel):
                    # Preserve coded_value
                    try:
                        morsel_value = value.get(value.key, None)
                    except KeyError:
                        morsel_value = Morsel()
                    
                    morsel_value.set(value.key, value.value, value.coded_value)
                    value = morsel_value
                
                cookie[key] = value
            
            headers[COOKIE] = cookie.output(header = '', sep = ';').strip()
        
        # Check proxy settings.
        if proxy_url is not None:
            if proxy_url.scheme != 'http':
                raise ValueError(
                    f'Only http proxies are supported, got {proxy_url!r}.'
                )
            
            if (proxy_auth is not None) and not isinstance(proxy_auth, BasicAuth):
                raise TypeError(
                    f'`proxy_auth` can be `None`, `{BasicAuth.__name__}`, got '
                    f'{proxy_auth.__class__.__name__}; {proxy_auth!r}.'
                )
        
        # Needed for transfer data checks
        chunked = False
        compression = headers.get(CONTENT_ENCODING, None)
        
        # Get request content encoding.
        if (data is not None):
            if not data:
                data = None
            else:
                if (compression is not None):
                    if headers.get(CONTENT_ENCODING, ''):
                        raise ValueError(
                            f'Compression can not be set if `Content-Encoding` header is set.'
                        )
                    
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
                transfer_encoding = headers.get(TRANSFER_ENCODING, '').lower()
                
                if 'chunked' in transfer_encoding:
                    if chunked:
                        raise ValueError(
                            f'Chunked can not be set if `Transfer-Encoding: chunked` header is already set.'
                        )
                
                elif chunked:
                    if CONTENT_LENGTH in headers:
                        raise ValueError(
                            'Chunked can not be set if `Content-Length` header is set.'
                        )
                    headers[TRANSFER_ENCODING] = 'chunked'
                
                else:
                    if CONTENT_LENGTH not in headers:
                        headers[CONTENT_LENGTH] = '0' if data is None else str(len(data))
                
                # Set default content-type.
                if (method in METHOD_POST_ALL) and (CONTENT_TYPE not in headers):
                    headers[CONTENT_TYPE] = 'application/octet-stream'
                
        # Everything seems correct, create the object.
        self = object.__new__(cls)
        self.original_url = url
        self.url = request_url
        self.method = method
        self.loop = loop
        self.ssl = ssl
        self.chunked = chunked
        self.compression = compression
        self.body = data
        self.auth = auth
        self.writer = None
        self.response = None
        self.headers = headers
        self.proxy_url = proxy_url
        self.proxy_auth = proxy_auth
        
        return self
    
    def is_ssl(self):
        """
        Returns whether the request is ssl.
        
        Returns
        -------
        is_ssl : `bool`
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
        return ConnectionKey(self)
    
    @property
    def request_info(self):
        """
        Returns base information representing the request.
        
        Returns
        -------
        request_info : ``RequestInfo``
        """
        return RequestInfo(self)
    
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
        port : `int`
        """
        return self.url.port
    
    async def write_bytes(self, writer, connection):
        """
        Writes the request's body..
        
        This method is a coroutine.
        
        Parameters
        ----------
        writer : ``HTTPStreamWriter``
            Writer used to write the request's body into the connection's transport.
        connection : ``Connection``
            Connection of the request with what the payload is sent.
        """
        # Support coroutines that yields bytes objects.
        try:
            body = self.body
            if (body is not None):
                await self.body.write(writer)
            await writer.write_eof()
        except OSError as err:
            new_err = OSError(err.errno, f'Can not write request body for {self.url!r}.')
            new_err.__context__ = err
            new_err.__cause__ = err
            connection.protocol.set_exception(new_err)
        
        except CancelledError as err:
            if not connection.closed:
               connection.protocol.set_exception(err)
        
        except BaseException as err:
            connection.protocol.set_exception(err)
            raise
        
        finally:
            self.writer = None
    
    
    def send(self, connection):
        """
        Sends the request.
        
        Parameters
        ----------
        connection : ``Connection``
            Connection, what is used to send the request.
        
        Returns
        -------
        response : `CoroutineType` of ``ClientResponse.start`` ->
        """
        try:
            url = self.url
            if self.method == METHOD_CONNECT:
                path = f'{url.raw_host}:{url.port}'
            elif (self.proxy_url is not None) and (not self.is_ssl()):
                path = str(url)
            else:
                path = url.raw_path
                if url.raw_query_string:
                    path = f'{path}?{url.raw_query_string}'
            
            protocol = connection.protocol
            writer = HTTPStreamWriter(protocol, self.compression, self.chunked)
            
            protocol.write_http_request(self.method, path, self.headers)
            
            self.writer = Task(self.loop, self.write_bytes(writer, connection))
            
            self.response = response = ClientResponse(self, connection)
            
            return response.start()
        
        except:
            connection.close()
            raise
    
    
    def terminate(self):
        """
        Terminates the request's writing task if applicable.
        """
        writer = self.writer
        if (writer is not None):
            self.writer = None
            writer.cancel()
