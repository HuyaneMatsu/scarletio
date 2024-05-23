__all__ = ('EventThread', )

import errno, os, subprocess, sys
import socket as module_socket
from collections import deque
from datetime import datetime as DateTime
from functools import partial as partial_func
from heapq import heappop, heappush
from itertools import chain
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from ssl import SSLContext, create_default_context
from stat import S_ISSOCK
from threading import Thread, current_thread
from warnings import warn

from ...utils import IS_UNIX, Reference, WeakSet, alchemy_incendiary, copy_docs, export, include, is_coroutine

from ..exceptions import CancelledError
from ..protocols_and_transports import (
    DatagramSocketTransportLayer, ReadWriteProtocolBase, SSLBidirectionalTransportLayer, SocketTransportLayer,
    UnixReadPipeTransportLayer, UnixWritePipeTransportLayer
)
from ..subprocess import AsyncProcess
from ..time import LOOP_TIME, LOOP_TIME_RESOLUTION
from ..traps import Future, FutureWrapperAsync, Task, TaskGroup

from .cycler import Cycler
from .event_loop_functionality_helpers import (
    EventThreadRunDescriptor, _HAS_IPv6, _ip_address_info, _is_stream_socket, _iter_futures_of, _set_reuse_port
)
from .event_thread_suspender import ThreadSuspenderContext
from .event_thread_type import EventThreadType
from .executor import Executor
from .handles import Handle, TimerHandle, TimerWeakHandle
from .server import Server

write_exception_async = include('write_exception_async')
write_exception_maybe_async = include('write_exception_maybe_async')


CALL_LATER_DEPRECATED = DateTime.utcnow() > DateTime(2024, 1, 1)


