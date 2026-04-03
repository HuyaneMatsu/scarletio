__all__ = ('Event', )

from ...utils import copy_func, to_coroutine

from .future import Future


class Event:
    """
    Asynchronous equivalent to `threading.Event`.
    
    Attributes
    ----------
    _loop : ``EventThread``
        The event loop to what the event is bound.
    
    _value : `bool`
        The internal flag of the event, which defines, whether it is set.
    
    _waiters : `list` of ``Future``
        A list of futures waiting on the event to be set.
    """
    __slots__ = ('_loop', '_value', '_waiters',)
    
    def __new__(cls, loop):
        """
        Creates a new event object bound to the given event loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the event is bound.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._value = False
        self._waiters = []
        return self
    
    
    def is_set(self):
        """
        Returns whether the event's internal flag is set as `True`.
        
        Returns
        -------
        is_set: `bool`
        """
        return self._value
    
    
    def set(self):
        """
        Sets the event's internal flag to `True`, waking up all the tasks waiting for it.
        """
        if self._value:
            return
        
        self._value = True
        waiters = self._waiters
        for waiter in waiters:
            waiter.set_result_if_pending(None)
        
        waiters.clear()
    
    
    def clear(self):
        """
        Clears the internal flag of the event.
        """
        self._value = False
    
    
    def __iter__(self):
        """
        Waits util the event is set, or if it is already, returns immediately.
        
        This method is a generator. Should be used with `await` expression.
        """
        if self._value:
            return
        
        future = Future(self._loop)
        self._waiters.append(future)
        yield from future
    
    __await__ = __iter__
    
    wait = to_coroutine(copy_func(__iter__))
    
    def __repr__(self):
        """Returns the event's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
            ' ',
        ]
        
        if self._value:
            state = 'set'
        else:
            state = 'unset'
        repr_parts.append(state)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
