from types import CoroutineType, GeneratorType

import vampytest

from ....utils import to_coroutine

from ...event_loop import EventThread
from ...exceptions import CancelledError, InvalidStateError
from ...top_level import get_event_loop

from ..future import Future
from ..task import Task
from ..task_suppression import skip_ready_cycle


async def _coroutine_0():
    pass


async def test__task__new():
    """
    Tests whether ``Task.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    coroutine = _coroutine_0()
    task = Task(loop, coroutine)
    
    vampytest.assert_instance(task, Future)
    vampytest.assert_instance(task, Task)
    
    vampytest.assert_instance(task._blocking, bool)
    vampytest.assert_instance(task._callbacks, list, nullable = True)
    vampytest.assert_instance(task._loop, EventThread)
    vampytest.assert_instance(task._result, object)
    vampytest.assert_instance(task._state, int)
    vampytest.assert_instance(task._coroutine, CoroutineType, GeneratorType)
    vampytest.assert_instance(task._waited_future, Future, nullable = True)
    
    vampytest.assert_is(task._loop, loop)
    vampytest.assert_eq(task._state, 0)
    vampytest.assert_is(task._coroutine, coroutine)


async def test__Task__new__auto_start():
    """
    Tests whether ``Task.__new__`` works as intended.
    
    Case: Check whether it auto starts.
    
    This function is a coroutine.
    """
    coroutine_ran = False
    result = object()
    
    async def _test_coroutine():
        nonlocal coroutine_ran
        coroutine_ran = True
        return result
    
    task = Task(get_event_loop(), _test_coroutine())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(coroutine_ran)
    vampytest.assert_true(task.is_done())
    vampytest.assert_is(task.get_result(), result)


async def test__Task__repr__pending():
    """
    Tests whether ``Task.__repr__`` works as intended.
        
    Case: pending.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    representation = repr(task)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('state = ', representation)
    vampytest.assert_in('pending', representation)


async def test__Task__repr__callback():
    """
    Tests whether ``Task.__repr__`` works as intended.
    
    Case: with callback.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    task.add_done_callback(lambda future: None)
    task.silence()
    
    representation = repr(task)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('callbacks = ', representation)


async def test__Task__repr__result():
    """
    Tests whether ``Task.__repr__`` works as intended.
    
    Case: resulted.
    
    This function is a coroutine.
    """
    result = 'koishi'
    
    async def _test_coroutine():
        nonlocal result
        return result
    
    task = Task(get_event_loop(), _test_coroutine())
    task.silence()
    await skip_ready_cycle()
    
    representation = repr(task)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('result = ', representation)
    vampytest.assert_in(result, representation)


async def test__Task__repr__exception():
    """
    Tests whether ``Task.__repr__`` works as intended.
    
    Case: exception.
    
    This function is a coroutine.
    """
    exception_type = ValueError
    
    async def _test_coroutine():
        nonlocal exception_type
        raise exception_type
    
    task = Task(get_event_loop(), _test_coroutine())
    task.silence()
    await skip_ready_cycle()
    
    representation = repr(task)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('exception = ', representation)
    vampytest.assert_in(exception_type.__name__, representation)


async def test__Task__repr__coroutine():
    """
    Tests whether ``Task.__repr__`` works as intended.
    
    Case: coroutine.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    task.silence()
    await skip_ready_cycle()
    
    representation = repr(task)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('coroutine = ', representation)
    vampytest.assert_in(_coroutine_0.__qualname__, representation)


async def test__Task__cancel__pending():
    """
    Tests whether ``Task.cancel`` works as intended.
    
    Case: cancelling pending task.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    output = task.cancel()
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_false(task.is_silenced())
    vampytest.assert_eq(output, 1)


async def test__Task__cancel__callbacks():
    """
    Tests whether ``Task.cancel`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(task):
        nonlocal callback_called_with
        callback_called_with = task
    
    task = Task(get_event_loop(), _coroutine_0())
    task.add_done_callback(callback)
    
    task.cancel()
    
    vampytest.assert_is(callback_called_with, None)
    
    await skip_ready_cycle()
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, task)


async def test__Task__cancel__dome():
    """
    Tests whether ``Task.cancel`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    await skip_ready_cycle()
    
    output = task.cancel()
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_silenced())
    vampytest.assert_eq(output, 0)


