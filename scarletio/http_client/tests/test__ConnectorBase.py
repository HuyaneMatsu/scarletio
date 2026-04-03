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
from ..protocol_basket import ProtocolBasket

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
    vampytest.assert_instance(connector.clean_up_handle, TimerWeakHandle, nullable = True)
    vampytest.assert_instance(connector.closed, bool)
    vampytest.assert_instance(connector.cookies, SimpleCookie)
    vampytest.assert_instance(connector.force_close, bool)
    vampytest.assert_instance(connector.loop, EventThread)
    vampytest.assert_instance(connector.protocols_by_host, dict)


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


async def test__ConnectorBase__pop_available_protocol__no_protocol():
    """
    Tests whether ``ConnectorBase.pop_available_protocol`` works as intended.
    
    Case: No protocols.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    
    output = connector.pop_available_protocol(connection_key)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    output_protocol, output_performed_requests = output
    vampytest.assert_instance(output_protocol, AbstractProtocolBase, nullable = True)
    vampytest.assert_is(output_protocol, None)
    vampytest.assert_instance(output_performed_requests, int)
    vampytest.assert_eq(output_performed_requests, 0)


async def test__ConnectorBase__pop_available_protocol__no_alive_protocol():
    """
    Tests whether ``ConnectorBase.pop_available_protocol`` works as intended.
    
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_available_protocol(protocol_0, 0.0, 15.0, 0)
        protocol_basket.add_available_protocol(protocol_1, LOOP_TIME() - 1.0, 15.0, 6)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        output = connector.pop_available_protocol(connection_key)
        vampytest.assert_false(connector.protocols_by_host)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        output_protocol, output_performed_requests = output
        vampytest.assert_instance(output_protocol, AbstractProtocolBase, nullable = True)
        vampytest.assert_is(output_protocol, None)
        vampytest.assert_instance(output_performed_requests, int)
        vampytest.assert_eq(output_performed_requests, 0)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__pop_available_protocol__alive_protocol():
    """
    Tests whether ``ConnectorBase.pop_available_protocol`` works as intended.
    
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_available_protocol(protocol, LOOP_TIME() + 1.0, 15.0, 6)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        output = connector.pop_available_protocol(connection_key)
        vampytest.assert_false(connector.protocols_by_host)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        output_protocol, output_performed_requests = output
        vampytest.assert_instance(output_protocol, AbstractProtocolBase, nullable = True)
        vampytest.assert_is(output_protocol, protocol)
        vampytest.assert_instance(output_performed_requests, int)
        vampytest.assert_eq(output_performed_requests, 6)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__release_used_protocol():
    """
    Tests whether ``ConnectorBase.release_used_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    protocol = HttpReadWriteProtocol(loop)
    
    protocol_basket = ProtocolBasket(connection_key)
    protocol_basket.add_used_protocol(protocol)
    
    connector.protocols_by_host[connection_key] = protocol_basket
    
    connector.release_used_protocol(connection_key, protocol)
    
    # Should empty both.
    vampytest.assert_false(protocol_basket)
    vampytest.assert_false(connector.protocols_by_host)


