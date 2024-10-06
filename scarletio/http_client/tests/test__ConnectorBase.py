from http.cookies import SimpleCookie
from socket import socketpair as create_socket_pair

import vampytest

from ...core import (
    AbstractProtocolBase, EventThread, LOOP_TIME, SocketTransportLayerBase, TimerWeakHandle, get_event_loop
)
from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import HttpReadWriteProtocol, URL
from ...web_common.headers import METHOD_GET

from ..client_request import ClientRequest
from ..connection import Connection
from ..connector_base import ConnectorBase

from .helpers import Any, _get_default_connection_key


def _assert_fields_set(connector):
    """
    Asserts whether every fields are set of the given connector.
    
    Parameters
    ----------
    connector : ``ConnectorBase``
        The connector to check.
    """
    vampytest.assert_instance(connector, ConnectorBase)
    vampytest.assert_instance(connector.acquired_protocols_per_host, dict)
    vampytest.assert_instance(connector.alive_protocols_per_host, dict)
    vampytest.assert_instance(connector.clean_up_handle, TimerWeakHandle, nullable = True)
    vampytest.assert_instance(connector.closed, bool)
    vampytest.assert_instance(connector.cookies, SimpleCookie)
    vampytest.assert_instance(connector.force_close, bool)
    vampytest.assert_instance(connector.loop, EventThread)


async def test__ConnectorBase__new():
    """
    Tests whether ``ConnectorBase.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    force_close = False
    
    connector = ConnectorBase(loop, force_close = force_close)
    _assert_fields_set(connector)
    
    vampytest.assert_is(connector.loop, loop)
    vampytest.assert_eq(connector.force_close, force_close)


async def test__ConnectorBase__get_protocol__no_protocol():
    """
    Tests whether ``ConnectorBase.get_protocol`` works as intended.
    
    Case: No protocols.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    
    output = connector.get_protocol(connection_key)
    vampytest.assert_instance(output, AbstractProtocolBase, nullable = True)
    vampytest.assert_is(output, None)


async def test__ConnectorBase__get_protocol__no_alive_protocol():
    """
    Tests whether ``ConnectorBase.get_protocol`` works as intended.
    
    Case: No alive protocols.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        connector.alive_protocols_per_host[connection_key] = [
            (protocol_0, 0.0),
            (protocol_1, LOOP_TIME() + 1.0),
        ]
        
        output = connector.get_protocol(connection_key)
        vampytest.assert_false(connector.alive_protocols_per_host)
        vampytest.assert_instance(output, AbstractProtocolBase, nullable = True)
        vampytest.assert_is(output, None)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__get_protocol__alive_protocol():
    """
    Tests whether ``ConnectorBase.get_protocol`` works as intended.
    
    Case: Alive protocol.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connector.alive_protocols_per_host[connection_key] = [
            (protocol, LOOP_TIME() + 1.0),
        ]
        
        output = connector.get_protocol(connection_key)
        vampytest.assert_false(connector.alive_protocols_per_host)
        vampytest.assert_instance(output, AbstractProtocolBase, nullable = True)
        vampytest.assert_is(output, protocol)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__release_acquired_protocol():
    """
    Tests whether ``ConnectorBase.release_acquired_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    protocol = HttpReadWriteProtocol(loop)
    
    connector.acquired_protocols_per_host[connection_key] = {protocol}
    
    connector.release_acquired_protocol(connection_key, protocol)
    vampytest.assert_false(connector.acquired_protocols_per_host)


async def test__ConnectorBase__release_acquired_protocol__has_more():
    """
    Tests whether ``ConnectorBase.release_acquired_protocol`` works as intended.
    
    Case: has more.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    connector.acquired_protocols_per_host[connection_key] = {protocol_0, protocol_1}
    
    connector.release_acquired_protocol(connection_key, protocol_0)
    vampytest.assert_true(connector.acquired_protocols_per_host)
    vampytest.assert_eq(connector.acquired_protocols_per_host, {connection_key: {protocol_1}})


