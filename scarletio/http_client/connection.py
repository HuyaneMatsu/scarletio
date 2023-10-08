__all__ = ()

from ..core.top_level import write_exception_async


class Connection:
    """
    Reusable connection used by connectors to remember their details.
    
    Attributes
    ----------
    callbacks : `list` of `callable`
        Callable-s to run when the connection is ``.close``-d, ``.release``-d or ``.detach``-ed. They should accept no
        parameters.
    connector : ``ConnectorBase``
        The respective connector of the connection.
    key : ``ConnectionKey``
        A key which contains information about the host.
    protocol : `None`, ``HttpReadWriteProtocol``
        The connection's actual protocol. Set as `None` if the connection is ``.close``-d, ``.release``-d or
        ``.detach``-ed.
    """
    __slots__ = ('callbacks', 'connector', 'key', 'protocol',)
    
    def __init__(self, connector, key, protocol):
        """
        Creates a new ``Connection`` with the given parameters.
        
        connector : ``ConnectorBase``
            The respective connector of the connection.
        key : `tuple` (`str`, `int`)
            The host and the port to what the connection is connected too.
        protocol : ``HttpReadWriteProtocol``
            The connection's actual protocol.
        """
        self.connector = connector
        self.key = key
        self.protocol = protocol
        self.callbacks = []
    
    def __repr__(self):
        """Returns the representation of the connection."""
        repr_parts = [
            '<',
            self.__class__.__name__,
            ' to ',
            repr(self.key),
        ]
        
        if self.closed:
            repr_parts.append(' closed')
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __del__(self):
        """Releases the connector if not yet released."""
        connector = self.connector
        if connector.loop.running:
            protocol = self.protocol
            if (protocol is not None):
                connector.release(self.key, protocol, should_close = True)
    
    
    @property
    def transport(self):
        """
        Returns the connection's ``.protocol``'s transport if applicable.
        
        Returns
        -------
        transport : `object`
            Defaults to `None`.
        """
        protocol = self.protocol
        if protocol is None:
            return None
        
        return protocol.get_transport()
    
    @property
    def writer(self):
        """
        Returns the connection's ``.protocol``'s writer if applicable.
        
        Returns
        -------
        writer : `object`
            Defaults to `None`.
        """
        protocol = self.protocol
        if protocol is None:
            return None
        
        return protocol.writer
    
    
    def add_callback(self, callback):
        """
        Adds a callback to the connection. If the connection is already closed runs it instantly.
        
        Parameters
        ----------
        callback : `callable`
            Callable to run when the connection is ``.close``-d, ``.release``-d or ``.detach``-ed. Should accept no
            parameters.
        """
        if callback is None:
            return
        
        if not self.closed:
            self.callbacks.append(callback)
            return
        
        
        try:
            callback()
        except BaseException as err:
            write_exception_async(
                err,
                [
                    'Exception occurred at ',
                    repr(self),
                    '.add_callback\nAt running ',
                    repr(callback),
                    '\n',
                ],
                loop = self.connector.loop,
            )
    
    
    def _run_callbacks(self):
        """
        Runs the added callbacks of the connection.
        """
        callbacks = self.callbacks
        while callbacks:
            callback = callbacks.pop()
            
            try:
                callback()
            except BaseException as err:
                write_exception_async(
                    err,
                    [
                        'Exception occurred at ',
                        repr(self),
                        '._run_callbacks\nAt running ',
                        repr(callback),
                        '\n',
                    ],
                    loop = self.connector.loop,
                )
    
    
    def close(self):
        """
        Closes the connection by running it's callbacks and releasing with the intent of closing.
        """
        self._run_callbacks()
        
        protocol = self.protocol
        if (protocol is not None):
            self.protocol = None
            self.connector.release(self.key, protocol, should_close = True)
    
    
    def release(self):
        """
        Closes the connection by running it's callbacks and releasing it.
        """
        self._run_callbacks()
        
        protocol = self.protocol
        if (protocol is not None):
            self.protocol = None
            self.connector.release(self.key, protocol, should_close = protocol.should_close())
    
    
    def detach(self):
        """
        Detaches the connection from it ``.connector``.
        
        Note, that with detaching, the connection set it's ``.protocol`` as `None`, so you should save an instance of
        it down before.
        """
        self._run_callbacks()
        
        protocol = self.protocol
        if (protocol is not None):
            self.protocol = None
            self.connector.release_acquired_protocols(self.key, protocol)
   
   
    @property
    def closed(self):
        """
        Returns whether the connection is closed.
        
        Returns
        -------
        closed : `bool`
        """
        protocol = self.protocol
        if protocol is None:
            return True
        
        if protocol.get_transport() is None:
            return True
        
        return False
