__all__ = ('Cycler', 'EventThread', 'LOOP_TIME', 'LOOP_TIME_RESOLUTION', 'ThreadSuspenderContext', )

import sys, errno, weakref, subprocess, os
import socket as module_socket
from functools import partial as partial_func
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from threading import current_thread, Thread
from heapq import heappop, heappush
from collections import deque
from ssl import SSLContext, create_default_context
from stat import S_ISSOCK

IS_UNIX = (sys.platform != 'win32')

from ...utils import alchemy_incendiary, DOCS_ENABLED, set_docs, export, is_coroutine
from ...utils.trace import render_exception_into

from ..traps import Future, Task, Gatherer, FutureAsyncWrapper, WaitTillFirst
from ..time import LOOP_TIME, LOOP_TIME_RESOLUTION
from .event_loop_functionality_helpers import _HAS_IPv6, _is_stream_socket, _set_reuse_port, _ip_address_info, \
    EventThreadRunDescriptor
from .event_thread_type import EventThreadType
from .handles import Handle, TimerHandle, TimerWeakHandle
from .event_thread_suspender import ThreadSuspenderContext
from .server import Server
from .executor import Executor
from ..protocols_and_transports import ReadWriteProtocolBase, SocketTransportLayer, DatagramSocketTransportLayer, \
    SSLBidirectionalTransportLayer, UnixReadPipeTransportLayer, UnixWritePipeTransportLayer
from ..exceptions import CancelledError
from ..subprocess import AsyncProcess
from .cycler import Cycler

