from time import sleep as blocking_sleep

import vampytest

from ....utils import is_coroutine_function, is_generator_function

from ...exceptions import CancelledError, InvalidStateError
from ...event_loop import EventThread
from ...time import LOOP_TIME
from ...top_level import create_event_loop, get_event_loop

from ..future import Future
from ..future_wrapper_async import FutureWrapperAsync
from ..future_wrapper_sync import FutureWrapperSync
from ..task_suppression import skip_ready_cycle, sleep


async def test__Future__new():
    """
    Tests whether ``Future.__new__`` works as intended.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    future = Future(loop)
    
    vampytest.assert_instance(future, Future)
    
    vampytest.assert_instance(future._blocking, bool)
    vampytest.assert_instance(future._callbacks, list, nullable = True)
    vampytest.assert_instance(future._loop, EventThread)
    vampytest.assert_instance(future._result, object)
    vampytest.assert_instance(future._state, int)
    
    vampytest.assert_is(future._loop, loop)
    vampytest.assert_eq(future._state, 0)


async def test__Future__repr__pending():
    """
    Tests whether ``Future.__repr__`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    representation = repr(future)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('state = ', representation)
    vampytest.assert_in('pending', representation)

    
async def test__Future__repr__callback():
    """
    Tests whether ``Future.__repr__`` works as intended.
    
    Case: with callback.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.add_done_callback(lambda future: None)
    future.silence()
    
    representation = repr(future)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('callbacks = ', representation)


async def test__Future__repr__result():
    """
    Tests whether ``Future.__repr__`` works as intended.
    
    Case: resulted.
    
    This function is a coroutine.
    """
    result = 'koishi'
    
    future = Future(get_event_loop())
    future.set_result(result)
    future.silence()
    
    representation = repr(future)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('result = ', representation)
    vampytest.assert_in(result, representation)


async def test__Future__repr__exception():
    """
    Tests whether ``Future.__repr__`` works as intended.
    
    Case: exception.
    
    This function is a coroutine.
    """
    exception_type = ValueError
    
    future = Future(get_event_loop())
    future.set_exception(exception_type)
    future.silence()
    
    representation = repr(future)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('exception = ', representation)
    vampytest.assert_in(exception_type.__name__, representation)


async def test__Future__cancel__pending():
    """
    Tests whether ``Future.cancel`` works as intended.
    
    Case: cancelling pending task.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    output = future.cancel()
    
    vampytest.assert_true(future.is_cancelled())
    vampytest.assert_false(future.is_cancelling())
    vampytest.assert_true(future.is_silenced())
    vampytest.assert_eq(output, 1)


async def test__Future__cancel__callbacks():
    """
    Tests whether ``Future.cancel`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.add_done_callback(callback)
    
    future.cancel()
    
    await skip_ready_cycle()
    vampytest.assert_is(future, callback_called_with)


async def test__Future__cancel__dome():
    """
    Tests whether ``Future.cancel`` works as intended.
    
    Case: cancelling scheduled task.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    output = future.cancel()
    
    vampytest.assert_false(future.is_cancelled())
    vampytest.assert_true(future.is_silenced())
    vampytest.assert_eq(output, 0)


async def test__Future__cancel_with__pending():
    """
    Tests whether ``Future.cancel_with`` works as intended.
    
    Case: cancelling pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    output = future.cancel_with(TimeoutError)
    
    vampytest.assert_true(future.is_cancelled())
    vampytest.assert_false(future.is_cancelling())
    vampytest.assert_true(future.is_silenced())
    vampytest.assert_eq(output, 1)


async def test__Future__cancel_with__callbacks():
    """
    Tests whether ``Future.cancel_with`` works as intended.
    
    Case: cancelling scheduled.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.add_done_callback(callback)
    
    future.cancel_with(TimeoutError)
    
    await skip_ready_cycle()
    vampytest.assert_is(future, callback_called_with)


async def test__Future__cancel_with__dome():
    """
    Tests whether ``Future.cancel_with`` works as intended.
    
    Case: cancelling scheduled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    output = future.cancel_with(TimeoutError)
    
    vampytest.assert_false(future.is_cancelled())
    vampytest.assert_true(future.is_silenced())
    vampytest.assert_eq(output, 0)


