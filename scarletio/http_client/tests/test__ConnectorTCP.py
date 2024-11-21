from http.cookies import SimpleCookie
from socket import AddressFamily, SOCK_STREAM as SOCKET_TYPE_STREAM, SocketKind, socketpair as create_socket_pair
from ssl import Purpose as SSLPurpose, SSLContext, create_default_context as create_default_ssl_context

import vampytest

from ...core import (
    CancelledError, EventThread, Future, LOOP_TIME, SocketTransportLayerBase, Task, TimerWeakHandle, get_event_loop,
    skip_poll_cycle, skip_ready_cycle
)
from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import HttpReadWriteProtocol, URL
from ...web_common.headers import METHOD_GET

from ..client_request import ClientRequest
from ..connector_tcp import ConnectorTCP
from ..constants import SSL_CONTEXT_UNVERIFIED
from ..host_info import HostInfo
from ..host_info_basket import HostInfoBasket
from ..protocol_basket import ProtocolBasket
from ..ssl_fingerprint import SSLFingerprint

from .helpers import _get_default_connection_key


def _assert_fields_set(connector):
    """
    Asserts whether every fields are set of the given connector.
    
    Parameters
    ----------
    connector : ``ConnectorTCP``
        The connector to check.
    """
    vampytest.assert_instance(connector, ConnectorTCP)
    vampytest.assert_instance(connector.clean_up_handle, TimerWeakHandle, nullable = True)
    vampytest.assert_instance(connector.closed, bool)
    vampytest.assert_instance(connector.cookies, SimpleCookie)
    vampytest.assert_instance(connector.family, AddressFamily)
    vampytest.assert_instance(connector.force_close, bool)
    vampytest.assert_instance(connector.host_info_basket_cache, dict)
    vampytest.assert_instance(connector.local_address, tuple, nullable = True)
    vampytest.assert_instance(connector.loop, EventThread)
    vampytest.assert_instance(connector.resolve_host_tasks_and_waiters, dict)
    vampytest.assert_instance(connector.protocols_by_host, dict)
    vampytest.assert_instance(connector.ssl_context, SSLContext, nullable = True)


async def test__ConnectorTCP__new():
    """
    Tests whether ``ConnectorTCP.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    family = AddressFamily.AF_INET6
    force_close = True
    local_address = ('1.1.1.1', 96)
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    connector = ConnectorTCP(
        loop,
        family = family,
        force_close = force_close,
        local_address = local_address,
        ssl_context = ssl_context,
        ssl_fingerprint = ssl_fingerprint,
    )
    _assert_fields_set(connector)
    
    vampytest.assert_eq(connector.loop, loop)
    vampytest.assert_eq(connector.family, family)
    vampytest.assert_eq(connector.force_close, force_close)
    vampytest.assert_eq(connector.local_address, local_address)
    vampytest.assert_eq(connector.ssl_context, ssl_context)
    vampytest.assert_eq(connector.ssl_fingerprint, ssl_fingerprint)


async def test__ConnectorTCP__close():
    """
    Tests whether ``ConnectorTCP.close`` works as intended.
    
    This function is a coroutine.
    """
    read_socket, write_socket = create_socket_pair()
    
    try:
        connection_key = _get_default_connection_key()
        loop = get_event_loop()
        
        connector = ConnectorTCP(loop)
        
        protocol_0 = HttpReadWriteProtocol(loop)
        transport_0 = SocketTransportLayerBase(loop, {}, write_socket, protocol_0, None)
        protocol_0.connection_made(transport_0)
        
        protocol_1 = HttpReadWriteProtocol(loop)
        transport_1 = SocketTransportLayerBase(loop, {}, write_socket, protocol_1, None)
        protocol_1.connection_made(transport_1)
        
        
        resolve_host_function_cancelled = True
        
        async def resolve_host_function():
            nonlocal resolve_host_function_cancelled
            try:
                await skip_poll_cycle()
            except CancelledError:
                resolve_host_function_cancelled = True
        
        protocol_basket = ProtocolBasket(connection_key)
        protocol_basket.add_used_protocol(protocol_0)
        protocol_basket.add_available_protocol(protocol_1, LOOP_TIME() + 1000.0, 15.0, 2)
        connector.protocols_by_host[connection_key] = protocol_basket
        
        connector.resolve_host_tasks_and_waiters[(None, None)] = (Task(loop, resolve_host_function()), [])
        
        await skip_ready_cycle()
        
        connector.close()
        
        vampytest.assert_false(connector.protocols_by_host)
            
        vampytest.assert_true(connector.closed)
        vampytest.assert_true(transport_0.is_closing())
        vampytest.assert_true(transport_1.is_closing())
        
        await skip_ready_cycle()
        
        vampytest.assert_true(resolve_host_function_cancelled)
        
    finally:
        read_socket.close()
        write_socket.close()


async def test__ConnectorTCP__resolve_host__success():
    """
    Tests whether ``ConnectorTCP.resolve_host`` works as intended.
    
    Case: success.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    connector = ConnectorTCP(loop)
    host = 'orindance.party'
    port = 96
    
    waiter = Future(loop)
    
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    address_info_0 = (family_0, SocketKind.SOCK_STREAM, protocol_0, '', (host_0, port_0))
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    address_info_1 = (family_1, SocketKind.SOCK_STREAM, protocol_1, '', (host_1, port_1))
    
    def mock_get_address_info(self, input_host, input_port, *, family = 0, type = 0, protocol = 0, flags = 0):
        nonlocal connector
        nonlocal host
        nonlocal port
        nonlocal address_info_0
        nonlocal address_info_1
        
        vampytest.assert_eq(host, input_host)
        vampytest.assert_eq(port, input_port)
        vampytest.assert_eq(family, connector.family)
        vampytest.assert_eq(type, SOCKET_TYPE_STREAM)
        
        future = Future(self)
        future.set_result([address_info_0, address_info_1])
        return future
    
    original_get_address_info = type(loop).get_address_info
    try:
        type(loop).get_address_info = mock_get_address_info
        
        task = Task(loop, connector.resolve_host(host, port, [waiter]))
        
        task.apply_timeout(0.1)
        await task.wait_for_completion()
        
        vampytest.assert_true(task.is_done())
        vampytest.assert_is(task.get_exception(), None)
        vampytest.assert_is(task.get_result(), None)
        
        vampytest.assert_true(waiter.is_done())
        vampytest.assert_is(waiter.get_exception(), None)
        
        expected_host_info_basket = HostInfoBasket.from_address_infos(host, [address_info_0, address_info_1])
        output = waiter.get_result()
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        vampytest.assert_instance(output[0], HostInfoBasket)
        vampytest.assert_true(output[0] % expected_host_info_basket)
        vampytest.assert_is(output[1], None)
        vampytest.assert_true(connector.host_info_basket_cache.get((host, port), None) % expected_host_info_basket)
        
    finally:
        type(loop).get_address_info = original_get_address_info


