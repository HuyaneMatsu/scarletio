__all__ = ('TaskGroup',)

from types import MethodType

from ...utils import RichAttributeErrorBaseType, WeakReferer

from .future import Future
from .task import Task


def _context_manager_leaver_cancel_on_exception(task_group, exception):
    """
    Context manager leaver that cancels the task of the given task group on exception.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The wrapped task group by the context manager.
    exception : `None`, `BaseException`
        The occurred exception if any.
    
    Returns
    -------
    captured : `bool`
        Whether the exception was captured.
    """
    if (exception is not None):
        task_group.cancel_all()
    
    return False


class TaskGroupContextManager(RichAttributeErrorBaseType):
    """
    Task group context manager.
    
    Attributes
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    leaver : `FunctionType`
        Function to call when the context is left.
        
        Can be implemented as:
        - `(Taskgroup, None | BaseException) -> bool`
    """
    __slots__ = ('leaver', 'task_group')
    
    def __new__(cls, task_group, leaver):
        """
        Creates a new task group context manager.
        
        Parameters
        ----------
        task_group : ``TaskGroup``
            The parent task group.
        leaver : `FunctionType`
            Function to call when the context is left.
        """
        self = object.__new__(cls)
        self.leaver = leaver
        self.task_group = task_group
        return self
    
    
    def __enter__(self):
        """
        Enters the context manager.
        
        Returns
        -------
        task_group : ``TaskGroup``
        """
        return self.task_group
    
    
    def __exit__(self, exception_type, exception, exception_traceback):
        """
        Exits the context manager.
        
        Parameters
        ----------
        exception_type : `None`, `type<BaseException>`
            The occurred exception's type if any.
        exception : `None`, `BaseException`
            The occurred exception if any.
        exception_traceback : `None`, `TracebackType`
            the exception's traceback if any.
        
        Returns
        -------
        captured : `bool`
            Whether the exception was captured.
        """
        return self.leaver(self.task_group, exception)
    
    
    def __repr__(self):
        """Returns the task group context manager representation."""
        return f'<{self.__class__.__name__} task_group = {self.taskk_group}, leaver = {self.leaver.__name__}>'


def _handler_wait_next():
    """
    Task group handler waiting for the next finishing task.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : `Nobe`
        Yes, we return `None`.
    """
    yield 1
    return 1, None


def _handler_wait_first(task_group):
    """
    Task group handler waiting for the first task to finish.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first done task.
    """
    done = task_group.done
    if done:
        return 1, next(iter(done))
    
    return 1, (yield 1)


def _handler_wait_first_and_pop(task_group):
    """
    Task group handler waiting for the first task to finish.
    
    The finished task will be popped from the task group's `.done`.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first done task.
    """
    done = task_group.done
    if done:
        return 1, done.pop()
    
    return 0, (yield 0)


def _handler_wait_exception(task_group):
    """
    Task group handler waiting for the first task to finish with an exception.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first failing task.
    """
    for future in task_group.done:
        if future._exception is not None:
            return 1, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._exception is not None:
            return 1, future


def _handler_wait_exception_and_pop(task_group):
    """
    Task group handler waiting for the first task to finish with an exception.
    
    The finished task will be popped from the task group's `.done`.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first failing task.
    """
    for future in task_group.done:
        if future._exception is not None:
            task_group.done.discard(future)
            return 0, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._exception is not None:
            return 0, future


def _handler_wait_first_n(task_group, required_count):
    """
    Task group handler waiting for the first `0` task to finish.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    Returns
    -------
    done_count : `int`
        The amount of done futures.
    """
    done_count = len(task_group.done)
    while True:
        if done_count >= required_count:
            return 1, done_count
        
        (yield 1)
        done_count += 1


def _handler_wait_all(task_group):
    """
    Task group handler waiting for all tasks to finish.
    
    Parameters
    ----------
    task_group : ``TaskGroup``
        The parent task group.
    
    Yield
    -----
    should_add_to_done : `int`
        Whether the task should be added to done.
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    task_group : ``TaskGroup``
        The task group itself.
    """
    pending = task_group.pending
    while True:
        if not pending:
            return 1, task_group
        
        yield 1


def _waited_done_callback_with_weak_self(task_group_reference, future):
    """
    Calls ``TaskGroup._waited_done_callback`` if ``TaskGroup`` has not been garbage collected yet.
    
    Parameters
    ----------
    task_group_reference : ``WeakReferer`` to ``TaskGroup``
        Weak reference to a task group.
    future : ``Future``
        The completed future.
    """
    task_group = task_group_reference()
    if (task_group is not None):
        task_group._waited_done_callback(future)


