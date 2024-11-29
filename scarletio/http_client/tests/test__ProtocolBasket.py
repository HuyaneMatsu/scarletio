from socket import socketpair as create_socket_pair

import vampytest

from ...core import AbstractProtocolBase, SocketTransportLayerBase, get_event_loop
from ...web_common import HttpReadWriteProtocol

from ..connection_key import ConnectionKey
from ..protocol_basket import ProtocolBasket

from .helpers import _get_default_connection_key


def _assert_fields_set(protocol_basket):
    """
    Asserts whether every fields are set of the given protocol basket.
    
    Parameters
    ----------
    protocol_basket : ``ProtocolBasket``
        Protocol basket to test with.
    """
    vampytest.assert_instance(protocol_basket, ProtocolBasket)
    vampytest.assert_instance(protocol_basket.available, list, nullable = True)
    vampytest.assert_instance(protocol_basket.connection_key, ConnectionKey)
    vampytest.assert_instance(protocol_basket.used, set, nullable = True)


def test__ProtocolBasket__new():
    """
    Tests whether ``ProtocolBasket.__new__`` works as intended.
    """
    connection_key = _get_default_connection_key()
    
    protocol_basket = ProtocolBasket(connection_key)
    
    _assert_fields_set(protocol_basket)
    vampytest.assert_eq(protocol_basket.connection_key, connection_key)
    

def test__ProtocolBasket__repr__least_fields():
    """
    Tests whether ``ProtocolBasket.__repr__`` works as intended.
    
    Case: Least fields.
    """
    connection_key = _get_default_connection_key()
    
    protocol_basket = ProtocolBasket(connection_key)
    
    output = repr(protocol_basket)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in(ProtocolBasket.__name__, output)
    vampytest.assert_in(f'connection_key = {connection_key!r}', output)


async def test__ProtocolBasket__repr__all_fields():
    """
    Tests whether ``ProtocolBasket.__repr__`` works as intended.
    
    This function is a coroutine.
    
    Case: All fields.
    """
    loop = get_event_loop()
    connection_key = _get_default_connection_key()
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    now = 5000.0
    
    protocol_basket = ProtocolBasket(connection_key)
    protocol_basket.add_used_protocol(protocol_0)
    protocol_basket.add_available_protocol(protocol_1, now, 15.0, 0)
    
    output = repr(protocol_basket)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in(ProtocolBasket.__name__, output)
    vampytest.assert_in(f'connection_key = {connection_key!r}', output)
    vampytest.assert_in(f'available = {protocol_basket.available!r}', output)
    vampytest.assert_in(f'used = {protocol_basket.used!r}', output)


def _iter_options__eq():
    connection_key_0 = _get_default_connection_key(host = '1.2.3.4')
    connection_key_1 = _get_default_connection_key(host = '4.3.2.1')
    
    keyword_parameters = {
        'connection_key': connection_key_0
    }
    
    yield (
        keyword_parameters,
        0,
        0,
        5000.0,
        keyword_parameters,
        0,
        0,
        5000.0,
        True,
    )
    
    yield (
        keyword_parameters,
        0,
        0,
        5000.0,
        {
            **keyword_parameters,
            'connection_key': connection_key_1,
        },
        0,
        0,
        5000.0,  
        False,
    )
    
    yield (
        keyword_parameters,
        0,
        0,
        5000.0,
        keyword_parameters,
        1,
        0,
        5000.0,
        False,
    )
    
    yield (
        keyword_parameters,
        0,
        0,
        5000.0,
        keyword_parameters,
        0,
        1,
        5000.0,
        False,
    )
    
    yield (
        keyword_parameters,
        1,
        0,
        5000.0,
        keyword_parameters,
        1,
        0,
        4000.0,
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
async def test__ProtocolBasket__eq(
    keyword_parameters_0,
    available_protocol_0,
    used_protocol_0,
    now_0,
    keyword_parameters_1,
    available_protocol_1,
    used_protocol_1,
    now_1,
):
    """
    Tests whether ``ProtocolBasket.__eq__`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    available_protocol_0 : `int`
        Alive protocol identifier to add..
    
    used_protocol_0 : `int`
        Used protocol identifier.
    
    now_0 : `float`
        Monotonic time.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    available_protocol_1 : `int`
        Alive protocol identifier to add..
    
    used_protocol_1 : `int`
        Used protocol identifier.
    
    now_1 : `float`
        Monotonic time.
    
    Returns
    -------
    output : `bool`
    """
    loop = get_event_loop()
    protocols = {0 : None}
    
    for protocol_identifier in (available_protocol_0, used_protocol_0, available_protocol_1, used_protocol_1):
        if protocol_identifier in protocols:
            continue
        
        protocols[protocol_identifier] = HttpReadWriteProtocol(loop)
    
    protocol_basket_0 = ProtocolBasket(**keyword_parameters_0)
    
    protocol = protocols.get(available_protocol_0, None)
    if protocol is not None:
        protocol_basket_0.add_available_protocol(protocol, now_0, 15.0, 0)
    
    protocol = protocols.get(used_protocol_0, None)
    if protocol is not None:
        protocol_basket_0.add_used_protocol(protocol)

    protocol_basket_1 = ProtocolBasket(**keyword_parameters_1)
    
    protocol = protocols.get(available_protocol_1, None)
    if protocol is not None:
        protocol_basket_1.add_available_protocol(protocol, now_1, 15.0, 0)
    
    protocol = protocols.get(used_protocol_1, None)
    if protocol is not None:
        protocol_basket_1.add_used_protocol(protocol)
    
    output = protocol_basket_0 == protocol_basket_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__bool():
    yield (
        0,
        0,
        False,
    )
    
    yield (
        1,
        0,
        True,
    )
    
    yield (
        0,
        1,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__bool()).returning_last())
