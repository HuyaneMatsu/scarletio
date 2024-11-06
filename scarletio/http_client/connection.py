__all__ = ()

from warnings import warn

from ..core.top_level import write_exception_async
from ..utils import RichAttributeErrorBaseType
from ..web_common.constants import KEEP_ALIVE_MAX_REQUESTS_DEFAULT


class Connection(RichAttributeErrorBaseType):
    """
    Reusable connection used by connectors to remember their details.
    
    Attributes
    ----------
    callbacks : `list<callable>`
        Callable-s to run when the connection is ``.close``-d, ``.release``-d or ``.detach``-ed.
        They should accept no parameters.
    
    connector : ``ConnectorBase``
        The respective connector of the connection.
    
    key : ``ConnectionKey``
        A key which contains information about the host.
    
    performed_requests : `int`
        The amount of already performed requests.
    
    protocol : `None | HttpReadWriteProtocol`
        The connection's actual protocol.
        Set as `None` when the connection is ``.close``-d, ``.release``-d or ``.detach``-ed.
    """
    __slots__ = ('callbacks', 'connector', 'key', 'performed_requests', 'protocol',)
    
    def __new__(cls, connector, key, protocol, performed_requests):
        """
        Creates a new connection with the given parameters.
        
        Parameters
        ----------
        connector : ``ConnectorBase``
            The respective connector of the connection.
        
        key : ``ConnectionKey``
            A key to identify the connection.
        
        protocol : ``HttpReadWriteProtocol``
            The connection's actual protocol.
        
        performed_requests : `int`
            The amount of already performed requests.
        """
        self = object.__new__(cls)
        self.callbacks = []
        self.connector = connector
        self.key = key
        self.protocol = protocol
        self.performed_requests = performed_requests
        return self
    
    
    def __repr__(self):
        """Returns the representation of the connection."""
        repr_parts = ['<', type(self).__name__]
        
        # key
        repr_parts.append(' to ')
        repr_parts.append(repr(self.key))
        
        # closed
        if self.is_closed():
            repr_parts.append(' closed')
        
        # performed_requests
        performed_requests = self.performed_requests
        if performed_requests:
            repr_parts.append(', performed_requests = ')
            repr_parts.append(repr(performed_requests))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __del__(self):
        """Releases the connector if not yet released."""
        connector = self.connector
        if connector.loop.running:
            protocol = self.protocol
            if (protocol is not None):
                connector.release(self.key, protocol, True, -1.0, 0)
    
    
    def get_transport(self):
        """
        Returns the connection's ``.protocol``'s transport if applicable.
        
        Returns
        -------
        transport : `None | AbstractTransportLayerBase`
            Defaults to `None`.
        """
        protocol = self.protocol
        if (protocol is not None):    
            return protocol.get_transport()
    
    
    @property
    def transport(self):
        """
        Deprecated and will be removed in 2025 April. Please use ``.get_transport`` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.transport` is deprecated and will be removed in 2025 Apirl. '
                f'Please use `.get_transport()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return self.get_transport()
    
    
    def add_callback(self, callback):
        """
        Adds a callback to the connection. If the connection is already closed runs it instantly.
        
        Parameters
        ----------
        callback : `callable`
            Callable to run when the connection is ``.close``-d, ``.release``-d or ``.detach``-ed.
            Should accept no parameters.
        """
        if not self.is_closed():
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
            self.connector.release(self.key, protocol, True, -1.0, 0)
    
    
    def release(self, keep_alive_info):
        """
        Closes the connection by running it's callbacks and releasing it.
        """
        self._run_callbacks()
        
        protocol = self.protocol
        if (protocol is None):
            return
        
        self.protocol = None
        performed_requests = self.performed_requests + 1
        
        while True:
            should_close = protocol.should_close()
            if should_close:
                connection_keep_alive_timeout = -1.0
                break
            
            # no keep alive -> close
            if keep_alive_info is None:
                should_close = True
                connection_keep_alive_timeout = -1.0
                break
            
            # If we maxed our keep alive -> close
            max_requests = keep_alive_info.max_requests
            if (max_requests != KEEP_ALIVE_MAX_REQUESTS_DEFAULT) and (performed_requests >= max_requests):
                should_close = True
                connection_keep_alive_timeout = -1.0
                break
            
            should_close = False
            connection_keep_alive_timeout = keep_alive_info.connection_timeout
            break
        
        self.connector.release(self.key, protocol, should_close, connection_keep_alive_timeout, performed_requests)
    
    
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
            self.connector.release_used_protocol(self.key, protocol)
   
   
    def is_closed(self):
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
    
    
    @property
    def closed(self):
        """
        Deprecated and will be removed in 2025 April. Please use ``.is_closed`` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.closed` is deprecated and will be removed in 2025 Apirl. '
                f'Please use `.is_closed()` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return self.is_closed()