async def test__Future__silence():
    """
    Tests whether ``Future.silence`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    future.silence()
    
    vampytest.assert_true(future.is_silenced())
    vampytest.assert_true(future.is_pending())


async def test__Future__is_silenced__silenced():
    """
    Tests whether ``Future.is_silenced`` works as intended.
    
    Case: `.silenced()` called on it.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    future.silence()
    
    vampytest.assert_true(future.is_silenced())


async def test__Future__is_silenced__cancelled():
    """
    Tests whether ``Future.is_silenced`` works as intended.
    
    Case: `.cancelled()` called on it.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    future.cancel()
    
    vampytest.assert_true(future.is_silenced())


async def test__Future__is_silenced__result_set():
    """
    Tests whether ``Future.is_silenced`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    vampytest.assert_true(future.is_silenced())


async def test__Future__is_silenced__exception_set():
    """
    Tests whether ``Future.is_silenced`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    try:
        future.set_exception(ValueError)
        
        vampytest.assert_false(future.is_silenced())
    finally:
        future.silence()


async def test__Future__is_silenced__pending():
    """
    Tests whether ``Future.is_silenced`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_false(future.is_silenced())


async def test__Future__is_cancelling__pending():
    """
    Tests whether ``Future.is_cancelling`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_false(future.is_cancelling())


async def test__Future__is_cancelling__result_set():
    """
    Tests whether ``Future.is_cancelling`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    vampytest.assert_false(future.is_cancelling())


async def test__Future__is_cancelling__exception_set():
    """
    Tests whether ``Future.is_cancelling`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    try:
        future.set_exception(ValueError)
    
        vampytest.assert_false(future.is_cancelling())
    finally:
        future.silence()


async def test__Future__is_cancelling__cancelled():
    """
    Tests whether ``Future.is_cancelling`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_false(future.is_cancelling())


async def test__Future__is_cancelled__pending():
    """
    Tests whether ``Future.is_cancelled`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_false(future.is_cancelled())


async def test__Future__is_cancelled__result_set():
    """
    Tests whether ``Future.is_cancelled`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    vampytest.assert_false(future.is_cancelled())


async def test__Future__is_cancelled__exception_set():
    """
    Tests whether ``Future.is_cancelled`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    try:
        future.set_exception(ValueError)
    
        vampytest.assert_false(future.is_cancelled())
    finally:
        future.silence()


async def test__Future__is_cancelled__cancelled():
    """
    Tests whether ``Future.is_cancelled`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_true(future.is_cancelled())


async def test__Future__is_cancelled__silenced():
    """
    Tests whether ``Future.is_cancelled`` works as intended.
    
    Case: silenced.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    vampytest.assert_false(future.is_cancelled())


async def test__Future__is_done__pending():
    """
    Tests whether ``Future.is_done`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_false(future.is_done())


async def test__Future__is_done__cancelled():
    """
    Tests whether ``Future.is_done`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_true(future.is_done())


async def test__Future__is_done__silenced():
    """
    Tests whether ``Future.is_done`` works as intended.
    
    Case: silenced.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    vampytest.assert_false(future.is_done())


async def test__Future__is_done__result_set():
    """
    Tests whether ``Future.is_done`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    vampytest.assert_true(future.is_done())


async def test__Future__is_done__exception_set():
    """
    Tests whether ``Future.is_done`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    try:
        future.set_exception(ValueError)
    
        vampytest.assert_true(future.is_done())
    finally:
        future.silence()


async def test__Future__is_pending__pending():
    """
    Tests whether ``Future.is_pending`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_true(future.is_pending())


async def test__Future__is_pending__cancelled():
    """
    Tests whether ``Future.is_pending`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_false(future.is_pending())


async def test__Future__is_pending__silenced():
    """
    Tests whether ``Future.is_pending`` works as intended.
    
    Case: silenced.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    vampytest.assert_true(future.is_pending())


async def test__Future__is_pending__result_set():
    """
    Tests whether ``Future.is_pending`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    vampytest.assert_false(future.is_pending())