async def test__ConnectorTCP__resolve_host__cancelled():
    """
    Tests whether ``ConnectorTCP.resolve_host`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    connector = ConnectorTCP(loop)
    host = 'orindance.party'
    port = 96
    
    waiter = Future(loop)
    
    def mock_get_address_info(self, input_host, input_port, *, family = 0, type = 0, protocol = 0, flags = 0):
        nonlocal connector
        nonlocal host
        nonlocal port
        
        vampytest.assert_eq(host, input_host)
        vampytest.assert_eq(port, input_port)
        vampytest.assert_eq(family, connector.family)
        vampytest.assert_eq(type, SOCKET_TYPE_STREAM)
        
        future = Future(self)
        future.cancel()
        return future
    
    original_get_address_info = type(loop).get_address_info
    try:
        type(loop).get_address_info = mock_get_address_info
        
        task = Task(loop, connector.resolve_host(host, port, [waiter]))
        
        task.apply_timeout(0.1)
        await task.wait_for_completion()
        
        vampytest.assert_true(task.is_done())
        vampytest.assert_true(task.is_cancelled())
        
        vampytest.assert_true(waiter.is_done())
        vampytest.assert_is(waiter.get_exception(), None)
        
        output = waiter.get_result()
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        vampytest.assert_is(output[0], None)
        vampytest.assert_is(output[1], None)
        
    finally:
        type(loop).get_address_info = original_get_address_info


async def test__ConnectorTCP__resolve_host__exception():
    """
    Tests whether ``ConnectorTCP.resolve_host`` works as intended.
    
    Case: exception.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    connector = ConnectorTCP(loop)
    host = 'orindance.party'
    port = 96
    
    waiter = Future(loop)
    exception = ValueError('mister')
    
    def mock_get_address_info(self, input_host, input_port, *, family = 0, type = 0, protocol = 0, flags = 0):
        nonlocal connector
        nonlocal host
        nonlocal port
        nonlocal exception
        
        vampytest.assert_eq(host, input_host)
        vampytest.assert_eq(port, input_port)
        vampytest.assert_eq(family, connector.family)
        vampytest.assert_eq(type, SOCKET_TYPE_STREAM)
        
        future = Future(self)
        future.set_exception(exception)
        return future
    
    original_get_address_info = type(loop).get_address_info
    try:
        type(loop).get_address_info = mock_get_address_info
        
        task = Task(loop, connector.resolve_host(host, port, [waiter]))
        
        task.apply_timeout(0.1)
        await task.wait_for_completion()
        
        vampytest.assert_true(task.is_done())
        vampytest.assert_is(task.get_exception(), None)
        vampytest.assert_is(task.get_result(), None)
        
        vampytest.assert_true(waiter.is_done())
        vampytest.assert_is(waiter.get_exception(), None)
        
        output = waiter.get_result()
        vampytest.assert_instance(output, tuple)
        vampytest.assert_eq(len(output), 2)
        vampytest.assert_is(output[0], None)
        vampytest.assert_is(output[1], exception)
        
    finally:
        type(loop).get_address_info = original_get_address_info


