import vampytest

from ....utils import is_coroutine_function

from ...event_loop import EventThread
from ...time import LOOP_TIME
from ...top_level import create_event_loop, get_event_loop

from ..future import Future
from ..future_wrapper_async import FutureWrapperAsync
from ..task import Task
from ..task_suppression import skip_poll_cycle


async def test__FutureWrapperAsync__new():
    """
    Tests whether ``FutureWrapperAsync.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    future = Future(loop)
    
    wrapper = FutureWrapperAsync(future, loop)
    
    vampytest.assert_instance(wrapper, FutureWrapperAsync)
    vampytest.assert_instance(wrapper._future, Future)
    vampytest.assert_instance(wrapper._loop, EventThread)
    
    vampytest.assert_is(wrapper._future, future)
    vampytest.assert_is(wrapper._loop, loop)


def test__FutureWrapperAsync__wait__type():
    """
    Checks whether ``FutureWrapperAsync.wait`` is a coroutine function.
    """
    vampytest.assert_true(is_coroutine_function(FutureWrapperAsync.wait))


async def test__FutureWrapperAsync__wait__done():
    """
    Tests whether ``FutureWrapperAsync.wait`` works as intended.
    
    Case: already done.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        result = object()
        
        future = Future(loop)
        future.set_result(result)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        start = LOOP_TIME()
        output = await wrapper.wait()
        end = LOOP_TIME()
        
        vampytest.assert_true(end - start < 0.0001)
        vampytest.assert_is(output, result)
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait__result():
    """
    Tests whether ``FutureWrapperAsync.wait`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    result = object()
    
    async def _test_coroutine():
        await skip_poll_cycle()
        return result
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper.wait()
        
        vampytest.assert_is(output, result)
        vampytest.assert_true(future.is_done())
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait__timeout():
    """
    Tests whether ``FutureWrapperAsync.wait`` works as intended.
    
    Case: hitting timeout.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        with vampytest.assert_raises(TimeoutError):
            await wrapper.wait(timeout = 0.0)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait__propagate_cancellation__future():
    """
    Tests whether ``FutureWrapperAsync.wait`` works as intended.
    
    Case: propagating cancellation to the future.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        with vampytest.assert_raises(TimeoutError):
            await wrapper.wait(timeout = 0.0, propagate_cancellation = True)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait__propagate_cancellation__task():
    """
    Tests whether ``FutureWrapperAsync.wait`` works as intended.
    
    Case: propagating cancellation to the task.
    
    This function is a coroutine.
    """
    async def _test_coroutine():
        waiter = Future(get_event_loop())
        waiter.silence()
        await waiter
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        with vampytest.assert_raises(TimeoutError):
            await wrapper.wait(timeout = 0.0, propagate_cancellation = True)
        
        # Wait some
        await skip_poll_cycle()
        
        vampytest.assert_true(future.is_cancelled())
        vampytest.assert_false([*future.iter_callbacks()])
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait_for_completion__done():
    """
    Tests whether ``FutureWrapperAsync.wait_for_completion`` works as intended.
    
    Case: already done.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        future.set_result(None)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        start = LOOP_TIME()
        output = await wrapper.wait_for_completion()
        end = LOOP_TIME()
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_true(output)
        
        vampytest.assert_true(end - start < 0.0001)
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait_for_completion__result():
    """
    Tests whether ``FutureWrapperAsync.wait_for_completion`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    async def _test_coroutine():
        await skip_poll_cycle()
        return None
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper.wait_for_completion()
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_true(output)
        
        vampytest.assert_true(future.is_done())
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait_for_completion__timeout():
    """
    Tests whether ``FutureWrapperAsync.wait_for_completion`` works as intended.
    
    Case: hitting timeout.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper.wait_for_completion(timeout = 0.0)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait_for_completion__propagate_cancellation__future():
    """
    Tests whether ``FutureWrapperAsync.wait_for_completion`` works as intended.
    
    Case: propagating cancellation to the future.
    
    This function is a coroutine.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper.wait_for_completion(timeout = 0.0, propagate_cancellation = True)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__wait_for_completion__propagate_cancellation__task():
    """
    Tests whether ``FutureWrapperAsync.wait_for_completion`` works as intended.
    
    Case: propagating cancellation to the task.
    
    This function is a coroutine.
    """
    async def _test_coroutine():
        waiter = Future(get_event_loop())
        waiter.silence()
        await waiter
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper.wait_for_completion(timeout = 0.0, propagate_cancellation = True)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__await__done():
    """
    Tests whether ``FutureWrapperAsync.__await__`` works as intended.
    
    Case: already done.
    
    This function is a coroutine.
    """
    result = object()
    loop = create_event_loop()
    try:
        future = Future(loop)
        future.set_result(result)
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        start = LOOP_TIME()
        output = await wrapper
        end = LOOP_TIME()
        
        vampytest.assert_is(output, result)
        
        vampytest.assert_true(end - start < 0.0001)
        
    finally:
        loop.stop()


async def test__FutureWrapperAsync__await__result():
    """
    Tests whether ``FutureWrapperAsync.__await__`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    result = object()
    
    async def _test_coroutine():
        nonlocal result
        await skip_poll_cycle()
        return result
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperAsync(future, get_event_loop())
        
        output = await wrapper
        
        vampytest.assert_is(output, result)
        
        vampytest.assert_true(future.is_done())
        
    finally:
        loop.stop()


def test__FutureWrapperSync__iter():
    """
    Tests whether ``FutureWrapperAsync.__iter__`` works as intended.
    """
    vampytest.assert_is(FutureWrapperAsync.__iter__, FutureWrapperAsync.__await__)
