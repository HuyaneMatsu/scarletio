__all__ = ()

from http.cookies import SimpleCookie
from warnings import warn

from ..core import LOOP_TIME
from ..utils import RichAttributeErrorBaseType

from .connection import Connection
from .constants import CONNECTION_KEEP_ALIVE_TIMEOUT


class ConnectorBase(RichAttributeErrorBaseType):
    """
    Base connector class.
    
    Attributes
    ----------
    acquired_protocols_per_host : `dict<ConnectionKey, set<AbstractProtocolBase>>`
        Acquired protocols for each host.
    
    alive_protocols_per_host : `dict<ConnectionKey, list<(AbstractProtocolBase, float)>`
        Alive, not used protocols for each host.
        Each element of the values stores when the connection was last used as well.
    
    clean_up_handle : `None | TimerWeakHandle`
        Weak handle, which cleans up the timed out connections of the connector.
    
    closed : `bool`
        Whether the connector is closed.
        
    cookies : `http.cookies.SimpleCookie`
        Cookies of the connection.
    
    force_close : `bool`
        Whether after each request (and between redirects) the connections should be closed.
    
    loop : ``EventThread``
        The event loop to what the connector is bound to.
    
    Notes
    -----
    Connectors support weakreferencing.
    """
    __slots__ = (
        '__weakref__', 'acquired_protocols_per_host', 'alive_protocols_per_host', 'clean_up_handle', 'closed',
        'cookies', 'force_close', 'loop'
    )
    
    def __new__(cls, loop, *deprecated, force_close = False):
        """
        Creates a new connector bound to the given loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the connector is bound to.
        
        force_close : `bool` = `False`, Optional (Keyword only)
            Whether after each request (and between redirects) the connections should be closed. Defaults to `False`.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `force_close` parameter in `{cls.__name__}.__new__` is moved ot be keyword only. '
                    f'Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            force_close = deprecated[0]
        
        self = object.__new__(cls)
        self.acquired_protocols_per_host = {}
        self.alive_protocols_per_host = {}
        self.clean_up_handle = None
        self.closed = False
        self.cookies = SimpleCookie()
        self.force_close = force_close
        self.loop = loop
        return self
    
    
    def __del__(self):
        """
        Closes the connector if not yet closed.
        """
        self.close()
    
    
    def _clean_up(self):
        """
        Cleans ups the expired connections of the connector.
        """
        handle = self.clean_up_handle
        if (handle is not None):
            self.clean_up_handle = None
            handle.cancel()
        
        # Clean up unused transports.
        alive_protocols_per_host = self.alive_protocols_per_host
        if not alive_protocols_per_host:
            return
        
        now = LOOP_TIME()
        to_remove_keys = []
        
        for key, alive_protocols_for_host in alive_protocols_per_host.items():
            for index in reversed(range(len(alive_protocols_for_host))):
                protocol, expiration = alive_protocols_for_host[index]
                if expiration > now:
                    continue
                
                del alive_protocols_for_host[index]
                
                transport = protocol.get_transport()
                if key.secure and (transport is not None):
                    transport.abort()
            
            if not alive_protocols_for_host:
                to_remove_keys.append(key)
        
        for key in to_remove_keys:
            del alive_protocols_per_host[key]
        
        if alive_protocols_per_host:
            self.clean_up_handle = self.loop.call_after_weak(CONNECTION_KEEP_ALIVE_TIMEOUT, self._clean_up)
    
    
    def close(self):
        """
        Closes the connector and it's connections.
        """
        if self.closed:
            return
        
        self.closed = True
        
        try:
            if not self.loop.running:
                return
            
            for alive_protocols_for_host in self.alive_protocols_per_host.values():
                for protocol, expiration in alive_protocols_for_host:
                    protocol.close()
            
            for protocols in self.acquired_protocols_per_host.values():
                for protocol in protocols:
                    protocol.close()
        
        finally:
            self.acquired_protocols_per_host.clear()
            self.alive_protocols_per_host.clear()
    
    
    async def connect(self, request):
        """
        Gets connection from connection pool or creates a new one.
        
        This method is a coroutine.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request, which requires a connection.
        
        Returns
        -------
        connection : ``Connection``
            The created connection.
        
        Raises
        ------
        ConnectionError
            Connector closed.
        """
        key = request.connection_key
        
        protocol = self.get_protocol(key)
        if protocol is None:
            protocol = await self.create_connection(request)
            if self.closed:
                protocol.close()
                raise ConnectionError('Connector is closed.')
        
        acquired_protocols_per_host = self.acquired_protocols_per_host
        try:
            acquired_protocols_for_host = acquired_protocols_per_host[key]
        except KeyError:
            acquired_protocols_for_host = acquired_protocols_per_host[key] = set()
        
        acquired_protocols_for_host.add(protocol)
        
        return Connection(self, key, protocol)
    
    
    def get_protocol(self, key):
        """
        Gets a protocol for the given connection key.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.

        Returns
        -------
        protocol : `None | AbstractProtocolBase`
            Protocol connected to the respective host. Defaults to `None` if there is not any.
        """
        try:
            alive_protocols_for_host = self.alive_protocols_per_host[key]
        except KeyError:
            return None
        
        now = LOOP_TIME()
        
        while alive_protocols_for_host:
            protocol, expiration = alive_protocols_for_host.pop()
            if (protocol.get_transport() is None):
                continue
            
            if now > expiration:
                transport = protocol.get_transport()
                protocol.close()
                if key.secure and (transport is not None):
                    transport.abort()
                continue
            
            if not alive_protocols_for_host:
                del self.alive_protocols_per_host[key]
            
            return protocol
        
        del self.alive_protocols_per_host[key]
        return None
    
    
    def release_acquired_protocol(self, key, protocol):
        """
        Removes the given acquired protocol from the connector.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.
        
        protocol : ``AbstractProtocolBase``
            The connected protocol to the respective host.
        """
        if self.closed:
            return
        
        acquired_protocols_per_host = self.acquired_protocols_per_host
        try:
            acquired_protocols_for_host = acquired_protocols_per_host[key]
        except KeyError:
            return
        
        try:
            acquired_protocols_for_host.remove(protocol)
        except KeyError:
            return
        
        if not acquired_protocols_for_host:
            del acquired_protocols_per_host[key]
    
    
    def release(self, key, protocol, should_close = False):
        """
        Releases the given protocol from the connector.
        If the connection should not be closed, not closes it, instead stores it for future reuse.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.
            
        protocol : ``AbstractProtocolBase``
            Protocol of the released connection.
        
        should_close : `bool`
            Whether the respective connection should be closed.
        """
        if self.closed:
            return
        
        self.release_acquired_protocol(key, protocol)
        
        if should_close or self.force_close or protocol.should_close():
            transport = protocol.get_transport()
            protocol.close()
            if key.secure and (transport is not None):
                transport.abort()
            return
        
        try:
            alive_protocols_for_host = self.alive_protocols_per_host[key]
        except KeyError:
            alive_protocols_for_host = self.alive_protocols_per_host[key] = []
        
        alive_protocols_for_host.append((protocol, LOOP_TIME() + CONNECTION_KEEP_ALIVE_TIMEOUT))
        
        if self.clean_up_handle is None:
            self.clean_up_handle = self.loop.call_after_weak(CONNECTION_KEEP_ALIVE_TIMEOUT, self._clean_up)
    
    
    async def create_connection(self, request):
        """
        Creates a new connection for the given request.
        
        This method is a coroutine.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Request to create connection for.
        
        Returns
        -------
        protocol : ``AbstractProtocolBase``
            The created protocol connected to the respective host.
        
        Raises
        ------
        NotImplementedError
            ``ConnectorBase`` do not implements ``.create_connection``. Subclasses should do it.
        """
        raise NotImplementedError