async def test__Future__is_pending__exception_set():
    """
    Tests whether ``Future.is_pending`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    try:
        future.set_exception(ValueError)
    
        vampytest.assert_false(future.is_pending())
    finally:
        future.silence()


async def test__Future__get_result__result_set():
    """
    Tests whether ``Future.get_result`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    result = object()
    
    future = Future(get_event_loop())
    future.set_result(result)
    
    output = future.get_result()
    
    vampytest.assert_is(result, output)


async def test__Future__get_result__exception_set():
    """
    Tests whether ``Future.get_result`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    exception = ValueError()
    
    future = Future(get_event_loop())
    future.set_exception(exception)
    
    try:
        future.get_result()
    except ValueError as err:
        output = err
    else:
        output = None
    
    vampytest.assert_is(exception, output)
    vampytest.assert_true(future.is_silenced())


async def test__Future__get_result__pending():
    """
    Tests whether ``Future.get_result`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    with vampytest.assert_raises(InvalidStateError(future, 'get_result')):
        future.get_result()


async def test__Future__get_result__cancelled():
    """
    Tests whether ``Future.get_result`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    with vampytest.assert_raises(CancelledError):
        future.get_result()


async def test__Future__get_result__cancelled_with():
    """
    Tests whether ``Future.get_result`` works as intended.
    
    Case: cancelled with exception.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    
    future = Future(get_event_loop())
    future.cancel_with(exception)
    
    try:
        future.get_result()
    except TimeoutError as err:
        output = err
    else:
        output = None
    
    vampytest.assert_is(output, exception)


async def test__Future__get_exception__result_set():
    """
    Tests whether ``Future.get_exception`` works as intended.
    
    Case: result set.
    
    This function is a coroutine.
    """
    result = object()
    
    future = Future(get_event_loop())
    future.set_result(result)
    
    output = future.get_exception()
    
    vampytest.assert_is(output, None)


async def test__Future__get_exception__exception_set():
    """
    Tests whether ``Future.get_exception`` works as intended.
    
    Case: exception set.
    
    This function is a coroutine.
    """
    exception = ValueError()
    
    future = Future(get_event_loop())
    future.set_exception(exception)
    
    output = future.get_exception()
    
    vampytest.assert_is(exception, output)
    vampytest.assert_true(future.is_silenced())


async def test__Future__get_exception__pending():
    """
    Tests whether ``Future.get_exception`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    with vampytest.assert_raises(InvalidStateError(future, 'get_exception')):
        future.get_exception()


async def test__Future__get_exception__cancelled():
    """
    Tests whether ``Future.get_exception`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_instance(future.get_exception(), CancelledError)


async def test__Future__get_exception__cancelled_with():
    """
    Tests whether ``Future.get_exception`` works as intended.
    
    Case: cancelled with exception.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    future = Future(get_event_loop())
    future.cancel_with(exception)
    
    output = future.get_exception()
    vampytest.assert_is(output, exception)


async def test__Future__get_cancellation_exception__pending():
    """
    Tests whether ``Future.get_cancellation_exception`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    vampytest.assert_is(future.get_cancellation_exception(), None)


async def test__Future__get_cancellation_exception__done_result():
    """
    Tests whether ``Future.get_cancellation_exception`` works as intended.
    
    Case: done with result.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(object())
    
    vampytest.assert_is(future.get_cancellation_exception(), None)


async def test__Future__get_cancellation_exception__done_exception():
    """
    Tests whether ``Future.get_cancellation_exception`` works as intended.
    
    Case: done with exception.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_exception(IndexError)
    future.silence()
    
    vampytest.assert_is(future.get_cancellation_exception(), None)


async def test__Future__get_cancellation_exception__cancelled():
    """
    Tests whether ``Future.get_cancellation_exception`` works as intended.
    
    Case: cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    vampytest.assert_instance(future.get_cancellation_exception(), CancelledError)


async def test__Future__get_cancellation_exception__cancelled_with():
    """
    Tests whether ``Future.get_cancellation_exception`` works as intended.
    
    Case: cancelled with exception.
    
    This function is a coroutine.
    """
    exception = TimeoutError()
    future = Future(get_event_loop())
    future.cancel_with(exception)
    
    output = future.get_cancellation_exception()
    vampytest.assert_is(output, exception)



