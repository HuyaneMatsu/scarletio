import vampytest

from ...top_level import get_event_loop

from ..task_group import TaskGroup


async def test__TaskGroup__cancel_on_exception():
    """
    Tests whether ``TaskGroup.cancel_on_exception`` works as intended.
    
    This function is a coroutine.
    
    Case: No tasks given.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    future = task_group.create_future()
    
    with vampytest.assert_raises(ValueError):
        with task_group.cancel_on_exception() as output:
            
            # We should get the task group back.
            vampytest.assert_is(output, task_group)
            
            raise ValueError
    
    # The tasks of the group should be cancelled on exception
    vampytest.assert_true(future.is_cancelled())
