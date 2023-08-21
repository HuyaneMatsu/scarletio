__all__ = ('FutureWrapperAsync', )

from types import MethodType

from ...utils import export, ignore_frame

from .future import Future
from .future_wrapper_base import CANCELLATION_TIMEOUT, FutureWrapperBase


ignore_frame(__spec__.origin, 'wait', 'return future.get_result()')
ignore_frame(__spec__.origin, 'wait', 'result_set = await waiter')
ignore_frame(__spec__.origin, 'wait', 'return future.get_result()')
ignore_frame(__spec__.origin, 'wait_for_completion', 'result_set = await waiter')
ignore_frame(__spec__.origin, '__iter__', 'return future.get_result()')
ignore_frame(__spec__.origin, '__iter__', 'yield from waiter')


def _set_future_waiter_callback(waiter, future):
    """
    Sets waiter result.
    
    Parameters
    ----------
    waiter : ``Future``
        Waiter to set.
    future : ``Future``
        The finished future.
    """
    if waiter.set_result_if_pending(True):
        waiter._loop.wake_up()


def _skip_loop_then_set_cancellation_waiter_callback(loop, waiter):
    """
    Sets the cancellation waiter callback's result after 1 poll cycle.
    
    Parameters
    ----------
    loop : ``EventThread``
        Event loop to skip the cycle of.
    waiter : ``Future``
        Waiter to set.
    """
    loop.call_after(0.0, _set_cancellation_waiter_callback, waiter)


def _set_cancellation_waiter_callback(waiter):
    """
    Sets the cancellation waiter's callback's result.
    
    Parameters
    ----------
    waiter : ``Future``
        Waiter to set.
    """
    if waiter.set_result_if_pending(True):
        waiter._loop.wake_up()


async def _propagate_cancellation_async(future, loop):
    """
    Propagates cancellation and waits for result.
    
    This function is a coroutine.
    
    Parameters
    ----------
    future : ``Future``
        The future to cancel.
    loop : ``EventThread``
        Current event loop.
    
    Returns
    -------
    cancellation_exception : `None`, ``BaseException``
    """
    future_loop = future._loop
    if future.cancel():
        future_loop.wake_up()
    
    if future.is_cancelling():
        waiter = Future(loop)
        future_loop.call_soon(_skip_loop_then_set_cancellation_waiter_callback, future_loop, waiter)
        timeout_handle = loop.call_after(CANCELLATION_TIMEOUT, Future.set_result_if_pending, waiter, False)
        future_loop.wake_up()
        
        try:
            result_set = await waiter
        except:
            # Interrupted -> cancel timeout
            timeout_handle.cancel()
            raise
        
        # Not timeout -> cancel timeout
        if result_set:
            timeout_handle.cancel()
    
    # Use get exception in case an exception occurred while cancellation
    if future.is_done():
        return future.get_exception()


