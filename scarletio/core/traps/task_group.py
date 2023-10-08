__all__ = ('TaskGroup',)

from ...utils import RichAttributeErrorBaseType

from .future import Future
from .future_states import FUTURE_STATE_CANCELLED, FUTURE_STATE_RESULT_RAISE
from .task import Task


FUTURE_STATE_CANCELLED_OR_RAISE = FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE


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
    
    if task_group.pending:
        return 1, (yield 1)
    
    return 1, None


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
    
    if task_group.pending:
        return 0, (yield 0)
    
    return 1, None
    

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
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first failing task.
    """
    for future in task_group.done:
        if future._state & FUTURE_STATE_RESULT_RAISE:
            return 1, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._state & FUTURE_STATE_RESULT_RAISE:
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
    
    Returns
    -------
    should_add_to_done : `int`
        Whether the task should be added to done.
    result : ``Future``
        The first failing task.
    """
    for future in task_group.done:
        if future._state & FUTURE_STATE_RESULT_RAISE:
            task_group.done.discard(future)
            return 0, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._state & FUTURE_STATE_RESULT_RAISE:
            return 0, future


def _handler_wait_exception_or_cancellation(task_group):
    """
    Task group handler waiting for the first task to finish with an exception or with cancellation.
    
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
        The first failing task.
    """
    for future in task_group.done:
        if future._state & FUTURE_STATE_CANCELLED_OR_RAISE:
            return 1, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._state & FUTURE_STATE_CANCELLED_OR_RAISE:
            return 1, future