class TaskGroup(RichAttributeErrorBaseType):
    """
    Represents grouped tasks (actually futures) on which it is possible to execute shared operations.
    
    Attributes
    ----------
    _callback : `MethodType`
        Callback put on pending futures.
    done : `set` of ``Future``
        The done tasks.
    loop : ``EventThread``
        The event loop used.
    pending : `set` pf ``Future``
        The pending tasks.
    waiters : `dict` of (``Future``, ``Generator``)
        Contains the active waiters with their handlers.
    """
    __slots__ = ('__weakref__', '_callback', 'done', 'loop', 'pending', 'waiters')
    
    def __new__(cls, loop, tasks = None):
        """
        Creates a new task group.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to use.
        tasks : `None`, `iterable` of ``Future``
            Tasks (actually futures) to create the group with. 
        """
        done = set()
        pending = set()
        
        if (tasks is not None):
            for task in tasks:
                (done if task.is_done() else pending).add(task)
        
        self = object.__new__(cls)
        self.done = done
        self.loop = loop
        self.pending = pending
        self.waiters = {}
        callback = MethodType(_waited_done_callback_with_weak_self, WeakReferer(self))
        self._callback = callback
        
        if pending:
            for task in pending:
                task.add_done_callback(callback)
        
        return self
    
    
    def __repr__(self):
        """Returns the task group's representation."""
        return f'<{self.__class__.__name__} done = {self.done!r}, pending = {self.pending!r}>'
    
    
    def _waited_done_callback(self, future):
        """
        Called when a waited future is done.
        
        Moves the future into the done ones and
        
        Parameters
        ----------
        future : ``Future``
            An added future.
        """
        self.pending.discard(future)
    
        done_waiters = None
        should_add_to_done = 1
        
        for waiter, handler in self.waiters.items():
            try:
                should_add_to_done &= handler.send(future)
            except StopIteration as err:
                result = err.value
                should_add_to_done &= result[0]
                waiter.set_result_if_pending(result[1])
                
                if done_waiters is None:
                    done_waiters = []
                done_waiters.append(waiter)
            
            except BaseException as err:
                waiter.set_exception_if_pending(err)
                
                if done_waiters is None:
                    done_waiters = []
                done_waiters.append(waiter)
        
        if should_add_to_done:
            self.done.add(future)
        
        if (done_waiters is not None):
            for waiter in done_waiters:
                try:
                    del self.waiters[waiter]
                except KeyError:
                    pass
    
    
    def _waiter_done_callback(self, future):
        """
        Called when a waiter future is done.
        
        Closes the waiter's handler.
        
        Parameters
        ----------
        future : `bool`
        """
        try:
            handler = self.waiters.pop(future)
        except KeyError:
            pass
        else:
            handler.close()
    
    
    def _add_handler(self, handler):
        """
        Adds a new handler to the task group.
        
        Parameters
        ----------
        handler : `GeneratorType`
            Handler to use.
        
        Returns
        -------
        waiter : ``Future``
        """
        waiter = Future(self.loop)
        
        try:
            handler.send(None)
        except StopIteration as err:
            waiter.set_result_if_pending(err.value[1])
        except BaseException as err:
            waiter.set_exception_if_pending(err)
        else:
            self.waiters[waiter] = handler
            waiter.add_done_callback(self._waiter_done_callback)
        
        return waiter
    
    # Registering
    
    def add_future(self, future):
        """
        Adds a new future (or task) to the task group.
        
        Parameters
        ----------
        future : ``Future``
            The future to add.
        
        Returns
        -------
        future : ``Future``
        """
        if future.is_done():
            self._waited_done_callback(future)
        else:
            future.add_done_callback(self._callback)
            self.pending.add(future)
        
        return future
    
    
    add_task = add_future
    
    
    def add_awaitable(self, coroutine_or_future):
        """
        Adds the given coroutine or future to the task group.
        
        Parameters
        ----------
        coroutine_or_future : `awaitable`
            The coroutine or future to add.
        
        Returns
        -------
        future : ``Future``
        
        Raises
        ------
        TypeError
            If `coroutine_or_future` is not `awaitable`.
        """
        return self.add_future(self.loop.ensure_future(coroutine_or_future))
    
    
    def create_future(self):
        """
        Creates a new future and adds it to the task group.
        
        Returns
        -------
        future : ``Future``
        """
        future = Future(self.loop)
        future.add_done_callback(self._callback)
        self.pending.add(future)
        return future
    
    
    def create_task(self, coroutine):
        """
        Creates a new task and adds it to the task group.
        
        Parameters
        ----------
        coroutine : ``Coroutine``, ``Generator``
            The coroutine to create task with.
        
        Returns
        -------
        task : ``Task``
        """
        task = Task(coroutine, self.loop)
        task.add_done_callback(self._callback)
        self.pending.add(task)
        return task
    
    # Simple utility
    
    def pop_done(self):
        """
        Pops a done task from the group.
        
        Returns
        -------
        future : `None`, ``Future``
        """
        done = self.done
        if done:
            return done.pop()
    
    
    def has_done(self):
        """
        Returns whether there are done tasks in the group.
        
        Returns
        -------
        has_done : `bool`
        """
        return True if self.done else False
    
    
    def has_pending(self):
        """
        Returns whether there are pending tasks in the group.
        
        Returns
        -------
        has_pending : `bool`
        """
        return True if self.pending else False
    
    
    def cancel_all(self):
        """
        Cancels the done and the pending tasks of the task group.
        """
        for future in self.done:
            future.cancel()
            
        for future in self.pending:
            future.cancel()
    
    
    def cancel_done(self):
        """
        Cancels the done tasks of the task group.
        """
        for future in self.done:
            future.cancel()
    
    
    def cancel_pending(self):
        """
        Cancels the pending tasks of the task group.
        """
        for future in self.pending:
            future.cancel()
    
    # Waiters
    
    def wait_next(self):
        """
        Waits till the next future is completed.
        
        Returns
        -------
        waiter : ``Future``
        """
        return self._add_handler(_handler_wait_next())
        
    
    def wait_first(self):
        """
        Waits for the first task to complete and propagates its result.
        
        Returns
        -------
        waiter : ``Future`` -> ``Future``
            After awaiting the waiter propagates the first done task.
        """
        return self._add_handler(_handler_wait_first(self))
    
    
    def wait_first_and_pop(self):
        """
        Waits for the first task to complete and propagates its result.
        
        Removes the done task from the task group.
        
        Returns
        -------
        waiter : ``Future`` -> ``Future``
            After awaiting the waiter propagates the first done task.
        """
        return self._add_handler(_handler_wait_first_and_pop(self))
    
    
    def wait_exception(self):
        """
        Waits till the first task fails with an exception, or till all is done obviously.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.
        """
        return self._add_handler(_handler_wait_exception(self))
    
    
    def wait_exception_and_pop(self):
        """
        Waits till the first task fails with an exception, or till all is done obviously.
        
        Removes the done task from the task group.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.
        """
        return self._add_handler(_handler_wait_exception_and_pop(self))
    
    
    def wait_first_n(self, count):
        """
        Waits for the first `n` tasks to complete.
        
        Parameters
        ----------
        count : `int`
            The required amount of futures to wait for.
        
        Returns
        -------
        waiter : ``Future`` -> `int`
            After awaiting the waiter propagates the amount of done tasks.
            
            This amount can be higher than `count` if there are initially more done tasks in the task group.
            It can also be less than the amount of done tasks inside of task group if any was popped from it.
        """
        return self._add_handler(_handler_wait_first_n(self, count))
    
    
    def wait_all(self):
        """
        Waits till all the tasks are completed.
        
        Returns
        -------
        waiter : ``Future`` -> `self`
            A future to be waited propagating the task group itself.
        """
        return self._add_handler(_handler_wait_all(self))
    
    # Iterators
    
    def exhaust_done(self):
        """
        Iterates over the done tasks ands pops them.
        
        This method is an iterable generator.
        
        Yields
        ------
        future : ``Future``
        """
        done = self.done
        while done:
            yield done.pop()
    
    
    async def exhaust(self):
        """
        Async iterates over the added tasks. As one is done, yields and pops it.
        
        This method is a coroutine generator.
        
        Yields
        ------
        future : ``Future``
        """
        done = self.done
        pending = self.pending
        
        while True:
            while done:
                yield done.pop()
            
            if not pending:
                return
            
            waiter = self.wait_next()
            try:
                await waiter
            except GeneratorExit:
                waiter.cancel()
                raise
    
    # Context managers
    
    def cancel_on_exception(self):
        """
        Returns a context manager that can be used to cancel the task group if an exception occurs.
        
        Returns
        -------
        context_manager : ``TaskGroupContextManager``
        """
        return TaskGroupContextManager(self, _context_manager_leaver_cancel_on_exception)
