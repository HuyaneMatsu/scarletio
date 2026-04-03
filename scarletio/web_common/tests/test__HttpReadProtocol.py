from collections import deque as Deque
from types import CoroutineType, GeneratorType

import vampytest

from ...core import AbstractTransportLayerBase, EventThread, PayloadStream, Task, get_event_loop, skip_ready_cycle
from ...utils import IgnoreCaseMultiValueDictionary

from ..compressors import ZLIB_COMPRESSOR, ZLIB_MAX_WBITS
from ..exceptions import PayloadError
from ..headers import CONTENT_ENCODING, CONTENT_LENGTH, TRANSFER_ENCODING
from ..helpers import HttpVersion
from ..http_message import RawRequestMessage, RawResponseMessage
from ..http_protocol import HttpReadProtocol
from ..web_socket_frame import WEB_SOCKET_OPERATION_BINARY, WebSocketFrame, apply_web_socket_mask


def _assert_fields_set(protocol):
    """
    Asserts whether every fields of the given protocol.
    
    Parameters
    ----------
    protocol : ``HttpReadProtocol``
        The protocol to test.
    """
    vampytest.assert_instance(protocol, HttpReadProtocol)
    vampytest.assert_instance(protocol._at_eof, bool)
    vampytest.assert_instance(protocol._chunks, Deque)
    vampytest.assert_instance(protocol._exception, BaseException, nullable = True)
    vampytest.assert_instance(protocol._offset, int)
    vampytest.assert_instance(protocol._paused, bool)
    vampytest.assert_instance(protocol._payload_reader, CoroutineType, GeneratorType, nullable = True)
    vampytest.assert_instance(protocol._payload_stream, PayloadStream, nullable = True)
    vampytest.assert_instance(protocol._loop, EventThread)
    vampytest.assert_instance(protocol._transport, AbstractTransportLayerBase, nullable = True)


async def test__HttpReadProtocol__new():
    """
    Tests whether ``HttpReadProtocol.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    _assert_fields_set(protocol)
    
    vampytest.assert_is(protocol._loop, loop)


async def test__HTTPReadProtocol__should_close__has_payload_stream():
    """
    Tests whether ``HttpReadProtocol.should_close`` works as intended.
    
    This function is a coroutine.
    
    Case: has payload stream.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    task = Task(loop, protocol.read(5))
    try:
        await skip_ready_cycle()
        
        output = protocol.should_close()
        vampytest.assert_instance(output, bool)
        vampytest.assert_eq(output, True)
    finally:
        task.cancel()


async def test__HTTPReadProtocol__should_close__has_exception():
    """
    Tests whether ``HttpReadProtocol.should_close`` works as intended.
    
    This function is a coroutine.
    
    Case: has exception.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.set_exception(ValueError())
    
    output = protocol.should_close()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__HTTPReadProtocol__should_close__data_left():
    """
    Tests whether ``HttpReadProtocol.should_close`` works as intended.
    
    This function is a coroutine.
    
    Case: data left.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.data_received(b'aya')
    
    output = protocol.should_close()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__HTTPReadProtocol__should_close__all_good():
    """
    Tests whether ``HttpReadProtocol.should_close`` works as intended.
    
    This function is a coroutine.
    
    Case: all good..
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    
    output = protocol.should_close()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


async def test__HTTPReadProtocol__read_http_response__success():
    """
    Tests whether ``HttpReadProtocol.read_http_response`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.data_received(b'HTTP/1.1 500')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'hey: mister')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'\r\n')
    
    task = Task(loop, protocol.read_http_response())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    output = task.get_result()
    
    vampytest.assert_eq(
        output,
        RawResponseMessage(
            HttpVersion(1, 1),
            500,
            None,
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
        ),
    )


async def test__HTTPReadProtocol__read_http_response__failure():
    """
    Tests whether ``HttpReadProtocol.read_http_response`` works as intended.
    
    This function is a coroutine.
    
    Case: failure (eof).
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.eof_received()
    
    task = Task(loop, protocol.read_http_response())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(PayloadError):
        task.get_result()


async def test__HTTPReadProtocol__read_http_request__success():
    """
    Tests whether ``HttpReadProtocol.read_http_request`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.data_received(b'GET /party HTTP/1.1')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'hey: mister')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'\r\n')
    
    task = Task(loop, protocol.read_http_request())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    output = task.get_result()
    
    vampytest.assert_eq(
        output,
        RawRequestMessage(
            HttpVersion(1, 1),
            'GET',
            '/party',
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
        ),
    )


