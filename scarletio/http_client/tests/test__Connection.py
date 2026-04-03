import vampytest

from socket import socketpair as create_socket_pair

from ...core import AbstractTransportLayerBase, SocketTransportLayerBase, get_event_loop
from ...web_common import HttpReadWriteProtocol
from ...web_common.keep_alive_info import KeepAliveInfo

from ..connection import Connection
from ..connection_key import ConnectionKey
from ..connector_base import ConnectorBase
from ..protocol_basket import ProtocolBasket

from .helpers import Any, _get_default_connection_key


def _assert_fields_set(connection):
    """
    Tests whether the given connection has all of its fields set.
    
    Parameters
    ----------
    connection : ``Connection``
        The connection to check.
    """
    vampytest.assert_instance(connection, Connection)
    vampytest.assert_instance(connection.callbacks, list)
    vampytest.assert_instance(connection.connector, ConnectorBase)
    vampytest.assert_instance(connection.key, ConnectionKey)
    vampytest.assert_instance(connection.performed_requests, int)
    vampytest.assert_instance(connection.protocol, HttpReadWriteProtocol, nullable = True)


async def test__Connection__new():
    """
    Tests whether ``Connection.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    _assert_fields_set(connection)
    
    vampytest.assert_eq(connection.connector, connector)
    vampytest.assert_eq(connection.key, connection_key)
    vampytest.assert_eq(connection.protocol, protocol)
    vampytest.assert_eq(connection.performed_requests, performed_requests)


async def test__Connection__repr():
    """
    Tests whether ``Connection.__repr__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    
    output = repr(connection)
    vampytest.assert_instance(output, str)


async def test__Connection__del():
    """
    Tests whether ``Connection.__del__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    protocol_basket = ProtocolBasket(connection_key)
    protocol_basket.add_used_protocol(protocol)
    connector.protocols_by_host[connection_key] = protocol_basket
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    
    connection.__del__()
    vampytest.assert_false(connector.protocols_by_host)
    vampytest.assert_false(protocol_basket)


async def test__Connection__get_transport__no_protocol():
    """
    Tests whether ``Connection.get_transport`` works as intended.
    
    Case: no protocol.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    connection.close()
    
    output = connection.get_transport()
    vampytest.assert_instance(output, AbstractTransportLayerBase, nullable = True)
    vampytest.assert_is(output, None)


async def test__Connection__get_transport__protocol_no_transport():
    """
    Tests whether ``Connection.get_transport`` works as intended.
    
    Case: protocol no transport.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    
    output = connection.get_transport()
    vampytest.assert_instance(output, AbstractTransportLayerBase, nullable = True)
    vampytest.assert_is(output, None)


async def test__Connection__get_transport__protocol_has_transport():
    """
    Tests whether ``Connection.get_transport`` works as intended.
    
    Case: protocol has transport.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        output = connection.get_transport()
        vampytest.assert_instance(output, AbstractTransportLayerBase, nullable = True)
        vampytest.assert_is(output, transport)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__add_callback__open():
    """
    Tests whether ``Connection.add_callback`` works as intended.
    
    Case: open.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
            
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        callback_called = False
        
        def callback():
            nonlocal callback_called
            callback_called = True
        
        connection.add_callback(callback)
        vampytest.assert_false(callback_called)
        vampytest.assert_eq(connection.callbacks, [callback])
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__add_callback__closed():
    """
    Tests whether ``Connection.add_callback`` works as intended.
    
    Case: closed.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
            
        connection = Connection(connector, connection_key, protocol, performed_requests)
        connection.close()
        
        callback_called = False
        
        def callback():
            nonlocal callback_called
            callback_called = True
        
        connection.add_callback(callback)
        vampytest.assert_eq(connection.callbacks, [])
        vampytest.assert_true(callback_called)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__run_callbacks():
    """
    Tests whether ``Connection._run_callbacks`` works as intended.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
            
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        callback_0_called = False
        callback_1_called = False
        
        def callback_0():
            nonlocal callback_0_called
            callback_0_called = True
        
        def callback_1():
            nonlocal callback_1_called
            callback_1_called = True
        
        connection.add_callback(callback_0)
        connection.add_callback(callback_1)
        
        vampytest.assert_false(callback_0_called)
        vampytest.assert_false(callback_1_called)
        
        connection._run_callbacks()
        
        vampytest.assert_true(callback_0_called)
        vampytest.assert_true(callback_1_called)
        vampytest.assert_eq(connection.callbacks, [])
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__close():
    """
    Tests whether ``Connection.close`` works as intended.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        def callback():
            return None
        
        connection.add_callback(callback)
        
        connection.close()
        
        vampytest.assert_false(connector.protocols_by_host)
        vampytest.assert_eq(connection.callbacks, [])
        vampytest.assert_is(connection.protocol, None)
    
    finally:
        read_socket.close()
        write_socket.close()
    

