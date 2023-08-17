import vampytest

from ....core import EventThread, Future, get_event_loop, skip_poll_cycle, skip_ready_cycle, sleep
from ....ext.asyncio import asyncio


# This file is a rewrite of `asyncio.gather` tests

async def test__gather__shield_gather():
    # Arrange
    loop = get_event_loop()
    
    child_0 = Future(loop)
    child_1 = Future(loop)
    parent = asyncio.gather(child_0, child_1)
    
    outer = asyncio.shield(parent)
    
    # Act
    await skip_ready_cycle()
    outer.cancel()
    await skip_ready_cycle()
    vampytest.assert_true(outer.cancelled())
    
    # Act
    child_0.set_result(1)
    child_1.set_result(2)
    
    await skip_poll_cycle()
    
    # Assert
    vampytest.assert_eq({*parent.result()}, {1, 2})


async def test__gather__shield():
    # Arrange
    loop = get_event_loop()
    child_0 = Future(loop)
    child_1 = Future(loop)
    
    inner_0 = asyncio.shield(child_0)
    inner_1 = asyncio.shield(child_1)
    waiter = asyncio.gather(inner_0, inner_1)
    
    try:
        # Act
        await skip_ready_cycle()
        waiter.cancel()
        
        # This should cancel inner_0 and inner_1 but not child_0 and child_1.
        await skip_ready_cycle()
        
        # Assert
        vampytest.assert_true(waiter.cancelled())
        vampytest.assert_true(inner_0.cancelled())
        vampytest.assert_true(inner_1.cancelled())
    
    finally:
        child_0.cancel()
        child_1.cancel()


async def test__gather__cancel__0():
    # Ensure that a gathering future refuses to be cancelled once all children are done
    # Arrange
    loop = get_event_loop()
    future = Future(loop)
    
    async def create():
        # The indirection future -> child_coro is needed since otherwise the
        # gathering task is done at the same time as the child future
        async def child_coro():
            return await future
        
        return await asyncio.gather(child_coro())
    

    cancel_result = None
    def cancelling_callback(_):
        nonlocal cancel_result
        cancel_result = gather_task.cancel()
    
    # Act
    gather_task = loop.create_task(create())
    gather_task.add_done_callback(cancelling_callback)
    
    future.set_result(42) # calls `cancelling_callback`
    
    # At this point the task should be completed.
    await skip_ready_cycle()
    await skip_ready_cycle()
    await skip_poll_cycle()
    
    # Assert
    vampytest.assert_eq(cancel_result, False)
    vampytest.assert_false(gather_task.cancelled())
    vampytest.assert_eq(gather_task.result(), [42])
    

async def test__gather__cancel__2():
    # Arrange
    loop = get_event_loop()
    
    async def test():
        time = 0
        while True:
            time += 0.01
            await asyncio.gather(asyncio.sleep(0.01), return_exceptions = True)
            if time > 0.1:
                return
    
    # Act & Assert
    with vampytest.assert_raises(asyncio.CancelledError):
        task = loop.create_task(test())
        await asyncio.sleep(0.03)
        task.cancel()
        await task


async def _test__gather__check_success(return_exceptions):
    # Arrange
    loop = get_event_loop()
    a = loop.create_future()
    b = loop.create_future()
    c = loop.create_future()
    
    callback_called_with = set()
    
    def test_callback(future):
        nonlocal callback_called_with
        callback_called_with.add(future)
    
    waiter = None
    
    try:
        # Act
        waiter = asyncio.gather(a, b, c, return_exceptions = return_exceptions)
        waiter.add_done_callback(test_callback)
        
        b.set_result(1)
        a.set_result(2)
        
        await skip_ready_cycle()
        
        # Assert
        vampytest.assert_false(callback_called_with)
        vampytest.assert_false(waiter.done())
        
        # Act
        c.set_result(3)
        
        await skip_poll_cycle()
        
        # Assert
        vampytest.assert_in(waiter, callback_called_with)
        vampytest.assert_eq({*waiter.result()}, {1, 2, 3})
    
    finally:
        a.cancel()
        b.cancel()
        c.cancel()
        
        if (waiter is not None):
            waiter.cancel()


async def test__gather__success():
    await _test__gather__check_success(return_exceptions = False)


async def test__gather__result_exception_success():
    await _test__gather__check_success(return_exceptions = True)


