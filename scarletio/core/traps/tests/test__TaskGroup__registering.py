import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task import Task
from ..task_group import TaskGroup


async def test__TaskGroup__add_future__0():
    """
    Tests whether ``TaskGroup.add_future`` works as intended.
    
    This function is a coroutine.
    
    Case: Pending.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    
    task_group.add_future(future_0)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {future_0})
    
    vampytest.assert_eq(future_0._callbacks, [task_group._waited_done_callback])

    # Cancel the futures, so we get no error messages.
    future_0.cancel()


async def test__TaskGroup__add_future__1():
    """
    Tests whether ``TaskGroup.add_future`` works as intended.
    
    This function is a coroutine.
    
    Case: Done.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = Future(loop)
    future_0.set_result(None)
    
    task_group.add_future(future_0)
    
    vampytest.assert_eq(task_group.done, {future_0})
    vampytest.assert_eq(task_group.pending, set())
    vampytest.assert_eq(future_0._callbacks, [])

    # Cancel the futures, so we get no error messages.
    future_0.cancel()


async def test__TaskGroup__add_future__2():
    """
    Tests whether ``TaskGroup.add_future`` works as intended.
    
    This function is a coroutine.
    
    Case: Done & check triggering.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    waiter_0 = task_group.wait_next()
    vampytest.assert_true(waiter_0.is_pending())
    
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)

    vampytest.assert_false(waiter_0.is_pending())

    # Cancel the futures, so we get no error messages.
    waiter_0.cancel()
    future_0.cancel()


def test__TaskGroup__add_task():
    """
    Tests whether ``TaskGroup.add_task`` is same as ``TaskGroup.add_future``.
    """
    vampytest.assert_is(TaskGroup.add_task, TaskGroup.add_future)



async def test__TaskGroup__add_awaitable():
    """
    Tests whether ``TaskGroup.add_awaitable`` works as intended`.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    async def _coroutine_function(): pass
    
    future_0 = task_group.add_awaitable(_coroutine_function())
    vampytest.assert_instance(future_0, Task)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {future_0})
    vampytest.assert_eq(future_0._callbacks, [task_group._waited_done_callback])
    
    future_1 = Future(loop)
    future_2 = task_group.add_awaitable(future_1)
    vampytest.assert_eq(future_1, future_2)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {future_0, future_1})
    vampytest.assert_eq(future_1._callbacks, [task_group._waited_done_callback])
    
    # Cancel the futures, so we get no error messages.
    future_0.cancel()
    future_1.cancel()
    future_2.cancel()


async def test__Taskgroup__create_future():
    """
    Tests whether ``Taskgroup.create_future`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future_0 = task_group.create_future()
    vampytest.assert_instance(future_0, Future)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {future_0})
    
    vampytest.assert_eq(future_0._callbacks, [task_group._waited_done_callback])

    # Cancel the futures, so we get no error messages.
    future_0.cancel()


async def test__Taskgroup__create_task():
    """
    Tests whether ``Taskgroup.create_task`` works as intended.
    
    This function is a coroutine.
    """
    async def _coroutine_function(): pass
    
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    task_0 = task_group.create_task(_coroutine_function())
    vampytest.assert_instance(task_0, Task)
    
    vampytest.assert_eq(task_group.done, set())
    vampytest.assert_eq(task_group.pending, {task_0})
    
    vampytest.assert_eq(task_0._callbacks, [task_group._waited_done_callback])

    # Cancel the futures, so we get no error messages.
    task_0.cancel()
