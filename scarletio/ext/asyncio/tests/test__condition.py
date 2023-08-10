import vampytest

from ....core import CancelledError, Lock, create_event_loop, get_event_loop, skip_ready_cycle
from ....ext.asyncio import asyncio


async def test__Condition__wait():
    loop = get_event_loop()
    condition = asyncio.Condition()
    result = []
    
    
    async def coroutine_0(result):
        await condition.acquire()
        if await condition.wait():
            result.append(1)
    
        return True
    
    
    async def coroutine_1(result):
        await condition.acquire()
        if await condition.wait():
            result.append(2)
        
        return True
    
    
    async def coroutine_2(result):
        await condition.acquire()
        if await condition.wait():
            result.append(3)
        
        return True
    
    
    task_0 = loop.create_task(coroutine_0(result))
    task_1 = loop.create_task(coroutine_1(result))
    task_3 = loop.create_task(coroutine_2(result))
    
    await skip_ready_cycle()
    vampytest.assert_eq([], result)
    vampytest.assert_false(condition.locked())

    vampytest.assert_true(await condition.acquire())
    condition.notify()
    await skip_ready_cycle()
    vampytest.assert_eq([], result)
    vampytest.assert_true(condition.locked())

    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1], result)
    vampytest.assert_true(condition.locked())

    condition.notify(2)
    await skip_ready_cycle()
    vampytest.assert_eq([1], result)
    vampytest.assert_true(condition.locked())

    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1, 2], result)
    vampytest.assert_true(condition.locked())

    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1, 2, 3], result)
    vampytest.assert_true(condition.locked())

    vampytest.assert_true(task_0.done())
    vampytest.assert_true(task_0.result())
    vampytest.assert_true(task_1.done())
    vampytest.assert_true(task_1.result())
    vampytest.assert_true(task_3.done())
    vampytest.assert_true(task_3.result())


async def test__Condition__wait__cancel():
    loop = get_event_loop()
    condition = asyncio.Condition()
    await condition.acquire()

    wait_task = loop.create_task(condition.wait())
    
    loop.call_soon(wait_task.cancel)
    with vampytest.assert_raises(CancelledError):
        await wait_task
    
    vampytest.assert_false(condition._waiters)
    vampytest.assert_true(condition.locked())


async def test__Condition__wait__cancel_contested():
    loop = get_event_loop()
    condition = asyncio.Condition()
    
    await condition.acquire()
    vampytest.assert_true(condition.locked())
    
    wait_task = loop.create_task(condition.wait())
    await skip_ready_cycle()
    vampytest.assert_false(condition.locked())
    
    # Notify, but contest the lock before cancelling
    await condition.acquire()
    
    vampytest.assert_true(condition.locked())
    condition.notify()
    loop.call_soon(condition.release)
    loop.call_soon(wait_task.cancel)
    
    try:
        await wait_task
    except CancelledError:
        # Should not happen, since no cancellation points
        pass
    
    vampytest.assert_true(condition.locked())


async def test__Condition__wait_cancel_after_notify():
    loop = get_event_loop()
    waited = False

    condition = asyncio.Condition()

    async def wait_on_condition():
        nonlocal waited
        async with condition:
            # Make sure this area was reached
            waited = True  
            await condition.wait()

    waiter = loop.create_task(wait_on_condition())
    
    # Start waiting
    await skip_ready_cycle()
    
    async with condition:
        condition.notify()
        # Get to acquire()
        await skip_ready_cycle()
        waiter.cancel()
        # Activate cancellation
        await skip_ready_cycle()
    
    # Cancellation should occur
    vampytest.assert_true(waiter.cancelled())
    vampytest.assert_true(waited)


async def test__Condition__wait_not_acquired():
    condition = asyncio.Condition()
    with vampytest.assert_raises(RuntimeError):
        await condition.wait()


async def test__Condition__wait_for():
    loop = get_event_loop()
    condition = asyncio.Condition()
    return_from_predicate = False

    def predicate():
        nonlocal return_from_predicate
        return return_from_predicate

    result = []

    async def coroutine_0(result):
        await condition.acquire()
        if await condition.wait_for(predicate):
            result.append(1)
            condition.release()
        return True

    task = loop.create_task(coroutine_0(result))

    await skip_ready_cycle()
    vampytest.assert_eq([], result)

    await condition.acquire()
    condition.notify()
    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([], result)

    return_from_predicate = True
    await condition.acquire()
    condition.notify()
    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1], result)

    vampytest.assert_true(task.done())
    vampytest.assert_true(task.result())


async def test__Condition__wait_for__not_acquired():
    condition = asyncio.Condition()

    # predicate can return true immediately
    result = await condition.wait_for(lambda: [1, 2, 3])
    vampytest.assert_eq([1, 2, 3], result)

    with vampytest.assert_raises(RuntimeError):
        await condition.wait_for(lambda: False)


