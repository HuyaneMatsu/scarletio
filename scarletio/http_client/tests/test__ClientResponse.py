from http.cookies import SimpleCookie
from socket import socketpair as create_socket_pair

import vampytest

from ...core import EventThread, PayloadStream, SocketTransportLayerBase, Task, get_event_loop
from ...utils import IgnoreCaseMultiValueDictionary, from_json
from ...web_common import HttpReadWriteProtocol, HttpVersion, URL
from ...web_common.headers import CONTENT_LENGTH, CONTENT_TYPE, SET_COOKIE
from ...web_common.http_message import RawResponseMessage

from ..client_response import ClientResponse
from ..connection import Connection
from ..connector_base import ConnectorBase

from .helpers import Any, _get_default_request


def _assert_fields_set(client_response):
    """
    Checks whether every fields of the given client response are set.
    
    Parameters
    ----------
    client_response : ``ClientResponse``
        The client response to check.
    """
    vampytest.assert_instance(client_response, ClientResponse)
    vampytest.assert_instance(client_response._released, bool)
    vampytest.assert_instance(client_response.body, bytes, nullable = True)
    vampytest.assert_instance(client_response.closed, bool)
    vampytest.assert_instance(client_response.connection, Connection, nullable = True)
    vampytest.assert_instance(client_response.payload_stream, PayloadStream, nullable = True)
    vampytest.assert_instance(client_response.cookies, SimpleCookie)
    vampytest.assert_instance(client_response.history, tuple, nullable = True)
    vampytest.assert_instance(client_response.loop, EventThread)
    vampytest.assert_instance(client_response.method, str)
    vampytest.assert_instance(client_response.raw_message, RawResponseMessage, nullable = True)
    vampytest.assert_instance(client_response.url, URL)
    vampytest.assert_instance(client_response.write_body_task, Task, nullable = True)


async def test__ClientResponse__new():
    """
    Tests whether ``ClientResponse.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    async def mock_write_body(self, connector):
        self.write_body_task = None
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_request.write_body_task = Task(loop, mock_write_body(client_request, connector))
        
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        _assert_fields_set(client_response)
        vampytest.assert_is(client_response.connection, connection)
        vampytest.assert_is(client_response.loop, client_request.loop)
        vampytest.assert_eq(client_response.method, client_request.method)
        vampytest.assert_eq(client_response.url, client_request.original_url)
        vampytest.assert_eq(client_response.write_body_task, client_request.write_body_task)
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ClientResponse__repr():
    """
    Tests whether ``ClientResponse.__repr__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        output = repr(client_response)
        vampytest.assert_instance(output, str)
        
    finally:
        read_socket.close()
        write_socket.close()


def _iter_options__headers():
    yield (
        None,
        None,
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            None,
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
        ),
        IgnoreCaseMultiValueDictionary([
            ('hey', 'mister'),
        ]),
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey mister',
            IgnoreCaseMultiValueDictionary(),
        ),
        IgnoreCaseMultiValueDictionary(),
    )


