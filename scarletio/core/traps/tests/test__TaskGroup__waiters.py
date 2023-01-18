import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup
from ..task_suppression import skip_ready_cycle


async def test__TaskGroup__wait_next():
    """
    Tests whether ``TaskGroup.wait_next`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_0 = task_group.create_future()
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    
    vampytest.assert_is(waiter_0.get_result(), None)
    
    # If there is any done already, it should not be marked as done since we are waiting for the next to complete.
    
    waiter_1 = task_group.wait_next()
    vampytest.assert_false(waiter_1.is_done())
    
    # Cancel so we dont get error messages
    waiter_0.cancel()
    future_0.cancel()
    waiter_1.cancel()
    

async def test__TaskGroup__wait_first():
    """
    Tests whether ``TaskGroup.wait_first`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # If there is nothing added, waiter should not be done.
    waiter_0 = task_group.wait_first()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_0 = task_group.create_future()
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_is(waiter_0.get_result(), future_0)
    vampytest.assert_in(future_0, task_group.done)
    
    # If there is already any done, we should retrieve it instantly.
    
    waiter_1 = task_group.wait_first()
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_is(waiter_1.get_result(), future_0)
    vampytest.assert_in(future_0, task_group.done)
    
    # Cancel so we get no error messages
    waiter_0.cancel()
    waiter_1.cancel()
    future_0.cancel()


async def test__TaskGroup__wait_first_and_pop():
    """
    Tests whether ``TaskGroup.wait_first_and_pop`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # If there is nothing added, waiter should not be done.
    waiter_0 = task_group.wait_first_and_pop()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_false(waiter_0.is_done())
    
    future_0 = task_group.create_future()
    future_0.set_result(None)
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_is(waiter_0.get_result(), future_0)
    vampytest.assert_not_in(future_0, task_group.done)
    
    # If there is already any done, we should retrieve it instantly.
    
    future_1 = task_group.create_future()
    future_1.set_result(None)
    task_group.add_future(future_1)
    
    waiter_1 = task_group.wait_first_and_pop()
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_is(waiter_1.get_result(), future_1)
    vampytest.assert_not_in(future_1, task_group.done)
    
    # Cancel futures, so we dont get error message
    future_0.cancel()
    future_1.cancel()
    waiter_0.cancel()
    waiter_1.cancel()