async def test__ConnectorTCP__get_resolve_host_waiter():
    """
    Tests whether ``ConnectorTCP.get_resolve_host_waiter`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    connector = ConnectorTCP(loop)
    host = 'orindance.party'
    port = 96
    
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    address_info_0 = (family_0, SocketKind.SOCK_STREAM, protocol_0, '', (host_0, port_0))
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    address_info_1 = (family_1, SocketKind.SOCK_STREAM, protocol_1, '', (host_1, port_1))
    
    def mock_get_address_info(self, input_host, input_port, *, family = 0, type = 0, protocol = 0, flags = 0):
        nonlocal connector
        nonlocal host
        nonlocal port
        nonlocal address_info_0
        nonlocal address_info_1
        
        vampytest.assert_eq(host, input_host)
        vampytest.assert_eq(port, input_port)
        vampytest.assert_eq(family, connector.family)
        vampytest.assert_eq(type, SOCKET_TYPE_STREAM)
        
        future = Future(self)
        future.set_result([address_info_0, address_info_1])
        return future
    
    original_get_address_info = type(loop).get_address_info
    try:
        type(loop).get_address_info = mock_get_address_info
        
        waiter_0 = connector.get_resolve_host_waiter(host, port)
        waiter_1 = connector.get_resolve_host_waiter(host, port)
        
        waiter_0.apply_timeout(0.1)
        waiter_1.apply_timeout(0.1)
        
        await skip_ready_cycle()
        
        output_0 = waiter_0.get_result()
        vampytest.assert_instance(output_0, tuple)
        vampytest.assert_eq(len(output_0), 2)
        vampytest.assert_instance(output_0[0], HostInfoBasket)
        vampytest.assert_true(output_0[0] % HostInfoBasket.from_address_infos(host, [address_info_0, address_info_1]))
        
        output_1 = waiter_1.get_result()
        vampytest.assert_instance(output_1, tuple)
        vampytest.assert_eq(len(output_1), 2)
        vampytest.assert_instance(output_1[0], HostInfoBasket)
        vampytest.assert_true(output_1[0] % HostInfoBasket.from_address_infos(host, [address_info_0, address_info_1]))
        
        vampytest.assert_is(output_0[0], output_1[0])
        
    finally:
        type(loop).get_address_info = original_get_address_info


async def test__ConnectorTCP__resolve_host_iterator__ip_address():
    """
    Tests whether ``ConnectorTCP.resolve_host_iterator`` works as intended.
    
    Case: url is an ip address.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    host = '1.1.1.2'
    port = 97
    url = URL(f'https://{host!s}:{port}/')
    
    
    def mock_get_resolve_host_waiter(self, input_host, input_port):
        raise RuntimeError
    
    
    original_get_resolve_host_waiter = ConnectorTCP.get_resolve_host_waiter
    try:
        ConnectorTCP.get_resolve_host_waiter = mock_get_resolve_host_waiter
        
        connector = ConnectorTCP(loop)
        
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
        
        host_infos = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos.append(host_info)
        
        vampytest.assert_eq(
            host_infos,
            [HostInfo.from_ip(host, port, connector.family)],
        )
        
    finally:
        ConnectorTCP.get_resolve_host_waiter = original_get_resolve_host_waiter