async def test__Future__add_done_callback__pending():
    """
    Tests whether ``Future.add_done_callback`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    def callback(future):
        pass
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback)
    
    vampytest.assert_eq([*future.iter_callbacks()], [callback])


async def test__Future__add_done_callback__multiple():
    """
    Tests whether ``Future.add_done_callback`` works as intended.
    
    Case: adding multiple callbacks.
    
    This function is a coroutine.
    """
    def callback_0(future):
        pass
    
    def callback_1(future):
        pass
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    
    vampytest.assert_eq([*future.iter_callbacks()], [callback_0, callback_1, callback_0, callback_1])


async def test__Future__add_done_callback__done():
    """
    Tests whether ``Future.add_done_callback`` works as intended.
    
    Case: done.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.silence()
    future.set_result(None)
    
    future.add_done_callback(callback)
    
    callbacks = future._callbacks
    vampytest.assert_eq([*future.iter_callbacks()], [])
    
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, future)


async def test__Future__remove_done_callback__no_callbacks():
    """
    Tests whether ``Future.remove_done_callback`` works as intended.
    
    Case: No callbacks.
    
    This function is a coroutine.
    """
    def callback(future):
        pass
    
    future = Future(get_event_loop())
    
    output = future.remove_done_callback(callback)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    

async def test__Future__remove_done_callback__done():
    """
    Tests whether ``Future.remove_done_callback`` works as intended.
    
    Case: future already done.
    
    This function is a coroutine.
    """
    def callback(future):
        pass
    
    future = Future(get_event_loop())
    future.set_result(None)
    
    output = future.remove_done_callback(callback)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    

async def test__Future__remove_done_callback__multiple_callbacks():
    """
    Tests whether ``Future.remove_done_callback`` works as intended.
    
    Case: multiple callbacks.
    
    This function is a coroutine.
    """
    def callback_0(future):
        pass
    
    def callback_1(future):
        pass
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    
    output = future.remove_done_callback(callback_0)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)
    vampytest.assert_eq([*future.iter_callbacks()], [callback_1, callback_1])


async def test__Future__set_result__pending():
    """
    Tests whether ``Future.set_result`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    result = object()
    future = Future(get_event_loop())
    
    future.set_result(result)
    
    vampytest.assert_true(future.is_done())
    
    output = future.get_result()
    vampytest.assert_is(output, result)


async def test__Future__set_result__callback_scheduling():
    """
    Tests whether ``Future.set_result`` works as intended.
    
    Case: scheduling callbacks.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.add_done_callback(callback)
    future.set_result(None)
    
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, future)


async def test__Future__set_result__cancelled():
    """
    Tests whether ``Future.set_result`` works as intended.
    
    Case: Future cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_result')):
        future.set_result(None)


async def test__Future__set_result__result_set():
    """
    Tests whether ``Future.set_result`` works as intended.
    
    Case: Future result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_result')):
        future.set_result(None)


