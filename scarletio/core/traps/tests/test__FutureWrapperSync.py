from time import sleep as blocking_sleep

import vampytest

from ...time import LOOP_TIME
from ...top_level import create_event_loop, get_event_loop

from ..future import Future
from ..future_wrapper_sync import FutureWrapperSync
from ..task import Task
from ..task_suppression import skip_poll_cycle


async def test__FutureWrapperSync__new():
    """
    Tests whether ``FutureWrapperSync.__new__`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperSync(future)
    
    vampytest.assert_instance(wrapper, FutureWrapperSync)
    vampytest.assert_instance(wrapper._future, Future)
    
    vampytest.assert_is(wrapper._future, future)


def test__FutureWrapperSync__wait__done():
    """
    Tests whether ``FutureWrapperSync.wait`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        result = object()
        
        future = Future(loop)
        future.set_result(result)
        
        wrapper = FutureWrapperSync(future)
        
        start = LOOP_TIME()
        output = wrapper.wait()
        end = LOOP_TIME()
        
        vampytest.assert_true(end - start < 0.0001)
        vampytest.assert_is(output, result)
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait__result():
    """
    Tests whether ``FutureWrapperSync.wait`` works as intended.
    
    Case: result set.
    """
    result = object()
    
    async def _test_coroutine():
        await skip_poll_cycle()
        return result
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperSync(future)
        
        output = wrapper.wait()
        
        vampytest.assert_is(output, result)
        vampytest.assert_true(future.is_done())
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait__timeout():
    """
    Tests whether ``FutureWrapperSync.wait`` works as intended.
    
    Case: hitting timeout.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperSync(future)
        
        with vampytest.assert_raises(TimeoutError):
            wrapper.wait(timeout = 0.0)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait__propagate_cancellation__future():
    """
    Tests whether ``FutureWrapperSync.wait`` works as intended.
    
    Case: propagating cancellation to the future.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperSync(future)
        
        with vampytest.assert_raises(TimeoutError):
            wrapper.wait(timeout = 0.0, propagate_cancellation = True)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait__propagate_cancellation__task():
    """
    Tests whether ``FutureWrapperSync.wait`` works as intended.
    
    Case: propagating cancellation to the task.
    """
    async def _test_coroutine():
        waiter = Future(get_event_loop())
        waiter.silence()
        await waiter
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperSync(future)
        
        with vampytest.assert_raises(TimeoutError):
            wrapper.wait(timeout = 0.0, propagate_cancellation = True)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        
        for _ in range(3):
            blocking_sleep(0.0001)
            output = future.is_cancelled()
            if output:
                break
        
        vampytest.assert_true(output)
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait_for_completion__done():
    """
    Tests whether ``FutureWrapperSync.wait_for_completion`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        future.set_result(None)
        
        wrapper = FutureWrapperSync(future)
        
        start = LOOP_TIME()
        output = wrapper.wait_for_completion()
        end = LOOP_TIME()
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_true(output)
        
        vampytest.assert_true(end - start < 0.0001)
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait_for_completion__result():
    """
    Tests whether ``FutureWrapperSync.wait_for_completion`` works as intended.
    
    Case: result set.
    """
    async def _test_coroutine():
        await skip_poll_cycle()
        return None
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperSync(future)
        
        output = wrapper.wait_for_completion()
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_true(output)
        
        vampytest.assert_true(future.is_done())
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait_for_completion__timeout():
    """
    Tests whether ``FutureWrapperSync.wait_for_completion`` works as intended.
    
    Case: hitting timeout.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperSync(future)
        
        output = wrapper.wait_for_completion(timeout = 0.0)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait_for_completion__propagate_cancellation__future():
    """
    Tests whether ``FutureWrapperSync.wait_for_completion`` works as intended.
    
    Case: propagating cancellation to the future.
    """
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        wrapper = FutureWrapperSync(future)
        
        output = wrapper.wait_for_completion(timeout = 0.0, propagate_cancellation = True)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()


def test__FutureWrapperSync__wait_for_completion__propagate_cancellation__task():
    """
    Tests whether ``FutureWrapperSync.wait_for_completion`` works as intended.
    
    Case: propagating cancellation to the task.
    """
    async def _test_coroutine():
        waiter = Future(get_event_loop())
        waiter.silence()
        await waiter
    
    loop = create_event_loop()
    try:
        future = Task(loop, _test_coroutine())
        
        wrapper = FutureWrapperSync(future)
        
        output = wrapper.wait_for_completion(timeout = 0.0, propagate_cancellation = True)
        
        vampytest.assert_instance(output, bool)
        vampytest.assert_false(output)
        
        # Callbacks should be removed.
        vampytest.assert_false([*future.iter_callbacks()])
        vampytest.assert_true(future.is_cancelled())
        
    finally:
        loop.stop()
