from collections import deque as Deque
from functools import partial as partial_func
from socket import socketpair as create_socket_pair
from types import CoroutineType, GeneratorType

import vampytest

from ...event_loop import EventThread
from ...top_level import get_event_loop
from ...traps import Task, skip_ready_cycle

from ..abstract import AbstractTransportLayerBase
from ..payload_stream import PayloadStream
from ..protocol import ReadProtocolBase
from ..transport_layer import SocketTransportLayerBase


def _assert_fields_set(protocol):
    """
    Asserts whether every fields of the given protocol.
    
    Parameters
    ----------
    protocol : ``ReadProtocolBase``
        The protocol to test.
    """
    vampytest.assert_instance(protocol, ReadProtocolBase)
    vampytest.assert_instance(protocol._at_eof, bool)
    vampytest.assert_instance(protocol._chunks, Deque)
    vampytest.assert_instance(protocol._exception, BaseException, nullable = True)
    vampytest.assert_instance(protocol._offset, int)
    vampytest.assert_instance(protocol._paused, bool)
    vampytest.assert_instance(protocol._payload_reader, CoroutineType, GeneratorType, nullable = True)
    vampytest.assert_instance(protocol._payload_stream, PayloadStream, nullable = True)
    vampytest.assert_instance(protocol._loop, EventThread)
    vampytest.assert_instance(protocol._transport, AbstractTransportLayerBase, nullable = True)


async def test__ReadProtocolBase__new():
    """
    Tests whether ``ReadProtocolBase.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    _assert_fields_set(protocol)
    
    vampytest.assert_is(protocol._loop, loop)


async def test__ReadProtocolBase__repr():
    """
    Tests whether ``ReadProtocolBase.__repr__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    output = repr(protocol)
    vampytest.assert_instance(output, str)


async def test__ReadProtocolBase__connection_made():
    """
    Tests whether ``ReadProtocolBase.connection_made`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    read_socket, write_socket = create_socket_pair()
    
    try:
        protocol = ReadProtocolBase(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        
        protocol.connection_made(transport)
        
        vampytest.assert_is(protocol._transport, transport)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ReadProtocolBase__connection_lost__no_exception_no_reader():
    """
    Tests whether ``ReadProtocolBase.connection_lost`` works as intended.
    
    This function is a coroutine.
    
    Case: no exception & no reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.connection_lost(None)
    
    vampytest.assert_eq(protocol._at_eof, True)


async def test__ReadProtocolBase__connection_lost__no_exception_with_reader():
    """
    Tests whether ``ReadProtocolBase.connection_lost`` works as intended.
    
    This function is a coroutine.
    
    Case: no exception & with reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    task = Task(loop, protocol.read_exactly(1))
    await skip_ready_cycle()
    
    protocol.connection_lost(None)
    
    vampytest.assert_eq(protocol._at_eof, True)
    
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(ConnectionError):
        task.get_result()


async def test__ReadProtocolBase__connection_lost__with_exception_no_reader():
    """
    Tests whether ``ReadProtocolBase.connection_lost`` works as intended.
    
    This function is a coroutine.
    
    Case: with exception & no reader.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.connection_lost(exception)
    
    vampytest.assert_is(protocol._exception, exception)


async def test__ReadProtocolBase__connection_lost__with_exception_with_reader():
    """
    Tests whether ``ReadProtocolBase.connection_lost`` works as intended.
    
    This function is a coroutine.
    
    Case: with exception & with reader.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    task = Task(loop, protocol.read_exactly(1))
    await skip_ready_cycle()
    
    protocol.connection_lost(exception)
    
    vampytest.assert_is(protocol._exception, exception)
    
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(type(exception)):
        task.get_result()


async def test__ReadProtocolBase__get_extra_info__no_transport():
    """
    Tests whether ``ReadProtocolBase.get_extra_info`` works as intended.
    
    This function is a coroutine.
    
    Case: No transport.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    extra_info = protocol.get_extra_info('mister')
    vampytest.assert_eq(extra_info, None)


