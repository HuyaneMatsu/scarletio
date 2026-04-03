__all__ = ('Lock', 'ScarletLock')

from collections import deque

from .future import Future


class Lock:
    """
    Implements a mutex lock for hata tasks.

    A hata lock can be used to guarantee exclusive access to a shared resource.
    
    The preferred way of using a hata lock is with `async with` statement:
    
    ```py
    lock = Lock(loop)
    
    async with lock:
        # access resources
    ```
    
    You can also manually acquire and release locks, like:
    
    ```py
    lock = Lock(loop)
    
    await lock.acquire()
    try:
        # access resources
    finally:
        lock.release()
    ```
    
    Attributes
    ----------
    _loop : ``EventThread``
        The event loop to what the lock is bound to.
    _waiters : `deque` of ``Future``
        Futures on which the suspended tasks wait.
    """
    __slots__ = ('_loop', '_waiters', )
    
    def __new__(cls, loop):
        """
        Creates a new lock instance.
        
        loop : ``EventThread``
            The event loop to what the lock will be bound to.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._waiters = deque()
        return self
    
    
    async def __aenter__(self):
        """
        Acquires the lock.
        
        This method is a coroutine.
        """
        future = Future(self._loop)
        waiters = self._waiters
        waiters.appendleft(future)
        
        if len(waiters) > 1:
            waiter = waiters[1]
            try:
                await waiter
            except:
                try:
                    waiters.remove(waiter)
                except ValueError:
                    pass
                
                raise
    
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        """
        Releases the lock.
        
        This method is a coroutine.
        """
        future = self._waiters.pop()
        future.set_result_if_pending(None)
        return False
    
    
    def is_locked(self):
        """
        Returns whether the lock is entered anywhere.
        
        Returns
        -------
        is_locked: `bool`
        """
        if self._waiters:
            return True
        
        return False
    

    def __iter__(self):
        """
        Blocks until all the lock is unlocked everywhere. If lock is used meanwhile anywhere meanwhile the we acquire
        it, will await that as well.
        
        This method is a generator. Should be used with `await` expression.
        """
        waiters = self._waiters
        while waiters:
            yield from waiters[0]
    
    __await__ = __iter__
    
    acquire = __aenter__
    
    def release(self):
        """Releases the lock."""
        future = self._waiters.pop()
        future.set_result_if_pending(None)
    
    
    def __repr__(self):
        """Returns the lock's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
            ' locked = ',
        ]
        
        count = len(self._waiters)
        if count:
            repr_parts.append('True, waiting = ')
            repr_parts.append(repr(count))
        else:
            repr_parts.append('False')
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)


class ScarletLock(Lock):
    """
    A scarletio scarlet lock can be used to guarantee access to a shared resource `n` amount of times.
    
    Should be used with `async with` statement.
    
    Attributes
    ----------
    _loop : ``EventThread``
        The event loop to what the lock is bound to.
    _waiters : `deque` of ``Future``
        Futures on which the suspended tasks wait.
    _size : `int`
        The maximal amount of parallel entries to this lock.
    """
    __slots__ = ('_size',)
    
    def __new__(cls, loop, size = 1):
        """
        Creates a new lock instance.
        
        loop : ``EventThread``
            The event loop to what the lock will be bound to.
        size : `int`
            The maximal amount of parallel entries to this lock.
        
        Raises
        ------
        TypeError
            `size` is not given as `int`.
        ValueError
            `size` is given as non negative `int`.
        """
        size_type = size.__class__
        if size_type is int:
            pass
        elif issubclass(size_type, int):
            size = int(size)
        else:
            raise TypeError(
                f'`size` can be `int`, got {size_type.__name__}; {size!r}.'
            )
        
        if size < 1:
            raise ValueError(
                f'`size` can be only positive, got {size!r}.'
            )
        
        self = object.__new__(cls)
        self._loop = loop
        self._waiters = deque()
        self._size = size
        
        return self
    
    async def __aenter__(self):
        """
        Acquires the lock.
        
        This method is a coroutine.
        """
        future = Future(self._loop)
        waiters = self._waiters
        waiters.appendleft(future)
        
        size = self._size
        if len(waiters) > size:
            waiter = waiters[size]
            try:
                await waiter
            except:
                try:
                    waiters.remove(waiter)
                except ValueError:
                    pass
                
                raise
    
    acquire = __aenter__
    
    def get_size(self):
        """
        Returns the size of the ``ScarletLock``
        
        Returns
        -------
        size : `int`
        """
        return self._size
    
    
    def get_acquired(self):
        """
        Returns how much times the lock is acquired currently. Caps at the size of the lock.
        
        Returns
        --------
        acquired : `int`
        """
        waiter_count = len(self._waiters)
        size = self._size
        if waiter_count > size:
            waiter_count = size
        
        return waiter_count
    
    
    def get_waiting(self):
        """
        Returns how tasks are waiting to acquire the lock.
        
        Returns
        --------
        waiting : `int`
        """
        waiter_count = len(self._waiters)
        size = self._size
        if waiter_count > size:
            waiting = waiter_count - size
        else:
            waiting = 0
        
        return waiting
    
    # returns True if the Lock is entered anywhere
    def is_locked(self):
        """
        Returns whether the lock is entered same or more times than ``.size`` is set to.
        
        Returns
        -------
        is_locked: `bool`
        """
        if len(self._waiters) >= self._size:
            return True
        
        return False
    
    
    def __repr__(self):
        """Returns the scarlet lock's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
            ' size = ',
        ]
        
        size = self._size
        repr_parts.append(repr(size))
        
        repr_parts.append(', locked = ')
        count = len(self._waiters)
        if count >= size:
            repr_parts.append('True')
        else:
            repr_parts.append('False')
        
        if count:
            repr_parts.append(', waiting = ')
            repr_parts.append(repr(count))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
