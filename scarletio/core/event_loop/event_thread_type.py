__all__ = ()

import socket as module_socket
import threading
from threading import Event as SyncEvent, Thread, current_thread

from ...utils import ignore_frame


ignore_frame(threading.__spec__.origin, '_bootstrap', 'self._bootstrap_inner()', )
ignore_frame(threading.__spec__.origin, '_bootstrap_inner', 'self.run()', )


class EventThreadContextManager:
    """
    Context manager of an ``EventThread``, which wraps it's runner. when the runner is started up, set it's ``waiter.``
    allowing the starter thread to continue.
    
    Attributes
    ----------
    thread : `None`, ``EventThread``
        The wrapped event loop.
    thread_waiter : `None`, `threading.Event`
       Threading event, what is set, when the thread is started up. Set as `None` after set.
    """
    __slots__ = ('thread', 'thread_waiter',)
    
    
    def __new__(cls, thread):
        """
        Creates a new event thread context.
        
        Parameters
        ----------
        thread : ``EventThread``
            The event thread to wrap.
        
        Returns
        -------
        self : ``EventThreadContextManager``
            The created instance
        thread_waiter : `threading.Event`
            Threading event, what is set, when the thread is started up.
        """
        self = object.__new__(cls)
        self.thread = thread
        self.thread_waiter = SyncEvent()
        return self
    
    
    def __enter__(self):
        """
        Called, when the respective event loop's runner started up.
        
        Enters the event loop runner setting it's waiter and finishes the loop's initialization.
        
        Raises
        ------
        RuntimeError
            - If ``EventThreadContextManager.__enter__`` was called a second time.
            - If called from a different thread as is bound to.
            - If the ``EventThread`` is already running.
            - If the ``EventThread`` is already stopped.
        """
        thread_waiter = self.thread_waiter
        if thread_waiter is None:
            raise RuntimeError(
                f'`{self.__class__.__name__}.__enter__` called with thread waiter lock set.'
            )
        
        try:
            thread = self.thread
            if (thread is not current_thread()):
                raise RuntimeError(
                    f'`{thread!r}.run` called from an other thread: {current_thread()!r}'
                )
            
            if (thread.running):
                raise RuntimeError(
                    f'`{thread!r}.run` called when the thread is already running.'
                )
            
            if (thread._is_stopped):
                raise RuntimeError(
                    f'`{thread!r}.run` called when the thread is already stopped.'
                )
            
            thread.running = True
            
            self_read_socket, self_write_socket = module_socket.socketpair()
            self_read_socket.setblocking(False)
            self_write_socket.setblocking(False)
            thread._self_read_socket = self_read_socket
            thread._self_write_socket = self_write_socket
            thread.add_reader(self_read_socket.fileno(), thread.empty_self_socket)
        finally:
            thread_waiter.set()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When the event loop's runner stops, it's context closes it.
        """
        thread = self.thread
        self.thread = None
        
        thread.running = False
        thread.remove_reader(thread._self_read_socket.fileno())
        try:
            thread._self_read_socket.close()
        except OSError as err:
            if err.errno != 9:
                raise
        finally:
            thread._self_read_socket = None
        
        try:
            thread._self_write_socket.close()
        except OSError as err:
            if err.errno != 9:
                raise
        finally:
            thread._self_write_socket = None
        
        thread._ready.clear()
        thread._scheduled.clear()
        
        thread.cancel_executors()
        
        selector = thread.selector
        if (selector is not None):
            thread.selector = None
            selector.close()
        
        return False



class EventThreadType(type):
    """
    Type of even thread, which manages their instances creation.
    """
    def __call__(cls, daemon = False, name = None, start_later = True, **kwargs):
        """
        Creates a new ``EventThread`` with the given parameters.
        
        Parameters
        ----------
        daemon : `bool` = `False`, Optional
            Whether the created thread should be daemon. Defaults to `False`.
        name : `None`, `str` = `None`, Optional
            The created thread's name. Defaults to `None`
        start_later : `bool` = `True`, Optional
            Whether the event loop should be started only later. Defaults to `True`.
        **kwargs : keyword parameters
            Additional event thread specific parameters.
        
        Returns
        -------
        obj : ``EventThread``
            The created event loop.
        """
        obj = Thread.__new__(cls)
        cls.__init__(obj, **kwargs)
        Thread.__init__(obj, daemon = daemon, name = name)
        
        obj.context = EventThreadContextManager(obj)
        
        if not start_later:
            obj._do_start()
        
        return obj
