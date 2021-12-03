__all__ = ('enter_executor',)

from types import GeneratorType

from threading import current_thread

from ...utils import ignore_frame, include
from ..exceptions import CancelledError
from .future import Future, FUTURE_STATE_PENDING, FUTURE_STATE_CANCELLED
from .task import Task

ignore_frame(__spec__.origin, 'result', 'raise exception',)
ignore_frame(__spec__.origin, '__iter__', 'yield self',)

EventThread = include('EventThread')

class enter_executor:
    """
    Async context manager for moving a ``Task``'s section's execution to an executor thread.
    
    Usage
    -----
    ```py
    # Do async code
    async with enter_executor():
        # Do blocking stuff
        # Also async operation are still possible, but not recommended, because they cause my thread switch.
    
    # Do async code
    ```
    
    Attributes
    ----------
    _enter_future : `None` or ``Future``
        The future, what blocks the task's the execution, meanwhile the thread switch is taking place.
    _exit_future : `None` or ``Future``
        The future, what blocks the task's execution, meanwhile the thread is switching back.
    _waited_future : `None` or ``Future`` instance
        Blocking future used inside of the task, meanwhile it is in executor.
    _task : `None` or ``Task``
    """
    __slots__ = ('_enter_future', '_exit_future', '_waited_future', '_task')
    
    def __init__(self):
        self._enter_future = None
        self._task = None
        self._exit_future=None
        self._waited_future = None
    
    
    async def __aenter__(self):
        """
        Moves the current tasks's execution to an executor thread.
        
        This method is a coroutine.
        
        Raises
        ------
        RuntimeError
            - Called from outside of an ``EventThread``.
            - Called from outside of a ``Task``.
        """
        thread = current_thread()
        if not isinstance(thread, EventThread):
            raise RuntimeError(f'{self.__class__.__name__} used outside of {EventThread.__name__}, at {thread!r}.')
        
        task = thread.current_task
        if task is None:
            raise RuntimeError(f'{self.__class__.__name__} used outside of a {Task.__name__}.')
        
        self._task = task
        loop = task._loop
        future = Future(loop)
        self._enter_future = future
        loop.call_soon(self._enter_executor)
        await future
        return self
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Moves the current task's executor back from an executor thread.
        
        This method is a coroutine.
        """
        await self._exit_future
        self._enter_future = None
        self._task = None
        self._exit_future = None
        self._waited_future = None
        return False
    
    
    def _enter_executor(self):
        """
        Moves the task's execution to an executor thread and wakes it up.
        """
        callbacks = self._enter_future._callbacks
        callbacks.clear()
        
        task = self._task
        task.add_done_callback(self._cancel_callback)
        
        task._loop.run_in_executor(self._executor_task)
    
    
    def _cancel_callback(self, future):
        """
        Callback added to the wrapped task. If the wrapped task is cancelled, then the section running inside of the
        executor will be cancelled as well, whenever it gives back the context with an `await`.
        """
        if future._state != FUTURE_STATE_CANCELLED:
            return
        
        waited_future = self._waited_future
        if waited_future is None:
            return
        
        waited_future.cancel()
    
    
    def _executor_task(self):
        """
        Wraps the tasks's section's running inside of an executor, still allowing it to use `await`-s.
        """
        task = self._task
        # relink future task
        loop = task._loop
        end_future = Future(loop)
        task._waited_future = end_future
        self._exit_future = end_future
        
        # Set result to the enter task, so it can be retrieved.
        self._enter_future.set_result(None)
        
        exception = None
        coroutine = task._coroutine
        
        # If some1 await at the block, we will sync_wrap it. If the exit future is awaited, then we quit.
        local_waited_future = None
        
        try:
            while True:
                if task._must_cancel:
                    exception = task._must_exception(exception)
                    
                if (local_waited_future is not None):
                    if local_waited_future is end_future:
                        end_future.set_result(None)
                        loop.call_soon_thread_safe(task._step, exception)
                        break
                    
                    try:
                        self._waited_future = local_waited_future
                        if type(exception) is CancelledError:
                            local_waited_future.cancel()
                        local_waited_future.sync_wrap().wait()
                    
                    except CancelledError:
                        break
                    except BaseException as err:
                        exception = err
                    finally:
                        local_waited_future = None
                        self._waited_future = None
                
                if task._state != FUTURE_STATE_PENDING:
                    # there is no reason to raise
                    break
                
                # call either coroutine.throw(err) or coroutine.send(None).
                try:
                    if exception is None:
                        result = coroutine.send(None)
                    else:
                        result = coroutine.throw(exception)
                
                except StopIteration as exception:
                    if task._must_cancel:
                        # the task is cancelled meanwhile
                        task._must_cancel = False
                        Future.set_exception(task, CancelledError())
                    else:
                        Future.set_result(task, exception.value)
                    
                    loop.wake_up()
                    break
                    
                except CancelledError:
                    Future.cancel(task)
                    loop.wake_up()
                    break
                
                except BaseException as exception:
                    Future.set_exception(task, exception)
                    loop.wake_up()
                    break
                
                else:
                    try:
                        blocking = result._blocking
                    except AttributeError:
                        if result is None:
                            # bare yield relinquishes control for one event loop iteration.
                            continue
                        
                        elif isinstance(result, GeneratorType):
                            #Yielding a generator is just wrong.
                            exception = RuntimeError(f'`yield` was used instead of `yield from` in '
                                f'{self.__class__.__name__} {self!r} with `{result!r}`')
                            continue
                            
                        else:
                            # yielding something else is an error.
                            exception = RuntimeError(f'{self.__class__.__name__} got bad yield: `{result!r}`')
                            continue
                    else:
                        if blocking:
                            if loop is not result._loop:
                                exception = RuntimeError(f'{self.__class__.__name__} {self!r} got a Future {result!r} '
                                    f'attached to a different loop')
                                continue
                            
                            elif result is self:
                                exception = RuntimeError(f'{self.__class__.__name__} cannot await on itself: {self!r}')
                                continue
                            
                            else:
                                result._blocking = False
                                local_waited_future = result
                                if task._must_cancel:
                                    if local_waited_future.cancel():
                                        task._must_cancel = False
                                
                                continue
                        else:
                            exception = RuntimeError(f'`yield` was used instead of `yield from` in task {self!r} with '
                                f'{result!r}')
                            continue
        finally:
            task.remove_done_callback(self._cancel_callback)
            self = None
            task = None