@export
class FutureWrapperAsync(FutureWrapperBase):
    """
    Async wrapper for ``Future``-s enabling them to be awaited from an another event loop.
    
    Attributes
    ----------
    _future : ``Future``
        The waited future. If the future's state == modified by the sync wrapper, then ``._future`` is set as `None`,
        to not retrieve the result again.
    
    _loop : ``EventThread``
        The loop to what the async future wrapper is bound to.
    """
    __slots__ = ('_loop',)
    
    def __new__(cls, future, loop):
        """
        Creates a new ``FutureWrapperAsync`` object bound to the given `loop` and `future`.
        
        Parameters
        ----------
        loop : ``EventThread``
            The loop from where the created wrapper futures can be awaited.
        future : ``Future``
            The future to wrap.
        """
        self = object.__new__(cls)
        self._future = future
        self._loop = loop
        return self
    
    
    async def wait(self, timeout = None, propagate_cancellation = False):
        """
        Waits till the waited future's result or exception is set.
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future has exception set with `.set_exception`, `.set_exception_if_pending` successfully, then raises
        the given exception.
        
        If the future has result set with `.set_result`, `.set_result_if_pending` successfully, then returns the
        given object.
        
        This method is a coroutine.
        
        Parameters
        ----------
        timeout : `None`, `float` = `None`, Optional
            Timeout in seconds till the waited future's result should be set. Giving it as `None`, means no time limit.
        
        propagate_cancellation : `bool` = `False`, Optional
            Whether cancellation should be propagated towards the waited task.
        
        Returns
        -------
        result : `object`
            The future's result.
        
        Raises
        ------
        TimeoutError
            If `timeout` is over and the waited future is still pending.
        CancelledError
            The future is cancelled.
        TypeError
            The future has non `BaseException` set as exception.
        BaseException
            The future's set exception.
        """
        future = self._future
        if future.is_done():
            return future.get_result()
        
        waiter = Future(self._loop)
        
        callback = MethodType(_set_future_waiter_callback, waiter)
        future.add_done_callback(callback)
        
        if (timeout is None):
            timeout_handle = None
        else:
            timeout_handle = self._loop.call_after(timeout, Future.set_result_if_pending, waiter, False)
        
        future._loop.wake_up()
        
        try:
            result_set = await waiter
        except BaseException as err:
            # Interrupted -> remove callback
            future.remove_done_callback(callback)
            # Interrupted -> cancel timeout
            if (timeout_handle is not None):
                timeout_handle.cancel()
            
            # Cancel source future | Do not use await in GeneratorExit !!
            if propagate_cancellation:
                if isinstance(err, GeneratorExit):
                    future.cancel()
                else:
                    err.__cause__ = await _propagate_cancellation_async(future, self._loop)
            
            raise
        
        if result_set:
            return future.get_result()
        
        # Timeout -> remove callback
        future.remove_done_callback(callback)
        # Cancel source future
        if propagate_cancellation:
            cancellation_exception = await _propagate_cancellation_async(future, self._loop)
        else:
            cancellation_exception = None
        
        raise TimeoutError from cancellation_exception
    
    
    
    async def wait_for_completion(self, timeout = None, propagate_cancellation = False):
        """
        Waits till the waited future's result or exception is set.
        
        This method is a coroutine.
        
        Parameters
        ----------
        timeout : `None`, `float` = `None`, Optional
            Timeout in seconds till the waited future's result should be set. Giving it as `None`, means no time limit.
        
        propagate_cancellation : `bool` = `False`, Optional
            Whether cancellation should be propagated towards the waited task.
        
        Returns
        -------
        completed : `bool`
            Whether the wrapper future is completed.
        """
        future = self._future
        if future.is_done():
            return True
        
        waiter = Future(self._loop)
        
        callback = MethodType(_set_future_waiter_callback, waiter)
        future.add_done_callback(callback)
        
        if (timeout is None):
            timeout_handle = None
        else:
            timeout_handle = self._loop.call_after(timeout, Future.set_result_if_pending, waiter, False)
        
        future._loop.wake_up()
        
        try:
            result_set = await waiter
        except BaseException as err:
            # Interrupted -> remove callback
            future.remove_done_callback(callback)
            # Interrupted -> cancel timeout
            if (timeout_handle is not None):
                timeout_handle.cancel()
            
            # Cancel source future | Do not use await in GeneratorExit !!
            if propagate_cancellation:
                if isinstance(err, GeneratorExit):
                    future.cancel()
                else:
                    err.__cause__ = await _propagate_cancellation_async(future, self._loop)
            
            raise
        
        if result_set:
            return True
        
        # Timeout -> remove callback
        future.remove_done_callback(callback)
        # Cancel source future
        if propagate_cancellation:
            await _propagate_cancellation_async(future, self._loop)
        
        return False
    
    
    def __iter__(self):
        """Awaits the wrapped future."""
        future = self._future
        if future.is_done():
            return future.get_result()
        
        waiter = Future(self._loop)
        
        callback = MethodType(_set_future_waiter_callback, waiter)
        future.add_done_callback(callback)
        
        future._loop.wake_up()
        
        try:
            yield from waiter
        except:
            # Interrupted -> remove callback
            future.remove_done_callback(callback)
            raise
        
        return future.get_result()
    
    
    __await__ = __iter__