async def test__TaskGroup__wait_exception():
    """
    Tests whether ``TaskGroup.wait_exception`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # If there is nothing added, waiter should not be done. All done + no exception.
    waiter_0 = task_group.wait_exception()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_is(waiter_0.get_result(), None)
    
    # If we have a done future, but without exception, we should get back `None`.
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    waiter_1 = task_group.wait_exception()
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_is(waiter_1.get_result(), None)
    vampytest.assert_in(future_0, task_group.done)
    
    # We have one pending future.
    future_1 = task_group.create_future()
    
    waiter_3 = task_group.wait_exception()
    vampytest.assert_false(waiter_3.is_done())
    
    future_1.set_exception(ValueError(6))
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_3.is_done())
    vampytest.assert_is(waiter_3.get_result(), future_1)
    vampytest.assert_in(future_1, task_group.done)
    
    # If there is already any done with exception, we should retrieve it instantly.
    
    waiter_2 = task_group.wait_exception()
    vampytest.assert_true(waiter_2.is_done())
    vampytest.assert_is(waiter_2.get_result(), future_1)
    vampytest.assert_in(future_1, task_group.done)
    
    # Cancel it, so no error message pops up
    future_0.cancel()
    waiter_0.cancel()
    waiter_1.cancel()
    future_1.cancel()
    waiter_2.cancel()
    waiter_3.cancel()


async def test__TaskGroup__wait_exception_and_pop():
    """
    Tests whether ``TaskGroup.wait_exception_and_pop`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # If there is nothing added, waiter should not be done. All done + no exception.
    waiter_0 = task_group.wait_exception()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_is(waiter_0.get_result(), None)
    
    # If we have a done future, but without exception, we should get back `None`.
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    waiter_1 = task_group.wait_exception()
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_is(waiter_1.get_result(), None)
    vampytest.assert_in(future_0, task_group.done)
    
    # We have one pending future.
    future_1 = task_group.create_future()
    
    waiter_2 = task_group.wait_exception_and_pop()
    vampytest.assert_instance(waiter_2, Future)
    vampytest.assert_false(waiter_2.is_done())
    
    future_1.set_exception(ValueError(6))
    await skip_ready_cycle()
    
    vampytest.assert_true(waiter_2.is_done())
    vampytest.assert_is(waiter_2.get_result(), future_1)
    vampytest.assert_not_in(future_1, task_group.done)
    
    # If there is already any done with exception, we should retrieve it instantly.
    
    future_2 = task_group.create_future()
    future_2.set_exception(ValueError(6))
    task_group.add_future(future_2)
    
    waiter_3 = task_group.wait_exception_and_pop()
    vampytest.assert_true(waiter_3.is_done())
    vampytest.assert_is(waiter_3.get_result(), future_2)
    vampytest.assert_not_in(future_2, task_group.done)

    # Cancel it, so no error message pops up
    future_1.cancel()
    future_2.cancel()
    waiter_0.cancel()
    waiter_1.cancel()
    waiter_2.cancel()
    waiter_3.cancel()


async def test__TaskGroup__wait_all():
    """
    Tests whether ``TaskGroup.wait_all`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # Nothing should be retrieved instantly.
    waiter_0 = task_group.wait_all()
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    
    # Create futures and try to retrieve their results after completed
    
    future_0 = task_group.create_future()
    future_1 = task_group.create_future()
    
    waiter_1 = task_group.wait_all()
    vampytest.assert_false(waiter_1.is_done())
    
    
    future_0.set_result(0)
    await skip_ready_cycle()
    vampytest.assert_false(waiter_1.is_done())
    
    future_1.set_result(1)
    await skip_ready_cycle()
    vampytest.assert_true(waiter_1.is_done())
    
    vampytest.assert_in(future_0, task_group.done)
    vampytest.assert_in(future_1, task_group.done)
    
    # If there is already all done, we should retrieve it instantly.
    
    waiter_2 = task_group.wait_all()
    vampytest.assert_true(waiter_2.is_done())
    
    # cancel so we get no error messages
    waiter_0.cancel()
    waiter_1.cancel()
    waiter_2.cancel()
    future_0.cancel()
    future_1.cancel()


async def test__TaskGroup__wait_first_n():
    """
    Tests whether ``TaskGroup.wait_first_n`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # Nothing should be retrieved instantly.
    waiter_0 = task_group.wait_first_n(-1)
    vampytest.assert_instance(waiter_0, Future)
    vampytest.assert_true(waiter_0.is_done())
    vampytest.assert_eq(waiter_0.get_result(), 0)
    
    # Nothing should be retrieved instantly.
    waiter_1 = task_group.wait_first_n(0)
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_eq(waiter_1.get_result(), 0)
    
    # Wait for two
    future_0 = task_group.create_future()
    future_1 = task_group.create_future()

    waiter_2 = task_group.wait_first_n(2)
    vampytest.assert_false(waiter_2.is_done())
    
    future_0.set_result(0)
    await skip_ready_cycle()
    vampytest.assert_false(waiter_2.is_done())
    
    future_1.set_result(1)
    await skip_ready_cycle()
    vampytest.assert_true(waiter_2.is_done())
    vampytest.assert_eq(waiter_2.get_result(), 2)
    
    # Retrieve less
    waiter_3 = task_group.wait_first_n(1)
    vampytest.assert_true(waiter_3.is_done())
    vampytest.assert_eq(waiter_3.get_result(), 2)
    
    # cancel so we get no error messages
    waiter_0.cancel()
    waiter_1.cancel()
    future_0.cancel()
    future_1.cancel()
    waiter_2.cancel()
    waiter_3.cancel()