async def test__ProtocolBasket__bool(available_protocol, used_protocol):
    """
    Tests whether ``ProtocolBasket.__bool__`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    available_protocol : `int`
        Alive protocol identifier to add..
    
    used_protocol : `int`
        Used protocol identifier.
    
    Returns
    -------
    output : `bool`
    """
    loop = get_event_loop()
    connection_key = _get_default_connection_key()
    now = 5000.0
    
    protocol_basket = ProtocolBasket(connection_key)
    
    if available_protocol:
        protocol_basket.add_available_protocol(HttpReadWriteProtocol(loop), now, 15.0, 0)
    
    if used_protocol:
        protocol_basket.add_used_protocol(HttpReadWriteProtocol(loop))
    
    output = bool(protocol_basket)
    vampytest.assert_instance(output, bool)
    return output


async def test__ProtocolBasket__clean_up_expired_protocols__everything_cleaned_up():
    """
    Tests whether ``ProtocolBasket.clean_up_expired_protocols`` works as intended.
    
    Case: Everything is cleaned up.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000.0
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        protocol_basket.add_available_protocol(protocol_0, now - 100.0, 15.0, 0)
        protocol_basket.add_available_protocol(protocol_1, now - 100.0, 15.0, 0)
        
        protocol_basket.clean_up_expired_protocols(now)
        
        vampytest.assert_false(protocol_basket.available)
        
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_true(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()
    

async def test__CProtocolBasket__clean_up_expired_protocols__not_everything_is_cleaned_up():
    """
    Tests whether ``ProtocolBasket.clean_up_expired_protocols`` works as intended.
    
    Case: Not everything is cleaned up.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000.0
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        protocol_basket.add_available_protocol(protocol_0, now - 100.0, 15.0, 2)
        protocol_basket.add_available_protocol(protocol_1, now + 100.0, 15.0, 3)
        
        protocol_basket.clean_up_expired_protocols(now)
        
        vampytest.assert_eq(protocol_basket.available, [(protocol_1, now + 115.0, 3)])
        
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_false(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ProtocolBasket__close():
    """
    Tests whether ``ProtocolBasket.close`` works as intended.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000.0
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        protocol_basket.add_used_protocol(protocol_0)
        protocol_basket.add_available_protocol(protocol_1, now + 100.0, 15.0, 0)
        
        protocol_basket.close()
        
        vampytest.assert_is(protocol_basket.available, None)
        vampytest.assert_is(protocol_basket.used, None)
        
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_true(transport_1.is_closing())
        
    finally:
        read_socket.close()
        write_socket.close()


def test__ProtocolBasket__pop_available_protocol__no_protocol():
    """
    Tests whether ``ProtocolBasket.pop_available_protocol`` works as intended.
    
    Case: No protocols.
    """
    connection_key = _get_default_connection_key()
    now = 5000
    
    protocol_basket = ProtocolBasket(connection_key)
    
    output = protocol_basket.pop_available_protocol(now)
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    output_protocol, output_performed_requests = output
    vampytest.assert_instance(output_protocol, AbstractProtocolBase, nullable = True)
    vampytest.assert_is(output_protocol, None)
    vampytest.assert_instance(output_performed_requests, int)
    vampytest.assert_eq(output_performed_requests, 0)


async def test__ProtocolBasket__pop_available_protocol__no_alive_protocol():
    """
    Tests whether ``ProtocolBasket.pop_available_protocol`` works as intended.
    
    Case: No alive protocols.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        protocol_basket.add_available_protocol(protocol_0, now - 100.0, 15.0, 5)
        protocol_basket.add_available_protocol(protocol_1, now + 100.0, 15.5, 6)
        
        output = protocol_basket.pop_available_protocol(now)
        vampytest.assert_is(protocol_basket.available, None)
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


async def test__ProtocolBasket__pop_available_protocol__alive_protocol():
    """
    Tests whether ``ProtocolBasket.pop_available_protocol`` works as intended.
    
    Case: Alive protocol.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol = HttpReadWriteProtocol(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol_basket.add_available_protocol(protocol, now + 100.0, 15.0, 5)
        
        output = protocol_basket.pop_available_protocol(now)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        vampytest.assert_is(protocol_basket.available, None)
        output_protocol, output_performed_requests = output
        vampytest.assert_instance(output_protocol, AbstractProtocolBase, nullable = True)
        vampytest.assert_is(output_protocol, protocol)
        vampytest.assert_instance(output_performed_requests, int)
        vampytest.assert_eq(output_performed_requests, 5)
    
    finally:
        read_socket.close()
        write_socket.close()



async def test__ProtocolBasket__pop_available_protocol__pop_closest():
    """
    Tests whether ``ProtocolBasket.pop_available_protocol`` works as intended.
    
    Case: Pop closest.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    now = 5000
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        protocol_basket = ProtocolBasket(connection_key)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, None, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, None, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        protocol_2 = HttpReadWriteProtocol(loop)
        transport_2 = SocketTransportLayerBase(loop, None, write_socket, protocol_2, None)
        protocol_2.connection_made(transport_2)
        
        protocol_basket.add_available_protocol(protocol_0, now + 110.0, 15.0, 5)
        protocol_basket.add_available_protocol(protocol_1, now + 100.0, 15.0, 6)
        protocol_basket.add_available_protocol(protocol_2, now + 120.0, 15.0, 6)
        
        output = protocol_basket.pop_available_protocol(now)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        output_protocol, output_performed_requests = output
        vampytest.assert_is(output_protocol, protocol_1)
    
        output = protocol_basket.pop_available_protocol(now)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        output_protocol, output_performed_requests = output
        vampytest.assert_is(output_protocol, protocol_0)
    
        output = protocol_basket.pop_available_protocol(now)
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        output_protocol, output_performed_requests = output
        vampytest.assert_is(output_protocol, protocol_2)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ProtocolBasket__add_used_protocol():
    """
    Tests whether ``ProtocolBasket.add_used_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    protocol_basket = ProtocolBasket(connection_key)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    vampytest.assert_is(protocol_basket.used, None)
    protocol_basket.add_used_protocol(protocol_0)
    vampytest.assert_eq(protocol_basket.used, {protocol_0})
    protocol_basket.add_used_protocol(protocol_1)
    vampytest.assert_eq(protocol_basket.used, {protocol_0, protocol_1})


async def test__ProtocolBasket__remove_used_protocol():
    """
    Tests whether ``ProtocolBasket.add_used_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    
    protocol_basket = ProtocolBasket(connection_key)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    protocol_2 = HttpReadWriteProtocol(loop)
    
    protocol_basket.add_used_protocol(protocol_0)
    protocol_basket.add_used_protocol(protocol_1)
    
    vampytest.assert_eq(protocol_basket.used, {protocol_0, protocol_1})
    
    # Remove that is not in it
    protocol_basket.remove_used_protocol(protocol_2)
    vampytest.assert_eq(protocol_basket.used, {protocol_0, protocol_1})
    
    protocol_basket.remove_used_protocol(protocol_1)
    vampytest.assert_eq(protocol_basket.used, {protocol_0})
    protocol_basket.remove_used_protocol(protocol_0)
    vampytest.assert_is(protocol_basket.used, None)
    
    # Remove that is not in it
    protocol_basket.remove_used_protocol(protocol_2)
    vampytest.assert_is(protocol_basket.used, None)


async def test__ProtocolBasket__add_available_protocol():
    """
    Tests whether ``ProtocolBasket.add_available_protocol`` works as intended.
    
    This function is a coroutine.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    now = 5000.0
    
    protocol_basket = ProtocolBasket(connection_key)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    vampytest.assert_is(protocol_basket.available, None)
    protocol_basket.add_available_protocol(protocol_0, now, 15.0, 5)
    vampytest.assert_eq(
        protocol_basket.available,
        [
            (protocol_0, now + 15.0, 5)
        ],
    )
    protocol_basket.add_available_protocol(protocol_1, now + 100.0, 15.0, 6)
    vampytest.assert_eq(
        protocol_basket.available,
        [
            (protocol_0, now + 15.0, 5),
            (protocol_1, now + 100.0 + 15.0, 6),
        ],
    )


def test__ProtocolBasket__get_closest_expiration__get_expiration():
    """
    Tests whether ``ProtocolBasket.get_closest_expiration`` works as intended.
    
    Case: no expiration.
    """
    connection_key = _get_default_connection_key()
    
    protocol_basket = ProtocolBasket(connection_key)
    
    output = protocol_basket.get_closest_expiration()
    vampytest.assert_instance(output, float)
    vampytest.assert_eq(output, -1)


async def test__ProtocolBasket__get_closest_expiration__has_expiration():
    """
    Tests whether ``ProtocolBasket.get_closest_expiration`` works as intended.
    
    This function is a coroutine.
    
    Case: has expiration.
    """
    connection_key = _get_default_connection_key()
    loop = get_event_loop()
    now = 5000.0
    
    protocol_basket = ProtocolBasket(connection_key)
    
    protocol_0 = HttpReadWriteProtocol(loop)
    protocol_1 = HttpReadWriteProtocol(loop)
    
    protocol_basket.add_available_protocol(protocol_0, now + 2.0, 15.0, 0)
    protocol_basket.add_available_protocol(protocol_1, now + 1.0, 15.0, 2)
    
    output = protocol_basket.get_closest_expiration()
    vampytest.assert_instance(output, float)
    vampytest.assert_eq(output, now + 1.0 + 15.0)