async def test__ReadProtocolBase__get_extra_info__with_transport():
    """
    Tests whether ``ReadProtocolBase.get_extra_info`` works as intended.
    
    This function is a coroutine.
    
    Case: with transport.
    """
    loop = get_event_loop()
    extra_info = {'mister': 'hey'}
    read_socket, write_socket = create_socket_pair()
    
    try:
        protocol = ReadProtocolBase(loop)
        transport = SocketTransportLayerBase(loop, extra_info, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        extra_info = protocol.get_extra_info('mister')
        vampytest.assert_eq(extra_info, 'hey')
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ReadProtocolBase__close__no_transport():
    """
    Tests whether ``ReadProtocolBase.close`` works as intended.
    
    This function is a coroutine.
    
    Case: No transport.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    # Should do nothing
    protocol.close()


async def test__ReadProtocolBase__close__with_transport():
    """
    Tests whether ``ReadProtocolBase.close`` works as intended.
    
    This function is a coroutine.
    
    Case: with transport.
    """
    loop = get_event_loop()
    read_socket, write_socket = create_socket_pair()
    
    try:
        protocol = ReadProtocolBase(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        protocol.close()
        vampytest.assert_eq(transport._closing, True)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ReadProtocolBase__get_transport__no_transport():
    """
    Tests whether ``ReadProtocolBase.get_transport`` works as intended.
    
    This function is a coroutine.
    
    Case: No transport.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    output = protocol.get_transport()
    vampytest.assert_is(output, None)


async def test__ReadProtocolBase__get_transport__with_transport():
    """
    Tests whether ``ReadProtocolBase.get_transport`` works as intended.
    
    This function is a coroutine.
    
    Case: with transport.
    """
    loop = get_event_loop()
    read_socket, write_socket = create_socket_pair()
    
    try:
        protocol = ReadProtocolBase(loop)
        transport = SocketTransportLayerBase(loop, None, write_socket, protocol, None)
        protocol.connection_made(transport)
        
        output = protocol.get_transport()
        vampytest.assert_is(output, transport)
    
    finally:
        read_socket.close()
        write_socket.close()


async def test__ReadProtocolBase__get_size__no_reader_no_data():
    """
    Tests whether ``ReadProtocolBase.get_size`` works as intended.
    
    This function is a coroutine.
    
    Case: No reader & no data.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    output = protocol.get_size()
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__ReadProtocolBase__get_size__no_reader_with_data():
    """
    Tests whether ``ReadProtocolBase.get_size`` works as intended.
    
    This function is a coroutine.
    
    Case: No reader & with data.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    protocol.data_received(b'aya')
    protocol.data_received(b'ya')
    
    output = protocol.get_size()
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 5)


async def test__ReadProtocolBase__get_size__with_reader_whole():
    """
    Tests whether ``ReadProtocolBase.get_size`` works as intended.
    
    This function is a coroutine.
    
    Case: With reader & whole.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    task = Task(loop, payload_stream.__await__())
    await skip_ready_cycle()
    
    try:
        protocol.data_received(b'aya')
        protocol.data_received(b'ya')
        
        output = protocol.get_size()
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 0)
    
    finally:
        task.cancel()


async def test__ReadProtocolBase__get_size__with_reader_chunk():
    """
    Tests whether ``ReadProtocolBase.get_size`` works as intended.
    
    This function is a coroutine.
    
    Case: With reader # chunk.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    
    coroutine_iterator = payload_stream.__aiter__()
    task = Task(loop, coroutine_iterator.asend(None).__await__())
    await skip_ready_cycle()
    
    try:
        protocol.data_received(b'aya')
        protocol.data_received(b'ya')
        
        output = protocol.get_size()
        vampytest.assert_instance(output, int)
        
        # 1 chunk should be received the rest should be cached.
        vampytest.assert_eq(output, 2)
    
    finally:
        task.cancel()
        coroutine_iterator.aclose().close()