async def test__Task__cancel__waiting():
    """
    Tests whether ``Task.cancel`` works as intended.
    
    Case: waiting on an other future to complete.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    waited_future = Future(loop)
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    output = task.cancel()
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_true(waited_future.is_cancelled())
    vampytest.assert_eq(output, 1)
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_cancelled())


async def test__Task__cancel__waiting_on_cancelled():
    """
    Tests whether ``Task.cancel`` works as intended.
    
    Case: The waited function got cancelled.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    waited_future = Future(loop)
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    waited_future.cancel()
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_true(waited_future.is_cancelled())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_cancelled())


async def test__Task__cancel_with__pending():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: cancelling pending task.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    task = Task(get_event_loop(), _coroutine_0())
    
    output = task.cancel_with(exception)
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_false(task.is_silenced())
    vampytest.assert_eq(output, 1)


async def test__Task__cancel_with__callbacks():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    callback_called_with = None
    
    def callback(task):
        nonlocal callback_called_with
        callback_called_with = task
    
    task = Task(get_event_loop(), _coroutine_0())
    task.add_done_callback(callback)
    
    task.cancel_with(exception)
    
    vampytest.assert_is(callback_called_with, None)
    
    await skip_ready_cycle()
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, task)


async def test__Task__cancel_with__dome():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    task = Task(get_event_loop(), _coroutine_0())
    
    await skip_ready_cycle()
    
    output = task.cancel_with(exception)
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_silenced())
    vampytest.assert_eq(output, 0)


async def test__Task__cancel_with__waiting():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: waiting on an other future to complete.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    loop = get_event_loop()
    waited_future = Future(loop)
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    output = task.cancel_with(exception)
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_true(waited_future.is_cancelled())
    vampytest.assert_eq(output, 1)
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_cancelled())


async def test__Task__cancel_with__waiting_on_cancelled():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: The waited function got cancelled.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    
    loop = get_event_loop()
    waited_future = Future(loop)
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    waited_future.cancel_with(exception)
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_true(waited_future.is_cancelled())
    
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_done())
    vampytest.assert_is(task.get_exception(), exception)


async def test__Task__cancel_with__cause():
    """
    Tests whether ``Task.cancel_with`` works as intended.
    
    Case: Check cause.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    
    loop = get_event_loop()
    
    task = Task(loop, _coroutine_0())
    task.cancel_with(exception)
    
    await skip_ready_cycle()
    
    
    cause = task.get_exception().__cause__
    vampytest.assert_is_not(cause, None)
    vampytest.assert_instance(cause, CancelledError)


async def test__Task__is_cancelling__pending():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    vampytest.assert_false(task.is_cancelling())


async def test__Task__is_cancelling__result_set():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_cancelling())


async def test__Task__is_cancelling__exception_set():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    async def _test_coroutine():
        raise ValueError
    
    task = Task(get_event_loop(), _test_coroutine())
    try:
        await skip_ready_cycle()
    
        vampytest.assert_false(task.is_cancelling())
    finally:
        task.silence()


async def test__Task__is_cancelling__cancelled():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    task.cancel()
    
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_cancelling())


async def test__Task__is_cancelling__cancelling_direct():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: cancelling.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    task.cancel()
    
    vampytest.assert_true(task.is_cancelling())


async def test__Task__is_cancelling__waited_cancelling():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: waited future is cancelling.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    nested_future = Future(loop)
    
    async def _nested_coroutine():
        nonlocal nested_future
        await nested_future
    
    waited_future = Task(loop, _nested_coroutine())
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    waited_future.cancel()
    vampytest.assert_true(waited_future.is_cancelling())
    
    vampytest.assert_true(task.is_cancelling())


async def test__Task__is_cancelling__waited_cancelled():
    """
    Tests whether ``Task.is_cancelling`` works as intended.
    
    Case: upstream future is cancelled.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    waited_future = Future(loop)
    
    async def _test_coroutine():
        nonlocal waited_future
        await waited_future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    waited_future.cancel()
    vampytest.assert_true(waited_future.is_cancelled())
    
    vampytest.assert_true(task.is_cancelling())


