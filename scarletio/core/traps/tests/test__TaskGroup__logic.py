import vampytest

from ...top_level import get_event_loop

from ..task_group import TaskGroup
from ..task_suppression import skip_ready_cycle


async def test__TaskGroup__task_moving():
    """
    Tests whether ``TaskGroup`` task moving works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = task_group.create_future()
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {future_0})
    
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_eq(task_group.done, {future_0})
    vampytest.assert_eq(task_group.pending, set())

    # Cancel the futures, so we get no error messages.
    future_0.cancel()


async def test__TaskGroup__waiter_completion():
    """
    Tests whether ``TaskGroup`` marks a waiter done when a task is completed.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = task_group.create_future()
    
    waiter_0 = task_group.wait_next()
    
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())

    # Cancel the futures, so we get no error messages.
    future_0.cancel()
    waiter_0.cancel()


async def test__TaskGroup__waiter_removal():
    """
    Tests whether ``TaskGroup`` removes the waiter from itself if it is cancelled.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_in(waiter_0, task_group.waiters.keys())
    
    waiter_0.cancel()
    await skip_ready_cycle()
    
    vampytest.assert_not_in(waiter_0, task_group.waiters.keys())
    
    # Cancel the futures, so we get no error messages.
    waiter_0.cancel()
