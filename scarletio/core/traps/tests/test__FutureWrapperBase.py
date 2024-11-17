from time import sleep as blocking_sleep

import vampytest

from ...exceptions import CancelledError, InvalidStateError
from ...top_level import create_event_loop, get_event_loop

from ..future import Future
from ..future_wrapper_base import FutureWrapperBase
from ..task import Task


async def test__FutureWrapperBaseBaseWrapper__new():
    """
    Tests whether ``FutureWrapperBase.__new__`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_instance(wrapper, FutureWrapperBase)
    vampytest.assert_instance(wrapper._future, Future)
    
    vampytest.assert_is(wrapper._future, future)


async def test__FutureWrapperBase__repr__pending():
    """
    Tests whether ``FutureWrapperBase.__repr__`` works as intended.
    
    Case: pending.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    representation = repr(wrapper)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('state = ', representation)
    vampytest.assert_in('pending', representation)

    
async def test__FutureWrapperBase__repr__callback():
    """
    Tests whether ``FutureWrapperBase.__repr__`` works as intended.
    
    Case: with callback.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.add_done_callback(lambda future: None)
    future.silence()
    
    wrapper = FutureWrapperBase(future)
    
    representation = repr(wrapper)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('callbacks = ', representation)


async def test__FutureWrapperBase__repr__result():
    """
    Tests whether ``FutureWrapperBase.__repr__`` works as intended.
    
    Case: resulted.
    
    This function is a coroutine.
    """
    result = 'koishi'
    
    future = Future(get_event_loop())
    future.set_result(result)
    future.silence()
    
    wrapper = FutureWrapperBase(future)
    
    representation = repr(wrapper)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('result = ', representation)
    vampytest.assert_in(result, representation)


async def test__FutureWrapperBase__repr__exception():
    """
    Tests whether ``FutureWrapperBase.__repr__`` works as intended.
    
    Case: exception.
    
    This function is a coroutine.
    """
    exception_type = ValueError
    
    future = Future(get_event_loop())
    future.set_exception(exception_type)
    future.silence()
    
    wrapper = FutureWrapperBase(future)
    
    representation = repr(wrapper)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('exception = ', representation)
    vampytest.assert_in(exception_type.__name__, representation)


async def test__FutureWrapperBase__repr__future():
    """
    Tests whether ``FutureWrapperBase.__repr__`` works as intended.
    
    Case: future.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    representation = repr(wrapper)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in('future = ', representation)
    vampytest.assert_in(Future.__name__, representation)


def test__FutureWrapperBase__cancel__new():
    """
    Tests whether ``FutureWrapperBase.cancel`` works as intended.
    
    Case: new cancellation.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.cancel()
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 1)
        vampytest.assert_true(future.is_cancelled())
        
        for retry in range(2):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__cancel__before():
    """
    Tests whether ``FutureWrapperBase.cancel`` works as intended.
    
    Case: already cancelled.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.cancel()
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.cancel()
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 0)
        vampytest.assert_true(future.is_cancelled())
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__cancel_with__new():
    """
    Tests whether ``FutureWrapperBase.cancel_with`` works as intended.
    
    Case: new cancellation.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = IndexError()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.cancel_with(exception)
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 1)
        vampytest.assert_true(future.is_cancelled())
        vampytest.assert_is(future.get_exception(), exception)
        
        for retry in range(2):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__cancel_with__before():
    """
    Tests whether ``FutureWrapperBase.cancel_with`` works as intended.
    
    Case: already cancelled.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = IndexError()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.cancel_with(exception)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.cancel_with(ValueError())
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 0)
        vampytest.assert_true(future.is_cancelled())
        vampytest.assert_is(future.get_exception(), exception)
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
        
    finally:
        loop.stop()


async def test__FutureWrapperBase__silence():
    """
    Tests whether ``FutureWrapperBase.silence`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_false(future.is_silenced())
    wrapper.silence()
    vampytest.assert_true(future.is_silenced())


async def test__FutureWrapperBase__is_cancelled():
    """
    Tests whether ``FutureWrapperBase.is_cancelled`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_false(wrapper.is_cancelled())
    future.cancel()
    vampytest.assert_true(wrapper.is_cancelled())


async def test__FutureWrapperBase__is_cancelling():
    """
    Tests whether ``FutureWrapperBase.is_cancelling`` works as intended.
    
    This function is a coroutine.
    """
    async def _test_coroutine():
        pass
    
    future = Task(get_event_loop(), _test_coroutine())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_false(wrapper.is_cancelling())
    future.cancel()
    vampytest.assert_true(wrapper.is_cancelling())


async def test__FutureWrapperBase__is_done():
    """
    Tests whether ``FutureWrapperBase.is_done`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_false(wrapper.is_done())
    future.cancel()
    vampytest.assert_true(wrapper.is_done())