async def test__ConnectorTCP__resolve_host_iterator__from_cache():
    """
    Tests whether ``ConnectorTCP.resolve_host_iterator`` works as intended.
    
    Case: cache is alive.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    url = URL(f'https://orindance.party/')
    
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    
    def mock_get_resolve_host_waiter(self, input_host, input_port):
        raise RuntimeError
    
    
    original_get_resolve_host_waiter = ConnectorTCP.get_resolve_host_waiter
    try:
        ConnectorTCP.get_resolve_host_waiter = mock_get_resolve_host_waiter
        
        connector = ConnectorTCP(loop)
        connector.host_info_basket_cache[url.host, url.port] = HostInfoBasket([host_info_0, host_info_1])
        
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
        
        host_infos_0 = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos_0.append(host_info)
        
        vampytest.assert_eq(
            host_infos_0,
            [host_info_0, host_info_1],
        )
        
        # Also test rotation
        host_infos_1 = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos_1.append(host_info)
        
        vampytest.assert_eq(
            host_infos_1,
            [host_info_1, host_info_0],
        )
        
    finally:
        ConnectorTCP.get_resolve_host_waiter = original_get_resolve_host_waiter



async def test__ConnectorTCP__resolve_host_iterator__from_cache_and_new():
    """
    Tests whether ``ConnectorTCP.resolve_host_iterator`` works as intended.
    
    Case: from cache and new.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    url = URL(f'https://orindance.party/')
    
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    family_2 = AddressFamily.AF_INET6
    host_2 = '2.2.2.2'
    port_2 = 98
    protocol_2 = 225
    
    host_info_2 = HostInfo(
        family_2,
        2,
        host_2,
        'orindance.party',
        port_2,
        protocol_2,
    )
    
    new_basket = None
    connector = None
    get_resolve_host_waiter_called = False
    
    waiter = Future(loop)
    
    def waiter_done_callback(future):
        nonlocal url
        nonlocal connector
        nonlocal new_basket
        assert connector is not None
        assert new_basket is not None
        connector.host_info_basket_cache[url.host, url.port] = new_basket
    
    waiter.add_done_callback(waiter_done_callback)
    
    def mock_get_resolve_host_waiter(self, input_host, input_port):
        nonlocal get_resolve_host_waiter_called
        nonlocal waiter
        
        get_resolve_host_waiter_called = True
        return waiter
    
    
    original_get_resolve_host_waiter = ConnectorTCP.get_resolve_host_waiter
    try:
        ConnectorTCP.get_resolve_host_waiter = mock_get_resolve_host_waiter
        
        connector = ConnectorTCP(loop)
        old_basket = HostInfoBasket([host_info_0, host_info_1])
        old_basket.expiration -= 100.0
        connector.host_info_basket_cache[url.host, url.port] = old_basket
        
        new_basket = HostInfoBasket([host_info_0, host_info_2])
        new_basket.expiration += 100.0
        
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
        
        # before & break
        host_infos_0 = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos_0.append(host_info)
            break
        
        vampytest.assert_eq(
            host_infos_0,
            [host_info_0],
        )
        
        vampytest.assert_true(get_resolve_host_waiter_called)
        
        # meanwhile
        host_infos_1 = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos_1.append(host_info)
            waiter.set_result_if_pending((new_basket, None))
        
        vampytest.assert_eq(
            host_infos_1,
            [host_info_1, host_info_0, host_info_2],
        )
        
        # This is required only because we update the host infos in a callback.
        await skip_ready_cycle()
        
        # Also test rotation
        host_infos_2 = []
        async for host_info in connector.resolve_host_iterator(client_request):
            host_infos_2.append(host_info)
        
        vampytest.assert_eq(
            host_infos_2,
            [host_info_2, host_info_0],
        )
        
    finally:
        ConnectorTCP.get_resolve_host_waiter = original_get_resolve_host_waiter


def _iter_options__get_ssl_context():
    ssl_context_0 = create_default_ssl_context(purpose = SSLPurpose.SERVER_AUTH)
    ssl_context_1 = create_default_ssl_context(purpose = SSLPurpose.CLIENT_AUTH)
    
    url_0 = URL(f'http://orindance.party/')
    url_1 = URL(f'https://orindance.party/')
    
    yield (
        url_0,
        ssl_context_0,
        ssl_context_1,
        None,
    )

    yield (
        url_1,
        ssl_context_0,
        ssl_context_1,
        ssl_context_0,
    )

    yield (
        url_1,
        None,
        ssl_context_1,
        ssl_context_1,
    )
    
    yield (
        url_0,
        None,
        None,
        None,
    )
    
    yield (
        url_1,
        None,
        None,
        SSL_CONTEXT_UNVERIFIED,
    )