async def test__Future__set_result__exception_set():
    """
    Tests whether ``Future.set_result`` works as intended.
    
    Case: Future exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    future.set_exception(ValueError)
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_result')):
        future.set_result(None)


async def test__Future__set_result_if_pending__pending():
    """
    Tests whether ``Future.set_result_if_pending`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    result = object()
    future = Future(get_event_loop())
    
    output = future.set_result_if_pending(result)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    vampytest.assert_true(future.is_done())
    
    output = future.get_result()
    vampytest.assert_is(output, result)


async def test__Future__set_result_if_pending__callback_scheduling():
    """
    Tests whether ``Future.set_result_if_pending`` works as intended.
    
    Case: scheduling callbacks.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.add_done_callback(callback)
    future.set_result_if_pending(None)
    
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, future)


async def test__Future__set_result_if_pending__cancelled():
    """
    Tests whether ``Future.set_result_if_pending`` works as intended.
    
    Case: Future cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    output = future.set_result_if_pending(None)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    with vampytest.assert_raises(CancelledError):
        future.get_result()


async def test__Future__set_result_if_pending__result_set():
    """
    Tests whether ``Future.set_result_if_pending`` works as intended.
    
    Case: Future result set.
    
    This function is a coroutine.
    """
    result = object()
    
    future = Future(get_event_loop())
    future.set_result(result)
    
    output = future.set_result_if_pending(None)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    output = future.get_result()
    vampytest.assert_is(output, result)


async def test__Future__set_result_if_pending__exception_set():
    """
    Tests whether ``Future.set_result_if_pending`` works as intended.
    
    Case: Future exception set.
    
    This function is a coroutine.
    """
    exception = ValueError()
    
    future = Future(get_event_loop())
    future.silence()
    future.set_exception(exception)
    
    output = future.set_result_if_pending(None)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    try:
        future.get_result()
    except ValueError as err:
        output = err
    else:
        output = None
    
    vampytest.assert_is(output, exception)


async def test__Future__set_exception__pending():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    exception = ValueError()
    future = Future(get_event_loop())
    
    future.set_exception(exception)
    
    vampytest.assert_true(future.is_done())
    
    try:
        future.get_result()
    except ValueError as err:
        output = err
    else:
        output = None
    
    vampytest.assert_is(output, exception)


async def test__Future__set_exception__callback_scheduling():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: scheduling callbacks.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback)
    future.set_exception(ValueError())
    
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, future)


async def test__Future__set_exception__cancelled():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: Future cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_exception')):
        future.set_exception(None)


async def test__Future__set_exception__result_set():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: Future result set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_exception(LookupError())
    future.silence()
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_exception')):
        future.set_exception(ValueError())


async def test__Future__set_exception__exception_set():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: Future exception set.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    future.set_exception(ValueError())
    
    with vampytest.assert_raises(InvalidStateError(future, 'set_exception')):
        future.set_exception(ValueError())


async def test__Future__set_exception__instancing():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: whether it instances the exception type.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    future.set_exception(ValueError)
    
    try:
        future.get_result()
    except ValueError as err:
        output_0 = err
    else:
        output_0 = None
    
    vampytest.assert_is_not(output_0, None)
    vampytest.assert_instance(output_0, ValueError)
    
    try:
        future.get_result()
    except ValueError as err:
        output_1 = err
    else:
        output_1 = None
    
    vampytest.assert_is_not(output_1, None)
    vampytest.assert_instance(output_1, ValueError)
    
    vampytest.assert_is(output_0, output_1)


async def test__Future__set_exception__rejecting_stop_iteration():
    """
    Tests whether ``Future.set_exception`` works as intended.
    
    Case: whether ``StopIteration`` is rejected.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    with vampytest.assert_raises(TypeError):
        future.set_exception(StopIteration)
    
    with vampytest.assert_raises(TypeError):
        future.set_exception(StopIteration())


async def test__Future__set_exception_if_pending__pending():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    exception = ValueError()
    future = Future(get_event_loop())
    
    output = future.set_exception_if_pending(exception)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    vampytest.assert_true(future.is_done())
    
    try:
        future.get_result()
    except ValueError as err:
        output = err
    else:
        output = None
    vampytest.assert_is(output, exception)


async def test__Future__set_exception_if_pending__callback_scheduling():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: scheduling callbacks.
    
    This function is a coroutine.
    """
    callback_called_with = None
    
    def callback(future):
        nonlocal callback_called_with
        callback_called_with = future
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback)
    future.set_exception_if_pending(ValueError())
    
    await skip_ready_cycle()
    
    vampytest.assert_is(callback_called_with, future)


async def test__Future__set_exception_if_pending__cancelled():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: Future cancelled.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    output = future.set_exception_if_pending(ValueError())
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    with vampytest.assert_raises(CancelledError):
        future.get_result()


async def test__Future__set_exception_if_pending__result_set():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: Future result set.
    
    This function is a coroutine.
    """
    result = object()
    
    future = Future(get_event_loop())
    future.set_result(result)
    
    output = future.set_exception_if_pending(ValueError())
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    output = future.get_result()
    vampytest.assert_is(output, result)


async def test__Future__set_exception_if_pending__exception_set():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: Future exception set.
    
    This function is a coroutine.
    """
    exception = ValueError()
    
    future = Future(get_event_loop())
    future.silence()
    future.set_exception(exception)
    
    output = future.set_exception_if_pending(ValueError())
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)
    
    try:
        future.get_result()
    except ValueError as err:
        output = err
    else:
        output = None
    
    vampytest.assert_is(output, exception)


async def test__Future__set_exception_if_pending__instancing():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: whether it instances the exception type.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    future.set_exception_if_pending(ValueError)
    
    try:
        future.get_result()
    except ValueError as err:
        output_0 = err
    else:
        output_0 = None
    
    vampytest.assert_is_not(output_0, None)
    vampytest.assert_instance(output_0, ValueError)
    
    try:
        future.get_result()
    except ValueError as err:
        output_1 = err
    else:
        output_1 = None
    
    vampytest.assert_is_not(output_1, None)
    vampytest.assert_instance(output_1, ValueError)
    
    vampytest.assert_is(output_0, output_1)


async def test__Future__set_exception_if_pending__rejecting_stop_iteration():
    """
    Tests whether ``Future.set_exception_if_pending`` works as intended.
    
    Case: whether ``StopIteration`` is rejected.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    with vampytest.assert_raises(TypeError):
        future.set_exception_if_pending(StopIteration)
    
    with vampytest.assert_raises(TypeError):
        future.set_exception_if_pending(StopIteration())


def test__Future__iter__type():
    """
    Checks ``Future.__iter__`'s type.
    """
    vampytest.assert_true(is_generator_function(Future.__iter__))


async def test__Future__iter__pending():
    """
    Tests whether ``Future.__iter__`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    generator = future.__iter__()
    
    output = generator.send(None)
    vampytest.assert_is(output, future)
    vampytest.assert_true(future._blocking)
    
    result = object()
    
    future.set_result(result)
    
    try:
         generator.send(None)
    except StopIteration as err:
        output = err.value
    else:
        output = None
    
    vampytest.assert_is(output, result)


async def test__Future__iter__done():
    """
    Tests whether ``Future.__iter__`` works as intended.
    
    Case: done.
    
    This function is a coroutine.
    """
    result = object()
    future = Future(get_event_loop())
    future.set_result(result)
    
    generator = future.__iter__()
    
    try:
         generator.send(None)
    except StopIteration as err:
        output = err.value
    else:
        output = None
    
    vampytest.assert_is(output, result)


def test__Future__await__type():
    """
    Checks ``Future.__await__`'s type.
    """
    vampytest.assert_true(is_generator_function(Future.__await__))


def test__Future__await():
    """
    Tests whether ``Future.__await__`` works as intended.
    """
    vampytest.assert_is(Future.__iter__, Future.__await__)



def test__Future__wait_for_completion__type():
    """
    Checks ``Future.__await__`'s type.
    """
    vampytest.assert_true(is_generator_function(Future.wait_for_completion))
    vampytest.assert_true(is_coroutine_function(Future.wait_for_completion))


async def test__Future__wait_for_completion__pending():
    """
    Tests whether ``Future.wait_for_completion`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    generator = future.wait_for_completion()
    
    output = generator.send(None)
    vampytest.assert_is(output, future)
    vampytest.assert_true(future._blocking)
    
    result = object()
    
    future.set_result(result)
    
    try:
         generator.send(None)
    except StopIteration as err:
        output = err.value
    else:
        output = object()
    
    vampytest.assert_is(output, None)