@export
class EventThread(Executor, Thread, metaclass=EventThreadType):
    """
    Event loops run asynchronous tasks and callbacks, perform network IO operations, and runs subprocesses.
    
    At hata event loops are represented by ``EventThread``-s, which do not block the source thread, as they say, they
    use their own thread for it.
    
    Attributes
    ----------
    claimed_executors : `set` of ``ExecutorThread``
        Claimed executors, which are given back to the executor on release.
    free_executors : `deque`
        The free (or not used) executors of the executor.
    keep_executor_count : `int`
        The minimal amount of executors to keep alive (or not close).
    running_executors : `set` of ``ExecutorThread``
        The executors under use.
    _async_generators: `WeakSet` of `async_generator`
        The asynchronous generators bound to the event loop.
    _async_generators_shutdown_called : `bool`
        Whether the event loop's asynchronous generators where shut down.
    _self_write_socket : `socket.socket`
        Socket, which can be used to wake up the thread by writing into it.
    _ready : `deque` of ``Handle`` instances
        Ready to run handles of the event loop.
    _scheduled : `list` of ``TimerHandle`` instances
        Scheduled timer handles, which will be moved to ``._ready`` when their `when` becomes lower or equal to the
        respective loop time.
    _self_read_socket : `socket.socket`
        Socket, which reads from ``._self_write_socket``.
    context : ``EventThreadContextManager``
        Context of the event loop to ensure it's safe startup and closing.
    current_task : `None` or ``Task``
        The actually running task of the event thread. Set only meanwhile a task is executed.
    running : `bool`
        Whether the event loop is running.
    selector : `selectors.Default_selector`
        Selector to poll from socket.
    should_run : `bool`
        Whether the event loop should do more loops.
    started : `bool`
        Whether the event loop was already started.
    
    Notes
    -----
    Event threads support weakreferencing and dynamic attribute names as well.
    """
    time = LOOP_TIME
    time_resolution = LOOP_TIME_RESOLUTION
    __slots__ = ('__dict__', '__weakref__', '_async_generators', '_async_generators_shutdown_called',
        '_self_write_socket', '_ready', '_scheduled', '_self_read_socket', 'context', 'current_task', 'running',
        'selector', 'should_run', 'started',)
    
    def __init__(self, keep_executor_count=1):
        """
        Creates a new ``EventThread`` with the given parameters.
        
        Parameters
        ----------
        keep_executor_count : `int`
            The minimal amount of executors, what the event thread should keep alive. Defaults to `1`.
        
        Notes
        -----
        This magic method is called by ``EventThreadType.__call__``, what does the other steps of the initialization.
        """
        Executor.__init__(self, keep_executor_count)
        self.should_run = True
        self.running = False
        self.started = False
        self.selector = DefaultSelector()
        
        self._ready = deque()
        self._scheduled = []
        self.current_task = None
        
        self._async_generators = weakref.WeakSet()
        self._async_generators_shutdown_called = False
        
        self._self_read_socket = None
        self._self_write_socket = None
    
    
    def is_started(self):
        """
        Returns whether the event loop was started.
        
        Returns
        -------
        is_started : `bool`
        """
        thread_waiter = self.context.thread_waiter
        if thread_waiter is None:
            return True
        
        if thread_waiter.is_set():
            return True
        
        return False
    
    
    def is_stopped(self):
        """
        Returns whether the event loop was stopped.
        
        Returns
        -------
        is_stopped : `bool`
        """
        if not self.started:
            is_stopped = False
        elif self._is_stopped or (not self.running):
            is_stopped = True
        else:
            is_stopped = False
        
        return is_stopped
    
    
    def _maybe_start(self):
        """
        Starts the event loop's thread if not yet started.
        
        Returns
        -------
        started : `bool`
            Whether the thread was started up.
        """
        if self.is_started():
            return False
        
        self._do_start()
        return True
    
    
    def _do_start(self):
        """
        Starts the event loop's thread.
        
        If the event loop is already started will to start it again.
        """
        thread_waiter = self.context.thread_waiter
        # set as `None` if already started.
        if thread_waiter is None:
            return
        
        if not self._started.is_set():
            try:
                Thread.start(self)
            except:
                thread_waiter.set()
                raise
        
        thread_waiter.wait()
    
    
    def __repr__(self):
        """Returns the event thread's representation."""
        repr_parts = ['<', self.__class__.__name__, '(', self._name]
        self.is_alive() # easy way to get ._is_stopped set when appropriate
        if not self.started:
            state = ' created'
        elif self._is_stopped or (not self.running):
            state = ' stopped'
        else:
            state = ' started'
        repr_parts.append(state)
        
        if self._daemonic:
            repr_parts.append(' daemon')
        
        ident = self._ident
        if (ident is not None):
            repr_parts.append(' ident=')
            repr_parts.append(str(ident))
        
        repr_parts.append(' executor info: free=')
        repr_parts.append(str(self.free_executor_count))
        repr_parts.append(', used=')
        repr_parts.append(str(self.used_executor_count))
        repr_parts.append(', keep=')
        repr_parts.append(str(self.keep_executor_count))
        repr_parts.append(')>')

        return ''.join(repr_parts)
    
    
    def call_later(self, delay, callback, *args):
        """
        Schedule callback to be called after the given delay.
        
        Parameters
        ----------
        delay : `float`
            The delay after the `callback` would be called.
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``TimerHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerHandle(LOOP_TIME()+delay, callback, args)
        heappush(self._scheduled, handle)
        return handle
    
    
    def call_at(self, when, callback, *args):
        """
        Schedule callback to be called at the given loop time.
        
        Parameters
        ----------
        when : `float`
            The exact loop time, when the callback should be called.
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``TimerHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerHandle(when, callback, args)
        heappush(self._scheduled, handle)
        return handle
    
    
    def call_later_weak(self, delay, callback, *args):
        """
        Schedule callback with weakreferencing it to be called after the given delay.
        
        Parameters
        ----------
        delay : `float`
            The delay after the `callback` would be called.
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``TimerWeakHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        
        Raises
        ------
        TypeError
            If `callback` cannot be weakreferenced.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerWeakHandle(LOOP_TIME()+delay, callback, args)
        heappush(self._scheduled, handle)
        return handle
    
    
    def call_at_weak(self, when, callback, *args):
        """
        Schedule callback with weakreferencing it to be called at the given loop time.
        
        Parameters
        ----------
        when : `float`
            The exact loop time, when the callback should be called.
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``TimerWeakHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        
        Raises
        ------
        TypeError
            If `callback` cannot be weakreferenced.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerWeakHandle(when, callback, args)
        heappush(self._scheduled, handle)
        return handle
    
    
    def call_soon(self, callback, *args):
        """
        Schedules the callback to be called at the next iteration of the event loop.
        
        Parameters
        ----------
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``Handle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = Handle(callback, args)
        self._ready.append(handle)
        return handle
    
    
    def call_soon_thread_safe(self, callback, *args):
        """
        Schedules the callback to be called at the next iteration of the event loop. Wakes up the event loop if sleeping,
        so can be used from other threads as well.
        
        Parameters
        ----------
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``Handle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = Handle(callback, args)
        self._ready.append(handle)
        self.wake_up()
        return handle
    
    
    def call_soon_thread_safe_lazy(self, callback, *args):
        """
        Schedules the callback to be called at the next iteration of the event loop. If the event loop is already
        running, wakes it up.
        
        Parameters
        ----------
        callback : `callable`
            The function to call later.
        *args : parameters
            The parameters to call the `callback` with.
        
        Returns
        -------
        handle : `None` or ``Handle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if self.running:
            should_wake_up = True
        else:
            if self.is_started():
                should_wake_up = True
            elif self.should_run:
                should_wake_up = False
            else:
                return None
        
        handle = Handle(callback, args)
        self._ready.append(handle)
        
        if should_wake_up:
            self.wake_up()
        
        return handle
    
    
    def cycle(self, cycle_time, *funcs, priority=0):
        """
        Cycles the given functions on an event loop, by calling them after every `n` amount of seconds.
        
        Parameters
        ----------
        cycle_time : `float`
            The time interval of the cycler to call the added functions.
        *funcs : `callable`
            Callables, what the cycler will call.
        priority : `int`
            Priority order of the added callables, which define in which order the given `funcs` will be called.
            Defaults to `0`
        
        Returns
        -------
        cycler : ``Cycler``
            A cycler with what the added function and the cycling can be managed.
        """
        return Cycler(self, cycle_time, *funcs, priority=priority)
    
    
    def _schedule_callbacks(self, future):
        """
        Schedules the callbacks of the given future.
        
        Parameters
        ----------
        future : ``Future`` instance
            The future instance, what's callbacks should be ensured.
        
        Notes
        -----
        If the event loop is not running, clears the callback instead of scheduling them.
        """
        callbacks = future._callbacks
        if not self.running:
            if not self._maybe_start():
                callbacks.clear()
                return
        
        while callbacks:
            handle = Handle(callbacks.pop(), (future,))
            self._ready.append(handle)
    
    
    def create_future(self):
        """
        Creates a future bound to the event loop.
        
        Returns
        -------
        future : ``Future``
            The created future.
        """
        return Future(self)
    
    
    def create_task(self, coroutine):
        """
        Creates a task wrapping the given coroutine.
        
        Parameters
        ----------
        coroutine : `CoroutineType` or `GeneratorType`
            The coroutine, to wrap.
        
        Returns
        -------
        task : ``Task``
            The created task instance.
        """
        return Task(coroutine, self)
    
    
    def create_task_thread_safe(self, coroutine):
        """
        Creates a task wrapping the given coroutine and wakes up the event loop. Wakes up the event loop if sleeping,
        what means it is safe to use from other threads as well.
        
        Parameters
        ----------
        coroutine : `CoroutineType` or `GeneratorType`
            The coroutine, to wrap.
        
        Returns
        -------
        task : ``Task``
            The created task instance.
        """
        task = Task(coroutine, self)
        self.wake_up()
        return task
    
    
    def enter(self):
        """
        Can be used to pause the event loop. Check ``ThreadSuspenderContext`` for more details.
        
        Returns
        -------
        thread_syncer : ``ThreadSuspenderContext``
        """
        return ThreadSuspenderContext(self)
    
    
    def ensure_future(self, coroutine_or_future):
        """
        Ensures the given coroutine or future on the event loop. Returns an awaitable ``Future`` instance.
        
        Parameters
        ----------
        coroutine_or_future : `awaitable`
            The coroutine or future to ensure.
        
        Returns
        -------
        future : ``Future`` instance.
            The return type depends on `coroutine_or_future`'s type.
            
            - If `coroutine_or_future` is given as `CoroutineType` or as `GeneratorType`, returns a ``Task`` instance.
            - If `coroutine_or_future` is given as ``Future`` instance, bound to the current event loop, returns it.
            - If `coroutine_or_future`is given as ``Future`` instance, bound to an other event loop, returns a
                ``FutureAsyncWrapper``.
            - If `coroutine_or_future` defines an `__await__` method, then returns a ``Task`` instance.
        
        Raises
        ------
        TypeError
            If `coroutine_or_future` is not `awaitable`.
        """
        if is_coroutine(coroutine_or_future):
            return Task(coroutine_or_future, self)
        
        if isinstance(coroutine_or_future, Future):
            if coroutine_or_future._loop is not self:
                coroutine_or_future = FutureAsyncWrapper(coroutine_or_future, self)
            return coroutine_or_future
        
        type_ = type(coroutine_or_future)
        if hasattr(type_, '__await__'):
            return Task(type_.__await__(coroutine_or_future), self)
        
        raise TypeError('A Future, a coroutine or an awaitable is required.')
    
    
    def ensure_future_thread_safe(self, coroutine_or_future):
        """
        Ensures the given coroutine or future on the event loop. Returns an awaitable ``Future`` instance. Wakes up
        the event loop if sleeping, what means it is safe to use from other threads as well.
        
        Parameters
        ----------
        coroutine_or_future : `awaitable`
            The coroutine or future to ensure.
        
        Returns
        -------
        future : ``Future`` instance.
            The return type depends on `coroutine_or_future`'s type.
            
            - If `coroutine_or_future` is given as `CoroutineType` or as `GeneratorType`, returns a ``Task`` instance.
            - If `coroutine_or_future` is given as ``Future`` instance, bound to the current event loop, returns it.
            - If `coroutine_or_future`is given as ``Future`` instance, bound to an other event loop, returns a
                ``FutureAsyncWrapper``.
            - If `coroutine_or_future` defines an `__await__` method, then returns a ``Task`` instance.
        
        Raises
        ------
        TypeError
            If `coroutine_or_future` is not `awaitable`.
        """
        if is_coroutine(coroutine_or_future):
            task = Task(coroutine_or_future, self)
            self.wake_up()
            return task
        
        if isinstance(coroutine_or_future, Future):
            if coroutine_or_future._loop is not self:
                coroutine_or_future = FutureAsyncWrapper(coroutine_or_future, self)
            return coroutine_or_future
        
        type_ = type(coroutine_or_future)
        if hasattr(type_, '__await__'):
            task = Task(type_.__await__(coroutine_or_future), self)
            self.wake_up()
            return task

        raise TypeError('A Future, a coroutine or an awaitable is required.')
    
    run = EventThreadRunDescriptor()
    
    def runner(self):
        """
        Runs the event loop, until ``.stop`` is called.
        
        Hata ``EventThread`` are created as already running event loops.
        """
        with self.context:
            key = None
            file_object = None
            reader = None
            writer = None
            
            ready = self._ready # use thread safe type with no lock
            scheduled = self._scheduled # these can be added only from this thread
            
            while self.should_run:
                timeout = LOOP_TIME()+LOOP_TIME_RESOLUTION # calculate limit
                while scheduled: # handle 'later' callbacks that are ready.
                    handle = scheduled[0]
                    if handle.cancelled:
                        heappop(scheduled)
                        continue
                    
                    if handle.when >= timeout:
                        break
                    
                    ready.append(handle)
                    heappop(scheduled)
                
                if ready:
                    timeout = 0.
                elif scheduled:
                    # compute the desired timeout.
                    timeout = scheduled[0].when-LOOP_TIME()
                else:
                    timeout = None
                
                event_list = self.selector.select(timeout)
                if event_list:
                    for key, mask in event_list:
                        file_object = key.fileobj
                        reader, writer = key.data
                        if (reader is not None) and (mask&EVENT_READ):
                            if reader.cancelled:
                                self.remove_reader(file_object)
                            else:
                                if not reader.cancelled:
                                    ready.append(reader)
                        if (writer is not None) and (mask&EVENT_WRITE):
                            if writer.cancelled:
                                self.remove_writer(file_object)
                            else:
                                if not writer.cancelled:
                                    ready.append(writer)
                    
                    key = None
                    file_object = None
                    reader = None
                    writer = None
                    
                event_list = None
                
                # process callbacks
                for _ in range(len(ready)):
                    handle = ready.popleft()
                    if not handle.cancelled:
                        handle._run()
                handle = None # remove from locals or the gc derps out.
    
    
    def caller(self, awaitable, timeout=None):
        """
        Ensures the given awaitable on the event loop and returns it's result when done.
        
        Parameters
        ----------
        awaitable : `awaitable`
            The awaitable to run.
        timeout : `None` or `float`, Optional
            Timeout after the awaitable should be cancelled. Defaults to `None`.

        Returns
        -------
        result : `Any`
            Value returned by `awaitable`.
        
        Raises
        ------
        TypeError
            If `awaitable` is not `awaitable`.
        TimeoutError
             If `awaitable` did not finish before the given `timeout` is over.
        AssertionError
            If called from itself.
        BaseException
            Any exception raised by `awaitable`.
        """
        if __debug__:
            if current_thread() is self:
                raise AssertionError(f'`{self.__class__.__name__}.run` should not be called from itself.')
        
        return self.ensure_future_thread_safe(awaitable).sync_wrap().wait(timeout)
    
    if __debug__:
        def render_exception_async(self, exception, before=None, after=None, file=None):
            future = self.run_in_executor(alchemy_incendiary(self._render_exception_sync, (exception, before, after, file),))
            future.__silence__()
            return future
        
        @classmethod
        def render_exception_maybe_async(cls, exception, before=None, after=None, file=None):
            local_thread = current_thread()
            if isinstance(local_thread, EventThread):
                future = local_thread.run_in_executor(alchemy_incendiary(cls._render_exception_sync,
                    (exception, before, after, file),))
                future.__silence__()
            else:
                cls._render_exception_sync(exception, before, after, file)
    
    else:
        def render_exception_async(self, exception, before=None, after=None, file=None):
            return self.run_in_executor(alchemy_incendiary(self._render_exception_sync, (exception, before, after, file),))
        
        @classmethod
        def render_exception_maybe_async(cls, exception, before=None, after=None, file=None):
            local_thread = current_thread()
            if isinstance(local_thread, EventThread):
                local_thread.run_in_executor(alchemy_incendiary(cls._render_exception_sync,
                    (exception, before, after, file),))
            else:
                cls._render_exception_sync(exception, before, after, file)
    
    if DOCS_ENABLED:
        render_exception_async.__doc__ = (
        """
        Renders the given exception's traceback in a non blocking way.
        
        Parameters
        ----------
        exception : ``BaseException``
            The exception to render.
        before : `None` or `str`, `list` of `str`, Optional
            Any content, what should go before the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.
        after : `None` or `str`, `list` of `str`, Optional
            Any content, what should go after the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.

        file : `None` or `I/O stream`, Optional
            The file to print the stack to. Defaults to `sys.stderr`.
        
        Returns
        -------
        future : ``Future``
            Returns a future, what can be awaited to wait for the rendering to be done.
        """)
    
    if DOCS_ENABLED:
        render_exception_maybe_async.__doc__ = (
        """
        Renders the given exception's traceback. If called from an ``EventThread`` instance, then will not block it.
        
        This method is called from function or methods, where being on an ``EventThread`` is not guaranteed.
        
        Parameters
        ----------
        exception : ``BaseException``
            The exception to render.
        before : `None` or `str`, `list` of `str`, Optional
            Any content, what should go before the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.
        after : `None` or `str`, `list` of `str`, Optional
            Any content, what should go after the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.

        file : `None` or `I/O stream`, Optional
            The file to print the stack to. Defaults to `sys.stderr`.
        """)
    
    @staticmethod
    def _render_exception_sync(exception, before, after, file):
        """
        Renders the given exception in a blocking way.
        
        Parameters
        ----------
        exception : ``BaseException``
            The exception to render.
        before : `str`, `list` of `str`
            Any content, what should go before the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.
        after : `str`, `list` of `str`
            Any content, what should go after the exception's traceback.
            
            If given as `str`, or if `list`, then the last element of it should end with linebreak.
        file : `None` or `I/O stream`
            The file to print the stack to. Defaults to `sys.stderr`.
        """
        extracted = []
        
        if before is None:
            pass
        elif isinstance(before, str):
            extracted.append(before)
        elif isinstance(before, list):
            for element in before:
                if type(element) is str:
                    extracted.append(element)
                else:
                    extracted.append(repr(element))
                    extracted.append('\n')
        else:
            # ignore exception cases
            extracted.append(repr(before))
            extracted.append('\n')
        
        render_exception_into(exception, extend=extracted)
        
        if after is None:
            pass
        elif isinstance(after, str):
            extracted.append(after)
        elif isinstance(after, list):
            for element in after:
                if type(element) is str:
                    extracted.append(element)
                else:
                    extracted.append(repr(element))
                    extracted.append('\n')
        else:
            extracted.append(repr(after))
            extracted.append('\n')
        
        if file is None:
            # ignore exception cases
            file = sys.stderr
        
        file.write(''.join(extracted))
    
    def stop(self):
        """
        Stops the event loop. Thread safe.
        """
        if self.should_run:
            if current_thread() is self:
                self._stop()
            else:
                self.call_soon(self._stop)
                self.wake_up()

    def _stop(self):
        """
        Stops the event loop. Internal function of ``.stop``, called or queued up by it.
        
        Should be called only from the thread of the event loop.
        """
        self.release_executors()
        self.should_run = False

    async def shutdown_async_generators(self):
        """
        Shuts down the asynchronous generators running on the event loop.
        
        This method is a coroutine.
        """
        self._async_generators_shutdown_called = True
        
        async_generators = self._async_generators
        if async_generators:
            return
        
        closing_async_generators = list(async_generators)
        async_generators.clear()
        
        results = await Gatherer(self, (ag.aclose() for ag in closing_async_generators))
        
        for result, async_generator in zip(results, closing_async_generators):
            exception = result.exception
            if (exception is not None) and (type(exception) is not CancelledError):
                extracted = [
                    'Exception occurred during shutting down async generator:\n',
                    repr(async_generator),
                ]
                render_exception_into(exception, extend=extracted)
                sys.stderr.write(''.join(extracted))
    
    
    def _make_socket_transport(self, socket, protocol, waiter=None, *, extra=None, server=None):
        """
        Creates a socket transport with the given parameters.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket, what the transport will use.
        protocol : `Any`
            The protocol of the transport.
        waiter : `None` or ``Future``, Optional
            Waiter, what's result should be set, when the transport is ready to use.
        extra : `None` or `dict` of (`str`, `Any`) item, Optional (Keyword only)
            Optional transport information.
        server : `None` or ``Server``, Optional (Keyword only)
            The server to what the created socket will be attached to.
        
        Returns
        -------
        transport : ``SocketTransportLayer``
        """
        return SocketTransportLayer(self, extra, socket, protocol, waiter, server)
    
    
    def _make_ssl_transport(self, socket, protocol, ssl, waiter=None, *, server_side=False, server_hostname=None,
            extra=None, server=None):
        """
        Creates an ssl transport with the given parameters.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket, what the transport will use.
        protocol : `Any`
            Asynchronous protocol implementation for the transport. The given protocol is wrapped into an
            ``SSLBidirectionalTransportLayer``
        ssl : ``ssl.SSLContext``
            Ssl context of the respective connection.
        waiter : `None` or ``Future``, Optional
            Waiter, what's result should be set, when the transport is ready to use.
        server_side : `bool`, Optional (Keyword only)
            Whether the created ssl transport is a server side. Defaults to `False`.
        server_hostname : `None` or `str`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            By default the value of the host parameter is used. If host is empty, there is no default and you must pass
            a value for `server_hostname`. If `server_hostname` is an empty string, hostname matching is disabled
            (which is a serious security risk, allowing for potential man-in-the-middle attacks).
        extra : `None` or `dict` of (`str`, `Any`) item, Optional (Keyword only)
            Optional transport information.
        server : `None` or ``Server``, Optional (Keyword only)
            The server to what the created socket will be attached to.
        
        Returns
        -------
        transport : ``_SSLBidirectionalTransportLayerTransport``
            The created ssl transport.
        """
        ssl_protocol = SSLBidirectionalTransportLayer(self, protocol, ssl, waiter, server_side, server_hostname)
        SocketTransportLayer(self, extra, socket, ssl_protocol, None, server)
        return ssl_protocol.app_transport
    
    
    def empty_self_socket(self):
        """
        Reads all the data out from self socket.
        
        Familiar to async-io event loop's `._read_from_self`.
        """
        while True:
            try:
                data = self._self_read_socket.recv(4096)
                if not data:
                    break
            except InterruptedError:
                continue
            except BlockingIOError:
                break
    
    
    def wake_up(self):
        """
        Wakes up the event loop. Thread safe.
        
        Familiar as async-io event loop's `._write_to_self`.
        """
        self_write_socket = self._self_write_socket
        if self_write_socket is None:
            if self.running:
                return
            
            # If we start it not needed to wake_up. If we don't, we wont wake_up anyway.
            self._maybe_start()
            return
        
        try:
            self_write_socket.send(b'\0')
        except OSError:
            pass
    
    
    def _start_serving(self, protocol_factory, socket, ssl=None, server=None, backlog=100):
        """
        Starts serving the given socket on the event loop. Called by ``Server.start``. Adds a reader callback for the
        socket, what will call ``._accept_connection``. (At edge cases ``._accept_connection`` might call this
        method as well for repeating itself after a a delay.)
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating an asynchronous compatible protocol.
        socket : `socket.socket`
            The sockets to serve by the respective server if applicable.
        ssl : `None` or `ssl.SSLContext`, Optional
            To enable ssl for the connections, give it as  `ssl.SSLContext`.
        server : `None` or ``Server``, Optional
            The respective server, what started to serve if applicable.
        backlog : `int`, Optional
            The maximum number of queued connections passed to `listen()` (defaults to 100).
        """
        self.add_reader(socket.fileno(), self._accept_connection, protocol_factory, socket, ssl, server, backlog)
    
    
    def _stop_serving(self, socket):
        """
        Stops serving the given socket. by removing it's reader callback and closing it.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket, what's respective reader callback will be removed if applicable.
        """
        self.remove_reader(socket.fileno())
        socket.close()
    
    
    def _accept_connection(self, protocol_factory, socket, ssl, server, backlog):
        """
        Callback added by ``._start_serving``, what is triggered by a read event. This method is only called once for
        each event loop tick. There may be multiple connections waiting for an `.accept()` so it is called in a loop.
        See `https://bugs.python.org/issue27906` for more details.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating an asynchronous compatible protocol.
        socket : `socket.socket`
            The sockets to serve by the respective server if applicable.
        ssl : `None` or `ssl.SSLContext`
            The ssl type of the connection if any.
        server : `None` or ``Server``
            The respective server if applicable.
        backlog : `int`, Optional
            The maximum number of queued connections passed to `listen()`.
        """
        for _ in range(backlog):
            try:
                connection_socket, address = socket.accept()
                connection_socket.setblocking(False)
            except (BlockingIOError, InterruptedError, ConnectionAbortedError):
                # Early exit because the socket accept buffer is empty.
                return None
            except OSError as err:
                # There's nowhere to send the error, so just log it.
                if err.errno in (errno.EMFILE, errno.ENFILE, errno.ENOBUFS, errno.ENOMEM):
                    # Some platforms (e.g. Linux keep reporting the FD as ready, so we remove the read handler
                    # temporarily. We'll try again in a while.
                    self.render_exception_async(
                        err,
                        before = [
                            'Exception occurred at',
                            repr(self),
                            '._accept_connection\n',
                        ],
                    )
                    
                    self.remove_reader(socket.fileno())
                    self.call_later(1., self._start_serving, protocol_factory, socket, ssl, server, backlog)
                else:
                    raise # The event loop will catch and log it.
            else:
                extra = {'peer_name': address}
                Task(self._accept_connection_task(protocol_factory, connection_socket, extra, ssl, server), self)
    
    
    async def _accept_connection_task(self, protocol_factory, connection_socket, extra, ssl, server):
        """
        Called by ``._accept_connection``, when a connection is accepted.
        
        Because ``._accept_connection`` might have more connections to accept, multiple tasks are launched up from
        this method to run parallelly.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating an asynchronous compatible protocol.
        connection_socket : `socket.socket`
            The accepted connection.
        extra : `None` or `dict` of (`str`, `Any`) item
            Optional transport information.
        ssl : `None` or `ssl.SSLContext`
            The ssl type of the connection if any.
        server : `None` or ``Server``
            The respective server if applicable.
        """
        try:
            protocol = protocol_factory()
            waiter = Future(self)
            if (ssl is None):
                transport = self._make_socket_transport(connection_socket, protocol, waiter=waiter, extra=extra,
                    server=server)
            else:
                transport = self._make_ssl_transport(connection_socket, protocol, ssl, waiter=waiter, server_side=True,
                    extra=extra, server=server)
            
            try:
                await waiter
            except:
                transport.close()
                raise
        
        except BaseException as err:
            self.render_exception_async(
                err,
                [
                    'Exception occurred at ',
                    self.__class__.__name__,
                    '._accept_connection2\n',
                ],
            )
    
    
    def add_reader(self, fd, callback, *args):
        """
        Registers read callback for the given fd.
        
        Parameters
        ----------
        fd : `int`
            The respective file descriptor.
        callback : `callable`
            The function, what is called, when data is received on the respective file descriptor.
        *args : Parameters
            Parameters to call `callback` with.
        """
        if not self.running:
            if not self._maybe_start():
                raise RuntimeError('Event loop stopped.')
        
        handle = Handle(callback, args)
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            self.selector.register(fd, EVENT_READ, (handle, None))
        else:
            mask = key.events
            reader, writer = key.data
            self.selector.modify(fd, mask|EVENT_READ, (handle, writer))
            if reader is not None:
                reader.cancel()
    
    
    def remove_reader(self, fd):
        """
        Removes a read callback for the given fd.
        
        Parameters
        ----------
        fd : `int`
            The respective file descriptor.
        
        Returns
        -------
        removed : `bool`
            Whether a reader callback was removed.
        """
        if not self.running:
            if not self._maybe_start():
                return False
        
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            return False
        
        mask = key.events
        reader, writer = key.data
        mask &= ~EVENT_READ
        
        if mask:
            self.selector.modify(fd, mask, (None, writer))
        else:
            self.selector.unregister(fd)
        
        if reader is not None:
            reader.cancel()
            return True
        
        return False
    
    
    def add_writer(self, fd, callback, *args):
        """
        Registers a write callback for the given fd.
        
        Parameters
        ----------
        fd : `int`
            The respective file descriptor.
        callback : `callable`
            The function, what is called, when data the respective file descriptor becomes writable.
        *args : Parameters
            Parameters to call `callback` with.
        """
        if not self.running:
            if not self._maybe_start():
                raise RuntimeError('Event loop is cancelled.')
        
        handle = Handle(callback, args)
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            self.selector.register(fd, EVENT_WRITE, (None, handle))
            return
        
        mask = key.events
        reader, writer = key.data
        
        self.selector.modify(fd, mask|EVENT_WRITE, (reader, handle))
        if writer is not None:
            writer.cancel()
    
    
    def remove_writer(self, fd):
        """
        Removes a write callback for the given fd.
        
        Parameters
        ----------
        fd : `int`
            The respective file descriptor.
        
        Returns
        -------
        removed : `bool`
            Whether a writer callback was removed.
        """
        if not self.running:
            if not self._maybe_start():
                return False
        
        try:
            key = self.selector.get_key(fd)
        except KeyError:
            return False
        
        mask = key.events
        reader, writer = key.data
        # remove both writer and connector.
        mask &= ~EVENT_WRITE
        if mask:
            self.selector.modify(fd, mask, (reader, None))
        else:
            self.selector.unregister(fd)
            
        if writer is not None:
            writer.cancel()
            return True
        
        return False
    
    
    async def connect_accepted_socket(self, protocol_factory, socket, *, ssl=None):
        """
        Wrap an already accepted connection into a transport/protocol pair.
        
        This method can be used by servers that accept connections outside of hata but use it to handle them.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        socket : `socket.socket`
            A preexisting socket object returned from `socket.accept`.
        ssl : `None` or `ssl.SSLContext`, Optional (Keyword only)
            Whether ssl should be enabled.
        
        Returns
        -------
        transport : ``_SSLBidirectionalTransportLayerTransport`` or ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``_SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : `Any`
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            If `socket` is not a stream socket.
        """
        if not _is_stream_socket(socket):
            raise ValueError(f'A stream socket was expected, got {socket!r}.')
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, '', True)
    
    
    async def create_connection(self, protocol_factory, host=None, port=None, *, ssl=None, family=0, protocol=0,
            flags=0, socket=None, local_address=None, server_hostname=None):
        """
        Open a streaming transport connection to a given address specified by `host` and `port`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        host : `None` or `str`, Optional
            To what network interfaces should the connection be bound.
            
            Mutually exclusive with the `socket` parameter.
        port : `None` or `int`, Optional
            The port of the `host`.
            
            Mutually exclusive with the `socket` parameter.
        ssl : `None`, `bool` or `ssl.SSLContext`, Optional (Keyword only)
            Whether ssl should be enabled.
        family : `AddressFamily` or `int`, Optional (Keyword only)
            Can be either `AF_INET`, `AF_INET6` or `AF_UNIX`.
        protocol : `int`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        flags : `int`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        socket : `None` or `socket.socket`, Optional (Keyword only)
            Whether should use an existing, already connected socket.
            
            Mutually exclusive with the `host` and the `port` parameters.
        local_address : `tuple` of (`None` or  `str`, `None` or `int`), Optional (Keyword only)
            Can be given as a `tuple` (`local_host`, `local_port`) to bind the socket locally. The `local_host` and
            `local_port` are looked up by ``.get_address_info``.
        server_hostname : `None` or `str`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If host
            is empty, there is no default and you must pass a value for `server_hostname`. If `server_hostname` is an
            empty string, hostname matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        
        Returns
        -------
        transport : ``_SSLBidirectionalTransportLayerTransport`` or ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``_SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : `Any`
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            - If `host` or `port` is given meanwhile `socket` is also specified.
            - If `server_hostname` is not set, meanwhile using `ssl` without `host`.
            - If `server_hostname` is set, but `ssl` is.
            - If neither `host`, `port` or `socket` are specified.
            - `socket` is given, but not as a stream socket.
        OSError
            - `get_address_info()` returned empty list.
            - Error while attempting to bind to address.
            - Cannot open connection to any address.
        """
        if isinstance(ssl, bool):
            if ssl:
                ssl = create_default_context()
            else:
                ssl = None
        
        if (server_hostname is None):
            if (ssl is not None):
                # Use host as default for server_hostname. It is an error if host is empty or not set, e.g. when an
                # already-connected socket was passed or when only a port is given.  To avoid this error, you can pass
                # server_hostname='' -- this will bypass the hostname check. (This also means that if host is a numeric
                # IP/IPv6 address, we will attempt to verify that exact address; this will probably fail, but it is
                # possible to create a certificate for a specific IP address, so we don't judge it here.)
                if host is None:
                    raise ValueError('You must set `server_hostname` when using `ssl` without a `host`.')
                server_hostname = host
        else:
            if ssl is None:
                raise ValueError('`server_hostname` is only meaningful with `ssl`.')
        
        if (host is not None) or (port is not None):
            if (socket is not None):
                raise ValueError('`host`, `port` and `socket` can not be specified at the same time.')
            
            f1 = self._ensure_resolved((host, port), family=family, type=module_socket.SOCK_STREAM, protocol=protocol,
                flags=flags)
            fs = [f1]
            if local_address is not None:
                f2 = self._ensure_resolved(local_address, family=family, type=module_socket.SOCK_STREAM,
                    protocol=protocol, flags=flags)
                fs.append(f2)
            else:
                f2 = None
            
            await Gatherer(self, fs)
            
            infos = f1.result()
            if not infos:
                raise OSError('`get_address_info` returned empty list')
            if (f2 is not None):
                local_address_infos = f2.result()
                if not local_address_infos:
                    raise OSError('`get_address_info` returned empty list')
            
            exceptions = []
            for family, type_, protocol, canonical_name, address in infos:
                try:
                    socket = module_socket.socket(family=family, type=type_, proto=protocol)
                    socket.setblocking(False)
                    if (f2 is not None):
                        for element in local_address_infos:
                            local_address = element[4]
                            try:
                                socket.bind(local_address)
                                break
                            except OSError as err:
                                err = OSError(err.errno, f'Error while attempting to bind on address '
                                    f'{local_address!r}: {err.strerror.lower()}.')
                                exceptions.append(err)
                        else:
                            socket.close()
                            socket = None
                            continue
                    
                    await self.socket_connect(socket, address)
                except OSError as err:
                    if (socket is not None):
                        socket.close()
                    exceptions.append(err)
                except:
                    if (socket is not None):
                        socket.close()
                    raise
                else:
                    break
            else:
                if len(exceptions) == 1:
                    raise exceptions[0]
                else:
                    # If they all have the same str(), raise one.
                    model = repr(exceptions[0])
                    all_exception = [repr(exception) for exception in exceptions]
                    if all(element == model for element in all_exception):
                        raise exceptions[0]
                    # Raise a combined exception so the user can see all the various error messages.
                    raise OSError(f'Multiple exceptions: {", ".join(all_exception)}')
        
        else:
            if socket is None:
                raise ValueError('`host` and `port`, neither `socket` was given.')
            
            if not _is_stream_socket(socket):
                raise ValueError(f'A stream socket was expected, got {socket!r}.')
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, server_hostname, False)
    
    
    async def _create_connection_transport(self, socket, protocol_factory, ssl, server_hostname, server_side):
        """
        Open a streaming transport connection to a given address specified by `host` and `port`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        ssl : `None`, `ssl.SSLContext`
            Whether ssl should be enabled.
        socket : `socket.socket`
            The socket to what the created transport should be connected to.
        server_hostname : `None` or `str`
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If host
            is empty, there is no default and you must pass a value for `server_hostname`. If `server_hostname` is an
            empty string, hostname matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        server_side : `bool`
            Whether the server or the client creates the connection transport.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        """
        socket.setblocking(False)
        
        protocol = protocol_factory()
        waiter = Future(self)
        
        if ssl is None:
            transport = self._make_socket_transport(socket, protocol, waiter)
        else:
            transport = self._make_ssl_transport(socket, protocol, ssl, waiter, server_side=server_side,
                server_hostname=server_hostname)
        
        try:
            await waiter
        except:
            transport.close()
            raise
        
        return protocol
    
    
    if IS_UNIX:
        async def create_unix_connection(self, protocol_factory, path=None, *, socket=None, ssl=None,
                server_hostname=None):
            if (ssl is None):
                if server_hostname is not None:
                    raise ValueError('`server_hostname` is only meaningful with `ssl`.')
            else:
                if server_hostname is None:
                    raise ValueError('`server_hostname` parameter is required with `ssl`.')
            
            if path is not None:
                if socket is not None:
                    raise ValueError('`path` and `socket` parameters are mutually exclusive.')
                
                path = os.fspath(path)
                socket = module_socket.socket(module_socket.AF_UNIX, module_socket.SOCK_STREAM, 0)
                
                try:
                    socket.setblocking(False)
                    await self.socket_connect(socket, path)
                except:
                    socket.close()
                    raise
            
            else:
                if socket is None:
                    raise ValueError('Either `socket` or `path` parameters are required.')
                
                if socket.family not in (module_socket.AF_UNIX, module_socket.SOCK_STREAM):
                    raise ValueError(f'A UNIX Domain Stream Socket was expected, got {socket!r}.')
                
                socket.setblocking(False)
            
            return await self._create_connection_transport(socket, protocol_factory, ssl, server_hostname, False)
        
        
        async def open_unix_connection(self, path=None, **kwargs):
            return await self.create_unix_connection(partial_func(ReadWriteProtocolBase, self), path, **kwargs)
        
        
        async def create_unix_server(self, protocol_factory, path=None, *, socket=None, backlog=100, ssl=None,):
            if (ssl is not None) and (not isinstance(ssl, ssl.SSlContext)):
                raise TypeError(f'`ssl` can be given as `None` or as ``SSLContext``, got {ssl.__class__.__name__}.')
            
            if path is not None:
                if socket is not None:
                    raise ValueError('`path` and `socket` parameters are mutually exclusive.')
                
                path = os.fspath(path)
                socket = module_socket.socket(module_socket.AF_UNIX, module_socket.SOCK_STREAM)
                
                # Check for abstract socket.
                if not path.startswith('\x00'):
                    try:
                        if S_ISSOCK(os.stat(path).st_mode):
                            os.remove(path)
                    except FileNotFoundError:
                        pass
                
                try:
                    socket.bind(path)
                except OSError as exc:
                    socket.close()
                    if exc.errno == errno.EADDRINUSE:
                        # Let's improve the error message by adding  with what exact address it occurs.
                        raise OSError(errno.EADDRINUSE, f'Address {path!r} is already in use.') from None
                    else:
                        raise
                except:
                    socket.close()
                    raise
            else:
                if socket is None:
                    raise ValueError('Either `path` or `socket` parameter is required.')
                
                if socket.family not in (module_socket.AF_UNIX, module_socket.SOCK_STREAM):
                    raise ValueError(f'A UNIX Domain Stream Socket was expected, got {socket!r}.')
            
            socket.setblocking(False)
            
            return Server(self, [socket], protocol_factory, ssl, backlog)
        
    else:
        async def create_unix_connection(self, protocol_factory, path=None, *, socket=None, ssl=None,
                server_hostname=None):
            raise NotImplementedError
        
        
        async def open_unix_connection(self, path=None, **kwargs):
            raise NotImplementedError
    
    
        async def create_unix_server(self, protocol_factory, path=None, *, socket=None, backlog=100, ssl=None,):
            raise NotImplementedError
    
    
    set_docs(create_unix_connection,
        """
        Establish a unix socket connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        path : `None` or `str`, Optional
            The path to open connection to.
        socket : `socket.socket`, Optional (Keyword only)
            A preexisting socket object to use up.
            
            Mutually exclusive with the `path` parameter.
        ssl : `None` or `ssl.SSLContext`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_hostname : `None` or `str`
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If hos
            is empty, there is no default and you must pass a value for `server_hostname`. If `server_hostname` is an
            empty string, hostname matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        
        Returns
        -------
        transport : ``_SSLBidirectionalTransportLayerTransport`` or ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``_SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : `Any`
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            - If `server_hostname` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_hostname` is not.
            - If `path` parameter is given, when `socket` is defined as well.
            - If neither `path` and `socket` parameters are given.
            - If `socket`'s is not an unix domain stream socket.
        NotImplementedError
            Not supported on windows by the library.
        """)
    
    set_docs(open_unix_connection,
        """
        Creates an unix connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        path : `None` or `str`, Optional
            The path to open connection to.
        **kwargs : Keyword parameters
            Additional keyword parameters to pass to ``.create_unix_connection``.
        
        Other Parameters
        ----------------
        socket : `socket.socket`, Optional (Keyword only)
            A preexisting socket object to use up.
            
            Mutually exclusive with the `path` parameter.
        ssl : `None` or `ssl.SSLContext`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_hostname : `None` or `str`
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If hos
            is empty, there is no default and you must pass a value for `server_hostname`. If `server_hostname` is an
            empty string, hostname matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        
        Returns
        -------
        protocol : ``BaseProtocol``
            The connected read and write protocol.
        
        Raises
        ------
        ValueError
            - If `server_hostname` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_hostname` is not.
            - If `path` parameter is given, when `socket` is defined as well.
            - If neither `path` and `socket` parameters are given.
            - If `socket`'s is not an unix domain stream socket.
        NotImplementedError
            Not supported on windows by the library.
        """)
    
    set_docs(create_unix_server,
        """
        Creates an unix server (socket type AF_UNIX) listening on the given path.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        path : `None` or `str`
            The path to open connection to.
        socket : `None` or `socket.socket`, Optional (Keyword only)
            Can be specified in order to use a preexisting socket object.
            
            Mutually exclusive with the `path` parameter.
        backlog : `int`, Optional (Keyword only)
            The maximum number of queued connections passed to `listen()` (defaults to 100).
        ssl : `None` or ``SSLContext``, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        
        Returns
        -------
        server : ``Server``
            The created server instance.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given neither as `None` nor as `ssl.SSLContext` instance.
        ValueError
            - If both `path` and `socket` parameters are given.ó
            - If neither `path` nor `socket` were given.
            - If `socket` is given, but it's type is not `module_socket.SOCK_STREAM`.
        FileNotFoundError:
            The given `path` do not exists.
        OsError
            - Path already in use.
            - Error while attempting to connect to `path`.
        NotImplementedError
            Not supported on windows by the library.
        """)
    
    
    # await it
    def get_address_info(self, host, port, *, family=0, type=0, protocol=0, flags=0):
        """
        Asynchronous version of `socket.getaddrinfo()`.
        
        Parameters
        ----------
        host : `None` or `str`
            To respective network interface.
        port : `None` or `int`
            The port of the `host`.
        family :  `AddressFamily` or `int`, Optional (Keyword only)
            The address family.
        type : `SocketKind` or `int`, Optional (Keyword only)
            Socket type.
        protocol : `int`, Optional (Keyword only)
            Protocol type. Can be used to narrow host resolution.
        flags : `int`, Optional (Keyword only)
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what will yield the lookup's result.
            
            Might raise `OSError` or return a `list` of `tuple`-s with the following elements:
            - `family` : `AddressFamily` or `int`. Address family.
            - `type` : `SocketKind` or `int`. Socket type.
            - `protocol` : `int`. Protocol type.
            - `canonical_name` : `str`. Represents the canonical name of the host.
            - `socket_address` : `tuple` (`str, `int`). Socket address containing the `host` and the `port`.
        """
        return self.run_in_executor(alchemy_incendiary(
            module_socket.getaddrinfo, (host, port, family, type, protocol, flags,),))
    
    # await it
    def get_name_info(self, socket_address, flags=0):
        """
        Asynchronous version of `socket.getnameinfo()`.
        
        Parameters
        ----------
        socket_address : `tuple` (`str`, `int`)
             Socket address as a tuple of `host` and `port`.
        flags : `int`, Optional
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what will yield the lookup's result.
        """
        return self.run_in_executor(alchemy_incendiary(module_socket.getnameinfo, (socket_address, flags,),))
    
    
    def _ensure_resolved(self, address, *, family=0, type=module_socket.SOCK_STREAM, protocol=0, flags=0):
        """
        Ensures, that the given address is already a resolved IP. If not, gets it's address.
        
        Parameters
        ----------
        address : `tuple` (`None` or `str`, `None` or `int`)
            Address as a tuple of `host` and `port`.
        type : `SocketKind` or `int`, Optional
            Socket type.
        protocol : `int`, Optional
            Protocol type. Can be used to narrow host resolution.
        flags : `int`, Optional
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what returns a `list` of `tuples` with the following elements:
            
            - `family` : `AddressFamily` or `int`. Address family.
            - `type` : `SocketKind` or `int`. Socket type.
            - `protocol` : `int`. Protocol type.
            - `canonical_name` : `str`. Represents the canonical name of the host.
            - `socket_address` : `tuple` (`str, `int`). Socket address containing the `host` and the `port`.
            
            Might raise `OSError` as well.
        """
        # Address might have more than 2 elements?
        host = address[0]
        port = address[1]
        
        info = _ip_address_info(host, port, family, type, protocol)
        if info is None:
            return self.get_address_info(host, port, family=family, type=type, protocol=protocol, flags=flags)
        
        # "host" is already a resolved IP.
        future = Future(self)
        future.set_result([info])
        return future
    
    
    async def socket_accept(self, socket):
        """
        Accept a connection. Modeled after the blocking `socket.accept()` method.
        
        The socket must be bound to an address and listening for connections.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            Must be a non-blocking socket.
        
        Returns
        -------
        conn : `socket.socket`
            The connected socket.
        address : `tuple` (`str`, `int`)
            The address to what the connection is connected to.
        """
        future = Future(self)
        self._socket_accept(future, False, socket)
        return await future
    
    
    def _socket_accept(self, future, registered, socket):
        """
        Method used by ``.socket_accept`` to check whether the respective socket can be accepted already.
        
        If the respective socket is already connected, then sets the waiter future's result instantly, else adds itself
        as a reader callback.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception is set, when the socket can be accepted or when an exception
            occurs.
        registered : `bool`
            Whether the given `socket is registered as a reader and should be removed.
        socket : `socket.socket`
            The respective socket, what's is listening for a connection.
        """
        fd = socket.fileno()
        if registered:
            self.remove_reader(fd)
            
            # First time `registered` is given as `False` and at the case, the `future` can not be cancelled yet.
            # Later it is called with `True`.
            if future.cancelled():
                return
        
        try:
            conn, address = socket.accept()
            conn.setblocking(False)
        except (BlockingIOError, InterruptedError):
            self.add_reader(fd, self._socket_accept, future, True, socket)
        except BaseException as err:
            future.set_exception(err)
        else:
            future.set_result((conn, address))
    
    
    async def socket_connect(self, socket, address):
        """
        Connect the given socket to a remote socket at address.
        
        Asynchronous version of `socket.connect`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            Must be a non-blocking socket.
        address : `tuple` (`str`, `int`)
            The address to connect to.
        """
        if not hasattr(module_socket, 'AF_UNIX') or (socket.family != module_socket.AF_UNIX):
            resolved = self._ensure_resolved(address, family=socket.family, protocol=socket.proto)
            if not resolved.done():
                await resolved
            address = resolved.result()[0][4]
        
        future = Future(self)
        
        fd = socket.fileno()
        try:
            socket.connect(address)
        except (BlockingIOError, InterruptedError):
            self.add_writer(fd, self._socket_connect_callback, future, socket, address)
            future.add_done_callback(self._socket_connect_done(fd),)
            
        except BaseException as err:
            future.set_exceptio_if_pending(err)
        else:
            future.set_result_if_pending(None)
        
        await future
    
    
    class _socket_connect_done:
        """
        Callback added to the waited future by ``EventThread.socket_connect`` to remove the respective socket from the
        writers by it's file descriptor.
        
        Attributes
        ----------
        fd : `int`
            The respective socket's file descriptor's identifier.
        """
        __slots__ = ('fd',)
        
        def __init__(self, fd):
            """
            Creates a new ``_socket_connect_done`` instance with the given fd.
            
            Parameters
            ----------
            fd : `int`
                The respective socket's file descriptor's identifier.
            """
            self.fd = fd
        
        def __call__(self, future):
            """
            Callback what runs when the respective waiter future is marked as done.
            
            Removes the respective socket from writers.
            
            Parameters
            ----------
            future : ``Future``
                The respective future, what's result is set, when the respective connected.
            """
            future._loop.remove_writer(self.fd)
    
    
    def _socket_connect_callback(self, future, socket, address):
        """
        Reader callback, what is called, when the respective socket is connected. Added by ``.socket_connect``, when the
        socket is not yet connected.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result is set, when the socket is connected.
        socket : `socket.socket`
            The respective socket, on what's connection we are waiting for.
        address : `tuple` (`str`, `int`)
            The address to connect to.
        """
        if future.done():
            return
        
        try:
            err_number = socket.getsockopt(module_socket.SOL_SOCKET, module_socket.SO_ERROR)
            if err_number != 0:
                raise OSError(err_number, f'Connect call failed {address!r}.')
        except (BlockingIOError, InterruptedError):
            # socket is still registered, the callback will be retried later
            pass
        except BaseException as err:
            future.set_exception(err)
        else:
            future.set_result(None)
    
    
    async def socket_receive(self, socket, n):
        """
        Receive up to `n` from the given socket. Asynchronous version of `socket.recv()`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket to receive the data from. Must be a non-blocking socket.
        n : `int`
            The amount of data to receive in bytes.
        
        Returns
        -------
        data : `bytes`
            The received data.
        
        Notes
        -----
        There is no way to determine how much data, if any was successfully received on the other end of the connection.
        """
        future = Future(self)
        self._socket_receive(future, False, socket, n)
        return await future
    
    
    def _socket_receive(self, future, registered, socket, n):
        """
        Added reader callback by ``.socket_receive``. This method is repeated till the data is successfully polled.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception will be set.
        registered : `bool`
            Whether `socket` is registered as a reader and should be removed.
        socket : `socket.socket`
            The socket from what we read.
        n : `int`
            The amount of data to receive in bytes.
        """
        fd = socket.fileno()
        if registered:
            self.remove_reader(fd)
        
        if future.done():
            return
        
        try:
            data = socket.recv(n)
        except (BlockingIOError,InterruptedError):
            self.add_reader(fd, self._socket_receive, future, True, socket, n)
        except BaseException as err:
            future.set_exception(err)
        else:
            future.set_result(data)
    
    
    async def socket_send_all(self, socket, data):
        """
        Send data to the socket. Asynchronous version of `socket.sendall`.
        
        Continues sending to the socket until all data is sent or an error occurs.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket to send the data to. Must be a non-blocking socket.
        data : `bytes-like`
            The data to send.
        
        Notes
        -----
        There is no way to determine how much data, if any was successfully received on the other end of the connection.
        """
        if not isinstance(data, memoryview):
            data = memoryview(data)
        
        if data:
            future = Future(self)
            self._socket_send_all(future, False, socket, data)
            await future
    
    
    def _socket_send_all(self, future, registered, socket, data):
        """
        Added writer callback by ``.socket_send_all``. This method is repeated till the whole data is exhausted.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception will be set.
        registered : `bool`
            Whether `socket` is registered as a writer and should be removed.
        socket : `socket.socket`
            The socket to what the data is sent to.
        data : `memoryview`
            Memoryview on the data to send.
        """
        fd = socket.fileno()
        
        if registered:
            self.remove_writer(fd)
        
        if future.done():
            return
        
        try:
            n = socket.send(data)
        except (BlockingIOError, InterruptedError):
            n = 0
        except BaseException as err:
            future.set_exception(err)
            return
        
        if n == len(data):
            future.set_result(None)
        else:
            if n:
                data = data[n:]
            
            self.add_writer(fd, self._socket_send_all, future, True, socket, data)
    
    
    async def create_datagram_endpoint(self, protocol_factory, local_address=None, remote_address=None, *, family=0,
            protocol=0, flags=0, reuse_port=False, allow_broadcast=False, socket=None):
        """
        Creates a datagram connection. The socket type will be `SOCK_DGRAM`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        
        local_address : `None`, `tuple` of (`None` or  `str`, `None` or `int`), `str`, `bytes`, Optional
            Can be given as a `tuple` (`local_host`, `local_port`) to bind the socket locally. The `local_host` and
            `local_port` are looked up by ``.get_address_info``.
            
            If `family` is given as `AF_UNIX`, then also can be given as path of a file or a file descriptor.
            
            Mutually exclusive with the `socket` parameter.
        remote_address : `None`, `tuple` of (`None` or  `str`, `None` or `int`), `str`, `bytes`, Optional
            Can be given as a `tuple` (`remote_host`, `remote_port`) to connect the socket to remove address. The
            `remote_host` and `remote_port` are looked up by ``.get_address_info``.
            
            If `family` is given as `AF_UNIX`, then also can be given as path of a file or a file descriptor.
            
            Mutually exclusive with the `socket` parameter.
        family : `AddressFamily` or `int`, Optional (Keyword only)
            Can be either `AF_INET`, `AF_INET6` or `AF_UNIX`.
            
            Mutually exclusive with the `socket` parameter.
        protocol : `int`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
            
            Mutually exclusive with the `socket` parameter.
        flags : `int`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
            
            Mutually exclusive with the `socket` parameter.
        reuse_port : `bool`, Optional (Keyword only)
            Tells to the kernel to allow this endpoint to be bound to the same port as an other existing endpoint
            already might be bound to.
            
            Not supported on Windows.
        allow_broadcast : `bool`, Optional (Keyword only)
            Tells the kernel to allow this endpoint to send messages to the broadcast address.
        socket : `None` or `socket.socket`, Optional (Keyword only)
            Can be specified in order to use a preexisting socket object.
            
            Mutually exclusive with `host` and `port` parameters.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        """
        if socket is not None:
            if socket.type != module_socket.SOCK_DGRAM:
                raise ValueError(f'A UDP socket was expected, got {socket!r}.')
            
            if (local_address is not None) or (remote_address is not None) or family  or protocol or flags or \
                    reuse_port or allow_broadcast:
                
                collected = []
                if (local_address is not None):
                    collected.append(('local_address', local_address))
                
                if (remote_address is not None):
                    collected.append(('remote_address', remote_address))
                    
                if family:
                    collected.append(('family', family))
                
                if protocol:
                    collected.append(('protocol', protocol))
                
                if flags:
                    collected.append(('flags', flags))
                
                if reuse_port:
                    collected.append(('reuse_port', reuse_port))
                
                if allow_broadcast:
                    collected.append(('allow_broadcast', allow_broadcast))
                
                error_message_parts = ['Socket modifier keyword parameters can not be used when `socket` is given: ']
                
                index = 0
                limit = len(error_message_parts)
                while True:
                    name, value = collected[index]
                    error_message_parts.append(name)
                    error_message_parts.append('=')
                    error_message_parts.append(repr(value))
                    
                    index += 1
                    if index == limit:
                        break
                    
                    error_message_parts.append(', ')
                    continue
                
                error_message_parts.append('.')
                
                raise ValueError(''.join(error_message_parts))
            
            socket.setblocking(False)
            remote_address = None
        else:
            address_info = []
            
            if (local_address is None) and (remote_address is None):
                if family == 0:
                    raise ValueError(f'Unexpected address family: {family!r}.')
                
                address_info.append((family, protocol, None, None))
            
            elif hasattr(module_socket, 'AF_UNIX') and family == module_socket.AF_UNIX:
                if __debug__:
                    if (local_address is not None):
                        if not isinstance(local_address, (str, bytes)):
                            raise TypeError('`local_address` should be given as `None` or as `str` or `bytes` '
                                f'instance, if `family` is given as ``AF_UNIX`, got '
                                f'{local_address.__class__.__name__}')
                    
                    if (remote_address is not None):
                        if not isinstance(remote_address, (str, bytes)):
                            raise TypeError('`remote_address` should be given as `None` or as `str` or `bytes` '
                                f'instance, if `family` is given as ``AF_UNIX`, got '
                                f'{remote_address.__class__.__name__}')
                
                if (local_address is not None) and local_address and \
                        (local_address[0] != (0 if isinstance(local_address, bytes) else '\x00')):
                    try:
                        if S_ISSOCK(os.stat(local_address).st_mode):
                            os.remove(local_address)
                    except FileNotFoundError:
                        pass
                    except OSError as err:
                        # Directory may have permissions only to create socket.
                        sys.stderr.write(f'Unable to check or remove stale UNIX socket {local_address!r}: {err!s}.\n')
                
                address_info.append((family, protocol, local_address, remote_address))
            
            else:
                # join address by (family, protocol)
                address_infos = {}
                if (local_address is not None):
                    infos = await self._ensure_resolved(local_address, family=family, type=module_socket.SOCK_DGRAM,
                        protocol=protocol, flags=flags)
                    
                    if not infos:
                        raise OSError('`get_address_info` returned empty list')
                    
                    for it_family, it_type, it_protocol, it_canonical_name, it_socket_address in infos:
                        address_infos[(it_family, it_protocol)] = (it_socket_address, None)
                
                if (remote_address is not None):
                    infos = await self._ensure_resolved(remote_address, family=family, type=module_socket.SOCK_DGRAM,
                        protocol=protocol, flags=flags)
                    
                    if not infos:
                        raise OSError('`get_address_info` returned empty list')
                    
                    
                    for it_family, it_type, it_protocol, it_canonical_name, it_socket_address in infos:
                        key = (it_family, it_protocol)
                        
                        try:
                            value = address_infos[key]
                        except KeyError:
                            address_value_local = None
                        else:
                            address_value_local = value[0]
                        
                        address_infos[key] = (address_value_local, it_socket_address)
                
                for key, (address_value_local, address_value_remote) in address_infos.items():
                    if (local_address is not None) and (address_value_local is None):
                        continue
                    
                    if (remote_address is not None) and (address_value_remote is None):
                        continue
                    
                    address_info.append((*key, address_value_local, address_value_remote))
                
                if not address_info:
                    raise ValueError('Can not get address information.')
            
            exception = None
            
            for family, protocol, local_address, remote_address in address_info:
                try:
                    socket = module_socket.socket(family=family, type=module_socket.SOCK_DGRAM, proto=protocol)
                    
                    if reuse_port:
                        _set_reuse_port(socket)
                    
                    if allow_broadcast:
                        socket.setsockopt(module_socket.SOL_SOCKET, module_socket.SO_BROADCAST, 1)
                    
                    socket.setblocking(False)
                    
                    if (local_address is not None):
                        socket.bind(local_address)
                    
                    if (remote_address is not None):
                        if not allow_broadcast:
                            await self.socket_connect(socket, remote_address)
                
                except BaseException as err:
                    if (socket is not None):
                        socket.close()
                        socket = None
                    
                    if not isinstance(err, OSError):
                        raise
                    
                    if (exception is None):
                        exception = err
                    
                else:
                    break
            
            else:
                raise exception
        
        protocol = protocol_factory()
        waiter = Future(self)
        transport = DatagramSocketTransportLayer(self, socket, protocol, remote_address, waiter, None)
        
        try:
            await waiter
        except:
            transport.close()
            raise
        
        return protocol
    
    
    def _create_server_get_address_info(self, host, port, family, flags):
        """
        Gets address info for the given parameters. This method is used by ``.create_server``, when resolving hosts.
        
        Parameters
        ----------
        host : `None` or `str`, (`None` or `str`)
            Network interfaces should the server be bound.
        port : `None` or `int`
            The port to use by the `host`.
        family : `AddressFamily` or `int`
            The family of the address.
        flags : `int`
            Bit-mask for `get_address_info`.
        
        Returns
        -------
        future : ``Future``
            A future, what's result is set, when the address is dispatched.
        """
        return self._ensure_resolved((host, port), family=family, type=module_socket.SOCK_STREAM, flags=flags)
    
    
    async def create_server(self, protocol_factory, host=None, port=None, *, family=module_socket.AF_UNSPEC,
            flags=module_socket.AI_PASSIVE, socket=None, backlog=100, ssl=None,
            reuse_address=(os.name == 'posix' and sys.platform != 'cygwin'), reuse_port=False):
        """
        Creates a TCP server (socket type SOCK_STREAM) listening on port of the host address.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        host : `None` or `str`, `iterable` of (`None` or `str`), Optional
            To what network interfaces should the server be bound.
            
            Mutually exclusive with the `socket` parameter.
        port : `None` or `int`, Optional
            The port to use by the `host`(s).
            
            Mutually exclusive with the `socket` parameter.
        family : `AddressFamily` or `int`, Optional (Keyword only)
            Can be given either as `socket.AF_INET` or `socket.AF_INET6` to force the socket to use `IPv4` or `IPv6`.
            If not given, then  will be determined from host name.
        flags : `int`, Optional (Keyword only)
            Bit-mask for `get_address_info`.
        socket : `None` or `socket.socket`, Optional (Keyword only)
            Can be specified in order to use a preexisting socket object.
            
            Mutually exclusive with `host` and `port` parameters.
        backlog : `int`, Optional (Keyword only)
            The maximum number of queued connections passed to `listen()` (defaults to 100).
        ssl : `None` or ``SSLContext``, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        reuse_address : `bool`, Optional (Keyword only)
            Tells the kernel to reuse a local socket in `TIME_WAIT` state, without waiting for its natural timeout to
            expire. If not specified will automatically be set to True on Unix.
        reuse_port : `bool`, Optional (Keyword only)
            Tells to the kernel to allow this endpoint to be bound to the same port as an other existing endpoint
            already might be bound to.
            
            Not supported on Windows.
        
        Returns
        -------
        server : ``Server``
            The created server instance.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given either as `None` or as `ssl.SSLContext` instance.
            - If `reuse_port` is given as non `bool`.
            - If `reuse_address` is given as non `bool`.
            - If `reuse_port` is given as non `bool`.
            - If `host` is not given as `None`, `str` and neither as `iterable` of `None` or `str`.
        ValueError
            - If `host` or `port` parameter is given, when `socket` is defined as well.
            - If `reuse_port` is given as `True`, but not supported.
            - If neither `host`, `port` nor `socket` were given.
            - If `socket` is given, but it's type is not `module_socket.SOCK_STREAM`.
        OsError
            Error while attempting to binding to address.
        """
        if (ssl is not None) and (type(ssl) is not SSLContext):
            raise TypeError(f'`ssl` can be given as `None` or as ``SSLContext``, got {ssl.__class__.__name__}.')
        
        if (host is not None) or (port is not None):
            if (socket is not None):
                raise ValueError('`host` and `port` parameters are mutually exclusive with `socket`.')
            
            if (reuse_address is not None) and (not isinstance(reuse_address, bool)):
                raise TypeError('`reuse_address` can be `None` or type `bool`, got '
                    f'`{reuse_address.__class__.__name__}`.')
            
            if (reuse_port is not None) and (not isinstance(reuse_port, bool)):
                raise TypeError('`reuse_address` can be `None` or type `bool`, got '
                    f'`{reuse_port.__class__.__name__}`.')
            
            if reuse_port and (not hasattr(module_socket, 'SO_REUSEPORT')):
                raise ValueError('`reuse_port` not supported by the socket module.')
            
            hosts = []
            if (host is None) or (host == ''):
                 hosts.append(None)
            elif isinstance(host, str):
                hosts.append(host)
            elif hasattr(type(host), '__iter__'):
                for host in host:
                    if (host is None) or (host == ''):
                        hosts.append(None)
                        continue
                    
                    if isinstance(host, str):
                        hosts.append(host)
                        continue
                    
                    raise TypeError('`host` is passed as iterable, but it yielded at least 1 not `None`, or `str` '
                        f'instance; `{host!r}`')
            else:
                raise TypeError('`host` should be `None`, `str` instance or iterable of `None` or of `str` instances, '
                    f'got {host!r}')
            
            sockets = []
            
            futures = {self._create_server_get_address_info(host, port, family, flags) for host in hosts}
            
            try:
                while True:
                    done, pending = await WaitTillFirst(futures, self)
                    for future in done:
                        futures.discard(future)
                        address_infos = future.result()
                        
                        for address_info in address_infos:
                            socket_family, socket_type, socket_protocol, canonical_name, socket_address = address_info
                            
                            try:
                                socket = module_socket.socket(socket_family, socket_type, socket_protocol)
                            except module_socket.error:
                                continue
                            
                            sockets.append(socket)
                            
                            if reuse_address:
                                socket.setsockopt(module_socket.SOL_SOCKET, module_socket.SO_REUSEADDR, True)
                            
                            if reuse_port:
                                try:
                                    socket.setsockopt(module_socket.SOL_SOCKET, module_socket.SO_REUSEPORT, 1)
                                except OSError as err:
                                    raise ValueError('reuse_port not supported by socket module, SO_REUSEPORT defined '
                                        'but not implemented.') from err
                            
                            if (_HAS_IPv6 and (socket_family == module_socket.AF_INET6) and \
                                    hasattr(module_socket, 'IPPROTO_IPV6')):
                                socket.setsockopt(module_socket.IPPROTO_IPV6, module_socket.IPV6_V6ONLY, True)
                            try:
                                socket.bind(socket_address)
                            except OSError as err:
                                raise OSError(err.errno, f'Error while attempting to bind on address '
                                    f'{socket_address!r}: {err.strerror.lower()!s}.') from None
                    
                    if futures:
                        continue
                    
                    break
            except:
                for socket in sockets:
                    socket.close()
                    
                for future in futures:
                    future.cancel()
                
                raise
            
        else:
            if socket is None:
                raise ValueError('Neither `host`, `port` nor `socket` were given.')
            
            if socket.type != module_socket.SOCK_STREAM:
                raise ValueError(f'A stream socket was expected, got {socket!r}.')
            
            sockets = [socket]
        
        for socket in sockets:
            socket.setblocking(False)
        
        return Server(self, sockets, protocol_factory, ssl, backlog)
    
    if IS_UNIX:
        async def connect_read_pipe(self, protocol, pipe):
            return await UnixReadPipeTransportLayer(self, pipe, protocol)
        
        async def connect_write_pipe(self, protocol, pipe):
            return await UnixWritePipeTransportLayer(self, pipe, protocol)
        
        async def subprocess_shell(self, command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                *, extra=None, preexecution_function=None, close_fds=True, cwd=None, startup_info=None,
                creation_flags=0, restore_signals=True, start_new_session=False, pass_fds=(), **process_open_kwargs):
            
            if not isinstance(command, (bytes, str)):
                raise TypeError(f'`cmd` must be `bytes` or `str` instance, got {command.__class__.__name__}.')
            
            process_open_kwargs = {
                'preexec_fn' : preexecution_function,
                'close_fds' : close_fds,
                'cwd' : cwd,
                'startupinfo' : startup_info,
                'creationflags' : creation_flags,
                'restore_signals' : restore_signals,
                'start_new_session' : start_new_session,
                'pass_fds' : pass_fds,
                **process_open_kwargs
            }
            
            return await AsyncProcess(self, command, True, stdin, stdout, stderr, 0, extra, process_open_kwargs)
        
        async def subprocess_exec(self, program, *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  extra=None, preexecution_function=None, close_fds=True, cwd=None,
                startup_info=None, creation_flags=0, restore_signals=True, start_new_session=False, pass_fds=(),
                **process_open_kwargs):
            
            process_open_kwargs = {
                'preexec_fn' : preexecution_function,
                'close_fds' : close_fds,
                'cwd' : cwd,
                'startupinfo' : startup_info,
                'creationflags' : creation_flags,
                'restore_signals' : restore_signals,
                'start_new_session' : start_new_session,
                'pass_fds' : pass_fds,
                **process_open_kwargs,
            }
            
            return await AsyncProcess(self, (program, *args), False, stdin, stdout, stderr, 0, extra,
                process_open_kwargs)
    
    else:
        async def connect_read_pipe(self, protocol, pipe):
            raise NotImplementedError
        
        async def connect_write_pipe(self, protocol, pipe):
            raise NotImplementedError
        
        async def subprocess_shell(self, cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, *,
                extra=None, preexecution_function=None, close_fds=True, cwd=None, startup_info=None, creation_flags=0,
                restore_signals=True, start_new_session=False, pass_fds=(), **process_open_kwargs):
            raise NotImplementedError
        
        async def subprocess_exec(self, program, *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, extra=None, preexecution_function=None, close_fds=True, cwd=None,
                startup_info=None, creation_flags=0, restore_signals=True, start_new_session=False, pass_fds=(),
                **process_open_kwargs):
            raise NotImplementedError
    
    set_docs(connect_read_pipe,
        """
        Register the read end of the given pipe in the event loop.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol : `Any`
            An async-io protocol implementation to use as the transport's protocol.
        pipe : `file-like` object
            The pipe to connect to on read end.
            
            Is set to non-blocking mode.
        
        Returns
        -------
        transport : ``UnixReadPipeTransportLayer``
            The created transport.
        
        Raises
        ------
        ValueError
            Pipe transport is only for pipes, sockets and character devices.'
        NotImplementedError
            Not supported on windows by the library.
        """)
    
    set_docs(connect_write_pipe,
        """
        Register the write end of the given pipe in the event loop.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol : `Any`
            An async-io protocol implementation to use as the transport's protocol.
        pipe : `file-like` object
            The pipe to connect to on write end.
            
            Is set to non-blocking mode.
        
        Returns
        -------
        transport : ``UnixReadPipeTransportLayer``
            The created transport.
        
        Raises
        ------
        ValueError
            Pipe transport is only for pipes, sockets and character devices.'
        NotImplementedError
            Not supported on windows by the library.
        """)
        
    set_docs(subprocess_shell,
        """
        Create a subprocess from cmd.
        
        This is similar to the standard library `subprocess.Popen` class called with `shell=True`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        cmd : `str` or `bytes`
            The command to execute. Should use the platform’s “shell” syntax.
        stdin : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, Optional
            Standard input for the created shell. Defaults to `subprocess.PIPE`.
        stdout : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, Optional
            Standard output for the created shell. Defaults to `subprocess.PIPE`.
        stderr : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, `subprocess.STDOUT`, Optional
            Standard error for the created shell. Defaults to `subprocess.PIPE`.
        extra : `None` or `dict` of (`str`, `Any`) items, Optional (Keyword only)
            Optional transport information.
        preexecution_function : `None` or `callable`, Optional (Keyword only)
            This object is called in the child process just before the child is executed. POSIX only, defaults to
            `None`.
        close_fds : `bool`, Optional (Keyword only)
            Defaults to `True`
            
            If `close_fds` is True, all file descriptors except `0`, `1` and `2` will be closed before the child
            process is executed. Otherwise when `close_fds` is False, file descriptors obey their inheritable flag as
            described in Inheritance of File Descriptors.
        cwd : `str`, `bytes`, `path-like` or `None`, Optional (Keyword only)
            If `cwd` is not `None`, the function changes the working directory to cwd before executing the child.
            Defaults to `None`
        startup_info : `subprocess.STARTUPINFO` or `None`, Optional (Keyword only)
            Is passed to the underlying `CreateProcess` function.
        creation_flags : `int`, Optional (Keyword only)
            Can be given as 1 of the following flags:
            
            - `CREATE_NEW_CONSOLE`
            - `CREATE_NEW_PROCESS_GROUP`
            - `ABOVE_NORMAL_PRIORITY_CLASS`
            - `BELOW_NORMAL_PRIORITY_CLASS`
            - `HIGH_PRIORITY_CLASS`
            - `IDLE_PRIORITY_CLASS`
            - `NORMAL_PRIORITY_CLASS`
            - `REALTIME_PRIORITY_CLASS`
            - `CREATE_NO_WINDOW`
            - `DETACHED_PROCESS`
            - `CREATE_DEFAULT_ERROR_MODE`
            - `CREATE_BREAKAWAY_FROM_JOB`
            
            Defaults to `0`.
        restore_signals : `bool`, Optional
            If given as `True`, so by default, all signals that Python has set to `SIG_IGN` are restored to `SIG_DFL`
            in the child process before the exec. Currently this includes the `SIGPIPE`, `SIGXFZ` and `SIGXFSZ`
            signals. POSIX only.
        start_new_session : `bool`, Optional
            If given as `True` the `setsid()` system call will be made in the child process prior to the execution of
            the subprocess. POSIX only, defaults to `False`.
        pass_fds : `tuple`, Optional
            An optional sequence of file descriptors to keep open between the parent and the child. Providing any
            `pass_fds` forces `close_fds` to be `True`. POSIX only, defaults to empty tuple.
        **process_open_kwargs : Additional keyword parameters
            Additional parameters to pass to the `Popen`.
        
        Returns
        -------
        process : ``AsyncProcess``
        
        Raises
        ------
        TypeError
            If `cmd` is not given as `str` not `bytes` object.
        NotImplementedError
            Not supported on windows by the library.
        """)
    
    set_docs(subprocess_exec,
        """
        Create a subprocess from one or more string parameters specified by args.
        
        This is similar to the standard library `subprocess.Popen` class called with `shell=False`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        program : `str`
            The program executable.
        *args : `str`
            Parameters to open the `program` with.
        stdin : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, Optional (Keyword only)
            Standard input for the created shell. Defaults to `subprocess.PIPE`.
        stdout : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, Optional (Keyword only)
            Standard output for the created shell. Defaults to `subprocess.PIPE`.
        stderr : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, `subprocess.STDOUT`, Optional (Keyword only)
            Standard error for the created shell. Defaults to `subprocess.PIPE`.
        extra : `None` or `dict` of (`str`, `Any`) items, Optional (Keyword only)
            Optional transport information.
        preexecution_function : `None` or `callable`, Optional (Keyword only)
            This object is called in the child process just before the child is executed. POSIX only, defaults to
            `None`.
        close_fds : `bool`, Optional (Keyword only)
            Defaults to `True`
            
            If `close_fds` is True, all file descriptors except `0`, `1` and `2` will be closed before the child
            process is executed. Otherwise when `close_fds` is False, file descriptors obey their inheritable flag as
            described in Inheritance of File Descriptors.
        cwd : `str`, `bytes`, `path-like` or `None`, Optional (Keyword only)
            If `cwd` is not `None`, the function changes the working directory to cwd before executing the child.
            Defaults to `None`
        startup_info : `subprocess.STARTUPINFO` or `None`, Optional (Keyword only)
            Is passed to the underlying `CreateProcess` function.
        creation_flags : `int`, Optional (Keyword only)
            Can be given as 1 of the following flags:
            
            - `CREATE_NEW_CONSOLE`
            - `CREATE_NEW_PROCESS_GROUP`
            - `ABOVE_NORMAL_PRIORITY_CLASS`
            - `BELOW_NORMAL_PRIORITY_CLASS`
            - `HIGH_PRIORITY_CLASS`
            - `IDLE_PRIORITY_CLASS`
            - `NORMAL_PRIORITY_CLASS`
            - `REALTIME_PRIORITY_CLASS`
            - `CREATE_NO_WINDOW`
            - `DETACHED_PROCESS`
            - `CREATE_DEFAULT_ERROR_MODE`
            - `CREATE_BREAKAWAY_FROM_JOB`
            
            Defaults to `0`.
        restore_signals : `bool`, Optional (Keyword only)
            If given as `True`, so by default, all signals that Python has set to `SIG_IGN` are restored to `SIG_DFL`
            in the child process before the exec. Currently this includes the `SIGPIPE`, `SIGXFZ` and `SIGXFSZ`
            signals. POSIX only.
        start_new_session : `bool`, Optional (Keyword only)
            If given as `True` the `setsid()` system call will be made in the child process prior to the execution of
            the subprocess. POSIX only, defaults to `False`.
        pass_fds : `tuple`, Optional (Keyword only)
            An optional sequence of file descriptors to keep open between the parent and the child. Providing any
            `pass_fds` forces `close_fds` to be `True`. POSIX only, defaults to empty tuple.
        **process_open_kwargs : Additional keyword parameters
            Additional parameters to pass to the `Popen`.
        
        Returns
        -------
        process : ``AsyncProcess``
        
        Raises
        ------
        NotImplementedError
            Not supported on windows by the library.
        """)