async def test__ReadProtocolBase__is_at_eof__true():
    """
    Tests whether ``ReadProtocolBase.is_at_eof`` works as intended.
    
    This function is a coroutine.
    
    Case: true.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    protocol.eof_received()
    
    output = protocol.is_at_eof()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__ReadProtocolBase__is_at_eof__false__eof_not_set():
    """
    Tests whether ``ReadProtocolBase.is_at_eof`` works as intended.
    
    This function is a coroutine.
    
    Case: false & eof not set.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    output = protocol.is_at_eof()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


async def test__ReadProtocolBase__is_at_eof__false__has_unprocessed_data():
    """
    Tests whether ``ReadProtocolBase.is_at_eof`` works as intended.
    
    This function is a coroutine.
    
    Case: false & has unprocessed data.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    protocol.data_received(b'ara')
    protocol.eof_received()
    
    output = protocol.is_at_eof()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


async def test__ReadProtocolBase__set_exception__no_reader():
    """
    Tests whether ``ReadProtocolBase.set_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: no reader
    """
    loop = get_event_loop()
    exception = ValueError()
    protocol = ReadProtocolBase(loop)
    protocol.set_exception(exception)
    
    vampytest.assert_is(protocol._exception, exception)


async def test__ReadProtocolBase__set_exception__has_reader():
    """
    Tests whether ``ReadProtocolBase.set_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: has reader.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    protocol.set_exception(exception)
    
    vampytest.assert_is(protocol._exception, exception)
    vampytest.assert_is(payload_stream._exception, exception)


async def test__ReadProtocolBase__eof_received__no_reader():
    """
    Tests whether ``ReadProtocolBase.eof_received`` works as intended.
    
    This function is a coroutine.
    
    Case: no reader
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    protocol.eof_received()
    
    vampytest.assert_eq(protocol._at_eof, True)


async def test__ReadProtocolBase__eof_received__has_reader():
    """
    Tests whether ``ReadProtocolBase.eof_received`` works as intended.
    
    This function is a coroutine.
    
    Case: has reader.
    """
    loop = get_event_loop()
    protocol = ReadProtocolBase(loop)
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    protocol.eof_received()
    
    vampytest.assert_eq(protocol._at_eof, True)
    vampytest.assert_is_not(payload_stream._exception, None)


async def test__ReadProtocolBase__data_received__no_reader():
    """
    Tests whether ``ReadProtocolBase.data_received`` works as intended.
    
    This function is a coroutine.
    
    Case: no reader.
    """
    loop = get_event_loop()
    chunk = b'hey mister sister'
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(chunk)
    
    vampytest.assert_eq([*protocol._chunks], [chunk])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__data_received__has_reader():
    """
    Tests whether ``ReadProtocolBase.data_received`` works as intended.
    
    This function is a coroutine.
    
    Case: has reader.
    """
    loop = get_event_loop()
    chunk = b'hey mister sister'
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(chunk)
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    
    vampytest.assert_eq([*protocol._chunks], [chunk])
    vampytest.assert_eq(protocol._offset, 10)
    
    task = Task(loop, payload_stream.__await__())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), chunk[:10])


async def test__ReadProtocolBase__cancel_current_reader__no_reader():
    """
    Tests whether ``ReadProtocolBase.cancel_current_reader`` works as intended.
    
    This function is a coroutine.
    
    Case: no reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.cancel_current_reader()


