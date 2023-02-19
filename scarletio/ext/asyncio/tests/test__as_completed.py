import vampytest

from ....core import Future, LOOP_TIME, get_event_loop
from ....ext.asyncio import asyncio


# This file is a rewrite of `asyncio.as_completed` tests

async def test__as_completed():
    # Arrange
    start_time = LOOP_TIME()
    
    completed = set()

    async def sleeper(duration, x):
        await asyncio.sleep(duration)
        completed.add(x)
        return x
    
    
    a = sleeper(0.01, 'a')
    b = sleeper(0.01, 'b')
    c = sleeper(0.03, 'c')
    
    # Act
    values = []
    for coroutine in asyncio.as_completed([b, c, a]):
        values.append(await coroutine)
    
    # Assert
    vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.01)
    vampytest.assert_in('a', values[:2])
    vampytest.assert_in('b', values[:2])
    vampytest.assert_eq(values[2], 'c')


async def test__as_completed__with_timeout():
    # Arrange
    loop = get_event_loop()
    start_time = LOOP_TIME()

    a = loop.create_task(asyncio.sleep(0.01, 'a'))
    b = loop.create_task(asyncio.sleep(0.05, 'b'))
    
    try:
        # Act
        values = []
        for coroutine in asyncio.as_completed([a, b], timeout = 0.03):
            try:
                value = await coroutine
                values.append((1, value))
            except asyncio.TimeoutError as exc:
                values.append((2, exc))
        
        # Assert
        vampytest.assert_eq(len(values), 2)
        vampytest.assert_eq(values[0], (1, 'a'))
        vampytest.assert_eq(values[1][0], 2)
        vampytest.assert_instance(values[1][1], asyncio.TimeoutError)
        vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.03) < 0.1)
    
    finally:
        a.cancel()
        b.cancel()


async def test__as_completed__with_unused_timeout():
    # Arrange
    a = asyncio.sleep(0.01, 'a')
    
    # Act
    for coroutine in asyncio.as_completed([a], timeout = 1):
        value = await coroutine
        
        # Assert
        vampytest.assert_eq(value, 'a')


async def test__as_completed__reverse_wait():
    # Arrange
    start_time = LOOP_TIME()

    a = asyncio.sleep(0.02, 'a')
    b = asyncio.sleep(0.04, 'b')
    
    # Act & Assert
    futures = [*asyncio.as_completed([a, b])]
    vampytest.assert_eq(len(futures), 2)

    x = await futures[1]
    vampytest.assert_eq(x, 'a')
    vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.02) < 0.01)
    
    y = await futures[0]
    vampytest.assert_eq(y, 'b')
    vampytest.assert_true(abs(LOOP_TIME() - start_time - 0.04) < 0.01)


async def test__as_completed__concurrent():
    # Arrange
    a = asyncio.sleep(0.05, 'a')
    b = asyncio.sleep(0.05, 'b')
    futures = [*asyncio.as_completed([a, b])]
    
    # Act & Assert
    vampytest.assert_eq(len(futures), 2)
    done, pending = await asyncio.wait([asyncio.ensure_future(future) for future in futures])
    vampytest.assert_eq({future.result() for future in done}, {'a', 'b'})


async def test__as_completed__duplicate_coroutines():
    # Arrange
    async def coro(s):
        return s

    result = []
    a = coro('ham')
    b = coro('spam')
    
    try:
        # Act
        for coroutine in asyncio.as_completed([a, a, b]):
            result.append(await coroutine)
        
        # Assert
        vampytest.assert_eq({*result}, {'ham', 'spam'})
        vampytest.assert_eq(len(result), 2)

    finally:
        a.close()
        b.close()


def test__as_completed__coroutine_without_loop():
    # Arrange
    async def coro():
        return 42

    a = coro()
    
    try:
        # Act & assert
        futures = asyncio.as_completed([a])
        with vampytest.assert_raises(RuntimeError):
            try:
                [*futures]
            except RuntimeError as err:
                vampytest.assert_in('no current event loop', repr(err))
                raise
            pass # This is required, so python wont blame the raise line above, lol
    
    finally:
        a.close()
    

async def test__as_completed__coroutine_use_running_loop():
    # Arrange
    async def coro():
        return 42
    
    a = coro()
    try:
        # Act
        awaitables = [*asyncio.as_completed([a])]
        
        # Assert
        vampytest.assert_eq(len(awaitables), 1)
        vampytest.assert_eq(await awaitables[0], 42)
    
    finally:
        a.close()


async def test__as_completed__invalid_args():
    # ``as_completed`` expects an iterable of awaitables, not a awaitable itself
    # Arrange
    loop = get_event_loop()
    
    async def coro():
        pass
    
    # Arrange
    future = Future(loop)
    
    # Act # Assert
    with vampytest.assert_raises(TypeError):
        for _ in asyncio.as_completed(future):
            pass
    
    # Arrange
    a = coro()
    
    # Act # Assert
    try:
        with vampytest.assert_raises(TypeError):
            for _ in asyncio.as_completed(a):
                pass
    finally:
        a.close()
