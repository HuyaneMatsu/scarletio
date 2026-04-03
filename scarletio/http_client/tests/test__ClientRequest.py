from socket import socketpair as create_socket_pair
from ssl import SSLContext, create_default_context as create_default_ssl_context

import vampytest

from ...core import  SocketTransportLayer, Task, get_event_loop
from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import BasicAuthorization, HttpReadWriteProtocol, URL
from ...web_common.headers import (
    AUTHORIZATION, CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TYPE, COOKIE, HOST, METHOD_CONNECT, METHOD_GET,
    PROXY_AUTHORIZATION, TRANSFER_ENCODING
)
from ...web_common.multipart import BytesPayload
from ...web_common.multipart import PayloadBase

from ..client_request import ClientRequest
from ..client_response import ClientResponse
from ..connection import Connection
from ..connection_key import ConnectionKey
from ..connector_base import ConnectorBase
from ..constants import DEFAULT_HEADERS
from ..request_info import RequestInfo
from ..proxy import Proxy
from ..ssl_fingerprint import SSLFingerprint


def _assert_fields_set(client_request):
    """
    Asserts whether every fields are set of the given client request.
    
    Parameters
    ----------
    client_request : ``ClientRequest``
        The client request to test.
    """
    vampytest.assert_instance(client_request, ClientRequest)
    vampytest.assert_instance(client_request.authorization, BasicAuthorization, nullable = True)
    vampytest.assert_instance(client_request.body, PayloadBase, nullable = True)
    vampytest.assert_instance(client_request.chunked, bool)
    vampytest.assert_instance(client_request.compression, str, nullable = True)
    vampytest.assert_instance(client_request.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(client_request.method, str)
    vampytest.assert_instance(client_request.original_url, URL)
    vampytest.assert_instance(client_request.proxied_url, URL, nullable = True)
    vampytest.assert_instance(client_request.proxy, Proxy, nullable = True)
    vampytest.assert_instance(client_request.ssl_context, SSLContext, nullable = True)
    vampytest.assert_instance(client_request.ssl_fingerprint, SSLFingerprint, nullable = True)
    vampytest.assert_instance(client_request.url, URL)
    vampytest.assert_instance(client_request.write_body_task, Task, nullable = True)


async def test__ClientRequest__new():
    """
    Tests whether ``ClientRequest.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    method = METHOD_GET
    url = URL('https://orindance.party/#mister')
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    data = b'aya'
    query = {'query': 'me'}
    cookies = {'nue': 'murasa'}
    authorization = BasicAuthorization('okuu', 'crown')
    proxied_url = URL('https://orindance.party')
    proxy = Proxy(URL('https://orindance.party/miau'))
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    client_request = ClientRequest(
        loop,
        method,
        url,
        headers,
        data,
        query,
        cookies,
        authorization,
        proxied_url,
        proxy,
        ssl_context,
        ssl_fingerprint,
    )
    
    _assert_fields_set(client_request)
    
    vampytest.assert_eq(client_request.method, method)
    vampytest.assert_eq(client_request.ssl_context, ssl_context)
    vampytest.assert_eq(client_request.ssl_fingerprint, ssl_fingerprint)


async def test__ClientRequest__repr():
    """
    Tests whether ``ClientRequest.__repr__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    method = METHOD_GET
    url = URL('https://orindance.party/#mister')
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    data = b'aya'
    query = {'query': 'me'}
    cookies = {'nue': 'murasa'}
    authorization = BasicAuthorization('okuu', 'crown')
    proxied_url = URL('https://orindance.party')
    proxy = Proxy(URL('https://orindance.party/miau'))
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    client_request = ClientRequest(
        loop,
        method,
        url,
        headers,
        data,
        query,
        cookies,
        authorization,
        proxied_url,
        proxy,
        ssl_context,
        ssl_fingerprint,
    )
    
    output = repr(client_request)
    vampytest.assert_instance(output, str)


def _iter_options__new():
    url = URL('https://orindance.party/')
    
    keyword_parameters = {
        'method': METHOD_GET,
        'url': url,
        'headers': IgnoreCaseMultiValueDictionary(),
        'data': None,
        'query': None,
        'cookies': None,
        'authorization': None,
        'proxied_url': None,
        'proxy': None,
        'ssl_context': None,
        'ssl_fingerprint': None,
    }
    
    
    # Test url | without query string parameters
    yield (
        keyword_parameters,
        ('original_url', 'url'),
        (url, url),
    )
    
    # Test url | with query string parameters
    yield (
        {
            **keyword_parameters,
            'query': {'hey': 'mister'},
        },
        ('original_url', 'url'),
        (
            url.extend_query({'hey': 'mister'}),
            url.extend_query({'hey': 'mister'}),
        ),
    )
    
    # Test url with query string parameters | with query string parameters 
    yield (
        {
            **keyword_parameters,
            'url': url.extend_query({'hoy': 'murasa'}),
            'query': {'hey': 'mister'},
        },
        ('original_url', 'url'),
        (
            url.extend_query({'hoy': 'murasa', 'hey': 'mister'}),
            url.extend_query({'hoy': 'murasa', 'hey': 'mister'}),
        ),
    )
    
    # Test url with fragment
    yield (
        {
            **keyword_parameters,
            'url': url.with_fragment('remilia'),
        },
        ('original_url', 'url'),
        (
            url.with_fragment('remilia'),
            url,
        ),
    )
    
    # Test default headers
    yield (
        keyword_parameters,
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
            ]),
        ),
    )
    
    # Test default headers | connect request
    yield (
        {
            **keyword_parameters,
            'method': METHOD_CONNECT,
            'proxied_url': URL('https://orindance.party/'),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary(),
        ),
    )
    
    # Test default headers | host non default port
    yield (
        {
            **keyword_parameters,
            'url': url.with_port(99),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party:99'),
            ]),
        ),
    )
    
    # Test default headers | host ipv6
    yield (
        {
            **keyword_parameters,
            'url': URL('https://[::2]/'),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, '[::2]'),
            ]),
        ),
    )
    
    # Test default headers | host ipv6 | non default port
    yield (
        {
            **keyword_parameters,
            'url': URL('https://[::2]:99/'),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, '[::2]:99'),
            ]),
        ),
    )
    
    # Test default headers | trailing dot 1
    yield (
        {
            **keyword_parameters,
            'url': URL('https://orindance.party./'),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
            ]),
        ),
    )
    
    # Test default headers | trailing dot 2
    yield (
        {
            **keyword_parameters,
            'url': URL('https://orindance.party../'),
        },
        ('headers', ),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
            ]),
        ),
    )
    
    # Test authorization in url
    yield (
        {
            **keyword_parameters,
            'url': url.with_user('hey').with_password('mister'),
        },
        ('authorization', 'headers', 'url'),
        (
            BasicAuthorization('hey', 'mister'),
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (AUTHORIZATION, BasicAuthorization('hey', 'mister').to_header())
            ]),
            url.with_user('hey').with_password('mister'),
        ),
    )
    
    # Test authorization as parameter
    yield (
        {
            **keyword_parameters,
            'authorization': BasicAuthorization('hey', 'mister'),
        },
        ('authorization', 'headers', 'url'),
        (
            BasicAuthorization('hey', 'mister'),
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (AUTHORIZATION, BasicAuthorization('hey', 'mister').to_header())
            ]),
            url,
        ),
    )
    
    # Test authorization as parameter | connect request.
    yield (
        {
            **keyword_parameters,
            'method': METHOD_CONNECT,
            'authorization': BasicAuthorization('hey', 'mister'),
            'proxied_url': URL('https://orindance.party/'),
        },
        ('authorization', 'headers', 'url'),
        (
            BasicAuthorization('hey', 'mister'),
            IgnoreCaseMultiValueDictionary([
                (PROXY_AUTHORIZATION, BasicAuthorization('hey', 'mister').to_header())
            ]),
            url,
        ),
    )
    
    # Cookies parameter
    yield (
        {
            **keyword_parameters,
            'cookies': {'hey': 'sister'},
        },
        ('headers',),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (COOKIE, 'hey=sister'),
            ]),
        ),
    )
    
    # Cookies parameter # cookies in headers
    yield (
        {
            **keyword_parameters,
            'cookies': {'hey': 'sister'},
            'headers': IgnoreCaseMultiValueDictionary([
                (COOKIE, 'hoy=murasa')
            ])
        },
        ('headers',),
        (
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (COOKIE, 'hey=sister; hoy=murasa'),
            ]),
        ),
    )
    
    # Empty data.
    yield (
        keyword_parameters,
        ('body', 'chunked', 'compression', 'headers'),
        (
            None,
            False,
            None,
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
            ]),
        ),
    )
    
    # No data | with headers
    yield (
        {
            **keyword_parameters,
            'headers': IgnoreCaseMultiValueDictionary([
                (CONTENT_ENCODING, 'gzip'),
                (CONTENT_LENGTH, '0'),
                (CONTENT_TYPE, 'application/json'),
                (TRANSFER_ENCODING, 'chunked'),
            ])
        },
        ('body', 'chunked', 'compression', 'headers'),
        (
            None,
            False,
            None,
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
            ]),
        ),
    )
    
    # With data -> add content length
    yield (
        {
            **keyword_parameters,
            'data': b'koishi',
        },
        ('body', 'chunked', 'compression', 'headers'),
        (
            BytesPayload(b'koishi', {}),
            False,
            None,
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (CONTENT_LENGTH, '6'),
                (CONTENT_TYPE, 'application/octet-stream'),
            ]),
        ),
    )
    
    # With data | with compression -> add chunked
    yield (
        {
            **keyword_parameters,
            'headers': IgnoreCaseMultiValueDictionary([
                (CONTENT_ENCODING, 'gzip'),
            ]),
            'data': b'koishi',
        },
        ('body', 'chunked', 'compression', 'headers'),
        (
            BytesPayload(b'koishi', {}),
            True,
            'gzip',
            IgnoreCaseMultiValueDictionary([
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (CONTENT_ENCODING, 'gzip'),
                (CONTENT_TYPE, 'application/octet-stream'),
                (TRANSFER_ENCODING, 'chunked'),
            ]),
        ),
    )


