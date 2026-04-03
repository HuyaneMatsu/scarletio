import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup
from ..task_suppression import skip_ready_cycle


async def test__TaskGroup__pop_one():
    """
    Tests whether ``TaskGroup.pop_one`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # No Future
    vampytest.assert_is(task_group.pop_done(), None)
    
    # Done future
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    vampytest.assert_is(task_group.pop_done(), future_0)
    vampytest.assert_is(task_group.pop_done(), None)
    
    # Pending future
    future_1 = Future(loop)
    task_group.add_future(future_1)
    vampytest.assert_is(task_group.pop_done(), None)

    # Cancel the futures, so we get no error messages.
    future_0.cancel()
    future_1.cancel()


async def test__TaskGroup__has_done():
    """
    Tests whether ``TaskGroup.has_done`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # No future
    vampytest.assert_false(task_group.has_done())
    
    # Pending future
    future_0 = Future(loop)
    task_group.add_future(future_0)
    vampytest.assert_false(task_group.has_done())
    
    # Done future
    future_1 = Future(loop)
    future_1.set_result(None)
    task_group.add_future(future_1)
    vampytest.assert_true(task_group.has_done())

    # Cancel the futures, so we get no error messages.
    future_0.cancel()
    future_1.cancel()


async def test__TaskGroup__has_pending():
    """
    Tests whether ``TaskGroup.has_pending`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # No future
    vampytest.assert_false(task_group.has_pending())
    
    # Done future
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    vampytest.assert_false(task_group.has_pending())

    # Pending future
    future_1 = Future(loop)
    task_group.add_future(future_1)
    vampytest.assert_true(task_group.has_pending())

    # Cancel the futures, so we get no error messages.
    future_0.cancel()
    future_1.cancel()


async def test__Taskgroup__cancel_all():
    """
    Tests whether ``TaskGroup.cancel_all`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future_done = Future(loop)
    future_done.set_result(None)
    
    future_pending = Future(loop)
    
    task_group = TaskGroup(loop, [future_done, future_pending])
    
    task_group.cancel_all()
    
    vampytest.assert_true(future_done.is_done()) # if they are done, they arent marked as cancelled, sadge
    vampytest.assert_true(future_pending.is_cancelled())
    
    # Cancel the futures, so we get no error messages.
    future_done.cancel()
    future_pending.cancel()


async def test__Taskgroup__cancel_done():
    """
    Tests whether ``TaskGroup.cancel_done`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future_done = Future(loop)
    future_done.set_result(None)
    
    future_pending = Future(loop)
    
    task_group = TaskGroup(loop, [future_done, future_pending])
    
    task_group.cancel_done()
    
    vampytest.assert_true(future_done.is_done()) # if they are done, they arent marked as cancelled, sadge
    vampytest.assert_false(future_pending.is_cancelled())

    # Cancel the futures, so we get no error messages.
    future_done.cancel()
    future_pending.cancel()


async def test__Taskgroup__cancel_pending():
    """
    Tests whether ``TaskGroup.cancel_done`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future_done = Future(loop)
    future_done.set_result(None)
    
    future_pending = Future(loop)
    
    task_group = TaskGroup(loop, [future_done, future_pending])
    
    task_group.cancel_pending()
    
    vampytest.assert_true(future_done.is_done()) # if they are done, they arent marked as cancelled, sadge
    vampytest.assert_true(future_pending.is_cancelled())

    # Cancel the futures, so we get no error messages.
    future_done.cancel()
    future_pending.cancel()
