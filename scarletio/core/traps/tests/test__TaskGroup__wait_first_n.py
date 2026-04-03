import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup
from ..task_suppression import skip_ready_cycle


async def test__TaskGroup__wait_first_n__no_futures():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    
    Case: Nothing to wait for.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_first_n(1)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()

async def test__TaskGroup__wait_first_n__no_futures_with_negative_count():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    
    Case: Nothing to wait for.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_first_n(-1)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_eq(waiter_0.get_result(), 0)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()


async def test__TaskGroup__wait_first_n__result_set_before():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    
    Case: Result set before waiting.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    future_1 = Future(loop)
    future_1.set_result(None)
    task_group.add_future(future_1)
    
    waiter_0 = task_group.wait_first_n(1)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_eq(waiter_0.get_result(), 2)
    
    vampytest.assert_eq(task_group.done, {future_0, future_1})
    vampytest.assert_eq(task_group.pending, set())
    
    # Cleanup
    waiter_0.cancel()
    future_0.cancel()
    future_1.cancel()


async def test__TaskGroup__wait_first_n__result_set_after():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    
    Case: Result set after waiting.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    task_group.add_future(future_0)
    
    future_1 = Future(loop)
    task_group.add_future(future_1)
    
    waiter_0 = task_group.wait_first_n(1)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_eq(waiter_0.get_result(), 1)
    
    vampytest.assert_eq(task_group.done, {future_0})
    vampytest.assert_eq(task_group.pending, {future_1})
    
    # Cleanup
    waiter_0.cancel()
    future_0.cancel()
    future_1.cancel()


async def test__TaskGroup__wait_first_n__results_set_after():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    
    Case: Result set after waiting.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    future_1 = Future(loop)
    task_group.add_future(future_1)
    
    future_2 = Future(loop)
    task_group.add_future(future_2)
    
    waiter_0 = task_group.wait_first_n(2)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_1.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_eq(waiter_0.get_result(), 2)
    
    vampytest.assert_eq(task_group.done, {future_0, future_1})
    vampytest.assert_eq(task_group.pending, {future_2})
    
    # Cleanup
    waiter_0.cancel()
    future_0.cancel()
    future_1.cancel()
    future_2.cancel()