@vampytest._(vampytest.call_from(_iter_options__new()).returning_last())
async def test__ClientRequest__new__processing(keyword_parameters, return_attribute_names):
    """
    Tests whether ``ClientRequest.__new__`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameter to create the request with.
    return_attribute_names : `tuple<str>`
        Attribute names to return their value of.
    
    Returns
    -------
    return_attributes : `tuple<object>`
    """
    loop = get_event_loop()
    
    # copy headers
    keyword_parameters['headers'] = keyword_parameters['headers'].copy()
    
    # Construct
    client_request = ClientRequest(
        loop,
        **keyword_parameters,
    )
    _assert_fields_set(client_request)
    
    # Return
    return (*(getattr(client_request, attribute_name) for attribute_name in return_attribute_names),)


def _iter_options__is_secure():
    yield (
        URL('http://orindance.party/'),
        None,
        False,
    )
    
    yield (
        URL('ws://orindance.party/'),
        None,
        False,
    )
    
    yield (
        URL('https://orindance.party/'),
        None,
        True,
    )
    
    yield (
        URL('wss://orindance.party/'),
        None,
        True,
    )
    
    yield (
        URL('orindance.party/'),
        create_default_ssl_context(),
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__is_secure()).returning_last())
async def test__ClientRequest__is_secure(url, ssl_context):
    """
    Tests whether ``ClientRequest.is_secure`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    url : ``URL``
        Url to create client request with.
    
    ssl_context : `None | SSLContext`
        Ssl context to create the request with.
    
    Returns
    -------
    output : `bool`
    """
    loop = get_event_loop()
    
    # Construct
    client_request = ClientRequest(
        loop,
        METHOD_GET,
        url,
        IgnoreCaseMultiValueDictionary(),
        None,
        None,
        None,
        None,
        None,
        None,
        ssl_context,
        None,
    )
    
    output = client_request.is_secure()
    vampytest.assert_instance(output, bool)
    return output


