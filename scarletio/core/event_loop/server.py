__all__ = ('Server', )

from ..traps import Future, skip_ready_cycle


class Server:
    """
    Server returned by ``EventThread.create_server``.
    
    Attributes
    ----------
    active_count : `int`
        The amount of active connections bound to the server.
    backlog : `int`
        The maximum number of queued connections passed to `listen()` (defaults to 100).
    close_waiters : `None`, `list` of ``Future``
        Futures, which are waiting for the server to close. If the server is already closed, set as `None`.
    loop : ``EventThread``
        The event loop to what the server is bound to.
    protocol_factory : `callable`
        Factory function for creating a protocols.
    serving : `bool`
        Whether the server is serving.
    sockets : `None`, `list` of `socket.socket`
        The sockets served by the server. If the server is closed, then i set as `None`.
    ssl_context : `None`, `ssl.SSLContext`
        If ssl is enabled for the connections, then set as `ssl.SSLContext`.
    """
    __slots__ = (
        'active_count', 'backlog', 'close_waiters', 'loop', 'protocol_factory', 'serving', 'sockets', 'ssl_context'
    )
    
    def __init__(self, loop, sockets, protocol_factory, ssl_context, backlog):
        """
        Creates a new server with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the server will be bound to.
        sockets : `list` of `socket.socket`
            The sockets to serve by the server.
        protocol_factory : `callable`
            Factory function for creating a protocols.
        ssl_context : `None`, `ssl.SSLContext`
            To enable ssl for the connections, give it as  `ssl.SSLContext`.
        backlog : `int`
            The maximum number of queued connections passed to `listen()` (defaults to 100).
        """
        self.loop = loop
        self.sockets = sockets
        self.active_count = 0
        self.close_waiters = []
        self.protocol_factory = protocol_factory
        self.backlog = backlog
        self.ssl_context = ssl_context
        self.serving = False
    
    
    def __repr__(self):
        """Returns the server's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        if self.serving:
            repr_parts.append(' serving')
            
        repr_parts.append(' sockets = ')
        repr_parts.append(repr(self.sockets))
        
        repr_parts.append(', protocol_factory = ')
        repr_parts.append(repr(self.protocol_factory))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def _attach(self):
        """
        Adds `1` to the server active counter.
        """
        self.active_count += 1
    
    
    def _detach(self):
        """
        Removes `1` from the server's active counter. If there no more active sockets of the server, then closes it.
        """
        active_count = self.active_count - 1
        self.active_count = active_count
        if active_count:
            return
        
        if (self.sockets is None):
            self._wake_up_close_waiters()


    def _wake_up_close_waiters(self):
        """
        Wakes up the server's close waiters.
        """
        close_waiters = self.close_waiters
        if close_waiters is None:
            return
        
        self.close_waiters = None
        for close_waiter in close_waiters:
            close_waiter.set_result(None)
    
    
    def close(self):
        """
        Closes the server by stopping serving it's sockets and waking up it's close waiters.
        """
        sockets = self.sockets
        if sockets is None:
            return
        
        self.sockets = None
        
        loop = self.loop
        for socket in sockets:
            loop._stop_serving(socket)
        
        self.serving = False
        
        if self.active_count == 0:
            self._wake_up_close_waiters()
    
    
    async def start(self):
        """
        Starts the server by starting serving it's sockets.
        
        This method is a coroutine.
        """
        if self.serving:
            return
        
        self.serving = True
        
        protocol_factory = self.protocol_factory
        ssl_context = self.ssl_context
        backlog = self.backlog
        loop = self.loop
        
        for socket in self.sockets:
            socket.listen(backlog)
            loop._start_serving(protocol_factory, socket, ssl_context, self, backlog)
        
        # Skip one event loop cycle, so all the callbacks added up ^ will run before returning.
        await skip_ready_cycle()
    

    async def wait_closed(self):
        """
        Blocks the task, till the sever is closes.
        
        This method is a coroutine.
        """
        if self.sockets is None:
            return
        
        close_waiters = self.close_waiters
        if close_waiters is None:
            return
        
        close_waiter = Future(self.loop)
        close_waiters.append(close_waiter)
        await close_waiter