async def test__HTTPReadProtocol__read_http_request__failure():
    """
    Tests whether ``HttpReadProtocol.read_http_request`` works as intended.
    
    This function is a coroutine.
    
    Case: failure (eof).
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.eof_received()
    
    task = Task(loop, protocol.read_http_request())
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(PayloadError):
        task.get_result()


async def test__HTTPReadProtocol__read_web_socket_frame__success__client_side():
    """
    Tests whether ``HttpReadProtocol.read_web_socket`` works as intended.
    
    This function is a coroutine.
    
    Case: success & client side.
    """
    loop = get_event_loop()
    data = b'hey mister'
    
    protocol = HttpReadProtocol(loop)
    
    web_socket_frame = WebSocketFrame(True, WEB_SOCKET_OPERATION_BINARY, data)
    
    protocol.data_received(web_socket_frame.head_0.to_bytes(1, 'big'))
    protocol.data_received(len(data).to_bytes(1, 'big'))
    protocol.data_received(data)
    
    task = Task(loop, protocol.read_web_socket_frame(True, 10000))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    output = task.get_result()
    
    vampytest.assert_eq(
        output,
        web_socket_frame,
    )


async def test__HTTPReadProtocol__read_web_socket_frame__success__server_side():
    """
    Tests whether ``HttpReadProtocol.read_web_socket`` works as intended.
    
    This function is a coroutine.
    
    Case: success & server side.
    """
    loop = get_event_loop()
    data = b'hey mister'
    mask = b'orin'
    
    protocol = HttpReadProtocol(loop)
    
    web_socket_frame = WebSocketFrame(True, WEB_SOCKET_OPERATION_BINARY, data)
    
    protocol.data_received(web_socket_frame.head_0.to_bytes(1, 'big'))
    protocol.data_received((len(data) | (1 << 7)).to_bytes(1, 'big'))
    protocol.data_received(mask)
    protocol.data_received(apply_web_socket_mask(mask, data))
    
    task = Task(loop, protocol.read_web_socket_frame(False, 10000))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    output = task.get_result()
    vampytest.assert_eq(
        output,
        web_socket_frame,
    )


async def test__HTTPReadProtocol__read_web_socket_frame__failure():
    """
    Tests whether ``HttpReadProtocol.read_web_socket`` works as intended.
    
    This function is a coroutine.
    
    Case: failure (eof).
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    protocol.eof_received()
    
    task = Task(loop, protocol.read_web_socket_frame(True, 10000))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    with vampytest.assert_raises(ConnectionError):
        task.get_result()