async def test__ClientRequest__connection_key():
    """
    Tests whether ``ClientRequest.connection_key`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    method = METHOD_GET
    url = URL('https://orindance.party/#mister')
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    data = b'aya'
    query = {'query': 'me'}
    cookies = {'nue': 'murasa'}
    authorization = BasicAuthorization('okuu', 'crown')
    proxied_url = URL('https://orindance.party/')
    proxy = Proxy(URL('https://orindance.party/miau'))
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    client_request = ClientRequest(
        loop,
        method,
        url,
        headers,
        data,
        query,
        cookies,
        authorization,
        proxied_url,
        proxy,
        ssl_context,
        ssl_fingerprint,
    )
    
    connection_key = client_request.connection_key
    
    vampytest.assert_instance(connection_key, ConnectionKey)
    vampytest.assert_eq(
        connection_key,
        ConnectionKey(
            'orindance.party',
            443,
            proxy,
            True,
            ssl_context,
            ssl_fingerprint,
        ),
    )


async def test__ClientRequest__request_info():
    """
    Tests whether ``ClientRequest.request_info`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    method = METHOD_GET
    url = URL('https://orindance.party/#mister')
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    data = b'aya'
    query = {'query': 'me'}
    cookies = {'nue': 'murasa'}
    authorization = BasicAuthorization('okuu', 'crown')
    proxied_url = URL('https://orindance.party/')
    proxy = Proxy(URL('https://orindance.party/miau'))
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    client_request = ClientRequest(
        loop,
        method,
        url,
        headers,
        data,
        query,
        cookies,
        authorization,
        proxied_url,
        proxy,
        ssl_context,
        ssl_fingerprint,
    )
    
    request_info = client_request.request_info
    
    vampytest.assert_instance(request_info, RequestInfo)
    vampytest.assert_eq(
        request_info,
        RequestInfo(
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
                (AUTHORIZATION, BasicAuthorization('okuu', 'crown').to_header()),
                *DEFAULT_HEADERS,
                (HOST, 'orindance.party'),
                (COOKIE, 'nue=murasa'),
                (CONTENT_LENGTH, '3'),
                (CONTENT_TYPE, 'application/octet-stream'),
            ]),
            method,
            url.extend_query(query),
            url.extend_query(query).with_fragment(None),
        ),
    )


def _iter_options__host():
    yield(
        URL('https://orindance.party/'),
        'orindance.party',
    )
    
    yield(
        URL('http://1.1.1.1/'),
        '1.1.1.1',
    )
    
    yield(
        URL('https://orindance.party:99/'),
        'orindance.party',
    )
    
    yield(
        URL('https://1.1.1.1:99/'),
        '1.1.1.1',
    )


@vampytest._(vampytest.call_from(_iter_options__host()).returning_last())
async def test__ClientRequest__host(url):
    """
    Tests whether ``ClientRequest.host`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    url : ``URL``
        Url to create client request with.
    
    Returns
    -------
    output : `str`
    """
    loop = get_event_loop()
    
    # Construct
    client_request = ClientRequest(
        loop,
        METHOD_GET,
        url,
        IgnoreCaseMultiValueDictionary(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    
    output = client_request.host
    vampytest.assert_instance(output, str)
    return output


def _iter_options__port():
    yield(
        URL('https://orindance.party/'),
        443,
    )
    
    yield(
        URL('http://1.1.1.1/'),
        80,
    )
    
    yield(
        URL('https://orindance.party:99/'),
        99,
    )
    
    yield(
        URL('https://1.1.1.1:99/'),
        99,
    )


@vampytest._(vampytest.call_from(_iter_options__port()).returning_last())
async def test__ClientRequest__port(url):
    """
    Tests whether ``ClientRequest.port`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    url : ``URL``
        Url to create client request with.
    
    Returns
    -------
    output : `int`
    """
    loop = get_event_loop()
    
    # Construct
    client_request = ClientRequest(
        loop,
        METHOD_GET,
        url,
        IgnoreCaseMultiValueDictionary(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    
    output = client_request.port
    vampytest.assert_instance(output, int)
    return output


async def test__ClientResponse__begin():
    """
    Tests whether ``ClientRequest.begin`` works as intended.
    Also tests `.write_body` for now as well.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    try:
        read_socket.setblocking(False)
        write_socket.setblocking(False)
        
        loop = get_event_loop()
        url = URL('https://orindance.party/#mister')
        data = b'aya'
        
        # Construct
        client_request = ClientRequest(
            loop,
            METHOD_GET,
            url,
            IgnoreCaseMultiValueDictionary(),
            data,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        
        connector = ConnectorBase(loop)
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayer(loop, {}, write_socket, protocol, None, None)
        protocol.connection_made(transport)
        performed_requests = 2
        
        connection = Connection(connector, client_request.connection_key, protocol, performed_requests)
        
        client_response = client_request.begin(connection)
        vampytest.assert_instance(client_response, ClientResponse)
        
        vampytest.assert_is(client_request.response, client_response)
        
        write_body_task = client_request.write_body_task
        vampytest.assert_is_not(write_body_task, None)
        vampytest.assert_instance(write_body_task, Task)
        
        write_body_task.apply_timeout(1.0)
        await write_body_task
        
        output = read_socket.recv(4096)
        vampytest.assert_eq(
            output,
            (
                b'GET / HTTP/1.1\r\n'
                b'Accept: */*\r\n'
                b'Accept-Encoding: gzip, deflate\r\n'
                b'Host: orindance.party\r\n'
                b'Content-Length: 3\r\n'
                b'Content-Type: application/octet-stream\r\n'
                b'\r\n'
                b'aya'
            )
        )
        
    finally:
        read_socket.close()
        write_socket.close()


def _iter_options__build_path_to_request():
    url = URL('https://orindance.party/')
    
    keyword_parameters = {
        'method': METHOD_GET,
        'url': url,
        'headers': IgnoreCaseMultiValueDictionary(),
        'data': None,
        'query': None,
        'cookies': None,
        'authorization': None,
        'proxied_url': None,
        'proxy': None,
        'ssl_context': None,
        'ssl_fingerprint': None,
    }
    
    
    yield (
        keyword_parameters,
        '/',
    )
    
    yield (
        {
            **keyword_parameters,
            'url': URL('https://orindance.party/hey/mister'),
        },
        '/hey/mister',
    )
    
    yield (
        {
            **keyword_parameters,
            'url': URL('https://orindance.party:8000/'),
        },
        '/',
    )
    
    yield (
        {
            **keyword_parameters,
            'url': URL('https://orindance.party?nyan=er'),
        },
        '/?nyan=er',
    )
    
    yield (
        {
            **keyword_parameters,
            'method': METHOD_CONNECT,
            'url': URL('https://www.astil.dev/'),
            'proxied_url': URL('https://orindance.party?nyan=er'),
        },
        'orindance.party:443',
    )
    
    yield (
        {
            **keyword_parameters,
            'method': METHOD_CONNECT,
            'url': URL('https://www.astil.dev/'),
            'proxied_url': URL('https://orindance.party:8000?nyan=er'),
        },
        'orindance.party:8000',
    )


@vampytest._(vampytest.call_from(_iter_options__build_path_to_request()).returning_last())
async def test__ClientRequest__build_path_to_request__processing(keyword_parameters):
    """
    Tests whether ``ClientRequest._build_path_to_request`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameter to create the request with.
    
    Returns
    -------
    output : `str`
    """
    loop = get_event_loop()
    
    # copy headers
    keyword_parameters['headers'] = keyword_parameters['headers'].copy()
    
    # Construct
    client_request = ClientRequest(
        loop,
        **keyword_parameters,
    )
    _assert_fields_set(client_request)
    
    # Return
    output = client_request._build_path_to_request()
    vampytest.assert_instance(output, str)
    return output