async def test__Condition__notify():
    loop = get_event_loop()
    condition = asyncio.Condition()
    result = []

    async def coroutine_0(result):
        await condition.acquire()
        if await condition.wait():
            result.append(1)
            condition.release()
        return True

    async def coroutine_1(result):
        await condition.acquire()
        if await condition.wait():
            result.append(2)
            condition.release()
        return True

    async def coroutine_2(result):
        await condition.acquire()
        if await condition.wait():
            result.append(3)
            condition.release()
        return True
    
    task_0 = loop.create_task(coroutine_0(result))
    task_1 = loop.create_task(coroutine_1(result))
    task_3 = loop.create_task(coroutine_2(result))

    await skip_ready_cycle()
    vampytest.assert_eq([], result)

    await condition.acquire()
    condition.notify(1)
    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1], result)

    await condition.acquire()
    condition.notify(1)
    condition.notify(2048)
    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1, 2, 3], result)

    vampytest.assert_true(task_0.done())
    vampytest.assert_true(task_0.result())
    vampytest.assert_true(task_1.done())
    vampytest.assert_true(task_1.result())
    vampytest.assert_true(task_3.done())
    vampytest.assert_true(task_3.result())


async def test__Condition__notify_all():
    loop = get_event_loop()
    condition = asyncio.Condition()

    result = []

    async def coroutine_0(result):
        await condition.acquire()
        if await condition.wait():
            result.append(1)
            condition.release()
        return True

    async def coroutine_1(result):
        await condition.acquire()
        if await condition.wait():
            result.append(2)
            condition.release()
        return True

    task_0 = loop.create_task(coroutine_0(result))
    task_1 = loop.create_task(coroutine_1(result))

    await skip_ready_cycle()
    vampytest.assert_eq([], result)

    await condition.acquire()
    condition.notify_all()
    condition.release()
    await skip_ready_cycle()
    vampytest.assert_eq([1, 2], result)

    vampytest.assert_true(task_0.done())
    vampytest.assert_true(task_0.result())
    vampytest.assert_true(task_1.done())
    vampytest.assert_true(task_1.result())


async def test__Condition__notify__not_acquired():
    condition = asyncio.Condition()
    with vampytest.assert_raises(RuntimeError):
        condition.notify()


async def test__Condition__notify_all__not_acquired():
    condition = asyncio.Condition()
    with vampytest.assert_raises(RuntimeError):
        condition.notify_all()


async def test__Condition__repr():
    loop = get_event_loop()
    condition = asyncio.Condition()
    vampytest.assert_true('unlocked' in repr(condition))

    await condition.acquire()
    vampytest.assert_true('locked' in repr(condition))

    condition._waiters.append(loop.create_future())
    vampytest.assert_true('waiters: 1' in repr(condition))

    condition._waiters.append(loop.create_future())
    vampytest.assert_true('waiters: 2' in repr(condition))


async def test__Condition__context_manager():
    condition = asyncio.Condition()
    vampytest.assert_false(condition.locked())
    
    async with condition:
        vampytest.assert_true(condition.locked())
    
    vampytest.assert_false(condition.locked())


async def _test__Condition__explicit_lock(lock = None, condition = None):
    loop = get_event_loop()
    
    if lock is None:
        lock = Lock(loop)
    
    if condition is None:
        condition = asyncio.Condition(lock)
    
    vampytest.assert_is(condition._lock, lock)
    vampytest.assert_false(lock.locked())
    vampytest.assert_false(condition.locked())
    
    async with condition:
        vampytest.assert_true(lock.locked())
        vampytest.assert_true(condition.locked())
    
    vampytest.assert_false(lock.locked())
    vampytest.assert_false(condition.locked())
    
    async with lock:
        vampytest.assert_true(lock.locked())
        vampytest.assert_true(condition.locked())
    
    vampytest.assert_false(lock.locked())
    vampytest.assert_false(condition.locked())


async def test__Condition__explicit_lock():
    loop = get_event_loop()
    
    # All should work in the same way.
    await _test__Condition__explicit_lock()
    await _test__Condition__explicit_lock(Lock(loop))
    lock = Lock(loop)
    await _test__Condition__explicit_lock(lock, asyncio.Condition(lock))


async def test__Condition__ambiguous_loops():
    loop = get_event_loop()
    loop_secondary = create_event_loop()
    try:
        lock = Lock(loop_secondary)
        
        with vampytest.assert_raises(RuntimeError):
            asyncio.Condition(lock)
    
        # Same analogy here with the condition's loop.
        lock = Lock(loop)
        with vampytest.assert_raises(RuntimeError):
            asyncio.Condition(lock, loop = loop_secondary)
    
    finally:
        loop_secondary.stop()


async def test__Condition__timeout_in_block():
    condition = asyncio.Condition()
    async with condition:
        with vampytest.assert_raises(TimeoutError):
            await asyncio.wait_for(condition.wait(), timeout = 0.01)