def _handler_wait_exception_or_cancellation_and_pop(task_group):
    """
    Task group handler waiting for the first task to finish with an exception or cancellation.
    
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
        The first failing task.
    """
    for future in task_group.done:
        if future._state & FUTURE_STATE_CANCELLED_OR_RAISE:
            task_group.done.discard(future)
            return 0, future
    
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        future = (yield 1)
        if future._state & FUTURE_STATE_CANCELLED_OR_RAISE:
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
    dummy : `None`
        Dummy value.
    """
    pending = task_group.pending
    while True:
        if not pending:
            return 1, None
        
        yield 1


class TaskGroup(RichAttributeErrorBaseType):
    """
    Represents grouped tasks (actually futures) on which it is possible to execute shared operations.
    
    Attributes
    ----------
    done : `set` of ``Future``
        The done tasks.
    loop : ``EventThread``
        The event loop used.
    pending : `set` pf ``Future``
        The pending tasks.
    waiters : `dict` of (``Future``, ``Generator``)
        Contains the active waiters with their handlers.
    """
    __slots__ = ('done', 'loop', 'pending', 'waiters')
    
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
        
        if pending:
            for task in pending:
                task.add_done_callback(self._waited_done_callback)
        
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
        
        Examples
        --------
        ```py3
        task_group = TaskGroup(loop)
        task_group.add_future(Task(loop, coro(12)))
        task_group.add_future(Future(loop))
        
        # Equals to:
        
        task_group = TaskGroup(loop, [Task(loop, coro(12)), Future(loop)])
        ```
        """
        if future.is_done():
            self._waited_done_callback(future)
        else:
            future.add_done_callback(self._waited_done_callback)
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
        
        Examples
        --------
        ```py3
        task_group = TaskGroup(loop)
        task_group.add_awaitable(coro(12))
        task_group.add_awaitable(Future(loop))
        
        # Equals to:
        
        task_group = TaskGroup(loop, [Task(loop, coro(12)), Future(loop)])
        ```
        """
        return self.add_future(self.loop.ensure_future(coroutine_or_future))
    
    
    def create_future(self):
        """
        Creates a new future and adds it to the task group.
        
        Returns
        -------
        future : ``Future``
        
        Examples
        --------
        ```py3
        task_group = TaskGroup(loop)
        future = task_group.create_future()
        
        # Equals to:
        
        task_group = TaskGroup(loop, [Future(loop)])
        ```
        """
        future = Future(self.loop)
        future.add_done_callback(self._waited_done_callback)
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
        
        Examples
        --------
        ```py3
        task_group = TaskGroup(loop)
        task = task_group.create_task(coro(11))
        
        # Equals to:
        
        task_group = TaskGroup(loop, [Task(loop, coro(11))])
        ```
        """
        task = Task(self.loop, coroutine)
        task.add_done_callback(self._waited_done_callback)
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
        
        Not like ``.wait_first`` this will not trigger if there are already finished tasks, but will only trigger
        if a pending task is completed.
        
        Returns
        -------
        waiter : ``Future``
        
        Examples
        --------
        ```py
        future_0 = Future(loop)
        future_0.set_result(None)
        future_1 = sleep(2.0)
        
        task_group = TaskGroup(loop, [future_0, future_1])
        
        # After 2 seconds, we should retrieve `future_1`.
        next_done = await task_group.wait_next()
        
        assert next_done is future_1
        ```
        """
        return self._add_handler(_handler_wait_next())
    
    
    def wait_first(self):
        """
        Waits for the first task to complete and propagates it.
        
        If there are already done tasks, propagates one of them.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first done task.
        
        Examples
        --------
        ```py
        future_0 = sleep(1.0)
        future_1 = sleep(2.0)
        
        task_group = TaskGroup(loop, [future_0, future_1])
        
        # After 1 seconds, we should retrieve `future_0`.
        first_done = await task_group.wait_first()
        
        assert first_done is future_0
        ```
        """
        return self._add_handler(_handler_wait_first(self))
    
    
    def wait_first_and_pop(self):
        """
        Waits for the first task to complete and propagates it.
        
        If there are already done tasks, propagates one of them.
        
        Removes the propagated task from the task group.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first done task.
        """
        return self._add_handler(_handler_wait_first_and_pop(self))
    
    
    def wait_exception(self):
        """
        Waits till the first task fails with an exception, or till all is done obviously.
        
        If there is any task in the task group failing with an exception, propagates that.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.

        Examples
        --------
        ```py
        future_0 = Future(loop)
        future_0.apply_timeout(1.0)
        future_1 = sleep(2.0)
        
        task_group = TaskGroup(loop, [future_0, future_1])
        
        # After 1 second, we should retrieve `future_0`.
        first_failing_with_exception = await task_group.wait_exception()
        
        assert first_failing_with_exception is future_0
        ```
        """
        return self._add_handler(_handler_wait_exception(self))
    
    
    def wait_exception_and_pop(self):
        """
        Waits till the first task fails with an exception or till all is done obviously.
        
        If there is any task in the task group failing with an exception, propagates that.
        
        Familiar to ``.wait_exception``, but removes the propagated task from the task group.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.
        """
        return self._add_handler(_handler_wait_exception_and_pop(self))
    
    
    def wait_exception_or_cancellation(self):
        """
        Waits till the first task fails with an exception, is cancelled, or till all is done obviously.
        
        If there is any task in the task group failing with an exception or with cancellation, propagates that.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.

        Examples
        --------
        ```py
        future_0 = sleep(1)
        future_1 = Future(loop)
        future_1.cancel()
        
        task_group = TaskGroup(loop, [future_0, future_1])
        
        # we should retrieve `future_0` as soon as possible.
        first_failing_with_exception_or_cancellation = await task_group.wait_exception()
        
        assert first_failing_with_exception_or_cancellation is future_1
        ```
        """
        return self._add_handler(_handler_wait_exception_or_cancellation(self))
    
    
    def wait_exception_or_cancellation_and_pop(self):
        """
        Waits till the first task fails with an exception, is cancelled or till all is done obviously.
        
        If there is any task in the task group failing with an exception or with cancellation, propagates that.
        
        Familiar to ``.wait_exception``, but removes the propagated task from the task group.
        
        Returns
        -------
        waiter : ``Future`` -> `None` | ``Future``
            After awaiting the waiter propagates the first task that failed with an exception.
        """
        return self._add_handler(_handler_wait_exception_or_cancellation_and_pop(self))
    
    
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
        
        Examples
        --------
        ```py
        future_0 = sleep(0.0)
        future_1 = sleep(1.0)
        future_2 = sleep(2.0)
        
        task_group = TaskGroup(loop, [future_0, future_1, future_2])
        
        # After 1 seconds 2 tasks should be done.
        done_count = await task_group.wait_first_n(2)
        
        assert done_count == 2
        assert future_0.is_done()
        assert future_1.is_done()
        assert future_2.is_pending()
        ```
        """
        return self._add_handler(_handler_wait_first_n(self, count))
    
    
    def wait_all(self):
        """
        Waits till all the tasks are completed.
        
        Returns
        -------
        waiter : ``Future``
            A future to be waited propagating the task group itself.
        
        Examples
        --------
        ```py
        future_0 = sleep(0.0)
        future_1 = sleep(1.0)
        
        task_group = TaskGroup(loop, [future_0, future_1])
        
        # After 2 seconds all tasks are finished.
        await task_group.wait_all()
        
        assert not task_group.has_pending()
        ```
        """
        return self._add_handler(_handler_wait_all(self))
    
    # Iterators
    
    def iter_futures(self):
        """
        Iterates over the tasks of the task group.
        
        This function is an iterable generator.
        
        Yields
        ------
        future : ``Future``
        """
        yield from self.done
        yield from self.pending
    
    
    def exhaust_done(self):
        """
        Iterates over the done tasks ands pops them.
        
        This method is an iterable generator.
        
        Yields
        ------
        future : ``Future``
        
        Examples
        --------
        ```py
        task_group = TaskGroup(loop)
        
        task_group.create_future().set_result(None)
        task_group.create_future().set_result(None)
        task_group.add_future(sleep(1.0))
        
        # We have 2 done futures and 1 pending.
        done = [*task_group.exhaust_done()]
        
        assert len(done) == 2
        assert not task_group.has_done()
        assert task_group.has_pending()
        ```
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
        
        Examples
        --------
        ```py
        future_0 = sleep(0.0)
        future_1 = sleep(1.0)
        future_2 = sleep(2.0)
        task_group = TaskGroup(loop, [future_0, future_1, future_2])
        
        # After 2 second our iteration should end with the last done future.
        done_futures = []
        async for future in task_group.exhaust():
            done_futures.append(future)
        
        # We should get back the futures in their completion order.
        assert done_futures = [future_0, future_1, future_2]
        ```
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
        
        Examples
        --------
        ```py
        task_group = TaskGroup(loop)
        future = task_group.create_future()
        
        try:
            with task_group.cancel_on_exception():
                raise ValueError()
        finally:
            assert future.is_cancelled()
        ```
        """
        return TaskGroupContextManager(self, _context_manager_leaver_cancel_on_exception)