async def test__gather__one_exception():
    # Arrange
    loop = get_event_loop()
    a = loop.create_future()
    b = loop.create_future()
    c = loop.create_future()
    
    callback_called_with = set()
    
    def test_callback(future):
        nonlocal callback_called_with
        callback_called_with.add(future)
    
    try:
        # Act
        waiter = asyncio.gather(a, b, c)
        
        waiter.add_done_callback(test_callback)
        exc = ZeroDivisionError()
        a.set_result(1)
        b.set_exception(exc)
        
        await skip_poll_cycle()
        
        # Assert
        vampytest.assert_true(waiter.done())
        vampytest.assert_in(waiter, callback_called_with)
        vampytest.assert_is(waiter.exception(), exc)
    
    finally:
        a.cancel()
        b.cancel()
        c.cancel()


async def test__gather__return_exceptions():
    # Arrange
    loop = get_event_loop()
    a = loop.create_future()
    b = loop.create_future()
    c = loop.create_future()
    d = loop.create_future()
    
    
    callback_called_with = set()
    
    def test_callback(future):
        nonlocal callback_called_with
        callback_called_with.add(future)
    
    waiter = None
    
    try:
        # Act
        waiter = asyncio.gather(a, b, c, d, return_exceptions = True)
        
        waiter.add_done_callback(test_callback)
        exception_0 = ZeroDivisionError()
        exception_1 = RuntimeError()
        b.set_result(1)
        c.set_exception(exception_0)
        a.set_result(3)
        
        await skip_poll_cycle()
        
        # Assert
        vampytest.assert_false(waiter.done())
        
        # Act
        d.set_exception(exception_1)
        
        await skip_poll_cycle()
        
        # Assert
        vampytest.assert_true(waiter.done())
        vampytest.assert_in(waiter, callback_called_with)
        vampytest.assert_eq({*waiter.result()}, {3, 1, exception_0, exception_1})
    
    finally:
        a.cancel()
        b.cancel()
        c.cancel()
        d.cancel()
        
        if (waiter is not None):
            waiter.cancel()


def test__gather__empty_sequence_without_loop():
    with vampytest.assert_raises(RuntimeError):
        try:
            asyncio.gather()
        except RuntimeError as err:
            vampytest.assert_in('no current event loop', repr(err))
            raise


async def test__gather__empty_sequence_use_running_loop():
    # Arrange
    loop = get_event_loop()
    
    waiter = None
    
    try:
        # Act
        waiter = asyncio.gather()
        
        # Assert
        vampytest.assert_instance(waiter, Future)
        vampytest.assert_is(waiter._loop, loop)
        
        vampytest.assert_true(waiter.done())
        vampytest.assert_eq(waiter.result(), [])
    finally:
        if (waiter is not None):
            waiter.cancel()


async def test__gather__empty_sequence_use_global_loop():
    # Deprecated in 3.10, un-deprecated in 3.12
    # Same as the other one in scarletio
    await test__gather__empty_sequence_use_running_loop()


def test__gather__heterogenous_futures():
    # Arrange
    loop_0 = EventThread()
    loop_1 = EventThread()
    
    future_0 = loop_0.create_future()
    future_1 = loop_1.create_future()
    
    # Act & Assert
    try:
        with vampytest.assert_raises(ValueError):
            asyncio.gather(future_0, future_1)
    
    finally:
        future_0.cancel()
        future_1.cancel()
        
        loop_0.stop()
        loop_1.stop()


async def test__gather__homogenous_futures():
    # Arrange
    loop = get_event_loop()
    other_loop = EventThread()
    
    a = other_loop.create_future()
    b = other_loop.create_future()
    c = other_loop.create_future()
    
    # Act & Assert
    try:
        future = asyncio.gather(a, b, c)
        vampytest.assert_is(future._loop, other_loop)
        
        await sleep(0.0001, loop = other_loop).async_wrap(loop)
        
        vampytest.assert_false(future.done())
        future = asyncio.gather(a, b, c)
        vampytest.assert_is(future._loop, other_loop)
        
        await sleep(0.0001, loop = other_loop).async_wrap(loop)
        
        vampytest.assert_false(future.done())
    finally:
        other_loop.stop()


async def test__gather__one_cancellation():
    # Arrange
    loop = get_event_loop()
    a = loop.create_future()
    b = loop.create_future()
    c = loop.create_future()
    
    callback_called_with = set()
    
    def test_callback(future):
        nonlocal callback_called_with
        callback_called_with.add(future)
    
    waiter = None
    try:
        waiter = asyncio.gather(a, b, c)
        waiter.add_done_callback(test_callback)
        a.set_result(1)
        b.cancel()
        
        await skip_poll_cycle()
        
        vampytest.assert_true(waiter.done())
        vampytest.assert_in(waiter, callback_called_with)
        vampytest.assert_false(waiter.cancelled())
        vampytest.assert_instance(waiter.exception(), asyncio.CancelledError)
    
    finally:
        a.cancel()
        b.cancel()
        c.cancel()
        
        if (waiter is not None):
            waiter.cancel()


