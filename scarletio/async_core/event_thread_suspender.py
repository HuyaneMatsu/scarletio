__all__ = ('ThreadSuspenderContext',)

from threading import Event as SyncEvent

from .handles import Handle


class ThreadSuspenderContext:
    """
    Thread syncer for ``EventThread``-s, to stop their execution, meanwhile they are used inside of a a `with` block.
    The local thread's exception is stopped, meanwhile it waits for the ``EventThread`` top pause.
    
    Can be used as a context manager, like:
    
    ```py
    with ThreadSuspenderContext(LOOP):
        # The event loop is paused inside here.
    ```
    
    Or, can be used with ``EventThread.enter()`` as well, like:
    
    ```py
    with LOOP.enter():
        # The event loop is paused inside here.
    ```
    
    Attributes
    ----------
    loop : ``EventThread``
        The respective event loop.
    enter_event : `threading.Event`
        Threading event, which blocks the local thread, till the respective event loop pauses.
    exit_event : `threading.Event`
        Blocks the respective event loop, till the local thread gives the control back to it with exiting the `with`
        block.
    """
    __slots__ = ('loop', 'enter_event', 'exit_event')
    
    def __init__(self, loop):
        """
        Creates a new ``ThreadSuspenderContext`` bound to the given event loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to pause.
        """
        self.loop = loop
        self.enter_event = SyncEvent()
        self.exit_event = SyncEvent()

    def __enter__(self):
        """
        Blocks the local thread, till the respective ``EventThread`` pauses. If the ``EventThread`` is stopped already,
        does nothing.
        """
        loop = self.loop
        if loop.running:
            handle = Handle(self._give_control_cb, ())
            loop._ready.append(handle)
            loop.wake_up()
            self.enter_event.wait()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Un-pauses the respective ``EventThread``."""
        self.exit_event.set()
        return False
    
    def _give_control_cb(self):
        """
        Callback used to pause the respective ``EventThread`` and give control to the other one.
        """
        self.enter_event.set()
        self.exit_event.wait()
