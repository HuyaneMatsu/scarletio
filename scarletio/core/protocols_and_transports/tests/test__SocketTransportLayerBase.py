from socket import SocketType, socketpair as create_socket_pair

import vampytest

from ...event_loop import EventThread
from ...top_level import get_event_loop
from ...traps import Future

from ..protocol import ReadProtocolBase
from ..transport_layer import SocketTransportLayerBase


def _assert_fields_set(transport):
    vampytest.assert_instance(transport, SocketTransportLayerBase)
    vampytest.assert_instance(transport._extra, dict)
    vampytest.assert_instance(transport._loop, EventThread)
    vampytest.assert_instance(transport._closing, bool)
    vampytest.assert_instance(transport._connection_lost, bool)
    vampytest.assert_instance(transport._high_water, int)
    vampytest.assert_instance(transport._low_water, int)
    vampytest.assert_instance(transport._paused, bool)
    vampytest.assert_instance(transport._protocol, object, nullable = True)
    vampytest.assert_instance(transport._protocol_paused, bool)
    vampytest.assert_instance(transport._socket, SocketType)
    vampytest.assert_instance(transport._file_descriptor, int)
    

async def test__SocketTransportLayerBase__new():
    """
    Tests whether ``SocketTransportLayerBase.__new__`` works as intended.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    loop = get_event_loop()
    extra = {
        'hey': 'mister',
    }
    
    protocol = ReadProtocolBase(loop)
    waiter = Future(loop)
    transport = None
    
    try:
        transport = SocketTransportLayerBase(loop, extra, read_socket, protocol, waiter)
        _assert_fields_set(transport)
        
        vampytest.assert_is(transport._loop, loop)
        vampytest.assert_is(transport._protocol, protocol)
        vampytest.assert_is(transport._socket, read_socket)
        vampytest.assert_eq(transport._extra, extra)
    finally:
        if (transport is not None):
            transport.abort()
        
        read_socket.close()
        write_socket.close()


async def test__SocketTransportLayerBase__repr():
    """
    Tests whether ``SocketTransportLayerBase.__new__`` works as intended.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    loop = get_event_loop()
    extra = {
        'hey': 'mister',
    }
    
    protocol = ReadProtocolBase(loop)
    waiter = Future(loop)
    transport = None
    
    try:
        transport = SocketTransportLayerBase(loop, extra, read_socket, protocol, waiter)
        output = repr(transport)
        vampytest.assert_instance(output, str)
        vampytest.assert_eq(
            output,
            (
                f'<SocketTransportLayerBase state = open, file_descriptor = {read_socket.fileno()}, '
                f'read = idle, write = idle, buffer_size = 0>'
            )
        )
    
    finally:
        if (transport is not None):
            transport.abort()
        
        read_socket.close()
        write_socket.close()