async def test__Task__set_result():
    """
    Tests whether ``Task.set_result`` works as intended.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    with vampytest.assert_raises(RuntimeError):
        task.set_result(None)


async def test__Task__set_result_if_pending():
    """
    Tests whether ``Task.set_result_if_pending`` works as intended.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    with vampytest.assert_raises(RuntimeError):
        task.set_result(None)


async def test__Task__set_exception():
    """
    Tests whether ``Task.set_exception`` works as intended.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    with vampytest.assert_raises(RuntimeError):
        task.set_exception(ValueError)
    

async def test__Task__set_exception_if_pending():
    """
    Tests whether ``Task.set_exception_if_pending`` works as intended.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    
    with vampytest.assert_raises(RuntimeError):
        task.set_exception(ValueError)


async def test__Task__step__done():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Task already done.
    
    This function is a coroutine.
    """
    task = Task(get_event_loop(), _coroutine_0())
    await task
    
    with vampytest.assert_raises(InvalidStateError):
        task._step()


async def test__Task__step__current_task():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Task already done.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    task = None
    
    async def _test_coroutine():
        nonlocal loop
        nonlocal task
        
        vampytest.assert_is(loop.current_task, task)
    
    task = Task(get_event_loop(), _test_coroutine())
    
    vampytest.assert_is_not(loop.current_task, task)
    await task
    vampytest.assert_is_not(loop.current_task, task)


async def test__Task__step__cancelling():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Cancelling.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    cancellation_received = False
    task = None
    
    async def _test_coroutine():
        nonlocal loop
        nonlocal cancellation_received
        nonlocal task
        
        try:
            await Future(loop)
        except CancelledError:
            cancellation_received = True
            vampytest.assert_is_not(task, None)
            vampytest.assert_false(task.is_cancelling())
            raise
        
        vampytest.assert_is(loop.current_task, task)
    
    task = Task(get_event_loop(), _test_coroutine())
    await skip_ready_cycle()
    task.cancel()
    await task.wait_for_completion()
    
    vampytest.assert_true(cancellation_received)
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())


async def test__Task__step__cancelling_with():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Cancelling.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    cancellation_received = False
    task = None
    exception = TimeoutError()
    
    async def _test_coroutine():
        nonlocal loop
        nonlocal cancellation_received
        nonlocal task
        
        try:
            await Future(loop)
        except CancelledError:
            cancellation_received = True
            vampytest.assert_is_not(task, None)
            vampytest.assert_false(task.is_cancelling())
            raise
        
        vampytest.assert_is(loop.current_task, task)
    
    task = Task(get_event_loop(), _test_coroutine())
    await skip_ready_cycle()
    task.cancel_with(exception)
    await task.wait_for_completion()
    
    vampytest.assert_true(cancellation_received)
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task.get_exception(), exception)


async def test__Task__step__resulting():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Return result.
    
    This function is a coroutine.
    """
    result = object()
    
    async def _test_coroutine():
        nonlocal result
        
        return result
    
    task = Task(get_event_loop(), _test_coroutine())
    await task.wait_for_completion()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task.get_result(), result)


async def test__Task__step__raising():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Raising exception.
    
    This function is a coroutine.
    """
    exception = ValueError()
    
    async def _test_coroutine():
        nonlocal exception
        
        raise exception
    
    task = Task(get_event_loop(), _test_coroutine())
    await task.wait_for_completion()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task.get_exception(), exception)


async def test__Task__step__resulting_while_cancelled():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Return result, but cancelled meanwhile.
    
    This function is a coroutine.
    """
    result = object()
    task = None
    
    async def _test_coroutine():
        nonlocal result
        nonlocal task
        
        vampytest.assert_is_not(task, None)
        task.cancel()
        
        return result
    
    task = Task(get_event_loop(), _test_coroutine())
    await task.wait_for_completion()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    
    vampytest.assert_instance(task.get_exception(), CancelledError)


async def test__Task__step__raising_while_cancelled():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Raising exception, but cancelled meanwhile.
    
    This function is a coroutine.
    """
    exception = ValueError()
    task = None
    
    async def _test_coroutine():
        nonlocal exception
        nonlocal task
        
        vampytest.assert_is_not(task, None)
        task.cancel()
        
        raise exception
    
    task = Task(get_event_loop(), _test_coroutine())
    await task.wait_for_completion()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task.get_exception(), exception)


async def test__Task__step__raising_cancellation():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Raising exception, but cancelled meanwhile.
    
    This function is a coroutine.
    """
    exception = CancelledError()
    
    async def _test_coroutine():
        nonlocal exception
        raise exception
    
    task = Task(get_event_loop(), _test_coroutine())
    await task.wait_for_completion()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    
    vampytest.assert_instance(task.get_exception(), CancelledError)


