__all__ = ()


class _HandleCancellerBase:
    """
    ``Future`` callback-base to cancel a respective ``Handle`` when the future is marked as done before the
    handle, or if the handle runs first, then sets the future result or exception.
    
    This class do not implements ``.__call__`. Subclasses should implement that.
    
    Attributes
    ----------
    _handle : `None`, ``Handle``
        The handle to cancel, when the future is marked as done before the respective handle ran.
    """
    __slots__ = ('_handle',)
    
    
    def __init__(self):
        """
        Creates a new handle canceller.
        
        Note, that a handle canceller is created with empty ``.handle``, because it is a callback and a ``Handle``'s
        function at the same time, so ``.handle`` is needed to be set from outside.
        """
        self._handle = None
    
    
    def __call__(self, future):
        """
        Called by the respective ``Future`` as callback, or by the respective handle.
        
        Subclasses should overwrite this method.
        
        Parameters
        ----------
        future : ``Future``
            The respective future to what the handle canceller was added as callback.
        """
        pass
    
    
    def cancel(self):
        """
        Cancels the handle.
        
        This method is usually called when the respective future's handles are cleared.
        """
        handle = self._handle
        if handle is None:
            return
         
        self._handle = None
        handle.cancel()
    
    
    def __repr__(self):
        """Returns the handler canceller's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        handle = self._handle
        if handle is None:
            state = 'cancelled'
        else:
            state = 'alive'
        
        repr_parts.append(' ')
        repr_parts.append(state)
        
        if (handle is not None):
            repr_parts.append(' handle = ')
            repr_parts.append(handle._get_repr_without(self))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


class _SleepHandleCanceller(_HandleCancellerBase):
    """
    ``Future`` callback to cancel a respective ``Handle`` when the future is marked as done before the
    handle, or if the handle runs first, then sets the future result as `None˛.
    
    Attributes
    ----------
    _handle : `None`, ``Handle``
        The handle to cancel, when the future is marked as done before the respective handle ran.
    """
    __slots__ = ()
    
    def __call__(self, future):
        """
        Called by the respective ``Future`` as callback, or by the respective handle. Sets the given
        `future`'s result as `None` if applicable.
        
        Sets ``._handle`` as `None`, marking the canceller as it ran already.
        
        Parameters
        ----------
        future : ``Future``
            The respective future to what the handle canceller was added as callback.
        """
        handle = self._handle
        if handle is None:
            return
        
        self._handle = None
        handle.cancel()
        future.set_result_if_pending(None)


class _TimeoutHandleCanceller(_HandleCancellerBase):
    """
    ``Future`` callback to cancel a respective ``Handle`` when the future is marked as done before the
    handle, or if the handle runs first, then sets the future's exception to `TimeoutError`.
    
    Attributes
    ----------
    _handle : `None`, ``Handle``
        The handle to cancel, when the future is marked as done before the respective handle ran.
    """
    __slots__ = ()
    
    def __call__(self, future):
        """
        Called by the respective ``Future`` as callback, or by the respective handle. Sets the given
        `future`'s exception to `TimeoutError` if applicable.
        
        Sets ``._handle`` as `None`, marking the canceller as it ran already.
        
        Parameters
        ----------
        future : ``Future``
            The respective future to what the handle canceller was added as callback.
        """
        handle = self._handle
        if handle is None:
            return
        
        handle.cancel()
        self._handle = None
        future.set_exception_if_pending(TimeoutError())
