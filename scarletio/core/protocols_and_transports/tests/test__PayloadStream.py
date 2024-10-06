from collections import deque as Deque

import vampytest

from ....utils import copy_docs

from ...top_level import get_event_loop
from ...traps import Future, Task, skip_ready_cycle

from ..payload_stream import (
    PayloadStream, STREAM_FLAG_DONE_ABORTED, STREAM_FLAG_DONE_CANCELLED, STREAM_FLAG_DONE_EXCEPTION,
    STREAM_FLAG_DONE_SUCCESS, STREAM_FLAG_WAIT_CHUNK, STREAM_FLAG_WAIT_WHOLE,
)
from ..protocol import ReadProtocolBase


class TestProtocol(ReadProtocolBase):
    @copy_docs(ReadProtocolBase._pause_reading)
    def _pause_reading(self):
        self._paused = True
    
    
    @copy_docs(ReadProtocolBase._resume_reading)
    def _resume_reading(self):
        self._paused = False


def _assert_fields_set(payload_stream):
    """
    Tests whether every fields of the given payload stream are correctly set.
    
    Parameters
    ----------
    payload_stream : ``PayloadStream``
        The payload stream to check.
    """
    vampytest.assert_instance(payload_stream, PayloadStream)
    vampytest.assert_instance(payload_stream._chunks, Deque)
    vampytest.assert_instance(payload_stream._done_callbacks, list, nullable = True)
    vampytest.assert_instance(payload_stream._flags, int)
    vampytest.assert_instance(payload_stream._exception, BaseException, nullable = True)
    vampytest.assert_instance(payload_stream._protocol, ReadProtocolBase)
    vampytest.assert_instance(payload_stream._waiter, Future, nullable = True)


async def test__PayloadStream__new():
    """
    Tests whether ``PayloadStream.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    _assert_fields_set(payload_stream)
    
    vampytest.assert_eq(payload_stream._protocol, protocol)


async def test__PayloadStream__add_received_chunk__success():
    """
    Tests whether ``PayloadStream.add_received_chunk`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'aya'
    chunk_1 = b'ya'
    
    payload_stream = PayloadStream(protocol)
    
    output = payload_stream.add_received_chunk(chunk_0)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [chunk_0])
    
    output = payload_stream.add_received_chunk(chunk_1)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [chunk_0, chunk_1])


async def test__PayloadStream__add_received_chunk__failure():
    """
    Tests whether ``PayloadStream.add_received_chunk`` works as intended.
    
    This function is a coroutine.
    
    Case: failure.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_cancelled()
    
    output = payload_stream.add_received_chunk(chunk)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    vampytest.assert_eq([*payload_stream._chunks], [])
    

async def test__PayloadStream__add_received_chunk__waiter_set_wait_whole():
    """
    Tests whether ``PayloadStream.add_received_chunk`` works as intended.
    
    This function is a coroutine.
    
    Case: waiter set # wait whole.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream._flags |= STREAM_FLAG_WAIT_WHOLE
    waiter = Future(loop)
    payload_stream._waiter = waiter
    
    output = payload_stream.add_received_chunk(chunk)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [chunk])
    vampytest.assert_true(waiter.is_pending())
    vampytest.assert_is(payload_stream._waiter, waiter)


async def test__PayloadStream__add_received_chunk__waiter_set_wait_chunk():
    """
    Tests whether ``PayloadStream.add_received_chunk`` works as intended.
    
    This function is a coroutine.
    
    Case: waiter set # wait chunk.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream._flags |= STREAM_FLAG_WAIT_CHUNK
    waiter = Future(loop)
    payload_stream._waiter = waiter
    
    output = payload_stream.add_received_chunk(chunk)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [])
    vampytest.assert_true(waiter.is_done())
    vampytest.assert_is(payload_stream._waiter, None)
    

async def test__PayloadStream__get_total_size__empty():
    """
    Tests whether ``PayloadStream.get_total_size`` works as intended.
    
    This function is a coroutine.
    
    Case: Empty.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    output = payload_stream.get_total_size()
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__PayloadStream__get_total_size__non_empty():
    """
    Tests whether ``PayloadStream.get_total_size`` works as intended.
    
    This function is a coroutine.
    
    Case: Non-empty.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'aya'
    chunk_1 = b'ya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_received_chunk(chunk_0)
    payload_stream.add_received_chunk(chunk_1)
    
    output = payload_stream.get_total_size()
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 5)

    
async def test__PayloadStream__get_buffer_size__empty():
    """
    Tests whether ``PayloadStream.get_buffer_size`` works as intended.
    
    This function is a coroutine.
    
    Case: Empty.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    output = payload_stream.get_buffer_size()
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__PayloadStream__get_buffer_size__non_empty():
    """
    Tests whether ``PayloadStream.get_total_size`` works as intended.
    
    This function is a coroutine.
    
    Case: Non-empty.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'aya'
    chunk_1 = b'ya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_received_chunk(chunk_0)
    payload_stream.add_received_chunk(chunk_1)
    
    output = payload_stream.get_buffer_size()
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 5)


async def test__PayloadStream__get_buffer_size__non_empty_wait_all():
    """
    Tests whether ``PayloadStream.get_total_size`` works as intended.
    
    This function is a coroutine.
    
    Case: Non empty & wait all.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'aya'
    chunk_1 = b'ya'
    
    payload_stream = PayloadStream(protocol)
    payload_stream._flags |= STREAM_FLAG_WAIT_WHOLE
    payload_stream.add_received_chunk(chunk_0)
    payload_stream.add_received_chunk(chunk_1)
    
    output = payload_stream.get_buffer_size()
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__PayloadStream__set_done_success__success():
    """
    Tests whether ``PayloadStream.set_done_success`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    callback_called = False
    
    def callback(input_payload_stream):
        nonlocal callback_called
        callback_called = True
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_done_callback(callback)
    payload_stream.add_received_chunk(chunk)
    
    output = payload_stream.set_done_success()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [chunk])
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_SUCCESS)
    vampytest.assert_true(callback_called)