async def test__ConnectorBase__release_used_protocol__has_more():
    """
    Tests whether ``ConnectorBase.release_used_protocol`` works as intended.
    
    Case: has more.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    protocol_basket_0 = ProtocolBasket(connection_key)
    protocol_basket_0.add_used_protocol(protocol_0)
    protocol_basket_0.add_used_protocol(protocol_1)
    
    protocol_basket_1 = ProtocolBasket(connection_key)
    protocol_basket_1.add_used_protocol(protocol_1)
    
    connector.protocols_by_host[connection_key] = protocol_basket_0
    
    connector.release_used_protocol(connection_key, protocol_0)
    vampytest.assert_eq(connector.protocols_by_host, {connection_key: protocol_basket_1})


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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
    
        connector.close()
        
        connector.release(connection_key, protocol, False, 15.0, 2)
        
        vampytest.assert_false(connector.protocols_by_host)
        
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector.release(connection_key, protocol, False, 15.0, 2)
        
        vampytest.assert_is_not(protocol_basket, None)
        protocol_basket = connector.protocols_by_host.get(connection_key, None)
        vampytest.assert_is_not(connector.clean_up_handle, None)
        vampytest.assert_is(protocol_basket.used, None)
        vampytest.assert_eq(protocol_basket.available, [(protocol, Any(float), 2)])
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector.release(connection_key, protocol, True, -1.0, 2)
        
        vampytest.assert_false(connector.protocols_by_host)
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol_0)
        protocol_basket.add_available_protocol(protocol_1, LOOP_TIME() + 100.0, 15.0, 2)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector.close()
        
        vampytest.assert_false(connector.protocols_by_host)
        
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_available_protocol(protocol_0, LOOP_TIME() - 100.0, 15.0, 2)
        protocol_basket.add_available_protocol(protocol_1, LOOP_TIME() - 100.0, 15.0, 3)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector._clean_up()
        
        vampytest.assert_false(connector.protocols_by_host)
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
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_available_protocol(protocol_0, LOOP_TIME() - 100.0, 15.0, 3)
        protocol_basket.add_available_protocol(protocol_1, LOOP_TIME() + 100.0, 15.0, 4)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector._clean_up()
        
        protocol_basket = connector.protocols_by_host.get(connection_key, None)
        vampytest.assert_is_not(protocol_basket, None)
        
        vampytest.assert_eq(protocol_basket.available, [(protocol_1, Any(float), 4)])
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
        )
        
        connector = ConnectorBase(loop)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket = ProtocolBasket(client_request.connection_key)
        protocol_basket.add_available_protocol(protocol, LOOP_TIME() + 100.0, 15.0, 6)
        connector.protocols_by_host[client_request.connection_key] = protocol_basket
        
        output = await connector.connect(client_request)
        
        vampytest.assert_instance(output, Connection)
        vampytest.assert_is(output.connector, connector)
        vampytest.assert_eq(output.key, client_request.connection_key)
        vampytest.assert_is(output.protocol, protocol)
        
        protocol_basket = connector.protocols_by_host.get(client_request.connection_key, None)
        vampytest.assert_is_not(protocol_basket, None)
        vampytest.assert_is(protocol_basket.available, None)
        vampytest.assert_eq(protocol_basket.used, {protocol})
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
        
        protocol_basket = connector.protocols_by_host.get(client_request.connection_key, None)
        vampytest.assert_is_not(protocol_basket, None)
        vampytest.assert_is(protocol_basket.available, None)
        vampytest.assert_eq(protocol_basket.used, {protocol})
        
    finally:
        ConnectorBase.create_connection = original_create_connection
        read_socket.close()
        write_socket.close()


async def test__ConnectorBase__get_closest_expiration__no_available_protocols():
    """
    Tests whether ``ConnectorBase.get_closest_expiration`` works as intended.
    
    Case: No available protocols.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    
    protocol = HttpReadWriteProtocol(loop)
    
    protocol_basket = ProtocolBasket(connection_key)
    protocol_basket.add_used_protocol(protocol)
    connector.protocols_by_host[connection_key] = protocol_basket
    
    output = connector.get_closest_expiration()
    vampytest.assert_instance(output, float)
    vampytest.assert_eq(output, -1.0)


async def test__ConnectorBase__get_closest_expiration__with_available_protocols():
    """
    Tests whether ``ConnectorBase.get_closest_expiration`` works as intended.
    
    Case: With available protocols.
    
    This function is a coroutine.
    """
    connection_key_0 = _get_default_connection_key(host = '1.1.1.1')
    connection_key_1 = _get_default_connection_key(host = '1.1.1.2')
    loop = get_event_loop()
    now = 5000.0
    
    connector = ConnectorBase(loop)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    protocol_basket_0 = ProtocolBasket(connection_key_0)
    protocol_basket_0.add_available_protocol(protocol_0, now + 2.0, 15.0, 2)
    connector.protocols_by_host[connection_key_0] = protocol_basket_0
    
    protocol_basket_1 = ProtocolBasket(connection_key_1)
    protocol_basket_1.add_available_protocol(protocol_1, now + 1.0, 15.0, 2)
    connector.protocols_by_host[connection_key_1] = protocol_basket_1
    
    output = connector.get_closest_expiration()
    vampytest.assert_instance(output, float)
    vampytest.assert_eq(output, now + 1.0 + 15.0)


async def test__ConnectorBase__add_available_protocol():
    """
    Tests whether ``ConnectorBase.add_available_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    # add 1
    connector.add_available_protocol(connection_key, protocol_0, 15.0, 2)
    
    protocol_basket = connector.protocols_by_host.get(connection_key, None)
    vampytest.assert_is_not(protocol_basket, None)
    vampytest.assert_eq(protocol_basket.available, [(protocol_0, Any(float), 2)])
    vampytest.assert_is(protocol_basket.used, None)

    # add 1 more
    connector.add_available_protocol(connection_key, protocol_1, 15.0, 4)
    
    protocol_basket = connector.protocols_by_host.get(connection_key, None)
    vampytest.assert_is_not(protocol_basket, None)
    vampytest.assert_eq(protocol_basket.available, [(protocol_0, Any(float), 2), (protocol_1, Any(float), 4)])
    vampytest.assert_is(protocol_basket.used, None)


async def test__ConnectorBase__add_used_protocol():
    """
    Tests whether ``ConnectorBase.add_used_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    connector = ConnectorBase(loop)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    # add 1
    connector.add_used_protocol(connection_key, protocol_0)
    
    protocol_basket = connector.protocols_by_host.get(connection_key, None)
    vampytest.assert_is_not(protocol_basket, None)
    vampytest.assert_is(protocol_basket.available, None)
    vampytest.assert_eq(protocol_basket.used, {protocol_0})

    # add 1 more
    connector.add_used_protocol(connection_key, protocol_1)
    
    protocol_basket = connector.protocols_by_host.get(connection_key, None)
    vampytest.assert_is_not(protocol_basket, None)
    vampytest.assert_is(protocol_basket.available, None)
    vampytest.assert_eq(protocol_basket.used, {protocol_0, protocol_1})
