import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup


async def test__TaskGroup__repr():
    """
    Tests whether ``TaskGroup.__repr__`` works as intended.
    
    This function is a coroutine.
    
    Case: Tasks given.
    """
    loop = get_event_loop()
    future_0 = Future(loop)
    future_1 = Future(loop)
    future_1.set_result(None)
    
    loop = get_event_loop()
    task_group = TaskGroup(loop, [future_0, future_1])
    
    vampytest.assert_instance(repr(task_group), str)
    
    # Cancel the futures, so we get no error messages
    future_0.cancel()
    future_1.cancel()