async def test__PayloadStream__set_done_success__failure():
    """
    Tests whether ``PayloadStream.set_done_success`` works as intended.
    
    This function is a coroutine.
    
    Case: failure.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_cancelled()
    
    output = payload_stream.set_done_success()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    vampytest.assert_false(payload_stream._flags & STREAM_FLAG_DONE_SUCCESS)
    

async def test__PayloadStream__set_done_success__waiter():
    """
    Tests whether ``PayloadStream.set_done_success`` works as intended.
    
    This function is a coroutine.
    
    Case: has waiter.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    waiter = Future(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream._waiter = waiter
    
    output = payload_stream.set_done_success()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_SUCCESS)
    vampytest.assert_true(waiter.is_done())
    vampytest.assert_is(payload_stream._waiter, None)


async def test__PayloadStream__set_done_cancelled__success():
    """
    Tests whether ``PayloadStream.set_done_cancelled`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    callback_called = False
    
    def callback(input_payload_stream):
        nonlocal callback_called
        callback_called = True
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_done_callback(callback)
    payload_stream.add_received_chunk(chunk)
    
    output = payload_stream.set_done_cancelled()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [])
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_CANCELLED)
    vampytest.assert_true(callback_called)


async def test__PayloadStream__set_done_cancelled__failure():
    """
    Tests whether ``PayloadStream.set_done_cancelled`` works as intended.
    
    This function is a coroutine.
    
    Case: failure.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_success()
    
    output = payload_stream.set_done_cancelled()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    vampytest.assert_false(payload_stream._flags & STREAM_FLAG_DONE_CANCELLED)
    

async def test__PayloadStream__set_done_cancelled__waiter():
    """
    Tests whether ``PayloadStream.set_done_cancelled`` works as intended.
    
    This function is a coroutine.
    
    Case: has waiter.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    waiter = Future(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream._waiter = waiter
    
    output = payload_stream.set_done_cancelled()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_CANCELLED)
    vampytest.assert_true(waiter.is_done())
    vampytest.assert_is(payload_stream._waiter, None)
    
    with vampytest.assert_raises(ConnectionError):
        waiter.get_result()


async def test__PayloadStream__set_done_exception__success():
    """
    Tests whether ``PayloadStream.set_done_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    exception = ValueError()
    callback_called = False
    
    def callback(input_payload_stream):
        nonlocal callback_called
        callback_called = True
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_received_chunk(chunk)
    payload_stream.add_done_callback(callback)
    
    output = payload_stream.set_done_exception(exception)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [])
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_EXCEPTION)
    vampytest.assert_is(payload_stream._exception, exception)
    vampytest.assert_true(callback_called)


async def test__PayloadStream__set_done_exception__failure():
    """
    Tests whether ``PayloadStream.set_done_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: failure.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    exception = ValueError()
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_success()
    
    output = payload_stream.set_done_exception(exception)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    vampytest.assert_false(payload_stream._flags & STREAM_FLAG_DONE_EXCEPTION)
    vampytest.assert_is(payload_stream._exception, None)
    

async def test__PayloadStream__set_done_exception__waiter():
    """
    Tests whether ``PayloadStream.set_done_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: has waiter.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    waiter = Future(loop)
    exception = ValueError()
    
    payload_stream = PayloadStream(protocol)
    payload_stream._waiter = waiter
    
    output = payload_stream.set_done_exception(exception)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_EXCEPTION)
    vampytest.assert_true(waiter.is_done())
    vampytest.assert_is(payload_stream._waiter, None)
    vampytest.assert_is(payload_stream._exception, exception)
    
    with vampytest.assert_raises(type(exception)):
        waiter.get_result()