async def test__Future__wait_for_completion__done():
    """
    Tests whether ``Future.wait_for_completion`` works as intended.
    
    Case: done.
    
    This function is a coroutine.
    """
    result = object()
    future = Future(get_event_loop())
    future.set_result(result)
    
    generator = future.wait_for_completion()
    
    try:
         generator.send(None)
    except StopIteration as err:
        output = err.value
    else:
        output = object()
    
    vampytest.assert_is(output, None)


async def test__Future__del__pending_with_callbacks():
    """
    Tests whether ``Future.__del__`` works as intended.
    
    Case: Has pending callbacks.
    
    This function is a coroutine.
    """
    def callback(future):
        pass
    
    future = Future(get_event_loop())
    future.add_done_callback(callback)
    
    capture = vampytest.capture_output()
    with capture:
        future.__del__()
        await sleep(0.001)
    
    future.silence()
    vampytest.assert_true(capture.get_value())


async def test__Future__del__un_retrieved_exception():
    """
    Tests whether ``Future.__del__`` works as intended.
    
    Case: Has un-retrieved exceptions.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_exception(ValueError)
    
    capture = vampytest.capture_output()
    with capture:
        future.__del__()
        await sleep(0.1)
    
    future.silence()
    value = capture.get_value()
    vampytest.assert_true(value)


async def test__Future__del__exception_silenced():
    """
    Tests whether ``Future.__del__`` works as intended.
    
    Case: exception silenced.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_exception(ValueError)
    future.silence()
    
    capture = vampytest.capture_output()
    with capture:
        future.__del__()
        await sleep(0.001)
    
    future.silence()
    vampytest.assert_false(capture.get_value())