async def test__Task__step__waiting_on_future():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Waiting on future.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future = Future(loop)
    result = object()
    
    async def _test_coroutine():
        nonlocal future
        return await future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_pending())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task._waited_future, future)
    
    future.set_result(result)
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    vampytest.assert_is(task.get_result(), result)


async def test__Task__step__loop_skipping():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Skipping loops.
    
    This function is a coroutine.
    """
    stepped = 0
    
    @to_coroutine
    def _test_coroutine():
        nonlocal stepped
    
        stepped += 1
        yield
        stepped += 1
        
    task = Task(get_event_loop(), _test_coroutine())
    
    vampytest.assert_eq(stepped, 0)
    await skip_ready_cycle()
    vampytest.assert_eq(stepped, 1)
    await skip_ready_cycle()
    vampytest.assert_eq(stepped, 2)
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())


async def test__Task__step__loop_cancelling():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Skipping loops.
    
    This function is a coroutine.
    """
    task = None
    
    @to_coroutine
    def _test_coroutine():
        nonlocal task
    
        vampytest.assert_is_not(task, None)
        task.cancel()
        yield
    
    task = Task(get_event_loop(), _test_coroutine())
    
    await skip_ready_cycle()
    
    vampytest.assert_false(task.is_done())
    vampytest.assert_false(task.is_cancelled())
    vampytest.assert_true(task.is_cancelling())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    
    vampytest.assert_instance(task.get_exception(), CancelledError)


async def test__Task__step__waiting_on_future_while_cancelling():
    """
    Tests whether ``Task._step`` works as intended.
    
    Case: Waiting on future.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future = Future(loop)
    task = None
    
    async def _test_coroutine():
        nonlocal future
        
        vampytest.assert_is_not(task, None)
        task.cancel()
        return await future
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_pending())
    vampytest.assert_true(task.is_cancelling())
    vampytest.assert_is(task._waited_future, future)
    vampytest.assert_true(future.is_cancelled())
    
    await skip_ready_cycle()
    
    vampytest.assert_true(task.is_done())
    vampytest.assert_true(task.is_cancelled())
    vampytest.assert_false(task.is_cancelling())
    
    vampytest.assert_instance(task.get_exception(), CancelledError)
        

async def test__Task__wake_up__waited_future_reset():
    """
    Tests whether ``Task._wake_up`` works as intended.
    
    Case: It should reset the waited future.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future = Future(loop)
    task = None
    
    async def _test_coroutine():
        nonlocal task
        nonlocal future
        
        vampytest.assert_is_not(task, None)
        vampytest.assert_is(task._waited_future, None)
        
        await future
        
        vampytest.assert_is_not(task, None)
        vampytest.assert_is(task._waited_future, None)
    
    
    task = Task(loop, _test_coroutine())
    
    await skip_ready_cycle()
    vampytest.assert_is(task._waited_future, future)
    future.set_result(None)
    
    await skip_ready_cycle()
    vampytest.assert_is(task._waited_future, None)
    
    await task.wait_for_completion()
    vampytest.assert_is(task._waited_future, None)


async def test__Task__name():
    """
    Tests whether ``Task.name`` works as intended.
    
    Note: how do we check the fallback getter?
    
    This function is a coroutine.
    """
    name = 'koishi'
    
    async def _test_coroutine():
        pass
    
    _test_coroutine.__name__ = name
    
    task = Task(get_event_loop(), _test_coroutine())
    
    output = task.name
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, name)
    

async def test__Task__qualname():
    """
    Tests whether ``Task.qualname`` works as intended.
    
    Note: how do we check the fallback getter?
    
    This function is a coroutine.
    """
    qualname = 'koishi'
    
    async def _test_coroutine():
        pass
    
    _test_coroutine.__qualname__ = qualname
    
    task = Task(get_event_loop(), _test_coroutine())
    
    output = task.qualname
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, qualname)
