__all__ = ()

from datetime import datetime as DateTime
from warnings import warn

from ...utils import copy_docs

from .future import Future
from .future_repr import render_callbacks_into, render_future_into, render_result_into, render_state_into


SILENCE_DEPRECATED =  DateTime.utcnow() > DateTime(2023, 11, 12)

CANCELLATION_TIMEOUT = 0.0004


class FutureWrapperBase:
    """
    Base future wrapper for cross-thread setting and retrieving.
    
    Attributes
    ----------
    _future : ``Future``
        The waited future.
    """
    __slots__ = ('_future',)
    
    def __new__(cls, future):
        """
        Creates a new future wrapper wrapping the given `future`.
        
        Parameters
        ----------
        future : ``Future``
            The future on what we would want to wait from a sync thread.
        """
        self = object.__new__(cls)
        self._future = future
        return self


    def __repr__(self):
        """Returns the future sync wrapper's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        future = self._future
        state = future._state
        repr_parts, field_added = render_state_into(repr_parts, False, state)
        repr_parts, field_added = render_result_into(repr_parts, field_added, state, future._result)
        repr_parts, field_added = render_future_into(repr_parts, field_added, future)
        repr_parts, field_added = render_callbacks_into(repr_parts, field_added, future._callbacks)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    @copy_docs(Future.cancel)
    def cancel(self):
        future = self._future
        cancelled = future.cancel()
        if cancelled:
            future._loop.wake_up()
        return cancelled
    
    
    @copy_docs(Future.cancel_with)
    def cancel_with(self, exception):
        future = self._future
        cancelled = future.cancel_with(exception)
        if cancelled:
            future._loop.wake_up()
        return cancelled
    
    
    @copy_docs(Future.silence)
    def silence(self):
        self._future.silence()
    
    
    @copy_docs(Future.is_cancelled)
    def is_cancelled(self):
        return self._future.is_cancelled()
    
    
    @copy_docs(Future.is_cancelling)
    def is_cancelling(self):
        return self._future.is_cancelling()
    
    
    @copy_docs(Future.is_done)
    def is_done(self):
        return self._future.is_done()
    
    
    @copy_docs(Future.is_pending)
    def is_pending(self):
        return self._future.is_pending()
    
    
    @copy_docs(Future.get_result)
    def get_result(self):
        return self._future.get_result()
    
    
    @copy_docs(Future.get_exception)
    def get_exception(self):
        return self._future.get_exception()
    
    
    @copy_docs(Future.get_cancellation_exception)
    def get_cancellation_exception(self):
        return self._future.get_cancellation_exception()
    
    
    @copy_docs(Future.set_result)
    def set_result(self, result):
        future = self._future
        future.set_result(result)
        future._loop.wake_up()
    
    
    @copy_docs(Future.set_result_if_pending)
    def set_result_if_pending(self, result):
        future = self._future
        result_set = future.set_result_if_pending(result)
        if result_set:
            future._loop.wake_up()
        
        return result_set
    
    
    @copy_docs(Future.set_exception)
    def set_exception(self, exception):
        future = self._future
        future.set_exception(exception)
        future._loop.wake_up()
    
    
    @copy_docs(Future.set_exception_if_pending)
    def set_exception_if_pending(self, exception):
        future = self._future
        exception_set = future.set_exception_if_pending(exception)
        if exception_set:
            future._loop.wake_up()
        
        return exception_set
    
    
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
        raise NotImplementedError
    
    
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
        raise NotImplementedError
    
    # Deprecations
    
    if __debug__:
        def __silence__(self):
            """
            Silences the future's `__del__`, so it will not notify if it would.
            
            Deprecated and will be removed in 2024 February.
            
            Notes
            -----
            This method is present only if `__debug__` is set as `True`.
            """
            if SILENCE_DEPRECATED:
                warn(
                    (
                        f'`{self.__class__.__name__}.__silence__` is deprecated and will be removed in 2024 february.'
                        f'Please use `.silence()` instead.'
                    ),
                    FutureWarning,
                    stacklevel = 2,
                )
            
            self.silence()
    

    def cancelled(self):
        warn(
            f'`{self.__class__.__name__}.cancelled` is deprecated.',
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_cancelled()
    
    
    def done(self):
        warn(
            f'`{self.__class__.__name__}.done` is deprecated.',
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_done()
    
    
    def pending(self):
        warn(
            f'`{self.__class__.__name__}.pending` is deprecated.',
            FutureWarning,
            stacklevel = 2,
        )
        return self.is_pending()
    
    
    @property
    def result(self):
        warn(
            (
                f'`{self.__class__.__name__}.result` is deprecated and will be removed in 2023 November. '
                f'Use `.get_result()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.get_result
    
    
    @property
    def exception(self):
        warn(
            (
                f'`{self.__class__.__name__}.result` is deprecated and will be removed in 2023 November. '
                f'Use `.get_result()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.get_exception
