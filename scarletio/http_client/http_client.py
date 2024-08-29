__all__ = ('HTTPClient', )

from ssl import SSLContext, create_default_context as create_default_ssl_context
from warnings import warn

from ..utils import IgnoreCaseMultiValueDictionary, RichAttributeErrorBaseType, export
from ..web_common import BasicAuth, CookieJar, URL
from ..web_common.headers import (
    AUTHORIZATION, CONTENT_LENGTH, LOCATION, METHOD_DELETE, METHOD_GET, METHOD_HEAD, METHOD_OPTIONS, METHOD_PATCH,
    METHOD_POST, METHOD_PUT, URI
)
from ..web_common.helpers import Timeout, set_tcp_nodelay
from ..web_socket import WebSocketClient

from .client_request import ClientRequest
from .connector_tcp import ConnectorTCP
from .constants import REQUEST_TIMEOUT_DEFAULT
from .request_context_manager import RequestContextManager
from .ssl_fingerprint import SSLFingerprint
from .web_socket_context_manager import WebSocketContextManager


@export
class HTTPClient(RichAttributeErrorBaseType):
    """
    HTTP client implementation.
    
    Attributes
    ----------
    connector : ``ConnectorBase``
        Connector of the http client. Defaults to ``ConnectorTCP``.
    
    cookie_jar : ``CookieJar``
        Cookies stored by the http client.
    
    loop : ``EventThread``
        The event loop used by the http client.
    
    proxy_url : `None | URL`
        Proxy url to use with all of the requests of the http client.
    
    proxy_auth : `None | BasicAuth`
        Proxy authorization to send with all the requests of the http client.
    """
    __slots__ = ('connector', 'cookie_jar', 'loop', 'proxy_headers', 'proxy_auth', 'proxy_url')
    
    def __new__(cls, loop, *deprecated, connector = None, proxy_auth = None, proxy_headers = None, proxy_url = None):
        """
        Creates a new ``HTTPClient`` with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop used by the http client.
        
        connector : `None | ConnectorBase` = `None`, Optional (Keyword only)
            Connector to be used by the client.
            If not given or given as `None`, a new ``ConnectorTCP`` is created and used.
        
        proxy_auth : `None | BasicAuth` = `None`, Optional (Keyword only)
            Proxy authorization to send with all the requests of the http client.
        
        proxy_headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional (Keyword only)
            Proxy headers to use with all of the requests of the http client.
            
        proxy_url : `None | str | URL` = `None`, Optional (Keyword only)
            Proxy url to use with all of the requests of the http client.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `proxy_url` and `proxy_headers` parameters in `{cls.__name__}.__new__` are moved to be '
                    f'keyword only. Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            proxy_url = deprecated[0]
            
            if deprecated_length > 1:
                proxy_auth = deprecated[1]
        
        
        # connector
        if (connector is None):
            connector = ConnectorTCP(loop)
        
        # proxy_auth
        if (proxy_auth is not None) and (not isinstance(proxy_auth, BasicAuth)):
            raise TypeError(
                f'`proxy_auth` can be `None`, `{BasicAuth.__name__}`, got '
                f'{type(proxy_auth).__name__}; {proxy_auth!r}.'
            )
        
        # proxy_headers
        if (proxy_headers is not None):
            proxy_headers = IgnoreCaseMultiValueDictionary(proxy_headers)
        
        # proxy_url
        if (proxy_url is not None):
            proxy_url = URL(proxy_url)
        
        # Construct
        self = object.__new__(cls)
        self.connector = connector
        self.cookie_jar = CookieJar()
        self.loop = loop
        self.proxy_auth = proxy_auth
        self.proxy_headers = proxy_headers
        self.proxy_url = proxy_url
        return self
    
    
    async def _request(self, method, url, headers, *, data = None, params = None, redirects = 3):
        """
        Internal method for executing an http request.
        
        This method is a coroutine.
        
        Parameters
        ----------
        method : `str`
            The method of the request.
        
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary`
            Request headers.
        
        data : `None | object` = `None`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>` = `None`, \
                Optional (Keyword only)
            Query string parameters
        
        redirects : `int` = `3`, Optional (Keyword only)
            The maximal amount of allowed redirects.
        
        Returns
        -------
        response : ``ClientResponse``
        
        Raises
        ------
        ConnectionError
            - Too many redirects.
            - Connector closed.
        ValueError
            - Host could not be detected from `url`.
            - `compression` and `Content-Encoding` would be set at the same time.
            - `chunked` cannot be set, because `Transfer-Encoding: chunked` is already set.
            - `chunked` cannot be set, because `Content-Length` header is already present.
        OSError
            If a system function returns a system-related error.
        RuntimeError
            - If one of `data`'s field's content has unknown content-encoding.
            - If one of `data`'s field's content has unknown content-transfer-encoding.
        TimeoutError
            Did not receive answer in time.
        TypeError
            - `proxy_auth`'s type is incorrect.
            - ˙Cannot serialize a field of the given `data`.
        
        See Also
        --------
        - ``.request`` : Executes an http request returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``._request2`` : Internal method for executing an http request with extra parameters.
        """
        headers = IgnoreCaseMultiValueDictionary(headers)
        
        history = []
        url = URL(url)
        
        with Timeout(self.loop, REQUEST_TIMEOUT_DEFAULT):
            while True:
                cookies = self.cookie_jar.filter_cookies(url)
                
                proxy_url = self.proxy_url
                if proxy_url is None:
                    proxy_auth = None
                    proxy_headers = None
                
                else:
                    proxy_auth = self.proxy_auth
                    proxy_headers = self.proxy_headers
                    if (proxy_headers is not None):
                        proxy_headers = proxy_headers.copy()
                
                request = ClientRequest(
                    self.loop,
                    method,
                    url,
                    headers,
                    data,
                    params,
                    cookies,
                    None,
                    proxy_url,
                    proxy_headers,
                    proxy_auth,
                    None,
                    None,
                )
                
                connection = await self.connector.connect(request)
                
                set_tcp_nodelay(connection.transport, True)
                
                response = request.begin(connection)
                await response.start_processing()
                
                # we do nothing with os error
                
                self.cookie_jar.update_cookies(response.cookies, response.url)
                
                # redirects
                if response.status in (301, 302, 303, 307) and redirects:
                    redirects -= 1
                    history.append(response)
                    if not redirects:
                        response.close()
                        raise ConnectionError('Too many redirects', history[0].request_info, tuple(history))
                    
                    if (
                        (response.status == 303 and response.method != METHOD_HEAD)
                        or (response.status in (301, 302) and response.method == METHOD_POST)
                    ):
                        method = METHOD_GET
                        data = None
                        try:
                            del headers[CONTENT_LENGTH]
                        except KeyError:
                            pass
                    
                    redirect_url = response.headers.get(LOCATION, None)
                    if redirect_url is None:
                        redirect_url = response.headers.get(URI, None)
                        if redirect_url is None:
                            break
                    
                    response.release()
                    
                    redirect_url = URL(redirect_url)
                    
                    scheme = redirect_url.scheme
                    if scheme not in ('http', 'https', ''):
                        response.close()
                        raise ConnectionError(
                            f'Can redirect only to http or https, got {scheme!r}',
                            history[0].request_info,
                            tuple(history),
                        )
                    
                    elif not scheme:
                        redirect_url = url.join(redirect_url)
                    
                    if url.origin() != redirect_url.origin():
                        try:
                            del headers[AUTHORIZATION]
                        except KeyError:
                            pass
                    
                    url = redirect_url
                    params = None
                    response.release()
                    continue
                
                break
        
        response.history = tuple(history)
        return response
    
    
    async def _request2(
        self,
        method,
        url,
        headers,
        *,
        auth = None,
        data = None,
        params = None,
        proxy_url = ...,
        proxy_auth = ...,
        proxy_headers = ...,
        redirects = 3,
        timeout = REQUEST_TIMEOUT_DEFAULT,
        ssl = ...,
        ssl_context = None,
        ssl_fingerprint = None,
    ):
        """
        Internal method for executing an http request with extra parameters
        
        This method is a coroutine.
        
        Parameters
        ----------
        method : `str`
            The method of the request.
        
        url : `str`, ``URL``
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary`
            Request headers.
        
        auth : `None`, ``BasicAuth`` = `None`, Optional (Keyword only)
            Authorization to use.
        
        data : `None`, `object` = `None`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>` = `None`, \
                Optional (Keyword only)
        
        proxy_url : `None | str | URL`, Optional (Keyword only)
            Proxy url to use instead of the client's own.
        
        proxy_auth : `None | BasicAuth`, Optional (Keyword only)
            Proxy authorization to use instead of the client's.
        
        proxy_headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary`, Optional (Keyword only)
            Proxy headers to use instead of the client's.
        
        redirects : `int` = `3`, Optional (Keyword only)
            The maximal amount of allowed redirects.
        
        timeout : `float` = `REQUEST_TIMEOUT_DEFAULT`, Optional (Keyword only)
            The maximal duration to wait for server response. Defaults to `60.0` seconds.
        
        ssl_context : `None | SSLContext`, Optional (Keyword only)
            SSL context to be used by the connector.
        
        ssl_fingerprint : `None | SSLFingerprint`, Optional (Keyword only)
            SSL finger print to use by the connector.
        
        Returns
        -------
        response : ``ClientResponse``
        
        Raises
        ------
        ConnectionError
            - Too many redirects.
            - Connector closed.
        TypeError
            - `proxy_auth`'s type is incorrect.
            - ˙Cannot serialize a field of the given `data`.
        ValueError
            - Host could not be detected from `url`.
            - `compression` and `Content-Encoding` would be set at the same time.
            - `chunked` cannot be set, because `Transfer-Encoding: chunked` is already set.
            - `chunked` cannot be set, because `Content-Length` header is already present.
            - `headers` contain authorization headers, but `auth` parameter is given as well.
        RuntimeError
            - If one of `data`'s field's content has unknown content-encoding.
            - If one of `data`'s field's content has unknown content-transfer-encoding.
        TimeoutError
            - Did not receive answer in time.
        
        See Also
        --------
        - ``.request`` : Executes an http request returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``._request`` : Internal method for executing an http request without extra parameters.
        """
        # Deprecations
        if (ssl is not ...):
            warn(
                (
                    f'`{type(self).__name__}._request2`\'s `ssl` parameter is deprecated '
                    f'and scheduled for removal in 2025 August. '
                    f'Please use either the `ssl_context` or the `ssl_fingerprint` parameters depending on your needs.'
                ),
                FutureWarning,
                stacklevel = 3,
            )
            
            if ssl is None:
                ssl_context = None
                ssl_fingerprint = None
            
            elif isinstance(ssl, SSLContext):
                ssl_context = ssl
                ssl_fingerprint = None
            
            elif isinstance(ssl, SSLFingerprint):
                ssl_context = None
                ssl_fingerprint = ssl
            
            elif isinstance(ssl, bool):
                ssl_context = create_default_ssl_context()
                ssl_fingerprint = None
                
            else:
                raise TypeError(
                    f'`ssl` can be `None`, `bool`, `{SSLContext.__name__}`, `{SSLFingerprint.__name__}`. '
                    f'Got {type(ssl).__name__}; {ssl!r}.'
                )
        
        # Transform headers to IgnoreCaseMultiValueDictionary
        headers = IgnoreCaseMultiValueDictionary(headers)
        
        if (headers and (auth is not None) and AUTHORIZATION in headers):
            raise ValueError(
                f'Can\'t combine {AUTHORIZATION!r} header with the `auth` parameter. '
                f'Got auth = {auth!r}; headers[{AUTHORIZATION!r}] = {headers[AUTHORIZATION]!r}.'
            )
        
        # proxy_url
        if (proxy_url is ...):
            proxy_url = self.proxy_url
        elif (proxy_url is not None):
            proxy_url = URL(proxy_url)
        
        if (proxy_url is None):
            proxy_auth = None
            proxy_headers = None
        
        else:
            # proxy_auth
            if (proxy_auth is ...):
                proxy_auth = self.proxy_auth
            elif (proxy_auth is not None) and (not isinstance(proxy_auth, BasicAuth)):
                raise TypeError(
                    f'`proxy_auth` can be `None`, `{BasicAuth.__name__}`, got '
                    f'{type(proxy_auth).__name__}; {proxy_auth!r}.'
                )
            
            # proxy_headers
            if (proxy_headers is ...):
                proxy_headers = self.proxy_headers
                if (proxy_headers is not None):
                    proxy_headers = proxy_headers.copy()
            else:
                proxy_headers = IgnoreCaseMultiValueDictionary(headers)
        
        history = []
        url = URL(url)
        
        with Timeout(self.loop, timeout):
            while True:
                cookies = self.cookie_jar.filter_cookies(url)

                if (proxy_url is not None):
                    proxy_url = URL(proxy_url)

                request = ClientRequest(
                    self.loop,
                    method,
                    url,
                    headers,
                    data,
                    params,
                    cookies,
                    auth,
                    proxy_url,
                    proxy_headers,
                    proxy_auth,
                    ssl_context,
                    ssl_fingerprint,
                )
                
                connection = await self.connector.connect(request)
                
                set_tcp_nodelay(connection.transport, True)
                
                response = request.begin(connection)
                await response.start_processing()
                
                # we do nothing with os error
                
                self.cookie_jar.update_cookies(response.cookies, response.url)
                
                # redirects
                if response.status in (301, 302, 303, 307) and redirects:
                    redirects -= 1
                    history.append(response)
                    if not redirects:
                        response.close()
                        raise ConnectionError('Too many redirects', history[0].request_info, tuple(history))
                    
                    # For 301 and 302, mimic IE behaviour, now changed in RFC.
                    if (
                        (response.status == 303 and response.method != METHOD_HEAD)
                        or (response.status in (301, 302) and response.method == METHOD_POST)
                    ):
                        method = METHOD_GET
                        data = None
                        content_length = headers.get(CONTENT_LENGTH, None)
                        if (content_length is not None) and content_length:
                            del headers[CONTENT_LENGTH]
                    
                    redirect_url = response.headers.get(LOCATION, None)
                    if redirect_url is None:
                        redirect_url = response.headers.get(URI, None)
                        if redirect_url is None:
                            break
                    
                    response.release()
                    
                    redirect_url = URL(redirect_url)
                    
                    scheme = redirect_url.scheme
                    if scheme not in ('http', 'https', ''):
                        response.close()
                        raise ConnectionError(
                            f'Can redirect only to http or https, got {scheme!r}',
                            history[0].request_info,
                            tuple(history),
                        )
                    
                    elif not scheme:
                        redirect_url = url.join(redirect_url)
                    
                    url = redirect_url
                    params = None
                    await response.release()
                    continue
                
                break
        
        response.history = tuple(history)
        return response
    
    
    @property
    def closed(self):
        """
        Returns whether the ``HTTPClient`` is closed.
        
        Returns
        -------
        closed : `bool`
        """
        connector = self.connector
        if connector is None:
            return True
        
        if connector.closed:
            return True
        
        return False
    
    
    async def __aenter__(self):
        """
        Enters the http client as an asynchronous context manager.
        
        This method is a coroutine.
        """
        return self
    
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        """
        Exits the http client with closing it.
        
        This method is a coroutine.
        """
        self.close()
    
    
    def __del__(self):
        """
        Closes the http client closed.
        """
        connector = self.connector
        if connector is None:
            return
        
        self.connector = None
        
        if not connector.closed:
            connector.close()
    
    
    close = __del__
    
    
    def request(self, method, url, headers = None, **keyword_parameters):
        """
        Executes an http request.
        
        Parameters
        ----------
        method : `str`
            The method of the request.
        
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.
        
        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(method, url, headers, **keyword_parameters))
    
    
    def request2(self, method, url, headers = None, **keyword_parameters):
        """
        Executes an http request with extra parameters.
        
        Parameters
        ----------
        method : `str`
            The method of the request.
        
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        auth : `None | BasicAuth`, Optional (Keyword only)
            Authorization to use.
        
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.
        
        proxy_auth : `None | BasicAuth`, Optional (Keyword only)
            Proxy authorization to use instead of the client's.
        
        proxy_headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary`, Optional (Keyword only)
            Proxy headers to use instead of the client's.
        
        proxy_url : `None | str | URL`, Optional  (Keyword only)
            Proxy url to use instead of the client's own.
        
        ssl_context : `None | SSLContext`, Optional (Keyword only)
            SSL context to be used by the connector.
        
        ssl_fingerprint : `None | SSLFingerprint`, Optional (Keyword only)
            SSL finger print to use by the connector.
        
        timeout : `float`, Optional (Keyword only)
            The maximal duration to wait for server response.
        
        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request2(method, url, headers, **keyword_parameters))
    
    
    def get(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a get request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_GET, url, headers, **keyword_parameters))
    
    
    def options(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a get request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_OPTIONS, url, headers, **keyword_parameters))
    
    
    def head(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a head request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_HEAD, url, headers, **keyword_parameters))
    
    
    def post(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a post request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_POST, url, headers, **keyword_parameters))
    
    
    def put(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a put request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.patch`` : Shortcut for executing a patch request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_PUT, url, headers, **keyword_parameters))
    
    
    def patch(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a patch request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.delete`` :  Shortcut for executing a delete request.
        """
        return RequestContextManager(self._request(METHOD_PATCH, url, headers, **keyword_parameters))
    
    
    def delete(self, url, headers = None, **keyword_parameters):
        """
        Shortcut for executing a delete request.
        
        Parameters
        ----------
        url : `str | URL`
            The url to request.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        data : `None | object`, Optional (Keyword only)
            Data to send a the body of the request.
        
        params : `None | str | dict<None, str | bool | int | float, iterable<...>> | iterable<...>`, \
                Optional (Keyword only)
            Query string parameters.
        
        redirects : `int`, Optional (Keyword only)
            The maximal amount of allowed redirects.

        Returns
        -------
        request_context_manager : ``RequestContextManager``
        
        See Also
        --------
        - ``.request`` : Executes an http request without extra parameters returning a request context manager.
        - ``.request2`` : Executes an http request with extra parameters returning a request context manager.
        - ``.get`` : Shortcut for executing a get request.
        - ``.options`` : Shortcut for executing an options request.
        - ``.head`` : Shortcut for executing a head request.
        - ``.post`` : Shortcut for executing a post request.
        - ``.put`` : Shortcut for executing a put request.
        - ``.patch`` : Shortcut for executing a patch request.
        """
        return RequestContextManager(self._request(METHOD_DELETE, url, headers, **keyword_parameters))
    
    
    def connect_websocket(self, url, **keyword_parameters):
        """
        Deprecated and will be removed in 2025 august. please use ``.connect_web_socket``.
        """
        warn(
            (
                f'`{type(self).__name__}.connect_websocket` is deprecated and will be removed in 2025 august. '
                f'Please use `.connect_web_socket` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.connect_web_socket(url, **keyword_parameters)
    
    
    def connect_web_socket(self, url, **keyword_parameters):
        """
        Connect a web socket client to the given url.
        
        Parameters
        ----------
        url : `str | URL`
            The url to connect to.
        
        **keyword_parameters : Keyword Parameters
            Additional keyword parameters.
        
        Other Parameters
        ----------------
        origin : `None`, `str`, Optional (Keyword only)
            Value of the Origin header.
        
        available_extensions : `None` or (`list` of `object`), Optional (Keyword only)
            Available web socket extensions.
            
            Each web socket extension should have the following `4` attributes / methods:
            - `name`: `str`. The extension's name.
            - `request_params` : `list` of `tuple` (`str`, `str`). Additional header parameters of the extension.
            - `decode` : `callable`. Decoder method, what processes a received web socket frame. Should accept `2`
                parameters: The respective ``WebSocketFrame``, and the ˙max_size` as `int`, what describes the
                maximal size of a received frame. If it is passed, ``PayloadError`` is raised.
            - `encode` : `callable`. Encoder method, what processes the web socket frames to send. Should accept `1`
                parameter, the respective ``WebSocketFrame``.
        
        available_subprotocols : `None | list<str>`, Optional (Keyword only)
            A list of supported subprotocols in order of decreasing preference.
        
        headers : `None | dict<str, str> | IgnoreCaseMultiValueDictionary` = `None`, Optional
            Request headers.
        
        http_client : `None | HTTPClient`, Optional (Keyword only)
            Http client to use to connect the web socket.
        
        close_timeout : `float`, Optional (Keyword only)
            The maximal duration in seconds what is waited for response after close frame is sent.
            Defaults to `10.0`.
        
        max_size : `int`, Optional (Keyword only)
            Max payload size to receive. If a payload exceeds it, ``PayloadError`` is raised.
            Defaults to `67108864` bytes.
        
        max_queue : `None`, `int`, Optional (Keyword only)
            Max queue size of ``.messages``.
            If a new payload is added to a full queue, the oldest element of it is removed.
        
        Returns
        -------
        web_socket_context_manager : ``WebSocketContextManager``
        """
        return WebSocketContextManager(WebSocketClient(self.loop, url, **keyword_parameters, http_client = self))