async def test__PayloadStream__check_raise_flags__no_raise():
    """
    Tests whether ``PayloadStream._check_raise_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: no raise.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream._check_raise_flags()


async def test__PayloadStream__check_raise_flags__cancelled():
    """
    Tests whether ``PayloadStream._check_raise_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: cancelled.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_cancelled()
    
    with vampytest.assert_raises(ConnectionError):
        payload_stream._check_raise_flags()


async def test__PayloadStream__check_raise_flags__exception():
    """
    Tests whether ``PayloadStream._check_raise_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: exception.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    exception = ValueError()
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_exception(exception)
    
    with vampytest.assert_raises(type(exception)):
        payload_stream._check_raise_flags()


async def test__PayloadStream__check_wait_flags__new():
    """
    Tests whether ``PayloadStream._check_wait_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: new.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream._check_wait_flags(STREAM_FLAG_WAIT_WHOLE)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_WAIT_WHOLE)


async def test__PayloadStream__check_wait_flags__same():
    """
    Tests whether ``PayloadStream._check_wait_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: same.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream._check_wait_flags(STREAM_FLAG_WAIT_WHOLE)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_WAIT_WHOLE)
    
    payload_stream._check_wait_flags(STREAM_FLAG_WAIT_WHOLE)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_WAIT_WHOLE)


async def test__PayloadStream__check_wait_flags__different():
    """
    Tests whether ``PayloadStream._check_wait_flags`` works as intended.
    
    This function is a coroutine.
    
    Case: different.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream._check_wait_flags(STREAM_FLAG_WAIT_WHOLE)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_WAIT_WHOLE)
    
    with vampytest.assert_raises(RuntimeError):
        payload_stream._check_wait_flags(STREAM_FLAG_WAIT_CHUNK)
    
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_WAIT_WHOLE)
    vampytest.assert_false(payload_stream._flags & STREAM_FLAG_WAIT_CHUNK)


async def test__PayloadStream__await():
    """
    Tests whether ``PayloadStream.__await__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'hey'
    chunk_1 = b'aya'
    chunk_2 = b'ya'
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream.add_received_chunk(chunk_0)
    task = Task(loop, payload_stream.__await__())
    payload_stream.add_received_chunk(chunk_1)
    payload_stream.add_received_chunk(chunk_2)
    
    await skip_ready_cycle()
    vampytest.assert_false(task.is_done())
    
    payload_stream.set_done_success()
    
    await skip_ready_cycle()
    vampytest.assert_true(task.is_done())
    
    result = task.get_result()
    vampytest.assert_instance(result, bytes)
    vampytest.assert_eq(result, b'heyayaya')
    vampytest.assert_eq([*payload_stream._chunks], [])


async def test__PayloadStream__await__abort():
    """
    Tests whether ``PayloadStream.__await__`` works as intended.
    
    This function is a coroutine.
    
    Case: awaiting aborted.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    task = Task(loop, payload_stream.__await__())
    
    await skip_ready_cycle()
    task.cancel()
    await skip_ready_cycle()
    
    vampytest.assert_true(payload_stream.is_aborted())


async def test__PayloadStream__aiter():
    """
    Tests whether ``PayloadStream.__await__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk_0 = b'hey'
    chunk_1 = b'aya'
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream.add_received_chunk(chunk_0)
    
    coroutine_iterator = payload_stream.__aiter__()
    
    try:
        task = Task(loop, coroutine_iterator.__anext__())
        await skip_ready_cycle()
        vampytest.assert_true(task.is_done())
        output = task.get_result()
        vampytest.assert_instance(output, bytes, memoryview)
        vampytest.assert_eq(output, chunk_0)
        
        task = Task(loop, coroutine_iterator.__anext__())
        await skip_ready_cycle()
        vampytest.assert_false(task.is_done())
        
        payload_stream.add_received_chunk(chunk_1)
        
        await skip_ready_cycle()
        output = task.get_result()
        vampytest.assert_instance(output, bytes, memoryview)
        vampytest.assert_eq(output, chunk_1)
        
        task = Task(loop, coroutine_iterator.__anext__())
        await skip_ready_cycle()
        vampytest.assert_false(task.is_done())
        
        payload_stream.set_done_success()
        
        await skip_ready_cycle()
        vampytest.assert_true(task.is_done())
        with vampytest.assert_raises(StopAsyncIteration):
            task.get_result()
    
    finally:
        coroutine_iterator.aclose().close()


async def test__PayloadStream__aiter__abort():
    """
    Tests whether ``PayloadStream.__aiter__`` works as intended.
    
    This function is a coroutine.
    
    Case: Iteration aborted.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    coroutine_iterator = payload_stream.__aiter__()
    
    try:
        task = Task(loop, coroutine_iterator.__anext__())
        
        await skip_ready_cycle()
        task.cancel()
        await skip_ready_cycle()
        
        vampytest.assert_true(payload_stream.is_aborted())
    
    finally:
        coroutine_iterator.aclose().close()


