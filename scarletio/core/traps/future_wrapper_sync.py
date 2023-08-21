__all__ = ('FutureWrapperSync', )

from threading import Event as SyncEvent
from types import MethodType

from ...utils import export, ignore_frame

from .future import Future
from .future_wrapper_base import CANCELLATION_TIMEOUT, FutureWrapperBase


ignore_frame(__spec__.origin, 'wait', 'return future.get_result()')
ignore_frame(__spec__.origin, 'wait', 'raise TimeoutError from cancellation_exception')
ignore_frame(__spec__.origin, 'wait', 'result_set = waiter.wait(timeout)')
ignore_frame(__spec__.origin, 'wait_for_completion', 'result_set = waiter.wait(timeout)')


def _set_waiter_future_callback(waiter, future):
    """
    Sets waiter result.
    
    Parameters
    ----------
    waiter : ``Threading.Event``
        Waiter to set.
    future : ``Future``
        The finished future.
    """
    waiter.set()


def _skip_loop_then_set_cancellation_waiter_callback(loop, waiter):
    """
    Sets the cancellation waiter callback's result after 1 poll cycle.
    
    Parameters
    ----------
    loop : ``EventThread``
        Event loop to skip the cycle of.
    waiter : ``Threading.Event``
        Waiter to set.
    """
    loop.call_after(0.0, _set_cancellation_waiter_callback, waiter)


def _set_cancellation_waiter_callback(waiter):
    """
    Sets the cancellation waiter's callback's result.
    
    Parameters
    ----------
    waiter : ``Threading.Event``
        Waiter to set.
    """
    waiter.set()


def _propagate_cancellation_sync(future):
    """
    Propagates cancellation and waits for result.
    
    Parameters
    ----------
    future : ``Future``
        The future to cancel.
    
    Returns
    -------
    cancellation_exception : `None`, ``BaseException``
    """
    future_loop = future._loop
    if future.cancel():
        future_loop.wake_up()
    
    if future.is_cancelling():
        waiter = SyncEvent()
        future_loop.call_soon(_skip_loop_then_set_cancellation_waiter_callback, future_loop, waiter)
        future_loop.wake_up()
        
        waiter.wait(CANCELLATION_TIMEOUT)
    
    # Use get exception in case an exception occurred while cancellation
    if future.is_done():
        return future.get_exception()


@export
class FutureWrapperSync(FutureWrapperBase):
    """
    Sync wrapper for ``Future``-s enabling them to be waited from a sync threads.
    
    Attributes
    ----------
    _future : ``Future``
        The waited future. If the future's state == modified by the sync wrapper, then ``._future`` is set as `None`,
        to not retrieve the result again.
    """
    __slots__ = ()
    
    def wait(self, timeout = None, propagate_cancellation = False):
        """
        Waits till the waited future's result or exception is set.
        
        If the future is cancelled, raises ``CancelledError``.
        
        If the future has exception set with `.set_exception`, `.set_exception_if_pending` successfully, then raises
        the given exception.
        
        If the future has result set with `.set_result`, `.set_result_if_pending` successfully, then returns the
        given object.
        
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
        
        waiter = SyncEvent()
        
        callback = MethodType(_set_waiter_future_callback, waiter)
        future.add_done_callback(callback)
        
        future._loop.wake_up()
        
        try:
            result_set = waiter.wait(timeout)
        except BaseException as err:
            # Interrupted -> remove callback
            future.remove_done_callback(callback)
            # Cancel source future
            if propagate_cancellation:
                err.__cause__ = _propagate_cancellation_sync(future)
            
            raise
        
        if result_set:
            return future.get_result()
        
        # Timeout -> remove callback
        future.remove_done_callback(callback)
        # Cancel source future
        if propagate_cancellation:
            cancellation_exception = _propagate_cancellation_sync(future)
        else:
            cancellation_exception = None
        
        raise TimeoutError from cancellation_exception
    
    
    def wait_for_completion(self, timeout = None, propagate_cancellation = False):
        """
        Waits till the waited future's result or exception is set.
        
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
        
        waiter = SyncEvent()
        
        callback = MethodType(_set_waiter_future_callback, waiter)
        future.add_done_callback(callback)
        
        future._loop.wake_up()
        
        try:
            result_set = waiter.wait(timeout)
        except BaseException as err:
            # Interrupted -> remove callback
            future.remove_done_callback(callback)
            # Cancel source future
            if propagate_cancellation:
                err.__cause__ = _propagate_cancellation_sync(future)
            
            raise
        
        if result_set:
            return True
        
        # Timeout -> remove callback
        future.remove_done_callback(callback)
        # Cancel source future
        if propagate_cancellation:
            _propagate_cancellation_sync(future)
        
        return False