def test__Future__del__closed_event_loop():
    """
    Tests whether ``Future.__del__`` works as intended.
    
    Case: event loop closed.
    """
    loop = create_event_loop()
    loop.stop()
    blocking_sleep(0.001)
    
    future = Future(loop)
    future.set_exception(ValueError)
    
    capture = vampytest.capture_output()
    with capture:
        future.__del__()
    
    future.silence()
    vampytest.assert_false(capture.get_value())


async def test__Future__sync_wrap():
    """
    Tests whether ``Future.sync_wrap`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    wrapper = future.sync_wrap()
    
    vampytest.assert_instance(wrapper, FutureWrapperSync)
    vampytest.assert_is(wrapper._future, future)


async def test__Future__async_wrap():
    """
    Tests whether ``Future.async_wrap`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    second_loop = create_event_loop()
    second_loop.stop()
    
    wrapper = future.async_wrap(second_loop)
    
    vampytest.assert_instance(wrapper, FutureWrapperAsync)
    vampytest.assert_is(wrapper._future, future)


async def test__Future__apply_timeout__done():
    """
    Tests whether ``Future.apply_timeout`` works as intended.
    
    Case: done.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    output = future.apply_timeout(0.001)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__Future__apply_timeout__done_without_timeout():
    """
    Tests whether ``Future.apply_timeout`` works as intended.
    
    Case: done, no timeout given.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.set_result(None)
    
    output = future.apply_timeout(0.0)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 0)


async def test__Future__apply_timeout__pending_without_timeout():
    """
    Tests whether ``Future.apply_timeout`` works as intended.
    
    Case: pending, no timeout given.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    output = future.apply_timeout(0.0)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    vampytest.assert_true(future.is_done())
    
    with vampytest.assert_raises(TimeoutError):
        future.get_result()


async def _test__Future__apply_timeout__pending():
    """
    Internal coroutine of ``test__Future__apply_timeout__pending``.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    output = future.apply_timeout(0.001)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    vampytest.assert_true(future.is_pending())
    
    start = LOOP_TIME()
    with vampytest.assert_raises(TimeoutError):
        await future
    
    end = LOOP_TIME()
    
    difference = end - start
    # We sleep at least the requested amount.
    vampytest.assert_true(difference > 0.001)
    
    # But everything has a limit!
    vampytest.assert_true(difference <= 0.015)


async def test__Future__apply_timeout__pending():
    """
    Tests whether ``Future.apply_timeout`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    task = get_event_loop().create_task(_test__Future__apply_timeout__pending())
    task.apply_timeout(0.05)
    await task



async def _test__Future__apply_timeout__pending_with_race():
    """
    Internal coroutine of ``test__Future__apply_timeout__pending``.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    # We should be done after the shortest time.
    output = future.apply_timeout(0.001)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    output = future.apply_timeout(0.1)
    
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 1)
    
    vampytest.assert_true(future.is_pending())
    
    start = LOOP_TIME()
    with vampytest.assert_raises(TimeoutError):
        await future
    
    end = LOOP_TIME()
    
    difference = end - start
    # We sleep at least the requested amount.
    vampytest.assert_true(difference > 0.001)
    
    # But everything has a limit!
    vampytest.assert_true(difference <= 0.015)


async def test__Future__apply_timeout__pending_with_race():
    """
    Tests whether ``Future.apply_timeout`` works as intended.
    
    Case: pending with race condition.
    
    This function is a coroutine.
    """
    task = get_event_loop().create_task(_test__Future__apply_timeout__pending_with_race())
    task.apply_timeout(0.05)
    await task


async def test__Future__iter_callbacks__non():
    """
    Tests whether ``Future.iter_callbacks`` works as intended.
    
    Case: No callbacks.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.silence()
    
    vampytest.assert_eq([*future.iter_callbacks()], [])
    

async def test__Future__iter_callbacks__many():
    """
    Tests whether ``Future.iter_callbacks`` works as intended.
    
    Case: Many callbacks.
    
    This function is a coroutine.
    """
    def callback_0(future):
        pass
    
    def callback_1(future):
        pass
    
    future = Future(get_event_loop())
    future.silence()
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    future.add_done_callback(callback_0)
    future.add_done_callback(callback_1)
    
    vampytest.assert_eq([*future.iter_callbacks()], [callback_0, callback_1, callback_0, callback_1])
