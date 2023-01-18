import vampytest

from ...top_level import get_event_loop

from ..future import Future
from ..task_group import TaskGroup
from ..task_suppression import sleep


async def test__TaskGroup__exhaust_done():
    """
    Tests whether ``TaskGroup.exhaust_done`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # Nothing is done
    vampytest.assert_eq([*task_group.exhaust_done()], [])
    
    # Something is done
    
    future_0 = Future(loop)
    future_0.set_result(None)
    task_group.add_future(future_0)
    
    vampytest.assert_eq([*task_group.exhaust_done()], [future_0])
    vampytest.assert_false(task_group.has_done())
    
    # Something is pending.
    future_1 = task_group.create_future()
    
    vampytest.assert_eq([*task_group.exhaust_done()], [])
    vampytest.assert_false(task_group.has_done())
    vampytest.assert_true(task_group.has_pending())
    
    # Cancel the futures, so we get no error messages
    future_0.cancel()
    future_1.cancel()


async def _list_construction_async(coroutine_generator):
    """
    Helper function for ``test__TaskGroup__exhaust`` to construct a list from a coroutine generator.
    
    This function is a coroutine.
    
    Parameters
    ----------
    coroutine_generator : ``CoroutineGeneratorType``
        The coroutine generator to construct list from.
    
    Returns
    -------
    values : `list` of `object`
    """
    values = []
    async for value in coroutine_generator:
        values.append(value)
    
    return values



async def test__TaskGroup__exhaust():
    """
    Tests whether ``TaskGroup.exhaust`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task_group = TaskGroup(loop)
    
    # Nothing is done
    vampytest.assert_eq(await _list_construction_async(task_group.exhaust()), [])
    
    # Something is done
    future_3 = Future(loop)
    future_3.set_result(3)
    task_group.add_future(future_3)
    
    vampytest.assert_eq(await _list_construction_async(task_group.exhaust()), [future_3])
    vampytest.assert_false(task_group.has_done())
    
    # Chaining done ...
    
    future_0 = task_group.create_future()
    future_1 = task_group.create_future()
    
    # After `future_0`'s result is set ensure that `future_1`'s result is set too.
    # # This will make `future_0` done always first and `future_1` will follow it.
    future_0.add_done_callback(lambda f: loop.call_later(0.0, future_1.set_result, 1))
    future_0.set_result(0)
    
    vampytest.assert_eq(await _list_construction_async(task_group.exhaust()), [future_0, future_1])
    vampytest.assert_false(task_group.has_done())
    
    future_0.cancel()
    future_1.cancel()
    future_3.cancel()