async def test__gather__result_exception_one_cancellation():
    # Arrange
    loop = get_event_loop()
    a = loop.create_future()
    b = loop.create_future()
    c = loop.create_future()
    d = loop.create_future()
    e = loop.create_future()
    f = loop.create_future()
    
    callback_called_with = set()
    
    def test_callback(future):
        nonlocal callback_called_with
        callback_called_with.add(future)
    
    waiter = None
    
    try:
        # Act
        waiter = asyncio.gather(a, b, c, d, e, f, return_exceptions = True)
        
        waiter.add_done_callback(test_callback)
        
        a.set_result(1)
        zde = ZeroDivisionError()
        b.set_exception(zde)
        c.cancel()
        
        # We assert some
        vampytest.assert_false(waiter.done())
        
        # Act once again
        d.set_result(3)
        e.cancel()
        raised_exception = RuntimeError()
        f.set_exception(raised_exception)
        
        result = await waiter
        
        # Assert
        only_cancellation = set()
        only_not_cancellation = set()
        for value in result:
            if isinstance(value, asyncio.CancelledError):
                only_cancellation.add(value)
            else:
                only_not_cancellation.add(value)
        
        vampytest.assert_eq(len(only_cancellation), 2)
        vampytest.assert_eq(only_not_cancellation, {1, zde, 3, raised_exception})
        
        await skip_ready_cycle()
        
        vampytest.assert_in(waiter, callback_called_with)
    
    finally:
        a.cancel()
        b.cancel()
        c.cancel()
        d.cancel()
        e.cancel()
        f.cancel()
        
        if (waiter is not None):
            waiter.cancel()


def test__gather__without_loop():
    # Arrange
    async def coro():
        return 'abc'
    
    a = coro()
    b = coro()
    
    try:
        # Act & Assert
        with vampytest.assert_raises(RuntimeError):
            try:
                asyncio.gather(a, b)
            except RuntimeError as err:
                vampytest.assert_in('no current event loop', repr(err))
                raise
    
    finally:
        a.close()
        b.close()


async def test__gather__use_running_loop():
    # Both is the same in scarletio, lol
    await test__gather__use_global_loop()


async def test__gather__use_global_loop():
    # Deprecated in 3.10, un-deprecated in 3.12
    # Arrange
    loop = get_event_loop()
    async def coro():
        return 'abc'
    
    a = coro()
    b = coro()
    waiter = asyncio.gather(a, b)
    
    # Assert
    try:
        vampytest.assert_is(waiter._loop, loop)
    finally:
        a.close()
        b.close()
        waiter.cancel()


async def test__gather__duplicate_coroutines():
    # Arrange
    async def coro(s):
        return s
    
    a = coro('abc')
    b = coro('def')
    
    waiter = None
    
    try:
        # Act
        waiter = asyncio.gather(a, a, b, a)
        
        await waiter
        
        # Assert
        vampytest.assert_eq({*waiter.result()}, {'abc', 'def'})
    
    finally:
        a.close()
        b.close()
        if (waiter is not None):
            waiter.cancel()


async def test__gather__cancellation_broadcast():
    # Cancelling outer() cancels all children.
    # Arrange
    loop = get_event_loop()
    
    proof = 0
    async def inner():
        nonlocal proof
        future = loop.create_future()
        
        try:
            await future
        finally:
            future.cancel()
        
        proof += 1
    
    child_0 = asyncio.ensure_future(inner(), loop = loop)
    child_1 = asyncio.ensure_future(inner(), loop = loop)
    
    # Act
    waiter = asyncio.gather(child_0, child_1)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter.cancel())
    
    # Assert
    with vampytest.assert_raises(asyncio.CancelledError):
        await waiter
    
    await skip_poll_cycle()
    vampytest.assert_false(waiter.cancel())
    vampytest.assert_true(waiter.cancelled())
    vampytest.assert_true(child_0.cancelled())
    vampytest.assert_true(child_1.cancelled())
    await skip_ready_cycle()
    vampytest.assert_eq(proof, 0)


async def test__gather__exception_marking():
    # Test for the first line marked "Mark exception retrieved."
    # Arrange
    loop = get_event_loop()
    
    async def inner(f):
        await f
        raise RuntimeError('should not be ignored')
    
    a = loop.create_future()
    b = loop.create_future()
    
    # Act
    waiter = asyncio.gather(inner(a), inner(b))
    await skip_ready_cycle()
    a.set_result(None)
    await skip_ready_cycle()
    b.set_result(None)
    await skip_poll_cycle()
    
    # Assert
    vampytest.assert_instance(waiter.exception(), RuntimeError)
