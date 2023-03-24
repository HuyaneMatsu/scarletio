import vampytest

from types import MethodType

from ...event_loop import EventThread
from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup


def _assert_fields_set(task_group):
    """
    Asserts whether every fields are set of the given `task_group`.
    """
    vampytest.assert_instance(task_group, TaskGroup)
    vampytest.assert_instance(task_group.done, set)
    vampytest.assert_instance(task_group.loop, EventThread)
    vampytest.assert_instance(task_group.pending, set)
    vampytest.assert_instance(task_group.waiters, dict)


async def test__TaskGroup__new__0():
    """
    Tests whether ``TaskGroup.__new__`` works as intended.
    
    This function is a coroutine.
    
    Case: No tasks given.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    _assert_fields_set(task_group)


async def test__TaskGroup__new__1():
    """
    Tests whether ``TaskGroup.__new__`` works as intended.
    
    This function is a coroutine.
    
    Case: Tasks given.
    """
    loop = get_event_loop()
    future_0 = Future(loop)
    future_1 = Future(loop)
    future_1.set_result(None)
    
    loop = get_event_loop()
    task_group = TaskGroup(loop, [future_0, future_1])
    _assert_fields_set(task_group)
    
    vampytest.assert_eq(task_group.pending, {future_0})
    vampytest.assert_eq(task_group.done, {future_1})
    
    vampytest.assert_eq(future_0._callbacks, [task_group._waited_done_callback])
    
    # Cancels the futures so we get no error message
    future_0.cancel()
    future_1.cancel()