async def test__Connection__run_callbacks__release__should_close():
    """
    Tests whether ``Connection.close`` works as intended.
    
    Case: should close.
    
    This function is a coroutine.
    """
    performed_requests = 2
    keep_alive_info = KeepAliveInfo.create_default()
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        protocol.set_exception(ConnectionError)
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        def callback():
            return None
        
        connection.add_callback(callback)
        
        connection.release(keep_alive_info)
        
        vampytest.assert_false(connector.protocols_by_host)
        vampytest.assert_eq(connection.callbacks, [])
        vampytest.assert_is(connection.protocol, None)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__run_callbacks__release__should_open():
    """
    Tests whether ``Connection.close`` works as intended.
    
    Case: should open.
    
    This function is a coroutine.
    """
    performed_requests = 2
    keep_alive_info = KeepAliveInfo.create_default()
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        def callback():
            return None
        
        connection.add_callback(callback)
        
        connection.release(keep_alive_info)
        
        protocol_basket = connector.protocols_by_host.get(connection_key, None)
        vampytest.assert_is_not(protocol_basket, None)
        vampytest.assert_is(protocol_basket.used, None)
        vampytest.assert_eq(
            protocol_basket.available,
            [(protocol, Any(float), performed_requests + 1)],
        )
        vampytest.assert_eq(connection.callbacks, [])
        vampytest.assert_is(connection.protocol, None)
    
    finally:
        read_socket.close()
        write_socket.close()



async def test__Connection__run_callbacks__detach():
    """
    Tests whether ``Connection.close`` works as intended.
    
    Case: should open.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        def callback():
            return None
        
        connection.add_callback(callback)
        
        connection.detach()
        
        vampytest.assert_false(connector.protocols_by_host)
        vampytest.assert_eq(connection.callbacks, [])
        vampytest.assert_is(connection.protocol, None)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__Connection__closed__no_protocol():
    """
    Tests whether ``Connection.closed`` works as intended.
    
    Case: no protocol.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    connection.close()
    
    output = connection.is_closed()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__Connection__is_closed__protocol_no_transport():
    """
    Tests whether ``Connection.is_closed`` works as intended.
    
    Case: protocol no transport.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    connector = ConnectorBase(loop)
    connection_key = _get_default_connection_key()
    protocol = HttpReadWriteProtocol(loop)
    performed_requests = 2
    
    connection = Connection(connector, connection_key, protocol, performed_requests)
    
    output = connection.is_closed()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__Connection__is_closed__protocol_has_transport():
    """
    Tests whether ``Connection.is_closed`` works as intended.
    
    Case: protocol has transport.
    
    This function is a coroutine.
    """
    performed_requests = 2
    read_socket, write_socket = create_socket_pair()
    
    try:
        loop = get_event_loop()
        connector = ConnectorBase(loop)
        connection_key = _get_default_connection_key()
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        connection = Connection(connector, connection_key, protocol, performed_requests)
        
        output = connection.is_closed()
        vampytest.assert_instance(output, bool)
        vampytest.assert_eq(output, False)
    
    finally:
        read_socket.close()
        write_socket.close()