async def test__FutureWrapperBase__is_pending():
    """
    Tests whether ``FutureWrapperBase.is_pending`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    vampytest.assert_true(wrapper.is_pending())
    future.cancel()
    vampytest.assert_false(wrapper.is_pending())


async def test__FutureWrapperBase__get_result():
    """
    Tests whether ``FutureWrapperBase.get_result`` works as intended.
    
    This function is a coroutine.
    """
    result = object()
    future = Future(get_event_loop())
    future.set_result(result)
    
    wrapper = FutureWrapperBase(future)
    
    output = wrapper.get_result()
    vampytest.assert_is(output, result)


async def test__FutureWrapperBase__get_exception():
    """
    Tests whether ``FutureWrapperBase.get_exception`` works as intended.
    
    This function is a coroutine.
    """
    exception = IndexError()
    future = Future(get_event_loop())
    future.set_exception(exception)
    
    wrapper = FutureWrapperBase(future)
    
    output = wrapper.get_exception()
    vampytest.assert_is(output, exception)



async def test__FutureWrapperBase__get_cancellation_exception():
    """
    Tests whether ``FutureWrapperBase.get_cancellation_exception`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    future.cancel()
    
    wrapper = FutureWrapperBase(future)
    
    output = wrapper.get_cancellation_exception()
    vampytest.assert_instance(output, CancelledError)


def test__FutureWrapperBase__set_result__new():
    """
    Tests whether ``FutureWrapperBase.set_result`` works as intended.
    
    Case: pending.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        result = object()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        wrapper.set_result(result)
        
        vampytest.assert_true(future.is_done())
        vampytest.assert_is(future.get_result(), result)
        
        # 3 retries
        for _ in range(3):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_result__before():
    """
    Tests whether ``FutureWrapperBase.set_result`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        result = object()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.set_result(result)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        
        with vampytest.assert_raises(InvalidStateError(future, 'set_result')):
            wrapper.set_result(result)
        
        vampytest.assert_is(future.get_result(), result)
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_result_if_pending__new():
    """
    Tests whether ``FutureWrapperBase.set_result_if_pending`` works as intended.
    
    Case: pending.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        result = object()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.set_result_if_pending(result)
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 1)
        vampytest.assert_true(future.is_done())
        vampytest.assert_is(future.get_result(), result)
        
        # 3 retries
        for _ in range(3):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_result_if_pending__before():
    """
    Tests whether ``FutureWrapperBase.set_result_if_pending`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        result = object()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.set_result_if_pending(result)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        
        output = wrapper.set_result_if_pending(object())
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 0)
        vampytest.assert_is(future.get_result(), result)
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_exception__new():
    """
    Tests whether ``FutureWrapperBase.set_exception`` works as intended.
    
    Case: pending.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = IndexError()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        wrapper.set_exception(exception)
        
        vampytest.assert_true(future.is_done())
        vampytest.assert_is(future.get_exception(), exception)
        
        for retry in range(2):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_exception__before():
    """
    Tests whether ``FutureWrapperBase.set_exception`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = IndexError()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.set_exception(exception)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        
        with vampytest.assert_raises(InvalidStateError(future, 'set_exception')):
            wrapper.set_exception(exception)
        
        vampytest.assert_is(future.get_exception(), exception)
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_exception_if_pending__new():
    """
    Tests whether ``FutureWrapperBase.set_exception_if_pending`` works as intended.
    
    Case: pending.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = IndexError()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        output = wrapper.set_exception_if_pending(exception)
        
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 1)
        vampytest.assert_true(future.is_done())
        vampytest.assert_is(future.get_exception(), exception)
        
        for retry in range(2):
            blocking_sleep(0.0001)
            if loop_waken_up:
                break
        
        vampytest.assert_true(loop_waken_up)
    
    finally:
        loop.stop()


def test__FutureWrapperBase__set_exception_if_pending__before():
    """
    Tests whether ``FutureWrapperBase.set_exception_if_pending`` works as intended.
    
    Case: already done.
    """
    loop = create_event_loop()
    try:
        loop_waken_up = False
        exception = Exception()
        
        def _loop_waken_up_callback():
            nonlocal loop_waken_up
            loop_waken_up = True
        
        future = Future(loop)
        future.set_exception_if_pending(exception)
        loop.call_soon(_loop_waken_up_callback)
        
        wrapper = FutureWrapperBase(future)
        
        output = wrapper.set_exception_if_pending(ValueError())
        vampytest.assert_instance(output, int)
        vampytest.assert_eq(output, 0)
        vampytest.assert_is(future.get_exception(), exception)
        
        blocking_sleep(0.0001)
        vampytest.assert_false(loop_waken_up)
    
    finally:
        loop.stop()


async def test__FutureWrapperBase__wait():
    """
    Tests whether ``FutureWrapperBase.wait`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    with vampytest.assert_raises(NotImplementedError):
        wrapper.wait()


async def test__FutureWrapperBase__wait_for_completion():
    """
    Tests whether ``FutureWrapperBase.wait_for_completion`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    
    wrapper = FutureWrapperBase(future)
    
    with vampytest.assert_raises(NotImplementedError):
        wrapper.wait_for_completion()