@export
class EventThread(Executor, Thread, metaclass = EventThreadType):
    """
    Event loops run asynchronous tasks and callbacks, perform network IO operations, and runs subprocesses.
    
    At hata event loops are represented by ``EventThread``-s, which do not block the source thread, as they say, they
    use their own thread for it.
    
    Attributes
    ----------
    _kept_executor_count : `int`
        The minimal amount of executors to keep alive (or not close).
    _kept_executor_last_schedule : `float`
        When was last time cleanup scheduled.
    _kept_executor_release_handle : `None`, ``TimerHandle``
        Executor release handle.
    claimed_executors : `set` of ``ExecutorThread``
        Claimed executors, which are given back to the executor on release.
    free_executors : `deque`
        The free (or not used) executors of the executor.
    running_executors : `set` of ``ExecutorThread``
        The executors under use.
    _async_generators: `WeakSet` of `async_generator`
        The asynchronous generators bound to the event loop.
    _async_generators_shutdown_called : `bool`
        Whether the event loop's asynchronous generators where shut down.
    _self_write_socket : `socket.socket`
        Socket, which can be used to wake up the thread by writing into it.
    _ready : `deque` of ``Handle``
        Ready to run handles of the event loop.
    _scheduled : `list` of ``TimerHandle``
        Scheduled timer handles, which will be moved to ``._ready`` when their `when` becomes lower or equal to the
        respective loop time.
    _self_read_socket : `socket.socket`
        Socket, which reads from ``._self_write_socket``.
    context : ``EventThreadContextManager``
        Context of the event loop to ensure it's safe startup and closing.
    current_task : `None`, ``Task``
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
    
    __slots__ = (
        '__dict__', '__weakref__', '_async_generators', '_async_generators_shutdown_called', '_self_write_socket',
        '_ready', '_scheduled', '_self_read_socket', 'context', 'current_task', 'running', 'selector', 'should_run',
        'started',
    )
    
    def __init__(self):
        """
        Creates a new ``EventThread`` with the given parameters.
        
        Notes
        -----
        This magic method is called by ``EventThreadType.__call__``, what does the other steps of the initialization.
        """
        Executor.__init__(self)
        self.should_run = True
        self.running = False
        self.started = False
        self.selector = DefaultSelector()
        
        self._ready = deque()
        self._scheduled = []
        self.current_task = None
        
        self._async_generators = WeakSet()
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
        repr_parts = ['<', self.__class__.__name__, ' ', self._name]
        self.is_alive() # easy way to get ._is_stopped set when appropriate
        
        if not self.started:
            state = 'created'
        elif self._is_stopped or (not self.running):
            state = 'stopped'
        else:
            state = 'started'
        repr_parts.append(', state = ')
        repr_parts.append(state)
        
        daemon = self._daemonic
        if daemon:
            repr_parts.append(', daemon = ')
            repr_parts.append(repr(daemon))
        
        ident = self._ident
        if (ident is not None):
            repr_parts.append(', ident = ')
            repr_parts.append(str(ident))
        
        repr_parts.append(' executor info: free = ')
        repr_parts.append(str(self.get_free_executor_count()))
        repr_parts.append(', used = ')
        repr_parts.append(str(self.get_used_executor_count()))
        
        repr_parts.append(' >')
        return ''.join(repr_parts)
    
    
    def call_later(self, delay, callback, *args):
        """
        Deprecated and will be removed in 2024 August. Please use ``.call_after`` instead.
        """
        if CALL_LATER_DEPRECATED:
            warn(
                (
                    f'`{self.__class__.__name__}.call_later` is deprecated and will be removed in 2024 August. '
                    f'Please use `.call_after` instead.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
        
        return self.call_after(delay, callback, *args)
    
    
    def call_after(self, delay, callback, *args):
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
        handle : `None`, ``TimerHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerHandle(LOOP_TIME() + delay, callback, args)
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
        handle : `None`, ``TimerHandle``
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
        Deprecated and will be removed in 2024 August. Please use ``.call_after_weak`` instead.
        """
        if CALL_LATER_DEPRECATED:
            warn(
                (
                    f'`{self.__class__.__name__}.call_later_weak` is deprecated and will be removed in 2024 August. '
                    f'Please use `.call_after_weak` instead.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
        
        return self.call_after_weak(delay, callback, *args)
    
    
    def call_after_weak(self, delay, callback, *args):
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
        handle : `None`, ``TimerWeakHandle``
            The created handle is returned, what can be used to cancel it. If the event loop is stopped, returns `None`.
        
        Raises
        ------
        TypeError
            If `callback` cannot be weakreferenced.
        """
        if not self.running:
            if not self._maybe_start():
                return None
        
        handle = TimerWeakHandle(LOOP_TIME() + delay, callback, args)
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
        handle : `None`, ``TimerWeakHandle``
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
        handle : `None`, ``Handle``
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
        handle : `None`, ``Handle``
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
        handle : `None`, ``Handle``
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
    
    
    def cycle(self, cycle_time, *funcs, priority = 0):
        """
        Cycles the given functions on an event loop, by calling them after every `n` amount of seconds.
        
        Parameters
        ----------
        cycle_time : `float`
            The time interval of the cycler to call the added functions.
        *funcs : `callable`
            Callables, what the cycler will call.
        priority : `int` = `0`, Optional (Keyword only)
            Priority order of the added callables, which define in which order the given `funcs` will be called.
        
        Returns
        -------
        cycler : ``Cycler``
            A cycler with what the added function and the cycling can be managed.
        """
        return Cycler(self, cycle_time, *funcs, priority = priority)
    
    
    def _schedule_callbacks(self, future):
        """
        Schedules the callbacks of the given future.
        
        Parameters
        ----------
        future : ``Future``
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
        coroutine : `CoroutineType`, `GeneratorType`
            The coroutine, to wrap.
        
        Returns
        -------
        task : ``Task``
            The created task instance.
        """
        return Task(self, coroutine)
    
    
    def create_task_thread_safe(self, coroutine):
        """
        Creates a task wrapping the given coroutine and wakes up the event loop. Wakes up the event loop if sleeping,
        what means it is safe to use from other threads as well.
        
        Parameters
        ----------
        coroutine : `CoroutineType`, `GeneratorType`
            The coroutine, to wrap.
        
        Returns
        -------
        task : ``Task``
            The created task instance.
        """
        task = Task(self, coroutine)
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
        Ensures the given coroutine or future on the event loop. Returns an awaitable ``Future``.
        
        Parameters
        ----------
        coroutine_or_future : `awaitable`
            The coroutine or future to ensure.
        
        Returns
        -------
        future : ``Future``.
            The return type depends on `coroutine_or_future`'s type.
            
            - If `coroutine_or_future` is given as `CoroutineType`, `GeneratorType`, returns a ``Task``.
            - If `coroutine_or_future` is given as ``Future``, bound to the current event loop, returns it.
            - If `coroutine_or_future`is given as ``Future``, bound to an other event loop, returns a
                ``FutureWrapperAsync``.
            - If `coroutine_or_future` defines an `__await__` method, then returns a ``Task``.
        
        Raises
        ------
        TypeError
            If `coroutine_or_future` is not `awaitable`.
        """
        if is_coroutine(coroutine_or_future):
            return Task(self, coroutine_or_future)
        
        if isinstance(coroutine_or_future, Future):
            if coroutine_or_future._loop is not self:
                coroutine_or_future = FutureWrapperAsync(coroutine_or_future, self)
            return coroutine_or_future
        
        type_ = type(coroutine_or_future)
        if hasattr(type_, '__await__'):
            return Task(self, type_.__await__(coroutine_or_future))
        
        raise TypeError(
            f'`coroutine_or_future` can be `{Future.__name__}`, `Coroutine`, `awaitable`, got '
            f'{coroutine_or_future.__class__.__name__}; {coroutine_or_future!r}.'
        )
    
    
    def ensure_future_thread_safe(self, coroutine_or_future):
        """
        Ensures the given coroutine or future on the event loop. Returns an awaitable ``Future``. Wakes up
        the event loop if sleeping, what means it is safe to use from other threads as well.
        
        Parameters
        ----------
        coroutine_or_future : `awaitable`
            The coroutine or future to ensure.
        
        Returns
        -------
        future : ``Future``.
            The return type depends on `coroutine_or_future`'s type.
            
            - If `coroutine_or_future` is given as `CoroutineType`, `GeneratorType`, returns a ``Task``.
            - If `coroutine_or_future` is given as ``Future``, bound to the current event loop, returns it.
            - If `coroutine_or_future`is given as ``Future``, bound to an other event loop, returns a
                ``FutureWrapperAsync``.
            - If `coroutine_or_future` defines an `__await__` method, then returns a ``Task``.
        
        Raises
        ------
        TypeError
            If `coroutine_or_future` is not `awaitable`.
        """
        if is_coroutine(coroutine_or_future):
            task = Task(self, coroutine_or_future)
            self.wake_up()
            return task
        
        if isinstance(coroutine_or_future, Future):
            if coroutine_or_future._loop is not self:
                coroutine_or_future = FutureWrapperAsync(coroutine_or_future, self)
            return coroutine_or_future
        
        type_ = type(coroutine_or_future)
        if hasattr(type_, '__await__'):
            task = Task(self, type_.__await__(coroutine_or_future))
            self.wake_up()
            return task

        raise TypeError(
            f'`coroutine_or_future` can be `{Future.__name__}`, `Coroutine`, `awaitable`, got '
            f'{coroutine_or_future.__class__.__name__}; {coroutine_or_future!r}.'
        )
    
    run = EventThreadRunDescriptor()
    
    def runner(self):
        """
        Runs the event loop, until ``.stop`` is called.
        
        Hata ``EventThread`` are created as already running event loops.
        """
        with self.context:
            key = None
            file_descriptor = None
            reader = None
            writer = None
            
            ready = self._ready # use thread safe type with no lock
            scheduled = self._scheduled # these can be added only from this thread
            
            while self.should_run:
                timeout = LOOP_TIME() + LOOP_TIME_RESOLUTION # calculate limit
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
                    timeout = scheduled[0].when - LOOP_TIME()
                else:
                    timeout = None
                
                event_list = self.selector.select(timeout)
                if event_list:
                    for key, mask in event_list:
                        file_descriptor = key.fileobj
                        reader, writer = key.data
                        if (reader is not None) and (mask & EVENT_READ):
                            if reader.cancelled:
                                self.remove_reader(file_descriptor)
                            else:
                                ready.append(reader)
                        if (writer is not None) and (mask & EVENT_WRITE):
                            if writer.cancelled:
                                self.remove_writer(file_descriptor)
                            else:
                                ready.append(writer)
                    
                    key = None
                    file_descriptor = None
                    reader = None
                    writer = None
                    
                event_list = None
                
                # process callbacks
                while ready:
                    handle = ready.popleft()
                    if not handle.cancelled:
                        handle._run()
                
                handle = None # remove from locals or the gc derps out.
    
    
    def caller(self, awaitable, timeout = None):
        """
        Ensures the given awaitable on the event loop and returns it's result when done.
        
        Parameters
        ----------
        awaitable : `awaitable`
            The awaitable to run.
        timeout : `None`, `float` = `None`, Optional
            Timeout after the awaitable should be cancelled. Defaults to `None`.
        
        Returns
        -------
        result : `object`
            Value returned by `awaitable`.
        
        Raises
        ------
        TypeError
            If `awaitable` is not `awaitable`.
        TimeoutError
             If `awaitable` did not finish before the given `timeout` is over.
        RuntimeError
            If called from itself.
        BaseException
            object exception raised by `awaitable`.
        """
        if current_thread() is self:
            raise RuntimeError(f'`{self.__class__.__name__}.run` should not be called from itself.')
        
        return self.ensure_future_thread_safe(awaitable).sync_wrap().wait(timeout, True)
    
    
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
        
        results = await TaskGroup(
            self,
            (Task(self, ag.aclose()) for ag in closing_async_generators),
        )
        
        for result, async_generator in zip(results, closing_async_generators):
            exception = result.exception
            if (exception is not None) and (not isinstance(exception,CancelledError)):
                await write_exception_async(
                    exception, [
                        'Exception occurred during shutting down async generator:\n',
                        repr(async_generator),
                    ],
                    loop = self,
                )
    
    
    def get_tasks(self):
        """
        Collects all the scheduled tasks and returns them.
        
        Returns
        -------
        tasks : `list` of ``Task``
        """
        future_checks_pending = set()
        
        # Collect all futures
        
        task = self.current_task
        if (task is not None):
            future_checks_pending.add(task)
        
        for handle in chain(self._ready, self._scheduled):
            future_checks_pending.update(_iter_futures_of(handle.func))
            
            for parameter in handle.iter_positional_parameters():
                future_checks_pending.update(_iter_futures_of(parameter))
        
        # Check callbacks
        
        future_checks_done = set()
        
        while future_checks_pending:
            future = future_checks_pending.pop()
            future_checks_done.add(future)
            
            for callback in future.iter_callbacks():
                for future in _iter_futures_of(callback):
                    if future not in future_checks_done:
                        future_checks_pending.add(future)
        
        # select tasks
        
        return [future for future in future_checks_done if isinstance(future, Task)]
    
    
    def _make_socket_transport(self, socket, protocol, waiter = None, *, extra = None, server = None):
        """
        Creates a socket transport with the given parameters.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket, what the transport will use.
        protocol : ``AbstractProtocolBase``
            The protocol of the transport.
        waiter : `None`, ``Future`` = `None`, Optional
            Waiter, what's result should be set, when the transport is ready to use.
        extra : `None`, `dict` of (`str`, `object`) item = `None`, Optional (Keyword only)
            Optional transport information.
        server : `None`, ``Server`` = `None`, Optional (Keyword only)
            The server to what the created socket will be attached to.
        
        Returns
        -------
        transport : ``SocketTransportLayer``
        """
        return SocketTransportLayer(self, extra, socket, protocol, waiter, server)
    
    
    def _make_ssl_transport(
        self,
        socket,
        protocol,
        ssl,
        waiter = None,
        *,
        server_side = False,
        server_host_name = None,
        extra = None,
        server = None,
    ):
        """
        Creates an ssl transport with the given parameters.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket, what the transport will use.
        protocol : ``AbstractProtocolBase``
            Asynchronous protocol implementation for the transport. The given protocol is wrapped into an
            ``SSLBidirectionalTransportLayer``
        ssl : `SSLContext`
            Ssl context of the respective connection.
        waiter : `None`, ``Future`` = `None`, Optional
            Waiter, what's result should be set, when the transport is ready to use.
        server_side : `bool` = `False`, Optional (Keyword only)
            Whether the created ssl transport is a server side.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            By default the value of the host parameter is used. If host is empty, there is no default and you must pass
            a value for `server_host_name`. If `server_host_name` is an empty string, hostname matching is disabled
            (which is a serious security risk, allowing for potential man-in-the-middle attacks).
        extra : `None`, `dict` of (`str`, `object`) items = `None`, Optional (Keyword only)
            Optional transport information.
        server : `None`, ``Server`` = `None`, Optional (Keyword only)
            The server to what the created socket will be attached to.
        
        Returns
        -------
        transport : ``SSLBidirectionalTransportLayerTransport``
            The created ssl transport.
        """
        ssl_transport = SSLBidirectionalTransportLayer(self, protocol, ssl, waiter, server_side, server_host_name, True)
        SocketTransportLayer(self, extra, socket, ssl_transport, None, server)
        return ssl_transport
    
    
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
    
    
    def _start_serving(self, protocol_factory, socket, ssl, server, backlog):
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
        ssl : `None`, `SSLContext`
            To enable ssl for the connections, give it as  `SSLContext`.
        server : `None`, ``Server``
            The respective server, what started to serve if applicable.
        backlog : `int`
            The maximum number of queued connections passed to `socket.listen()`.
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
        ssl : `None`, `SSLContext`
            The ssl type of the connection if any.
        server : `None`, ``Server``
            The respective server if applicable.
        backlog : `int`
            The maximum number of queued connections passed to `socket.listen()`.
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
                if err.errno not in (errno.EMFILE, errno.ENFILE, errno.ENOBUFS, errno.ENOMEM):
                    raise # The event loop will catch and log it.
                
                # Some platforms (e.g. Linux keep reporting the FD as ready, so we remove the read handler
                # temporarily. We'll try again in a while.
                self.remove_reader(socket.fileno())
                self.call_after(1.0, self._start_serving, protocol_factory, socket, ssl, server, backlog)
                
                write_exception_async(
                    err,
                    [
                        'Exception occurred at',
                        repr(self),
                        '._accept_connection\n',
                    ],
                    loop = self
                )
            
            else:
                extra = {'peer_name': address}
                Task(self, self._accept_connection_task(protocol_factory, connection_socket, extra, ssl, server))
    
    
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
        extra : `None`, `dict` of (`str`, `object`) item
            Optional transport information.
        ssl : `None`, `SSLContext`
            The ssl type of the connection if any.
        server : `None`, ``Server``
            The respective server if applicable.
        """
        try:
            protocol = protocol_factory()
            waiter = Future(self)
            if (ssl is None):
                transport = self._make_socket_transport(
                    connection_socket, protocol, waiter = waiter, extra = extra, server = server
                )
            else:
                transport = self._make_ssl_transport(
                    connection_socket,
                    protocol,
                    ssl,
                    waiter = waiter,
                    server_side = True,
                    extra = extra,
                    server = server,
                )
            
            try:
                await waiter
            except:
                transport.close()
                raise
        
        except (GeneratorExit, CancelledError):
            # Allow task cancellation
            raise
        
        except BaseException as err:
            await write_exception_async(
                err,
                [
                    'Exception occurred at ',
                    self.__class__.__name__,
                    '._accept_connection2\n',
                ],
                loop = self,
            )
    
    
    def add_reader(self, file_descriptor, callback, *args):
        """
        Registers read callback for the given fd.
        
        Parameters
        ----------
        file_descriptor : `int`
            The respective file descriptor.
        callback : `callable`
            The function, what is called, when data is received on the respective file descriptor.
        *args : Positional parameters
            Parameters to call `callback` with.
        
        Returns
        -------
        handle : ``Handle``
            The Handle ran when the socket is ready to be read.
        """
        if not self.running:
            if not self._maybe_start():
                raise RuntimeError('Event loop stopped.')
        
        handle = Handle(callback, args)
        try:
            key = self.selector.get_key(file_descriptor)
        except KeyError:
            self.selector.register(file_descriptor, EVENT_READ, (handle, None))
        else:
            reader, writer = key.data
            
            self.selector.modify(file_descriptor, key.events | EVENT_READ, (handle, writer))
            
            if reader is not None:
                reader.cancel()
        
        return handle
    
    
    def remove_reader(self, file_descriptor):
        """
        Removes a read callback for the given file descriptor.
        
        Parameters
        ----------
        file_descriptor : `int`
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
            key = self.selector.get_key(file_descriptor)
        except KeyError:
            return False
        
        reader, writer = key.data
        
        mask = key.events & ~EVENT_READ
        if mask:
            self.selector.modify(file_descriptor, mask, (None, writer))
        else:
            self.selector.unregister(file_descriptor)
        
        if reader is not None:
            reader.cancel()
            return True
        
        return False
    
    
    def add_writer(self, file_descriptor, callback, *args):
        """
        Registers a write callback for the given file descriptor.
        
        Parameters
        ----------
        file_descriptor : `int`
            The respective file descriptor.
        callback : `callable`
            The function, what is called, when data the respective file descriptor becomes writable.
        *args : Positional parameters
            Parameters to call `callback` with.
        
        Returns
        -------
        handle : ``Handle``
            The Handle ran when the socket is ready to be written.
        """
        if not self.running:
            if not self._maybe_start():
                raise RuntimeError('Event loop is cancelled.')
        
        handle = Handle(callback, args)
        try:
            key = self.selector.get_key(file_descriptor)
        except KeyError:
            self.selector.register(file_descriptor, EVENT_WRITE, (None, handle))
        
        else:
            reader, writer = key.data
            
            self.selector.modify(file_descriptor, key.events | EVENT_WRITE, (reader, handle))
            
            if writer is not None:
                writer.cancel()
        
        return handle
    
    
    def remove_writer(self, file_descriptor):
        """
        Removes a write callback for the given file_descriptor.
        
        Parameters
        ----------
        file_descriptor : `int`
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
            key = self.selector.get_key(file_descriptor)
        except KeyError:
            return False
        
        reader, writer = key.data
        
        mask = key.events & ~EVENT_WRITE
        if mask:
            self.selector.modify(file_descriptor, mask, (reader, None))
        else:
            self.selector.unregister(file_descriptor)
            
        if writer is not None:
            writer.cancel()
            return True
        
        return False
    
    
    async def connect_accepted_socket(self, protocol_factory, socket, *, ssl = None):
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
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        
        Returns
        -------
        transport : ``SSLBidirectionalTransportLayerTransport``, ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            If `socket` is not a stream socket.
        """
        if not _is_stream_socket(socket):
            raise ValueError(f'A stream `socket` was expected, got {socket!r}.')
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, '', True)
    
    
    def _create_connection_shared_precheck(self, ssl, server_host_name, host):
        """
        Shared precheck by ``.create_connection_to`` and by ``.create_connection_with``.
        
        Parameters
        ----------
        ssl : `None`, `bool`, `SSLContext`
            Whether ssl should be enabled.
        server_host_name : `None`, `str`
            Overwrites the host name that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If host
            is empty, there is no default and you must pass a value for `server_host_name`. If `server_host_name` is an
            empty string, host name matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        host : `None`, `str`
            To what network interfaces should the connection be bound.
        
        Returns
        -------
        ssl : ``None`, `SSLContext`
        server_host_name : `None`, `str`
        
        Raises
        ------
        ValueError
            - If `server_host_name` is not set, meanwhile using `ssl` without `host`.
            - If `server_host_name` is set, but `ssl` is.
        """
        if isinstance(ssl, bool):
            if ssl:
                ssl = create_default_context()
            else:
                ssl = None
        
        if (server_host_name is None):
            if (ssl is not None):
                # Use host as default for server_host_name.
                if host is None:
                    raise ValueError('You must set `server_host_name` when using `ssl` without a `host`.')
                
                server_host_name = host
        else:
            if ssl is None:
                raise ValueError('`server_host_name` is only meaningful with `ssl`.')
        
        return ssl, server_host_name
    
    
    async def create_connection_to(
        self,
        protocol_factory,
        host,
        port,
        *,
        ssl = None,
        socket_family = 0,
        socket_protocol = 0,
        socket_flags = 0,
        local_address = None,
        server_host_name = None,
    ):
        """
        Open a streaming transport connection to a given address specified by `host` and `port`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        host : `None`, `str`, Optional
            To what network interfaces should the connection be bound.
        port : `None`, `int`, Optional
            The port of the `host`.
        ssl : `None`, `bool`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        socket_family : `AddressFamily`, `int` = `0`, Optional (Keyword only)
            Can be either `AF_INET`, `AF_INET6`, `AF_UNIX`.
        socket_protocol : `int` = `0`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        socket_flags : `int` = `0`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        local_address : `tuple` of (`None`, `str`, `None`, `int`) = `None`, Optional (Keyword only)
            Can be given as a `tuple` (`local_host`, `local_port`) to bind the socket locally. The `local_host` and
            `local_port` are looked up by ``.get_address_info``.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            By default the value of the host parameter is used. If host is empty, there is no default and you must pass
            a value for `server_host_name`. If `server_host_name` is an empty string, hostname matching is disabled
            (which is a serious security risk, allowing for potential man-in-the-middle attacks).
        
        Raises
        ------
        ValueError
            - If `server_host_name` is not set, meanwhile using `ssl` without `host`.
            - If `server_host_name` is set, but `ssl` is.
        OSError
            - `get_address_info()` returned empty list.
            - Error while attempting to bind to address.
            - Cannot open connection to any address.
        """
        ssl, server_host_name = self._create_connection_shared_precheck(ssl, server_host_name, host)
        
        future_1 = self._ensure_resolved(
            (host, port),
            family = socket_family,
            type = module_socket.SOCK_STREAM,
            protocol = socket_protocol,
            flags = socket_flags,
        )
        
        if local_address is None:
            future_2 = None
        
        else:
            future_2 = self._ensure_resolved(
                local_address,
                family = socket_family,
                type = module_socket.SOCK_STREAM,
                protocol = socket_protocol,
                flags = socket_flags,
            )
        
        # await futures
        try:
            await future_1
        except:
            if (future_2 is not None):
                future_2.cancel()
            raise
        
        if (future_2 is not None):
            await future_2
        
        
        infos = future_1.get_result()
        if not infos:
            raise OSError('`get_address_info` returned empty list.')
        
        if (future_2 is None):
            local_address_infos = None
        else:
            local_address_infos = future_2.get_result()
            if not local_address_infos:
                raise OSError('`get_address_info` returned empty list.')
        
        exceptions = []
        for socket_family, socket_type, socket_protocol, socket_address_canonical_name, address in infos:
            
            socket = module_socket.socket(family = socket_family, type = socket_type, proto = socket_protocol)
            
            try:
                socket.setblocking(False)
                
                if (local_address_infos is not None):
                    for element in local_address_infos:
                        local_address = element[4]
                        try:
                            socket.bind(local_address)
                            break
                        except OSError as err:
                            err = OSError(
                                err.errno,
                                (
                                    f'Error while attempting to bind on address '
                                    f'{local_address!r}: {err.strerror.lower()}.'
                                ),
                            )
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
                exception_representations = [repr(exception) for exception in exceptions]
                exception_representation_model = exception_representations[0]
                
                for exception_representation in exception_representations:
                    if exception_representation != exception_representation_model:
                        break
                else:
                    raise exceptions[0]
                
                # Raise a combined exception so the user can see all the various error messages.
                raise OSError(
                    f'Multiple exceptions: {", ".join(exception_representations)}'
                )
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def create_connection_with(self, protocol_factory, socket, *, ssl = None, server_host_name = None):
        """
        Opens a stream transport connection to the given `socket`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            Whether should use an existing, already connected socket.
        ssl : `None`, `bool`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the host name that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If host
            is empty, there is no default and you must pass a value for `server_host_name`. If `server_host_name` is an
            empty string, host name matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            - If `server_host_name` is not set, meanwhile using `ssl` without `host`.
            - If `server_host_name` is set, but `ssl` is.
        OSError
            - `get_address_info()` returned empty list.
            - Error while attempting to bind to address.
            - Cannot open connection to any address.
        """
        ssl, server_host_name = self._create_connection_shared_precheck(ssl, server_host_name, None)
        
        if not _is_stream_socket(socket):
            raise ValueError(f'A stream `socket` was expected, got {socket!r}.')
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def _create_connection_transport(self, socket, protocol_factory, ssl, server_host_name, server_side):
        """
        Open a streaming transport connection to a given address specified by `host` and `port`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        ssl : `None`, `SSLContext`
            Whether ssl should be enabled.
        socket : `socket.socket`
            The socket to what the created transport should be connected to.
        server_host_name : `None`, `str`
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If host
            is empty, there is no default and you must pass a value for `server_host_name`. If `server_host_name` is an
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
            transport = self._make_ssl_transport(
                socket, protocol, ssl, waiter, server_side = server_side, server_host_name = server_host_name
            )
        
        try:
            await waiter
        except:
            transport.close()
            raise
        
        return protocol
    
    
    def _create_unix_connection_shared_precheck(self, ssl, server_host_name):
        """
        Shared precheck used by ``.create_unix_connection_to` and by ``.create_unix_connection_with``.
        
        Parameters
        ----------
        ssl : `None`, `bool`, `SSLContext`
            Whether ssl should be enabled.
        server_host_name : `None`, `str`
            Overwrites the host name that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`.
        
        Returns
        -------
        ssl : ``None`, `SSLContext`
        server_host_name : `None`, `str`
        
        Raises
        ------
            - If `server_host_name` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_host_name` is not.
        """
        if isinstance(ssl, bool):
            if ssl:
                ssl = create_default_context()
            else:
                ssl = None
        
        if (ssl is None):
            if server_host_name is not None:
                raise ValueError('`server_host_name` is only meaningful with `ssl`.')
        else:
            if server_host_name is None:
                raise ValueError('`server_host_name` parameter is required with `ssl`.')
        
        return ssl, server_host_name
    

    async def create_unix_connection_to(self, protocol_factory, path, *, ssl = None, server_host_name = None):
        """
        Establish a unix socket connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        path : `None`, `str`
            The path to open connection to.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`. By default the value of the host parameter is used. If hos
            is empty, there is no default and you must pass a value for `server_host_name`. If `server_host_name` is an
            empty string, hostname matching is disabled (which is a serious security risk, allowing for potential
            man-in-the-middle attacks).
        
        Returns
        -------
        transport : ``SSLBidirectionalTransportLayerTransport``, ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            - If `server_host_name` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_host_name` is not.
        NotImplementedError
            Not supported on windows by the library.
        """
        ssl, server_host_name = self._create_unix_connection_shared_precheck(ssl, server_host_name)
        
        path = os.fspath(path)
        socket = module_socket.socket(module_socket.AF_UNIX, module_socket.SOCK_STREAM, 0)
        
        try:
            socket.setblocking(False)
            await self.socket_connect(socket, path)
        except:
            socket.close()
            raise
        
        return await self._create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def create_unix_connection_with(self, protocol_factory, socket, *, ssl = None, server_host_name = None):
        """
        Establish a unix socket connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`.
            Callable returning an asynchronous protocol implementation.
        socket : `socket.socket`
            A preexisting socket object to use up.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`.
        
        Returns
        -------
        transport : ``SSLBidirectionalTransportLayerTransport``, ``SocketTransportLayer``
            The created transport. If `ssl` is enabled, creates ``SSLBidirectionalTransportLayerTransport``, else
            ``SocketTransportLayer``.
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        
        Raises
        ------
        ValueError
            - If `server_host_name` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_host_name` is not.
            - If `socket`'s is not an unix domain stream socket.
        NotImplementedError
            Not supported on windows by the library.
        """
        ssl, server_host_name = self._create_unix_connection_shared_precheck(ssl, server_host_name)
        
        if socket.family not in (module_socket.AF_UNIX, module_socket.SOCK_STREAM):
            raise ValueError(f'A unix domain stream `socket` was expected, got {socket!r}.')
        
        socket.setblocking(False)
    
        return await self._create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def open_unix_connection_to(self, path, *, ssl = None, server_host_name = None):
        """
        Creates an unix connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        path : `str`
            The path to open connection to.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`.
        
        Returns
        -------
        protocol : ``BaseProtocol``
            The connected read and write protocol.
        
        Raises
        ------
        ValueError
            - If `server_host_name` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_host_name` is not.
        NotImplementedError
            Not supported on windows by the library.
        """
        return await self.create_unix_connection_to(
            partial_func(ReadWriteProtocolBase, self),
            path,
            ssl = ssl,
            server_host_name = server_host_name,
        )
    
    async def open_unix_connection_with(self, socket, *, ssl = None, server_host_name = None):
        """
        Creates an unix connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            A preexisting socket object to use up.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether ssl should be enabled.
        server_host_name : `None`, `str` = `None`, Optional (Keyword only)
            Overwrites the hostname that the target server’s certificate will be matched against.
            Should only be passed if `ssl` is not `None`.
        
        Returns
        -------
        protocol : ``BaseProtocol``
            The connected read and write protocol.
        
        Raises
        ------
        ValueError
            - If `server_host_name` parameter is given, but `ssl` isn't.
            - If `ssl` parameter is given, but `server_host_name` is not.
            - If `socket`'s is not an unix domain stream socket.
        NotImplementedError
            Not supported on windows by the library.
        """
        return await self.create_unix_connection_with(
            partial_func(ReadWriteProtocolBase, self),
            socket,
            ssl = ssl,
            server_host_name = server_host_name,
        )
    
    
    def _create_unix_server_shared_precheck(self, ssl):
        """
        Shared precheck used by ``.create_unix_server_to`` and ``.create_unix_server_with``.
        
        Parameters
        ----------
        ssl : `None`, `SSLContext`
            Whether ssl should be enabled.
        
        Returns
        -------
        ssl : ``None`, `SSLContext`
        """
        if (ssl is not None) and (not isinstance(ssl, SSLContext)):
            raise TypeError(f'`ssl` can be `None`, `SSLContext`, got {ssl.__class__.__name__}.')
        
        return ssl
    
    
    async def create_unix_server_to(self, protocol_factory, path, *, backlog = 100, ssl = None):
        """
        Creates an unix server (socket type AF_UNIX) listening on the given path.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        path : `str`
            The path to open connection to.
        backlog : `int` = `100`, Optional (Keyword only)
            The maximum number of queued connections passed to `socket.listen()`.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        
        Returns
        -------
        server : ``Server``
            The created server instance.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given neither as `None` nor as `SSLContext`.
        FileNotFoundError:
            The given `path` do not exists.
        OsError
            - Path already in use.
            - Error while attempting to connect to `path`.
        NotImplementedError
            Not supported on windows by the library.
        """
        ssl = self._create_unix_server_shared_precheck(ssl)
    
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
        except OSError as err:
            socket.close()
            if err.errno == errno.EADDRINUSE:
                # Let's improve the error message by adding  with what exact address it occurs.
                raise OSError(
                    errno.EADDRINUSE,
                    f'Address {path!r} is already in use.'
                ) from None
            
            else:
                raise
        
        except:
            socket.close()
            raise
        
        
        socket.setblocking(False)
        
        return Server(self, [socket], protocol_factory, ssl, backlog)
    
    
    async def create_unix_server_with(self, protocol_factory, socket, *, backlog = 100, ssl = None):
        """
        Creates an unix server (socket type AF_UNIX) listening with the given socket.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        socket : `socket.socket`
            Can be specified in order to use a preexisting socket object.
        backlog : `int` = `100`, Optional (Keyword only)
            The maximum number of queued connections passed to `socket.listen()`.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        
        Returns
        -------
        server : ``Server``
            The created server instance.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given neither as `None` nor as `SSLContext`.
        ValueError
            - If `socket` is given, but it's type is not `module_socket.SOCK_STREAM`.
        NotImplementedError
            Not supported on windows by the library.
        """
        ssl = self._create_unix_server_shared_precheck(ssl)
        
        if socket.family not in (module_socket.AF_UNIX, module_socket.SOCK_STREAM):
            raise ValueError(f'A unix domain stream `socket` was expected, got {socket!r}.')
        
        socket.setblocking(False)
        
        return Server(self, [socket], protocol_factory, ssl, backlog)
    
    
    if not IS_UNIX:
        @copy_docs(create_unix_connection_to)
        async def create_unix_connection_to(self, protocol_factory, path, *, ssl = None, server_host_name = None):
            raise NotImplementedError
        
        @copy_docs(create_unix_connection_with)
        async def create_unix_connection_with(self, protocol_factory, socket, *, ssl = None, server_host_name = None):
            raise NotImplementedError
        
        @copy_docs(open_unix_connection_to)
        async def open_unix_connection_to(self, path, *, ssl = None, server_host_name = None):
            raise NotImplementedError
        
        @copy_docs(open_unix_connection_with)
        async def open_unix_connection_with(self, socket, *, ssl = None, server_host_name = None):
            raise NotImplementedError
        
        @copy_docs(create_unix_server_to)
        async def create_unix_server_to(self, protocol_factory, path, *, socket, backlog = 100, ssl = None):
            raise NotImplementedError
        
        @copy_docs(create_unix_server_with)
        async def create_unix_server_with(self, protocol_factory, socket, *, backlog = 100, ssl = None):
            raise NotImplementedError
    
    
    # await it
    def get_address_info(self, host, port, *, family = 0, type = 0, protocol = 0, flags = 0):
        """
        Asynchronous version of `socket.getaddrinfo()`.
        
        Parameters
        ----------
        host : `None`, `str`
            To respective network interface.
        port : `None`, `int`
            The port of the `host`.
        family :  `AddressFamily`, `int` = `0`, Optional (Keyword only)
            The address family.
        type : `SocketKind`, `int` = `0`, Optional (Keyword only)
            Socket type.
        protocol : `int` = `0`, Optional (Keyword only)
            Protocol type. Can be used to narrow host resolution.
        flags : `int` = `0`, Optional (Keyword only)
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what will yield the lookup's result.
            
            Might raise `OSError` or return a `list` of `tuple`-s with the following elements:
            - `family` : `AddressFamily`, `int`. Address family.
            - `type` : `SocketKind`, `int`. Socket type.
            - `protocol` : `int`. Protocol type.
            - `canonical_name` : `str`. Represents the canonical name of the host.
            - `socket_address` : `tuple` (`str, `int`). Socket address containing the `host` and the `port`.
        """
        return self.run_in_executor(
            alchemy_incendiary(module_socket.getaddrinfo, (host, port, family, type, protocol, flags))
        )
    
    # await it
    def get_name_info(self, socket_address, flags = 0):
        """
        Asynchronous version of `socket.getnameinfo()`.
        
        Parameters
        ----------
        socket_address : `tuple` (`str`, `int`)
             Socket address as a tuple of `host` and `port`.
        flags : `int` = `0`, Optional
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what will yield the lookup's result.
        """
        return self.run_in_executor(alchemy_incendiary(module_socket.getnameinfo, (socket_address, flags,),))
    
    
    def _ensure_resolved(self, address, *, family = 0, type = module_socket.SOCK_STREAM, protocol = 0, flags = 0):
        """
        Ensures, that the given address is already a resolved IP. If not, gets it's address.
        
        Parameters
        ----------
        address : `tuple` ((`None`, `str`), (`None`, `int`))
            Address as a tuple of `host` and `port`.
        family :  `AddressFamily`, `int` = `0`, Optional (Keyword only)
            The address family.
        type : `SocketKind`, `int` = `module_socket.SOCK_STREAM`, Optional
            Socket type.
        protocol : `int` = `0`, Optional
            Protocol type. Can be used to narrow host resolution.
        flags : `int` = `0`, Optional
            Can be used to narrow host resolution.
        
        Returns
        -------
        future : ``Future``
            An awaitable future, what returns a `list` of `tuples` with the following elements:
            
            - `family` : `AddressFamily`, `int`. Address family.
            - `type` : `SocketKind`, `int`. Socket type.
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
            return self.get_address_info(host, port, family = family, type = type, protocol = protocol, flags = flags)
        
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
        try:
            conn, address = socket.accept()
            conn.setblocking(False)
        except (BlockingIOError, InterruptedError):
            pass
        else:
            return conn, address
        
        future = Future(self)
        file_descriptor = socket.fileno()
        handle = self.add_reader(file_descriptor, self._socket_accept, future, socket)
        future.add_done_callback(partial_func(self._socket_read_done_callback, file_descriptor, handle))
        
        return await future
    
    
    def _socket_accept(self, future, socket):
        """
        Method used by ``.socket_accept`` to check whether the respective socket can be accepted already.
        
        If the respective socket is already connected, then sets the waiter future's result instantly, else adds itself
        as a reader callback.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception is set, when the socket can be accepted or when an exception
            occurs.
        socket : `socket.socket`
            The respective socket, what's is listening for a connection.
        """
        if future.is_done():
            return
        
        try:
            conn, address = socket.accept()
            conn.setblocking(False)
        except (BlockingIOError, InterruptedError):
            return
        except BaseException as err:
            future.set_exception_if_pending(err)
        else:
            future.set_result_if_pending((conn, address))
        
        self.remove_reader(socket.fileno())
    
    
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
            resolved = self._ensure_resolved(address, family = socket.family, protocol = socket.proto)
            if not resolved.is_done():
                await resolved
            address = resolved.get_result()[0][4]
        
        try:
            socket.connect(address)
        except (BlockingIOError, InterruptedError):
            pass
        else:
            return
        
        future = Future(self)
        file_descriptor = socket.fileno()
        handle = self.add_writer(file_descriptor, self._socket_connect_callback, future, socket, address)
        future.add_done_callback(partial_func(self._socket_write_done_callback, file_descriptor, handle))
        
        return await future
    
    
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
        if future.is_done():
            return
        
        try:
            error_number = socket.getsockopt(module_socket.SOL_SOCKET, module_socket.SO_ERROR)
        except (BlockingIOError, InterruptedError):
            return # socket is still registered, the callback will be retried later
        
        except BaseException as err:
            future.set_exception(err)
        
        else:
            if error_number:
                future.set_exception(OSError(error_number, f'Connect call failed to: {address!r}.'))
            else:
                future.set_result(None)
        
        self.remove_writer(socket.fileno())
    
    
    async def socket_receive(self, socket, number_of_bytes):
        """
        Receive up to `number_of_bytes` from the given socket. Asynchronous version of `socket.recv()`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket to receive the data from. Must be a non-blocking socket.
        number_of_bytes : `int`
            The amount of data to receive in bytes.
        
        Returns
        -------
        data : `bytes`
            The received data.
        """
        try:
            data = socket.recv(number_of_bytes)
        except (BlockingIOError, InterruptedError):
            pass
        else:
            return data
        
        future = Future(self)
        file_descriptor = socket.fileno()
        handle = self.add_reader(file_descriptor, self._socket_receive, future, socket, number_of_bytes)
        future.add_done_callback(partial_func(self._socket_read_done_callback, file_descriptor, handle))
        
        return await future
    
    
    def _socket_receive(self, future, socket, number_of_bytes):
        """
        Added reader callback by ``.socket_receive``. This method is repeated till the data is successfully polled.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception will be set.
        socket : `socket.socket`
            The socket from what we read.
        number_of_bytes : `int`
            The amount of data to receive in bytes.
        """
        if future.is_done():
            return
        
        try:
            data = socket.recv(number_of_bytes)
        except (BlockingIOError, InterruptedError):
            return
        except BaseException as err:
            future.set_exception(err)
        else:
            future.set_result(data)
        
        self.remove_reader(socket.fileno())
    
    
    async def socket_receive_into(self, socket, buffer):
        """
        Receive data from the socket and stores it into the given buffer. Asynchronous version of `socket.recv_into()`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        socket : `socket.socket`
            The socket to receive the data from. Must be a non-blocking socket.
        buffer : `object`
            Buffer to receive the data into. Can be `bytearray` for example.
            
        Returns
        -------
        number_of_bytes : `int`
            The number of bytes received.
        """
        try:
            number_of_bytes = socket.recv_into(buffer)
        except (BlockingIOError, InterruptedError):
            pass
        else:
            return number_of_bytes
        
        future = Future(self)
        file_descriptor = socket.fileno()
        
        handle = self.add_reader(file_descriptor, self._socket_receive_into, future, socket, buffer)
        future.add_done_callback(partial_func(self._socket_read_done_callback, file_descriptor, handle))
        
        return await future
    
    
    def _socket_receive_into(self, future, socket, buffer):
        """
        Added reader callback by ``.socket_receive_into``. This method is repeated till data is successfully polled.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception will be set.
        socket : `socket.socket`
            The socket from what we read.
        buffer : `object`
            Buffer to receive the data into. Can be `bytearray` for example.
        """
        if future.is_done():
            return
        
        try:
            number_of_bytes = socket.recv_into(buffer)
        except (BlockingIOError, InterruptedError):
            return
        except BaseException as err:
            future.set_exception(err)
        else:
            future.set_result(number_of_bytes)
        
        self.remove_reader(socket.fileno())
    
    
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
        
        if not data:
            return
        
        try:
            number_of_bytes_written = socket.send(data)
        except (BlockingIOError, InterruptedError):
            number_of_bytes_written = 0
        else:
            if number_of_bytes_written == len(data):
                return
        
        future = Future(self)
        file_descriptor = socket.fileno()
        handle = self.add_writer(
            file_descriptor, self._socket_send_all, future, socket, data, Reference(number_of_bytes_written)
        )
        future.add_done_callback(partial_func(self._socket_write_done_callback, file_descriptor, handle))
        
        await future
    
    
    def _socket_send_all(self, future, socket, data, start_reference):
        """
        Added writer callback by ``.socket_send_all``. This method is repeated till the whole data is exhausted.
        
        Parameters
        ----------
        future : ``Future``
            Waiter future, what's result or exception will be set.
        socket : `socket.socket`
            The socket to what the data is sent to.
        data : `memoryview`
            Memoryview on the data to send.
        start_reference : ``Reference`` to `int`
            Reference to the start index.
        """
        if future.is_done():
            return
        
        start = start_reference.value
        
        try:
            number_of_bytes_written = socket.send(data[start:])
        except (BlockingIOError, InterruptedError):
            return
        except BaseException as err:
            future.set_exception(err)
        else:
            start += number_of_bytes_written
            if start != len(data):
                start_reference.value = start
                return
            
            future.set_result(None)
        
        self.remove_writer(socket.fileno())
    
    
    def _socket_write_done_callback(self, file_descriptor, handle, future):
        """
        Callback added to the waited future by ``socket_connect`` to remove the respective socket from the
        writers by it's file descriptor.
        
        The `file_descriptor` and `handle` parameters are passed initially when the callback is created.
        
        Attributes
        ----------
        file_descriptor : `int`
            The respective socket's file descriptor's identifier.
        handle : ``Handle``
            The Handle ran when the socket is ready to be read.
        future : ``Future``
            The respective future what's result is set when the socket connected successfully.
        """
        if not handle.cancelled:
            self.remove_writer(file_descriptor)
    
    
    def _socket_read_done_callback(self, file_descriptor, handle, future):
        """
        Done callback of ``.socket_receive_into`` and ``.socket_receive_into``. Called when the waiter future is done.
        
        The `file_descriptor` and `handle` parameters are passed initially when the callback is created.
        
        Parameters
        ----------
        file_descriptor : `int`
            The respective file descriptor.
        handle : ``Handle``
            Reader callback.
        future : ``Future``
            The respective future what's result is set when data is read successfully.
        """
        if not handle.cancelled:
            self.remove_reader(file_descriptor)
    
    
    async def _create_datagram_connection(self, protocol_factory, socket, address):
        """
        Creates a datagram connection.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        socket : `socket.socket`
            Socket to bind the datagram transport to.
        address : `None`, `tuple` (`str`, `int`)
            The last address, where the transport sent data. Defaults to `None`. The send target address should not
            differ from the last, where the transport sent data.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        """
        protocol = protocol_factory()
        waiter = Future(self)
        transport = DatagramSocketTransportLayer(self, None, socket, protocol, waiter, address)
        
        try:
            await waiter
        except:
            transport.close()
            raise
        
        return protocol
    
    
    async def create_datagram_connection_to(
        self,
        protocol_factory,
        local_address,
        remote_address,
        *,
        socket_family = 0,
        socket_protocol = 0,
        socket_flags = 0,
        reuse_port = False,
        allow_broadcast = False,
    ):
        """
        Creates a datagram connection. The socket type will be `SOCK_DGRAM`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        
        local_address : `None`, `tuple` of (`None`, `str`, `None`, `int`), `str`
            Can be given as a `tuple` (`local_host`, `local_port`) to bind the socket locally. The `local_host` and
            `local_port` are looked up by ``.get_address_info``.
            
            If `socket_family` is given as `AF_UNIX`, then also can be path of a file or a file descriptor.
        remote_address : `None`, `tuple` of (`None`, `str`, `None`, `int`), `str`
            Can be given as a `tuple` (`remote_host`, `remote_port`) to connect the socket to remove address. The
            `remote_host` and `remote_port` are looked up by ``.get_address_info``.
            
            If `socket_family` is given as `AF_UNIX`, then also can be path of a file or a file descriptor.
        socket_family : `AddressFamily`, `int` = `0`, Optional (Keyword only)
            Can be either `AF_INET`, `AF_INET6`, `AF_UNIX`.
        socket_protocol : `int` = `0`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        socket_flags : `int` = `0`, Optional (Keyword only)
            Can be used to narrow host resolution. Is passed to ``.get_address_info``.
        reuse_port : `bool` = `False`, Optional (Keyword only)
            Tells to the kernel to allow this endpoint to be bound to the same port as an other existing endpoint
            already might be bound to.
            
            Not supported on Windows.
        allow_broadcast : `bool` = `False`, Optional (Keyword only)
            Tells the kernel to allow this endpoint to send messages to the broadcast address.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        """
        address_info = []
        
        if (local_address is None) and (remote_address is None):
            if socket_family == 0:
                raise ValueError(
                    f'Unexpected address family: {socket_family!r}.'
                )
            
            address_info.append((socket_family, socket_protocol, None, None))
        
        elif hasattr(module_socket, 'AF_UNIX') and socket_family == module_socket.AF_UNIX:
            if __debug__:
                if (local_address is not None):
                    if not isinstance(local_address, str):
                        raise TypeError(
                            '`local_address` can be `None`, `str` if `socket_family` is `AF_UNIX`, got '
                            f'{local_address.__class__.__name__}; {local_address!r}.'
                        )
                
                if (remote_address is not None):
                    if not isinstance(remote_address, str):
                        raise TypeError(
                            '`remote_address` can be `None`, `str` if `socket_family` is `AF_UNIX`, got '
                            f'{remote_address.__class__.__name__}; {remote_address!r}.'
                        )
            
            if (
                (local_address is not None) and
                local_address and
                (local_address[0] != '\x00')
            ):
                try:
                    if S_ISSOCK(os.stat(local_address).st_mode):
                        os.remove(local_address)
                except FileNotFoundError:
                    pass
                except OSError as err:
                    # Directory may have permissions only to create socket.
                    sys.stderr.write(f'Unable to check or remove stale UNIX socket {local_address!r}: {err!s}.\n')
            
            address_info.append((socket_family, socket_protocol, local_address, remote_address))
        
        else:
            # join address by (socket_family, socket_protocol)
            address_infos = {}
            if (local_address is not None):
                infos = await self._ensure_resolved(
                    local_address,
                    family = socket_family,
                    type = module_socket.SOCK_DGRAM,
                    protocol = socket_protocol,
                    flags = socket_flags,
                )
                
                if not infos:
                    raise OSError('`get_address_info` returned empty list')
                
                for (
                    iterated_socket_family,
                    iterated_socket_type,
                    iterated_socket_protocol,
                    iterated_socket_address_canonical_name,
                    iterated_socket_address
                ) in infos:
                    address_infos[(iterated_socket_family, iterated_socket_protocol)] = (iterated_socket_address, None)
            
            if (remote_address is not None):
                infos = await self._ensure_resolved(
                    remote_address,
                    family = socket_family,
                    type = module_socket.SOCK_DGRAM,
                    protocol = socket_protocol,
                    flags = socket_flags,
                )
                
                if not infos:
                    raise OSError('`get_address_info` returned empty list.')
                
                
                for (
                    iterated_socket_family,
                    iterated_socket_type,
                    iterated_socket_protocol,
                    iterated_socket_address_canonical_name,
                    iterated_socket_address,
                ) in infos:
                    key = (iterated_socket_family, iterated_socket_protocol)
                    
                    try:
                        value = address_infos[key]
                    except KeyError:
                        address_value_local = None
                    else:
                        address_value_local = value[0]
                    
                    address_infos[key] = (address_value_local, iterated_socket_address)
            
            for key, (address_value_local, address_value_remote) in address_infos.items():
                if (local_address is not None) and (address_value_local is None):
                    continue
                
                if (remote_address is not None) and (address_value_remote is None):
                    continue
                
                address_info.append((*key, address_value_local, address_value_remote))
            
            if not address_info:
                raise ValueError('Can not get address information.')
        
        exception = None
        
        for socket_family, socket_protocol, local_address, remote_address in address_info:
            socket = None
            try:
                socket = module_socket.socket(
                    family = socket_family,
                    type = module_socket.SOCK_DGRAM,
                    proto = socket_protocol,
                )
                
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
        
        return await self._create_datagram_connection(protocol_factory, socket, remote_address)
    

    async def create_datagram_connection_with(self, protocol_factory, socket):
        """
        Creates a datagram connection. The socket type will be `SOCK_DGRAM`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        socket : `socket.socket`
            Can be specified in order to use a preexisting socket object.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The protocol returned by `protocol_factory`.
        """
        if socket.type != module_socket.SOCK_DGRAM:
            raise ValueError(f'A UDP `socket` was expected, got {socket!r}.')
        
        socket.setblocking(False)
        
        return await self._create_datagram_connection(protocol_factory, socket, None)
    
    
    def _create_server_get_address_info(self, host, port, socket_family, socket_flags):
        """
        Gets address info for the given parameters. This method is used by ``.create_server``, when resolving hosts.
        
        Parameters
        ----------
        host : `None`, `str`, (`None`, `str`)
            Network interfaces should the server be bound.
        port : `None`, `int`
            The port to use by the `host`.
        socket_family : `AddressFamily`, `int`
            The family of the address.
        socket_flags : `int`
            Bit-mask for `get_address_info`.
        
        Returns
        -------
        future : ``Future``
            A future, what's result is set, when the address is dispatched.
        """
        return self._ensure_resolved(
            (host, port), family = socket_family, type = module_socket.SOCK_STREAM, flags = socket_flags
        )
    
    
    def _create_server_shared_precheck(self, ssl):
        """
        Shared precheck used by ``.create_server`` and by ``.create_server``.
        
        Parameters
        ----------
        ssl : `None`, `SSLContext`
            Whether and what ssl is enabled for the connections.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given either as `None`, `SSLContext`.
        """
        if (ssl is not None) and (not isinstance(ssl, SSLContext)):
            raise TypeError(f'`ssl` can be `None`, `SSLContext`, got {ssl.__class__.__name__}.')
        
        return ssl
    
    
    async def create_server_to(
        self,
        protocol_factory,
        host,
        port,
        *,
        socket_family = module_socket.AF_UNSPEC,
        socket_flags = module_socket.AI_PASSIVE,
        backlog = 100,
        ssl = None,
        reuse_address = (os.name == 'posix' and sys.platform != 'cygwin'),
        reuse_port = False,
    ):
        """
        Creates a TCP server (socket type SOCK_STREAM) listening on port of the host address.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        host : `None`, `str`, `iterable` of (`None`, `str`)
            To what network interfaces should the server be bound.
        port : `None`, `int`
            The port to use by the `host`(s).
        socket_family : `AddressFamily`, `int` = `module_socket.AF_UNSPEC`, Optional (Keyword only)
            Can be given either as `socket.AF_INET`, `socket.AF_INET6` to force the socket to use `IPv4`, `IPv6`.
            If not given, then  will be determined from host name.
        socket_flags : `int` = `module_socket.AI_PASSIVE`, Optional (Keyword only)
            Bit-mask for `get_address_info`.
        backlog : `int` = `100`, Optional (Keyword only)
            The maximum number of queued connections passed to `socket.listen()`.
        ssl : `None`, `SSLContext`, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        reuse_address : `bool`, Optional (Keyword only)
            Tells the kernel to reuse a local socket in `TIME_WAIT` state, without waiting for its natural timeout to
            expire. If not specified will automatically be set to True on Unix.
        reuse_port : `bool` = `False`, Optional (Keyword only)
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
            - If `ssl` is not given either as `None`, `SSLContext`.
            - If `reuse_port` is given as non `bool`.
            - If `reuse_address` is given as non `bool`.
            - If `reuse_port` is given as non `bool`.
            - If `host` is not given as `None`, `str` and neither as `iterable` of `None`, `str`.
        ValueError
            - If `reuse_port` is given as `True`, but not supported.
        OsError
            Error while attempting to binding to address.
        """
        ssl = self._create_server_shared_precheck(ssl)
        
        if (reuse_address is not None) and (not isinstance(reuse_address, bool)):
            raise TypeError(
                '`reuse_address` can be `None`,`bool`, got '
                f'{reuse_address.__class__.__name__};{reuse_address!r}.'
            )
        
        if (reuse_port is not None) and (not isinstance(reuse_port, bool)):
            raise TypeError(
                '`reuse_address` can be `None`, `bool`, got '
                f'{reuse_port.__class__.__name__}; {reuse_port!r}.'
            )
        
        if (reuse_port is not None) and reuse_port and (not hasattr(module_socket, 'SO_REUSEPORT')):
            raise ValueError('`reuse_port` not supported by the socket module.')
        
        hosts = []
        if (host is None) or (host == ''):
             hosts.append(None)
        elif isinstance(host, str):
            hosts.append(host)
        elif hasattr(type(host), '__iter__'):
            for host_element in host:
                if (host_element is None):
                    pass
                
                elif isinstance(host_element, str):
                    if host_element == '':
                        host_element = None
                
                else:
                    raise TypeError(
                        f'`host` can contain `None`, `str` elements, got '
                        f'`{host_element.__class__.__name__}`; {host_element!r}; host={host!r}.'
                    )
                
                hosts.append(host_element)
                continue
                
        else:
            raise TypeError(
                f'`host` can be `None`, `str`, `iterable` of (`None`, `str`), got {host.__class__.__name__}; {host!r}.'
            )
        
        sockets = []
        
        task_group = TaskGroup(
            self,
            (self._create_server_get_address_info(host, port, socket_family, socket_flags) for host in hosts),
        )
        
        try:
            async for future in task_group.exhaust():
                address_infos = future.get_result()
                
                for (
                    socket_family,
                    socket_type,
                    socket_protocol,
                    socket_address_canonical_name,
                    socket_address,
                ) in address_infos:
                    
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
                            raise ValueError(
                                '`reuse_port` not supported by socket module, `SO_REUSEPORT` defined '
                                'but not implemented.'
                            ) from err
                    
                    if (
                        _HAS_IPv6 and
                        (socket_family == module_socket.AF_INET6) and
                        hasattr(module_socket, 'IPPROTO_IPV6')
                    ):
                        socket.setsockopt(module_socket.IPPROTO_IPV6, module_socket.IPV6_V6ONLY, True)
                    try:
                        socket.bind(socket_address)
                    except OSError as err:
                        raise OSError(
                            err.errno,
                            (
                                f'Error while attempting to bind on address '
                                f'{socket_address!r}: {err.strerror.lower()!s}.'
                            ),
                        ) from None
        except:
            for socket in sockets:
                socket.close()
            
            task_group.cancel_all()
            raise
        
        for socket in sockets:
            socket.setblocking(False)
        
        return Server(self, sockets, protocol_factory, ssl, backlog)
    
    
    async def create_server_with(self, protocol_factory, socket, *, backlog = 100, ssl = None):
        """
        Creates a TCP server (socket type SOCK_STREAM) listening on port of the host address.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol_factory : `callable`
            Factory function for creating a protocols.
        socket : `None`, `socket.socket`
            Can be specified in order to use a preexisting socket object.
        backlog : `int` = `100`, Optional (Keyword only)
            The maximum number of queued connections passed to `socket.listen()`.
        ssl : `None`, `SSLContext` = `None`, Optional (Keyword only)
            Whether and what ssl is enabled for the connections.
        
        Returns
        -------
        server : ``Server``
            The created server instance.
        
        Raises
        ------
        TypeError
            - If `ssl` is not given either as `None`, `SSLContext`.
        ValueError
            - If `socket` is given, but it's type is not `module_socket.SOCK_STREAM`.
        OsError
            Error while attempting to binding to address.
        """
        ssl = self._create_server_shared_precheck(ssl)
        
        if socket.type != module_socket.SOCK_STREAM:
            raise ValueError(f'A stream `socket` was expected, got {socket!r}.')
        
        socket.setblocking(False)
        
        sockets = [socket]
        
        return Server(self, sockets, protocol_factory, ssl, backlog)
    
    
    async def connect_read_pipe(self, protocol, pipe):
        """
        Register the read end of the given pipe in the event loop.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            An async-io protocol implementation to use as the transport's protocol.
        pipe : `file-like`
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
        """
        return await UnixReadPipeTransportLayer(self, None, pipe, protocol)
    
    
    async def connect_write_pipe(self, protocol, pipe):
        """
        Register the write end of the given pipe in the event loop.
        
        This method is a coroutine.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            An async-io protocol implementation to use as the transport's protocol.
        pipe : `file-like`
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
        """
        return await UnixWritePipeTransportLayer(self, pipe, protocol)
    
    
    async def subprocess_shell(
        self,
        command,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        *,
        extra = None,
        preexecution_function = None,
        close_fds = True,
        cwd = None,
        startup_info = None,
        creation_flags = 0,
        restore_signals = True,
        start_new_session = False,
        pass_fds = (),
        **process_open_kwargs,
    ):
        """
        Create a subprocess from cmd.
        
        This is similar to the standard library `subprocess.Popen` class called with `shell = True`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        cmd : `str`, `bytes`
            The command to execute. Should use the platform’s “shell” syntax.
        stdin : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL` = `subprocess.PIPE`, Optional
            Standard input for the created shell
        stdout : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL` = `subprocess.PIPE`, Optional
            Standard output for the created shell.
        stderr : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, `subprocess.STDOUT` = `subprocess.PIPE`, Optional
            Standard error for the created shell
        extra : `None`, `dict` of (`str`, `object`) items = `None`, Optional (Keyword only)
            Optional transport information.
        preexecution_function : `None`, `callable` = `None`, Optional (Keyword only)
            This object is called in the child process just before the child is executed. POSIX only, defaults to
            `None`.
        close_fds : `bool` = `True`, Optional (Keyword only)
            Defaults to `True`
            
            If `close_fds` is True, all file descriptors except `0`, `1` and `2` will be closed before the child
            process is executed. Otherwise when `close_fds` is False, file descriptors obey their inheritable flag as
            described in Inheritance of File Descriptors.
        cwd : `None` `str`, `bytes`, `path-like` = `None`, Optional (Keyword only)
            The current working directory.
            
            If `cwd` is not `None`, the function changes the working directory to cwd before executing the child.
        
        startup_info : `None`, `subprocess.STARTUPINFO` = `None`, Optional (Keyword only)
            Is passed to the underlying `CreateProcess` function.
        creation_flags : `int` = `0`, Optional (Keyword only)
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
        restore_signals : `bool` = `True`, Optional (Keyword only)
            If given as `True`, so by default, all signals that Python has set to `SIG_IGN` are restored to `SIG_DFL`
            in the child process before the exec. Currently this includes the `SIGPIPE`, `SIGXFZ` and `SIGXFSZ`
            signals. POSIX only.
        start_new_session : `bool` = `False`, Optional (Keyword only)
            If given as `True` the `setsid()` system call will be made in the child process prior to the execution of
            the subprocess. POSIX only, defaults to `False`.
        pass_fds : `tuple` = `()`, Optional (Keyword only)
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
        """
        if not isinstance(command, (bytes, str)):
            raise TypeError(f'`command` can be `bytes`, `str`, got {command.__class__.__name__}; {command!r}.')
        
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
    
    
    async def subprocess_exec(
        self,
        program,
        *args,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        extra = None,
        preexecution_function = None,
        close_fds = True,
        cwd = None,
        startup_info = None,
        creation_flags = 0,
        restore_signals = True,
        start_new_session = False,
        pass_fds = (),
        **process_open_kwargs,
    ):
        """
        Create a subprocess from one or more string parameters specified by args.
        
        This is similar to the standard library `subprocess.Popen` class called with `shell = False`.
        
        This method is a coroutine.
        
        Parameters
        ----------
        program : `str`
            The program executable.
        *args : `str`
            Parameters to open the `program` with.
        stdin : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL` = `subprocess.PIPE`, Optional (Keyword only)
            Standard input for the created shell.
        stdout : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL` = `subprocess.PIPE`, Optional (Keyword only)
            Standard output for the created shell.
        stderr : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, `subprocess.STDOUT` = `subprocess.PIPE`
                , Optional (Keyword only)
            Standard error for the created shell.
        extra : `None`, `dict` of (`str`, `object`) items = `None`, Optional (Keyword only)
            Optional transport information.
        preexecution_function : `None`, `callable` = `None`, Optional (Keyword only)
            This object is called in the child process just before the child is executed. POSIX only, defaults to
            `None`.
        close_fds : `bool` = `True`, Optional (Keyword only)
            Defaults to `True`
            
            If `close_fds` is True, all file descriptors except `0`, `1` and `2` will be closed before the child
            process is executed. Otherwise when `close_fds` is False, file descriptors obey their inheritable flag as
            described in Inheritance of File Descriptors.
        cwd : `None`, `str`, `bytes`, `path-like` = `None`, Optional (Keyword only)
            The current working directory.
            
            If `cwd` is not `None`, the function changes the working directory to cwd before executing the child.
        startup_info : `None`, `subprocess.STARTUPINFO` = `None`, Optional (Keyword only)
            Is passed to the underlying `CreateProcess` function.
        creation_flags : `int` = `0`, Optional (Keyword only)
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
            
        restore_signals : `bool` = `True`, Optional (Keyword only)
            If given as `True`, so by default, all signals that Python has set to `SIG_IGN` are restored to `SIG_DFL`
            in the child process before the exec. Currently this includes the `SIGPIPE`, `SIGXFZ` and `SIGXFSZ`
            signals. POSIX only.
        start_new_session : `bool` = `False`, Optional (Keyword only)
            If given as `True` the `setsid()` system call will be made in the child process prior to the execution of
            the subprocess. POSIX only, defaults to `False`.
        pass_fds : `tuple` = `()`, Optional (Keyword only)
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
        """
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
        
        return await AsyncProcess(
            self, (program, *args), False, stdin, stdout, stderr, 0, extra, process_open_kwargs
        )

    if not IS_UNIX:
        @copy_docs(connect_read_pipe)
        async def connect_read_pipe(self, protocol, pipe):
            raise NotImplementedError
        
        @copy_docs(connect_write_pipe)
        async def connect_write_pipe(self, protocol, pipe):
            raise NotImplementedError
        
        @copy_docs(subprocess_shell)
        async def subprocess_shell(
            self,
            cmd,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            *,
            extra = None,
            preexecution_function = None,
            close_fds = True,
            cwd = None,
            startup_info = None,
            creation_flags = 0,
            restore_signals = True,
            start_new_session = False,
            pass_fds = (),
            **process_open_kwargs,
        ):
            raise NotImplementedError
        
        @copy_docs(subprocess_exec)
        async def subprocess_exec(
            self,
            program,
            *args,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            extra = None,
            preexecution_function = None,
            close_fds = True,
            cwd = None,
            startup_info = None,
            creation_flags = 0,
            restore_signals = True,
            start_new_session = False,
            pass_fds = (),
            **process_open_kwargs,
        ):
            raise NotImplementedError
