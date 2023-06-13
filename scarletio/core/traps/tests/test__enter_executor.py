from threading import current_thread

import vampytest

from ...exceptions import CancelledError
from ...event_loop import EventThread
from ...top_level import get_event_loop

from ..future import Future
from ..task import Task
from ..task_thread_switcher import enter_executor


async def test__enter_executor__switching():
    """
    Tests whether ``enter_executor`` switches the thread as intended.
    
    This function is a coroutine.
    """
    async with enter_executor():
        thread = current_thread()
        vampytest.assert_instance(thread, EventThread, reverse = True)


async def test__enter_executor__propagating():
    """
    Tests whether ``enter_executor`` propagates raised exceptions as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    future = Future(loop)
    future.set_exception(ValueError)
    
    async with enter_executor():
        with vampytest.assert_raises(ValueError):
            await future


async def _test__enter_executor__cancellation(ready_waiter, waiter_1, waiter_2):
    """
    The cancelled task used by ``test__enter_executor__cancellation``.
    
    This function is a coroutine.
    
    Parameters
    ----------
    ready_waiter : ``Future``
        Its result is set when the task is ready to be cancelled.
    waiter_1 : ``Future``
        Its result is set if the future is cancelled inside the executor thread.
    waiter_2 : ``Future``
        Its result is set if the future is cancelled outside the executor thread.
    """
    loop = get_event_loop()
    future = Future(loop)
    
    try:
        async with enter_executor():
            ready_waiter.set_result(None)
            
            try:
                await future
            except CancelledError:
                waiter_1.set_result(None)
                raise
    
    except CancelledError:
        waiter_2.set_result(None)
        raise


async def test__enter_executor__cancellation():
    """
    Tests whether ``enter_executor`` propagates cancelled waiter future cancellation as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    ready_waiter = Future(loop)
    waiter_1 = Future(loop)
    waiter_2 = Future(loop)
    
    task = Task(loop, _test__enter_executor__cancellation(ready_waiter, waiter_1, waiter_2))
    
    await ready_waiter
    task.cancel()
    
    with vampytest.assert_raises(CancelledError):
        await task
    
    vampytest.assert_true(waiter_1.is_done())
    vampytest.assert_true(waiter_2.is_done())