@vampytest._(vampytest.call_from(_iter_options__headers()).returning_last())
async def test__ClientResponse__headers(raw_message):
    """
    Tests whether ``ClientResponse.headers`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    raw_message : ``RawResponseMessage``
        Raw response message to test with.
    
    Returns
    -------
    output : `None | IgnoreCaseMultiValueDictionary<str, str>`
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        client_response.raw_message = raw_message
        
        output = client_response.headers
        vampytest.assert_instance(output, IgnoreCaseMultiValueDictionary, nullable = True)
        return output
        
    finally:
        read_socket.close()
        write_socket.close()


def _iter_options__reason():
    yield (
        None,
        None,
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey mister',
            IgnoreCaseMultiValueDictionary(),
        ),
        'hey mister',
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            None,
            IgnoreCaseMultiValueDictionary(),
        ),
        'OK',
    )


@vampytest._(vampytest.call_from(_iter_options__reason()).returning_last())
async def test__ClientResponse__reason(raw_message):
    """
    Tests whether ``ClientResponse.reason`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    raw_message : ``RawResponseMessage``
        Raw response message to test with.
    
    Returns
    -------
    output : `None | str`
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        client_response.raw_message = raw_message
        
        output = client_response.reason
        vampytest.assert_instance(output, str, nullable = True)
        return output
        
    finally:
        read_socket.close()
        write_socket.close()


def _iter_options__status():
    yield (
        None,
        0,
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey mister',
            IgnoreCaseMultiValueDictionary(),
        ),
        200,
    )
    
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            0,
            None,
            IgnoreCaseMultiValueDictionary(),
        ),
        0,
    )


@vampytest._(vampytest.call_from(_iter_options__status()).returning_last())
async def test__ClientResponse__status(raw_message):
    """
    Tests whether ``ClientResponse.status`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    raw_message : ``RawResponseMessage``
        Raw response message to test with.
    
    Returns
    -------
    output : `int`
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        client_response.raw_message = raw_message
        
        output = client_response.status
        vampytest.assert_instance(output, int)
        return output
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ClientResponse__start_processing():
    """
    Tests whether ``ClientResponse.start_processing`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        
        protocol.data_received(
            b'HTTP/1.1 200 miau\r\n'
            b'Content-Length: 3\r\n'
            b'Set-cookie: okuu=sun\r\n'
            b'\r\n'
            b'aya'
        )
        
        
        task = Task(loop, client_response.start_processing())
        task.apply_timeout(0.1)
        
        await task
        
        vampytest.assert_eq(
            client_response.raw_message,
            RawResponseMessage(
                HttpVersion(1, 1),
                200,
                'miau',
                IgnoreCaseMultiValueDictionary([
                    (CONTENT_LENGTH, '3'),
                    (SET_COOKIE, 'okuu=sun'),
                ])
            ),
        )
        
        task = Task(loop, client_response.payload_stream.__await__())
        task.apply_timeout(0.1)
        output = await task
        
        vampytest.assert_instance(output, bytes)
        vampytest.assert_eq(output, b'aya')
        
        vampytest.assert_true(client_response._released)
        vampytest.assert_true(client_response.closed)
        vampytest.assert_eq(
            {key: value.value for key, value in client_response.cookies.items()},
            {'okuu': 'sun'},
        )
        
        protocol_basket = connector.protocols_by_host.get(client_request.connection_key, None)
        vampytest.assert_is_not(protocol_basket, None)
        vampytest.assert_eq(
            protocol_basket.available,
            [(protocol, Any(float), 3)],
        )
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ClientResponse__read():
    """
    Tests whether ``ClientResponse.read`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        
        data = b'hey mister'
        payload_stream = PayloadStream(protocol)
        payload_stream.add_received_chunk(data)
        payload_stream.set_done_success()
        client_response.payload_stream = payload_stream
        
        
        task = Task(loop, client_response.read())
        task.apply_timeout(0.1)
        
        output = await task
        
        vampytest.assert_instance(output, bytes, nullable = True)
        vampytest.assert_eq(output, data)
        
        vampytest.assert_eq(client_response.body, data)
        vampytest.assert_is(client_response.payload_stream, None)
    
    finally:
        read_socket.close()
        write_socket.close()


def _iter_options__get_encoding():
    # nothing
    yield (
        None,
        None,
        'utf-8',
    )
    
    # charset given
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey mister',
            IgnoreCaseMultiValueDictionary([
                (CONTENT_TYPE, 'image/svg+xml; charset=ascii'),
            ]),
        ),
        b'orin',
        'ascii',
    )
    
    # body checks
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey sister',
            IgnoreCaseMultiValueDictionary(),
        ),
        b'orin',
        'ascii',
    )
    
    # This should be utf-8 actually but chardet thinks otherwise lmeow
    yield (
        RawResponseMessage(
            HttpVersion(1, 1),
            200,
            'hey sister',
            IgnoreCaseMultiValueDictionary(),
        ),
        b'orin ny\xc3\xa1',
        # 'tis-620',
        'iso-8859-13',
    )


@vampytest._(vampytest.call_from(_iter_options__get_encoding()).returning_last())
async def test__ClientResponse__get_encoding(raw_message, body):
    """
    Tests whether ``ClientResponse.get_encoding`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    raw_message : ``RawResponseMessage``
        Raw response message to test with.
    body : `None | bytes`
        Response body.
    
    Returns
    -------
    output : `None | str`
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        client_response.body = body
        client_response.raw_message = raw_message
        
        output = client_response.get_encoding()
        vampytest.assert_instance(output, str)
        return output
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ClientResponse__text():
    """
    Tests whether ``ClientResponse.text`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        
        data = b'hey mister'
        payload_stream = PayloadStream(protocol)
        payload_stream.add_received_chunk(data)
        payload_stream.set_done_success()
        client_response.payload_stream = payload_stream
        
        
        task = Task(loop, client_response.text())
        task.apply_timeout(0.1)
        
        output = await task
        
        vampytest.assert_instance(output, str, nullable = True)
        vampytest.assert_eq(output, data.decode())
        
        vampytest.assert_eq(client_response.body, data)
        vampytest.assert_is(client_response.payload_stream, None)
    
    finally:
        read_socket.close()
        write_socket.close()



async def test__ClientResponse__json():
    """
    Tests whether ``ClientResponse.json`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket, write_socket = create_socket_pair()
    
    try:
        connector = ConnectorBase(loop)
        client_request = _get_default_request()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        connection = Connection(connector, client_request.connection_key, protocol, 2)
        
        client_response = ClientResponse(
            client_request,
            connection,
        )
        
        data = b'{"hey":"mister"}'
        payload_stream = PayloadStream(protocol)
        payload_stream.add_received_chunk(data)
        payload_stream.set_done_success()
        client_response.payload_stream = payload_stream
        
        
        task = Task(loop, client_response.json())
        task.apply_timeout(0.1)
        
        output = await task
        
        vampytest.assert_instance(output, object, nullable = True)
        vampytest.assert_eq(output, from_json(data))
        
        vampytest.assert_eq(client_response.body, data)
        vampytest.assert_is(client_response.payload_stream, None)
    
    finally:
        read_socket.close()
        write_socket.close()