async def test__PayloadStream__add_done_callback__pending():
    """
    Tests whether ``PayloadStream.add_done_callback`` works as intended.
    
    This function is a coroutine.
    
    Case: pending.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    def callback(input_payload_stream):
        return None
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_done_callback(callback)
    
    vampytest.assert_eq(payload_stream._done_callbacks, [callback])


async def test__PayloadStream__add_done_callback__done():
    """
    Tests whether ``PayloadStream.add_done_callback`` works as intended.
    
    This function is a coroutine.
    
    Case: done.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    callback_called = False
    
    def callback(input_payload_stream):
        nonlocal callback_called
        callback_called = True
        return None
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_success()
    
    payload_stream.add_done_callback(callback)
    
    vampytest.assert_eq(payload_stream._done_callbacks, None)
    vampytest.assert_true(callback_called)


async def test__PayloadStream__run_done_callbacks():
    """
    Tests whether ``PayloadStream.add_done_callback`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    callbacks_run = 0
    
    def callback(input_payload_stream):
        nonlocal callbacks_run
        callbacks_run += 1
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_done_callback(callback)
    payload_stream.add_done_callback(callback)
    
    payload_stream._run_done_callbacks()
    
    vampytest.assert_eq(callbacks_run, 2)
    vampytest.assert_eq(payload_stream._done_callbacks, None)


async def test__PayloadStream__run_done_callback():
    """
    Tests whether ``PayloadStream._run_done_callback`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    callbacks_run = 0
    
    def callback(input_payload_stream):
        nonlocal callbacks_run
        callbacks_run += 1
    
    payload_stream = PayloadStream(protocol)
    
    payload_stream._run_done_callback(callback)
    
    vampytest.assert_eq(callbacks_run, 1)


async def test__PayloadStream__abort__success():
    """
    Tests whether ``PayloadStream._abort`` works as intended.
    
    This function is a coroutine.
    
    Case: success.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    chunk = b'aya'
    callback_called = False
    
    def callback(input_payload_stream):
        nonlocal callback_called
        callback_called = True
    
    payload_stream = PayloadStream(protocol)
    payload_stream.add_done_callback(callback)
    payload_stream.add_received_chunk(chunk)
    
    output = payload_stream._abort()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_eq([*payload_stream._chunks], [chunk])
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_ABORTED)
    vampytest.assert_true(callback_called)


async def test__PayloadStream__abort__failure():
    """
    Tests whether ``PayloadStream._abort`` works as intended.
    
    This function is a coroutine.
    
    Case: failure.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream.set_done_cancelled()
    
    output = payload_stream._abort()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    vampytest.assert_false(payload_stream._flags & STREAM_FLAG_DONE_ABORTED)
    

async def test__PayloadStream__abort__waiter():
    """
    Tests whether ``PayloadStream._abort`` works as intended.
    
    This function is a coroutine.
    
    Case: has waiter.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    waiter = Future(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream._waiter = waiter
    
    output = payload_stream._abort()
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
    vampytest.assert_true(payload_stream._flags & STREAM_FLAG_DONE_ABORTED)
    vampytest.assert_true(waiter.is_done())
    vampytest.assert_is(payload_stream._waiter, None)
    
    with vampytest.assert_raises(ConnectionError):
        waiter.get_result()


async def test__PayloadStream__is_aborted__true():
    """
    Tests whether ``PayloadStream.is_aborted`` works as intended.
    
    This function is a coroutine.
    
    Case: True.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    payload_stream._abort()
    
    output = payload_stream.is_aborted()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


async def test__PayloadStream__is_aborted__false():
    """
    Tests whether ``PayloadStream.is_aborted`` works as intended.
    
    This function is a coroutine.
    
    Case: False.
    """
    loop = get_event_loop()
    protocol = TestProtocol(loop)
    
    payload_stream = PayloadStream(protocol)
    
    output = payload_stream.is_aborted()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
