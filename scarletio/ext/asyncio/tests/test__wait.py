import vampytest

from ....core import Future, LOOP_TIME, get_event_loop
from ....ext.asyncio import asyncio


# This file is a rewrite of `asyncio.wait` tests

async def test__wait():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()
    
    a = loop.create_task(asyncio.sleep(0.01))
    b = loop.create_task(asyncio.sleep(0.03))
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a])
        
        # Assert
        vampytest.assert_eq(done, {a, b})
        vampytest.assert_eq(pending, set())
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)
    
        # Doing it again should finish instantly
        
        # Act
        done, pending = await asyncio.wait([b, a])
        
        # Assert
        vampytest.assert_eq(done, {a, b})
        vampytest.assert_eq(pending, set())
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__duplicate_coroutines():
    # Arrange
    loop = get_event_loop()
    
    async def coro(s):
        return s
    
    a = loop.create_task(coro('test'))
    b = loop.create_task(coro('spam'))
    
    try:
        # Act
        done, pending = await asyncio.wait([a, a, b])
        
        # Assert
        vampytest.assert_false(pending)
        vampytest.assert_eq({future.result() for future in done}, {'test', 'spam'})
    finally:
        a.cancel()
        b.cancel()


async def test__wait__errors():
    # Act & Assert
    with vampytest.assert_raises(ValueError):
        await asyncio.wait([])

    # Arrange
    # -1 is an invalid return_when value
    sleep_coro = asyncio.sleep(0.0)
    
    # Act & Assert
    try:
        with vampytest.assert_raises(ValueError):
            await asyncio.wait([sleep_coro], return_when = -1)
    finally:
        sleep_coro.close()


async def test__wait__first_completed():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()

    a = loop.create_task(asyncio.sleep(0.02))
    b = loop.create_task(asyncio.sleep(0.01))
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a], return_when = asyncio.FIRST_COMPLETED)
        
        # Assert
        vampytest.assert_eq({b}, done)
        vampytest.assert_eq({a}, pending)
        vampytest.assert_false(a.done())
        vampytest.assert_true(b.done())
        vampytest.assert_is(b.result(), None)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.01) < 0.01)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__really_done():
    # It is possible that some tasks in the pending set became done but their callbacks haven't all been called yet.
    
    # Arrange
    loop = get_event_loop()
    
    async def coro_0():
        await asyncio.sleep(0)

    async def coro_1():
        # `asyncio.sleep` does polling, but in scarletio we do not poll between callback loops.
        # So we cannot have 2 sleeps here, only 1.
        # await asyncio.sleep(0)
        await asyncio.sleep(0)
    
    a = loop.create_task(coro_0())
    b = loop.create_task(coro_1())
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a], return_when = asyncio.FIRST_COMPLETED)
        
        # Assert
        vampytest.assert_eq({a, b}, done)
        vampytest.assert_true(a.done())
        vampytest.assert_is(a.result(), None)
        vampytest.assert_true(b.done())
        vampytest.assert_is(b.result(), None)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__first_exception():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()
    
    async def exc():
        raise ZeroDivisionError('err')
    
    # first_exception, task already has exception
    a = loop.create_task(asyncio.sleep(0.02))
    b = loop.create_task(exc())
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a], return_when = asyncio.FIRST_EXCEPTION)
        
        # Assert
        vampytest.assert_eq({b}, done)
        vampytest.assert_eq({a}, pending)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.00) < 0.01)
        
    finally:
        a.cancel()
        b.cancel()


async def test__wait__first_exception_in_wait():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()
    
    async def exc():
        await asyncio.sleep(0.01)
        raise ZeroDivisionError('err')
    
    a = loop.create_task(asyncio.sleep(0.03))
    b = loop.create_task(exc())
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a], return_when = asyncio.FIRST_EXCEPTION)
        
        # Assert
        vampytest.assert_eq({b}, done)
        vampytest.assert_eq({a}, pending)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.01) < 0.01)
    finally:
        a.cancel()
        b.cancel()


async def test__wait__with_exception():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()
    
    async def sleeper():
        await asyncio.sleep(0.03)
        raise ZeroDivisionError('really')
    
    a = loop.create_task(asyncio.sleep(0.01))
    b = loop.create_task(sleeper())
    
    try:
        # Act
        done, pending = await asyncio.wait([b, a])
        
        # Assert
        vampytest.assert_eq(len(done), 2)
        vampytest.assert_eq(len(pending), 0)
        vampytest.assert_eq(sum(future.exception() is not None for future in done), 1)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)
        
        # Doing it again should instantly finish with the same result
        
        # Act
        done, pending = await asyncio.wait([b, a])
        
        # Assert
        vampytest.assert_eq(len(done), 2)
        vampytest.assert_eq(len(pending), 0)
        vampytest.assert_eq(sum(future.exception() is not None for future in done), 1)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)

    finally:
        a.cancel()
        b.cancel()


async def test__wait__with_timeout():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()

    a = loop.create_task(asyncio.sleep(0.01))
    b = loop.create_task(asyncio.sleep(0.03))

    try:
        # Act
        done, pending = await asyncio.wait([b, a], timeout = 0.02)
        
        # Assert
        vampytest.assert_eq(done, {a})
        vampytest.assert_eq(pending, {b})
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.02) < 0.01)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__concurrent_complete():
    # Since timeout is actually started before sleep, sleep `0.01` finishes after timeout `0.01`,
    # so we timeout for `0.02` instead.
    
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()
    
    a = loop.create_task(asyncio.sleep(0.01))
    b = loop.create_task(asyncio.sleep(0.03))
    
    try:
        # Act
        done, pending = await asyncio.wait([a, b], timeout = 0.02)
        
        # Assert
        vampytest.assert_eq(done, {a})
        vampytest.assert_eq(pending, {b})
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.02) < 0.01)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__with_iterator_of_tasks():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()

    a = loop.create_task(asyncio.sleep(0.01))
    b = loop.create_task(asyncio.sleep(0.03))
    
    try:
        # Act
        done, pending = await asyncio.wait(iter([b, a]))
        
        # Assert
        vampytest.assert_eq(done, {a, b})
        vampytest.assert_eq(len(pending), 0)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)
    
    finally:
        a.cancel()
        b.cancel()


async def test__wait__invalid_args():
    # ``wait`` expects an iterable of awaitables, not an awaitable itself
    # Arrange
    loop = get_event_loop()

    async def coro():
        pass
    
    # Act
    future = Future(loop)
    
    # Act # Assert
    with vampytest.assert_raises(TypeError):
        await asyncio.wait(future)
    
    # Arrange
    a = coro()
    
    # Act # Assert
    try:
        with vampytest.assert_raises(TypeError):
            await asyncio.wait(a)
    finally:
        a.close()