async def test__HTTPReadProtocol__get_payload_reader_task__read_chunked():
    """
    Tests whether ``HttpReadProtocol.get_payload_reader_task`` works as intended.
    
    This function is a coroutine.
    
    Case: reading chunked.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    
    # chunk 0
    protocol.data_received(b'5')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'hey m')
    protocol.data_received(b'\r\n')
    
    # chunk 1
    protocol.data_received(b'5')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'is')
    protocol.data_received(b'ter')
    protocol.data_received(b'\r\n')
    
    # mark end
    protocol.data_received(b'0')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'\r\n')
    
    
    message = RawResponseMessage(
        HttpVersion(1, 1),
        200,
        None,
        IgnoreCaseMultiValueDictionary([
            (TRANSFER_ENCODING, 'chunked'),
        ]),
    )
    
    
    payload_stream = protocol.set_payload_reader(protocol.get_payload_reader_task(message))
    iterator = payload_stream.__aiter__()
    
    # chunk 0
    task = Task(loop, iterator.asend(None))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    output = task.get_result()
    vampytest.assert_eq(output, b'hey m')
    
    # chunk 1 (part 0)
    task = Task(loop, iterator.asend(None))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    output = task.get_result()
    vampytest.assert_eq(output, b'is')
    
    # chunk 1 (part 0)
    task = Task(loop, iterator.asend(None))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    output = task.get_result()
    vampytest.assert_eq(output, b'ter')
    
    # end
    task = Task(loop, iterator.asend(None))
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    with vampytest.assert_raises(StopAsyncIteration):
        task.get_result()


async def test__HTTPReadProtocol__get_payload_reader_task__read_chunked_encoded():
    """
    Tests whether ``HttpReadProtocol.get_payload_reader_task`` works as intended.
    
    This function is a coroutine.
    
    Case: reading chunked & encoded.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    
    compressor = ZLIB_COMPRESSOR(wbits = 16 + ZLIB_MAX_WBITS)
    chunk_0_p_0 = compressor.compress(b'hey m')
    
    chunk_1_p_0 = compressor.compress(b'is')
    chunk_1_p_1 = compressor.compress(b'ter')
    chunk_1_p_2 = compressor.flush()
    
    # chunk 1
    protocol.data_received(format(len(chunk_0_p_0), 'x').encode())
    protocol.data_received(b'\r\n')
    protocol.data_received(chunk_0_p_0)
    protocol.data_received(b'\r\n')
    
    # chunk 2
    protocol.data_received(format(len(chunk_1_p_0) + len(chunk_1_p_1) + len(chunk_1_p_2), 'x').encode())
    protocol.data_received(b'\r\n')
    protocol.data_received(chunk_1_p_0)
    protocol.data_received(chunk_1_p_1)
    protocol.data_received(chunk_1_p_2)
    protocol.data_received(b'\r\n')
    
    # mark end
    protocol.data_received(b'0')
    protocol.data_received(b'\r\n')
    protocol.data_received(b'\r\n')
    
    
    message = RawResponseMessage(
        HttpVersion(1, 1),
        200,
        None,
        IgnoreCaseMultiValueDictionary([
            (CONTENT_ENCODING, 'gzip'),
            (TRANSFER_ENCODING, 'chunked'),
        ]),
    )
    
    payload_stream = protocol.set_payload_reader(protocol.get_payload_reader_task(message))
    iterator = payload_stream.__aiter__()
    
    collected = []
    
    while True:
        # chunk 1
        task = Task(loop, iterator.asend(None))
        await skip_ready_cycle()
        vampytest.assert_true(task.is_done())
        
        try:
            output = task.get_result()
        except StopAsyncIteration:
            break
        
        collected.append(output)
        continue
    
    vampytest.assert_eq(
        b''.join(collected),
        b'hey mister',
    )


async def test__HTTPReadProtocol__get_payload_reader_task__read_exactly_encoded():
    """
    Tests whether ``HttpReadProtocol.get_payload_reader_task`` works as intended.
    
    This function is a coroutine.
    
    Case: reading exactly & encoded.
    """
    loop = get_event_loop()
    
    protocol = HttpReadProtocol(loop)
    
    compressor = ZLIB_COMPRESSOR(wbits = 16 + ZLIB_MAX_WBITS)
    
    chunk_0_p_0 = compressor.compress(b'hey m')
    chunk_1_p_0 = compressor.compress(b'is')
    chunk_1_p_1 = compressor.compress(b'ter')
    chunk_1_p_2 = compressor.flush()
    
    protocol.data_received(chunk_0_p_0)
    protocol.data_received(chunk_1_p_0)
    protocol.data_received(chunk_1_p_1)
    protocol.data_received(chunk_1_p_2)
    
    content_length = len(chunk_0_p_0) + len(chunk_1_p_0) + len(chunk_1_p_1) + len(chunk_1_p_2)
    
    message = RawResponseMessage(
        HttpVersion(1, 1),
        200,
        None,
        IgnoreCaseMultiValueDictionary([
            (CONTENT_ENCODING, 'gzip'),
            (CONTENT_LENGTH, str(content_length)),
        ]),
    )
    
    payload_stream = protocol.set_payload_reader(protocol.get_payload_reader_task(message))
    iterator = payload_stream.__aiter__()
    
    collected = []
    
    while True:
        # chunk 1
        task = Task(loop, iterator.asend(None))
        await skip_ready_cycle()
        vampytest.assert_true(task.is_done())
        
        try:
            output = task.get_result()
        except StopAsyncIteration:
            break
        
        collected.append(output)
        continue
    
    vampytest.assert_eq(
        b''.join(collected),
        b'hey mister',
    )