async def test__ConnectorBase__release__closed():
    """
    Tests whether ``ConnectorBase.release`` works as intended.
    
    Case: Closed.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connector.acquired_protocols_per_host[connection_key] = {protocol}
        connector.close()
        
        connector.release(connection_key, protocol)
        
        vampytest.assert_false(connector.acquired_protocols_per_host)
        vampytest.assert_false(connector.alive_protocols_per_host)
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__release__keep():
    """
    Tests whether ``ConnectorBase.release`` works as intended.
    
    Case: keep.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connector.acquired_protocols_per_host[connection_key] = {protocol}
        
        connector.release(connection_key, protocol)
        
        vampytest.assert_false(connector.acquired_protocols_per_host)
        vampytest.assert_eq(connector.alive_protocols_per_host, {connection_key: [(protocol, Any(float))]})
        vampytest.assert_is_not(connector.clean_up_handle, None)
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__release__should_close():
    """
    Tests whether ``ConnectorBase.release`` works as intended.
    
    Case: should close.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connector.acquired_protocols_per_host[connection_key] = {protocol}
        
        connector.release(connection_key, protocol, should_close = True)
        
        vampytest.assert_false(connector.acquired_protocols_per_host)
        vampytest.assert_false(connector.alive_protocols_per_host)
        vampytest.assert_true(transport.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__close():
    """
    Tests whether ``ConnectorBase.close`` works as intended.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        connector.acquired_protocols_per_host[connection_key] = {protocol_0}
        connector.alive_protocols_per_host[connection_key] = [(protocol_1, LOOP_TIME() + 100.0)]
        
        connector.close()
        
        vampytest.assert_false(connector.acquired_protocols_per_host)
        vampytest.assert_false(connector.alive_protocols_per_host)
            
        vampytest.assert_true(connector.closed)
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_true(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__clean_up__everything_cleaned_up():
    """
    Tests whether ``ConnectorBase._clean_up`` works as intended.
    
    Case: Everything is cleaned up.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        connector.alive_protocols_per_host[connection_key] = [
            (protocol_0, LOOP_TIME() - 100.0),
            (protocol_1, LOOP_TIME() - 100.0),
        ]
        
        connector._clean_up()
        
        vampytest.assert_false(connector.alive_protocols_per_host)
        vampytest.assert_is(connector.clean_up_handle, None)
        
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_true(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()
    

async def test__ConnectorBase__clean_up__not_everything_is_cleaned_up():
    """
    Tests whether ``ConnectorBase._clean_up`` works as intended.
    
    Case: Not everything is cleaned up.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorBase(loop)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        connector.alive_protocols_per_host[connection_key] = [
            (protocol_0, LOOP_TIME() - 100.0),
            (protocol_1, LOOP_TIME() + 100.0),
        ]
        
        connector._clean_up()
        
        vampytest.assert_eq(connector.alive_protocols_per_host, {connection_key: [(protocol_1, Any(float))]})
        vampytest.assert_is_not(connector.clean_up_handle, None)
        
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_false(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()
    

async def test__ConnectorBase__connect__cache_hit():
    """
    Tests whether ``ConnectorBase.connect`` works as intended.
    
    Case: cache hit.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    async def mock_create_connection(self, request):
        raise RuntimeError
    
    original_create_connection = ConnectorBase.create_connection
    try:
        ConnectorBase.create_connection = mock_create_connection
        
        loop = get_event_loop()
        
        client_request = ClientRequest(
            loop,
            METHOD_GET,
            URL('https://orindance.party/'),
            IgnoreCaseMultiValueDictionary(),
            None,
            None,
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
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connector.alive_protocols_per_host[client_request.connection_key] = [(protocol, LOOP_TIME() + 100.0)]
        
        output = await connector.connect(client_request)
        
        vampytest.assert_instance(output, Connection)
        vampytest.assert_is(output.connector, connector)
        vampytest.assert_eq(output.key, client_request.connection_key)
        vampytest.assert_is(output.protocol, protocol)
        
        vampytest.assert_eq(connector.acquired_protocols_per_host, {client_request.connection_key: {protocol}})
        vampytest.assert_false(connector.alive_protocols_per_host)
        
    finally:
        ConnectorBase.create_connection = original_create_connection
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__connect__cache_miss():
    """
    Tests whether ``ConnectorBase.connect`` works as intended.
    
    Case: cache miss.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    protocol = None
    
    async def mock_create_connection(self, request):
        nonlocal protocol
        if protocol is None:
            raise RuntimeError
        
        return protocol
    
    original_create_connection = ConnectorBase.create_connection
    try:
        ConnectorBase.create_connection = mock_create_connection
        loop = get_event_loop()
        
        client_request = ClientRequest(
            loop,
            METHOD_GET,
            URL('https://orindance.party/'),
            IgnoreCaseMultiValueDictionary(),
            None,
            None,
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
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        output = await connector.connect(client_request)
        
        vampytest.assert_instance(output, Connection)
        vampytest.assert_is(output.connector, connector)
        vampytest.assert_eq(output.key, client_request.connection_key)
        vampytest.assert_is(output.protocol, protocol)
        
        vampytest.assert_eq(connector.acquired_protocols_per_host, {client_request.connection_key: {protocol}})
        vampytest.assert_false(connector.alive_protocols_per_host)
        
    finally:
        ConnectorBase.create_connection = original_create_connection
        read_socket.close()
        write_socket.close()