@vampytest._(vampytest.call_from(_iter_options__get_ssl_context()).returning_last())
async def test__ConnectorTCP__get_ssl_context(url, request_ssl_context, connector_ssl_context):
    """
    Tests whether ``ConnectorTCP.get_ssl_context`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    url : ``URL``
        Url to create request with.
    request_ssl_context : `None | SSLContext`
        Ssl context to create the request with.
    request_ssl_context : `None | SSLContext`
        Ssl context to create the connector with.
    
    Returns
    -------
    output : `None | SSLContext`
    """
    loop = get_event_loop()
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
        request_ssl_context,
        None,
    )
    
    connector = ConnectorTCP(loop, ssl_context = connector_ssl_context)
    
    output = connector.get_ssl_context(client_request)
    vampytest.assert_instance(output, SSLContext, nullable = True)
    return output



def _iter_options__get_ssl_fingerprint():
    ssl_fingerprint_0 = SSLFingerprint(b'a' * 32)
    ssl_fingerprint_1 = SSLFingerprint(b'b' * 32)
    
    url_0 = URL(f'http://orindance.party/')
    url_1 = URL(f'https://orindance.party/')
    
    yield (
        url_0,
        ssl_fingerprint_0,
        ssl_fingerprint_1,
        None,
    )

    yield (
        url_1,
        ssl_fingerprint_0,
        ssl_fingerprint_1,
        ssl_fingerprint_0,
    )

    yield (
        url_1,
        None,
        ssl_fingerprint_1,
        ssl_fingerprint_1,
    )

    yield (
        url_1,
        None,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__get_ssl_fingerprint()).returning_last())
async def test__ConnectorTCP__get_ssl_fingerprint(url, request_ssl_fingerprint, connector_ssl_fingerprint):
    """
    Tests whether ``ConnectorTCP.get_ssl_fingerprint`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    url : ``URL``
        Url to create request with.
    request_ssl_fingerprint : `None | SSLFingerprint`
        Ssl fingerprint to create the request with.
    request_ssl_fingerprint : `None | SSLFingerprint`
        Ssl fingerprint to create the connector with.
    
    Returns
    -------
    output : `None | SSLFingerprint`
    """
    loop = get_event_loop()
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
        request_ssl_fingerprint,
    )
    
    connector = ConnectorTCP(loop, ssl_fingerprint = connector_ssl_fingerprint)
    
    output = connector.get_ssl_fingerprint(client_request)
    vampytest.assert_instance(output, SSLFingerprint, nullable = True)
    return output



async def test__ConnectorTCP__create_connection():
    """
    Tests whether ``ConnectorTCP.create_connection`` works as intended.
    """
    loop = get_event_loop()
    url = URL(f'https://orindance.party/')
    
    family = AddressFamily.AF_INET
    flags = 3
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    
    host_info = HostInfo(
        family,
        flags,
        host,
        host_name,
        port,
        protocol,
    )
    
    connector = None
    write_socket = None
    protocol = None
    
    def mock_get_resolve_host_waiter(self, input_host, input_port):
        raise RuntimeError
    
    async def mock_create_connection_to(
        self,
        protocol_factory,
        host,
        port,
        *,
        ssl = None,
        socket_family = 0,
        socket_protocol = 0,
        socket_flags = 0,
        local_address = None,
        server_host_name = None,
    ):
        nonlocal connector
        nonlocal host_info
        nonlocal write_socket
        nonlocal protocol
        
        assert connector is not None
        assert write_socket is not None
        
        vampytest.assert_eq(host, host_info.host)
        vampytest.assert_eq(port, host_info.port)
        vampytest.assert_eq(ssl, SSL_CONTEXT_UNVERIFIED)
        
        vampytest.assert_eq(socket_family, host_info.family)
        vampytest.assert_eq(socket_flags, host_info.flags)
        vampytest.assert_eq(local_address, connector.local_address)
        vampytest.assert_eq(server_host_name, host_info.host_name)
        
        protocol = protocol_factory()
        transport = SocketTransportLayerBase(self, {}, write_socket, protocol, None)
        protocol.connection_made(transport)
        return protocol
    
    
    original_get_resolve_host_waiter = ConnectorTCP.get_resolve_host_waiter
    original_create_connection_to = type(loop).create_connection_to
    read_socket, write_socket = create_socket_pair()
    try:
        ConnectorTCP.get_resolve_host_waiter = mock_get_resolve_host_waiter
        type(loop).create_connection_to = mock_create_connection_to
        
        connector = ConnectorTCP(loop)
        connector.host_info_basket_cache[url.host, url.port] = HostInfoBasket([host_info])
        
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
        
        task = Task(loop, connector.create_connection(client_request))
        task.apply_timeout(0.1)
        
        output = await task
        vampytest.assert_is(output, protocol) 
        
    finally:
        read_socket.close()
        write_socket.close()
        
        ConnectorTCP.get_resolve_host_waiter = original_get_resolve_host_waiter
        type(loop).create_connection_to = original_create_connection_to
