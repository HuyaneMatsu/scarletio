__all__ = ()

from http.cookies import SimpleCookie
from warnings import warn

from ..core import LOOP_TIME
from ..utils import RichAttributeErrorBaseType

from .connection import Connection
from .protocol_basket import ProtocolBasket


class ConnectorBase(RichAttributeErrorBaseType):
    """
    Base connector class.
    
    Attributes
    ----------
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
    
    protocols_by_host : `dict<ConnectionKey, ConnectionBasket>`
        Protocols for each host.
    
    Notes
    -----
    Connectors support weakreferencing.
    """
    __slots__ = (
        '__weakref__', 'clean_up_handle', 'closed', 'cookies', 'force_close', 'loop', 'protocols_by_host'
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
        self.protocols_by_host = {}
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
        protocols_by_host = self.protocols_by_host
        if not protocols_by_host:
            return
        
        now = LOOP_TIME()
        to_remove_keys = None
        
        for protocol_basket in protocols_by_host.values():
            protocol_basket.clean_up_expired_protocols(now)
            if protocol_basket:
                continue
            
            if to_remove_keys is None:
                to_remove_keys = []
            
            to_remove_keys.append(protocol_basket.connection_key)
        
        if (to_remove_keys is not None):
            for key in to_remove_keys:
                del protocols_by_host[key]
        
        closest_expiration = self.get_closest_expiration()
        if closest_expiration != -1:
            self.clean_up_handle = self.loop.call_at_weak(closest_expiration, self._clean_up)
    
    
    def close(self):
        """
        Closes the connector and it's connections.
        """
        if self.closed:
            return
        
        self.closed = True
        
        protocols_by_host = self.protocols_by_host
        try:
            if not self.loop.running:
                return
            
            for protocol_basket in protocols_by_host.values():
                protocol_basket.close()
            
        finally:
            protocols_by_host.clear()
    
    
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
        
        protocol, performed_requests = self.pop_available_protocol(key)
        if protocol is None:
            protocol = await self.create_connection(request)
            if self.closed:
                protocol.close()
                raise ConnectionError('Connector is closed.')
        
        self.add_used_protocol(key, protocol)
        return Connection(self, key, protocol, performed_requests)
    
    
    def pop_available_protocol(self, key):
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
        
        performed_requests : `int`
            The amount of performed requests on the protocol.
        """
        protocols_by_host = self.protocols_by_host
        try:
            protocol_basket = protocols_by_host[key]
        except KeyError:
            return None, 0
        
        protocol_and_performed_requests = protocol_basket.pop_available_protocol(LOOP_TIME())
        if not protocol_basket:
            del protocols_by_host[key]
        
        return protocol_and_performed_requests
    
    
    def add_used_protocol(self, key, protocol):
        """
        Adds a protocol as used.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key that contains information about the host.
        
        protocol : ``AbstractProtocolBase``
            The protocol to add.
        """
        protocols_by_host = self.protocols_by_host
        try:
            protocol_basket = protocols_by_host[key]
        except KeyError:
            protocol_basket = ProtocolBasket(key)
            protocols_by_host[key] = protocol_basket
        
        protocol_basket.add_used_protocol(protocol)
    
    
    def add_available_protocol(self, key, protocol, keep_alive_timeout, performed_requests):
        """
        Adds a protocol as available.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key that contains information about the host.
        
        protocol : ``AbstractProtocolBase``
            The protocol to add.
        
        keep_alive_timeout : `float`
            How long the connection can be reused.
        
        performed_requests : `int`
            The amount of performed requests on the connection.
        """
        protocols_by_host = self.protocols_by_host
        try:
            protocol_basket = protocols_by_host[key]
        except KeyError:
            protocol_basket = ProtocolBasket(key)
            protocols_by_host[key] = protocol_basket
        
        protocol_basket.add_available_protocol(protocol, LOOP_TIME(), keep_alive_timeout, performed_requests)
    
    
    def release_used_protocol(self, key, protocol):
        """
        Removes the given used protocol from the connector.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.
        
        protocol : ``AbstractProtocolBase``
            The connected protocol to the respective host.
        """
        if self.closed:
            return
        
        protocols_by_host = self.protocols_by_host
        try:
            protocol_basket = protocols_by_host[key]
        except KeyError:
            return
        
        protocol_basket.remove_used_protocol(protocol)
        if not protocol_basket:
            del protocols_by_host[key]
    
    
    def release(self, key, protocol, should_close, keep_alive_timeout, performed_requests):
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
        
        keep_alive_timeout : `float`
            How long the connection can be reused.
        
        performed_requests : `int`
            The amount of performed requests on the connection.
        """
        if self.closed:
            return
        
        self.release_used_protocol(key, protocol)
        
        if should_close or self.force_close or protocol.should_close():
            transport = protocol.get_transport()
            protocol.close()
            if key.secure and (transport is not None):
                transport.abort()
            return
        
        self.add_available_protocol(key, protocol, keep_alive_timeout, performed_requests)
        
        if self.clean_up_handle is None:
            self.clean_up_handle = self.loop.call_after_weak(keep_alive_timeout, self._clean_up)
    
    
    def get_closest_expiration(self):
        """
        Returns the closest expiration time or `-1.0`.
        
        Returns
        -------
        closest_expiration : `float`
        """
        closest_expiration = -1.0
        
        for protocol_basket in self.protocols_by_host.values():
            expiration = protocol_basket.get_closest_expiration()
            if expiration == -1.0:
                continue
            
            if closest_expiration == -1.0:
                closest_expiration = expiration
                continue
            
            if expiration < closest_expiration:
                closest_expiration = expiration
                continue
        
        return closest_expiration
    
    
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