async def test__ReadProtocolBase__cancel_current_reader__has_reader():
    """
    Tests whether ``ReadProtocolBase.cancel_current_reader`` works as intended.
    
    This function is a coroutine.
    
    Case: has reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    
    protocol.cancel_current_reader()
    vampytest.assert_is(protocol._payload_stream, None)
    vampytest.assert_is(protocol._payload_reader, None)
    
    
    task = Task(loop, payload_stream.__await__())
    await skip_ready_cycle()
    
    with vampytest.assert_raises(ConnectionError):
        task.get_result()


async def test__ReadProtocolBase__handle_payload_stream_abortion__no_reader():
    """
    Tests whether ``ReadProtocolBase.handle_payload_stream_abortion`` works as intended.
    
    This function is a coroutine.
    
    Case: no reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.handle_payload_stream_abortion()


async def test__ReadProtocolBase__handle_payload_stream_abortion__has_reader():
    """
    Tests whether ``ReadProtocolBase.handle_payload_stream_abortion`` works as intended.
    
    This function is a coroutine.
    
    Case: has reader.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    payload_stream = protocol.set_payload_reader(partial_func(protocol._read_exactly, 10, False))
    
    protocol.handle_payload_stream_abortion()
    
    task = Task(loop, payload_stream.__await__())
    await skip_ready_cycle()
    task.cancel()
    
    await skip_ready_cycle()
    
    vampytest.assert_true(protocol.is_at_eof())


async def test__ReadProtocolBase__read__all():
    """
    Tests whether ``ReadProtocolBase.read`` works as intended.
    
    This function is a coroutine.
    
    Case: all.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read())
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    await skip_ready_cycle()
    vampytest.assert_false(task.is_done())
    
    protocol.eof_received()
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey sister')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read__zero():
    """
    Tests whether ``ReadProtocolBase.read`` works as intended.
    
    This function is a coroutine.
    
    Case: zero.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read(0))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read__exception():
    """
    Tests whether ``ReadProtocolBase.read`` works as intended.
    
    This function is a coroutine.
    
    Case: exception.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    protocol.set_exception(exception)
    
    task = Task(loop, protocol.read(0))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(type(exception)):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read__exact_amount():
    """
    Tests whether ``ReadProtocolBase.read`` works as intended.
    
    This function is a coroutine.
    
    Case: exact amount.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    task = Task(loop, protocol.read(5))
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey s')
    vampytest.assert_eq([*protocol._chunks], [b' sis', b'ter'])
    vampytest.assert_eq(protocol._offset, 2)

    task = Task(loop, protocol.read(5))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'ister')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read__exact_eof():
    """
    Tests whether ``ReadProtocolBase.read`` works as intended.
    
    This function is a coroutine.
    
    Case: ead exact eof.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read(12))
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    await skip_ready_cycle()
    vampytest.assert_false(task.is_done())
    
    protocol.eof_received()
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey sister')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_exactly__zero():
    """
    Tests whether ``ReadProtocolBase.read_exactly`` works as intended.
    
    This function is a coroutine.
    
    Case: zero.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_exactly(0))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_exactly__exception():
    """
    Tests whether ``ReadProtocolBase.read_exactly`` works as intended.
    
    This function is a coroutine.
    
    Case: exception.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    protocol.set_exception(exception)
    
    task = Task(loop, protocol.read_exactly(0))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(type(exception)):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_exactly__exact_amount():
    """
    Tests whether ``ReadProtocolBase.read_exactly`` works as intended.
    
    This function is a coroutine.
    
    Case: exact amount.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    task = Task(loop, protocol.read_exactly(5))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey s')
    
    vampytest.assert_eq([*protocol._chunks], [b' sis', b'ter'])
    vampytest.assert_eq(protocol._offset, 2)

    task = Task(loop, protocol.read_exactly(5))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'ister')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_exactly__eof():
    """
    Tests whether ``ReadProtocolBase.read_exactly`` works as intended.
    
    This function is a coroutine.
    
    Case: eof.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_exactly(12))
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    await skip_ready_cycle()
    vampytest.assert_false(task.is_done())
    
    protocol.eof_received()
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(ConnectionError):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_exactly__negative():
    """
    Tests whether ``ReadProtocolBase.read_exactly`` works as intended.
    
    This function is a coroutine.
    
    Case: negative.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_exactly(-3))
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(ValueError):
        task.get_result()


async def test__ReadProtocolBase__read_until__zero():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: zero length boundary.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_until(b''))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_until__exception():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: exception.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    protocol.set_exception(exception)
    
    task = Task(loop, protocol.read_until(0))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(type(exception)):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_until__first_chunk():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: all data in first chunk.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey sister sister')
    
    task = Task(loop, protocol.read_until(b'sis'))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey ')
    
    vampytest.assert_eq([*protocol._chunks], [b'hey sister sister'])
    vampytest.assert_eq(protocol._offset, 7)


async def test__ReadProtocolBase__read_until__repeat():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: repeat.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sist')
    protocol.data_received(b'er')
    protocol.data_received(b'sis')
    
    task = Task(loop, protocol.read_until(b'sis'))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey ')
    
    vampytest.assert_eq([*protocol._chunks], [b' sist', b'er', b'sis'])
    vampytest.assert_eq(protocol._offset, 4)

    task = Task(loop, protocol.read_until(b'sis'))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'ter')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_until__boundary_over_multiple_chunks():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: boundary over multiple lines.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    protocol.data_received(b'aya')
    protocol.data_received(b'ya')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    task = Task(loop, protocol.read_until(b'erayay'))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey sist')
    
    vampytest.assert_eq([*protocol._chunks], [b'ya', b' sis', b'ter'])
    vampytest.assert_eq(protocol._offset, 1)


async def test__ReadProtocolBase__read_until__boundary_in_two_chunks():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: boundary on two chunks.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'HTTP/1.1 500')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'hey: mister')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'\r\n')
    
    task = Task(loop, protocol.read_until(b'\r\n\r\n'))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'HTTP/1.1 500\r\nhey: mister')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_until__eof():
    """
    Tests whether ``ReadProtocolBase.read_until`` works as intended.
    
    This function is a coroutine.
    
    Case: eof.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_until(b'orin'))
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    await skip_ready_cycle()
    vampytest.assert_false(task.is_done())
    
    protocol.eof_received()
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(ConnectionError):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_once__exception():
    """
    Tests whether ``ReadProtocolBase.read_once`` works as intended.
    
    This function is a coroutine.
    
    Case: exception.
    """
    loop = get_event_loop()
    exception = ValueError()
    
    protocol = ReadProtocolBase(loop)
    protocol.set_exception(exception)
    
    task = Task(loop, protocol.read_once())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(type(exception)):
        task.get_result()
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_once__repeat():
    """
    Tests whether ``ReadProtocolBase.read_once`` works as intended.
    
    This function is a coroutine.
    
    Case: repeat.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    protocol.data_received(b'hey')
    protocol.data_received(b' sis')
    protocol.data_received(b'ter')
    
    task = Task(loop, protocol.read_once())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b'hey')
    
    vampytest.assert_eq([*protocol._chunks], [b' sis', b'ter'])
    vampytest.assert_eq(protocol._offset, 0)

    task = Task(loop, protocol.read_once())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    vampytest.assert_eq(task.get_result(), b' sis')
    
    vampytest.assert_eq([*protocol._chunks], [b'ter'])
    vampytest.assert_eq(protocol._offset, 0)


async def test__ReadProtocolBase__read_once__eof():
    """
    Tests whether ``ReadProtocolBase.read_once`` works as intended.
    
    This function is a coroutine.
    
    Case: eof.
    """
    loop = get_event_loop()
    
    protocol = ReadProtocolBase(loop)
    
    task = Task(loop, protocol.read_once())
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    
    protocol.eof_received()
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    
    vampytest.assert_eq(task.get_result(), b'')
    
    vampytest.assert_eq([*protocol._chunks], [])
    vampytest.assert_eq(protocol._offset, 0)
