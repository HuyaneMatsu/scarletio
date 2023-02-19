import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup
from ..task_suppression import skip_ready_cycle


async def test__TaskGroup__wait_next__no_futures():
    """
    Tests whether ``TaskGroup.wait_next`` works as intended.
    
    This function is a coroutine.
    
    Case: Nothing to wait for.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()


async def test__TaskGroup__wait_next__result_set_before():
    """
    Tests whether ``TaskGroup.wait_next`` works as intended.
    Wait next waits for the next completed, so result should not be set here.
    
    This function is a coroutine.
    
    Case: Result set before waiting.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    vampytest.assert_eq(task_group.done, {future_0})
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()
    future_0.cancel()


async def test__TaskGroup__wait_next__result_set_after():
    """
    Tests whether ``TaskGroup.wait_next`` works as intended.
    
    This function is a coroutine.
    
    Case: Result set after waiting.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    task_group.add_future(future_0)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_is(waiter_0.get_result(), None)
    
    vampytest.assert_eq(task_group.done, {future_0})
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()
    future_0.cancel()
