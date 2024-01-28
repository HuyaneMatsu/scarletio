__all__ = ('TCPConnector',)

import socket as module_socket
import ssl as module_ssl
from functools import partial as partial_func
from http.cookies import SimpleCookie

from ..core import LOOP_TIME, Task, shield
from ..utils import IgnoreCaseMultiValueDictionary
from ..web_common.exceptions import ProxyError
from ..web_common.headers import AUTHORIZATION, HOST, METHOD_CONNECT, METHOD_GET, PROXY_AUTHORIZATION
from ..web_common.helpers import is_ip_address
from ..web_common.http_protocol import HttpReadWriteProtocol

from .client_request import ClientRequest
from .connection import Connection
from .fingerprint import Fingerprint


KEEP_ALIVE_TIMEOUT = 15.0
DNS_CACHE_TIMEOUT = 10.0

SSL_ALLOWED_TYPES = (module_ssl.SSLContext, bool, Fingerprint, type(None))

SSL_EXCEPTION_TYPES = (module_ssl.SSLError, module_ssl.CertificateError)

SSL_CONTEXT_VERIFIED = module_ssl.create_default_context()

SSL_CONTEXT_UNVERIFIED = module_ssl.SSLContext(module_ssl.PROTOCOL_SSLv23)
SSL_CONTEXT_UNVERIFIED.options |= module_ssl.OP_NO_SSLv2 | module_ssl.OP_NO_SSLv3 | module_ssl.OP_NO_COMPRESSION
SSL_CONTEXT_UNVERIFIED.set_default_verify_paths()


class ConnectorBase:
    """
    Base connector class.
    
    Attributes
    ----------
    acquired_protocols : `set` of ``HttpReadWriteProtocol``
        Acquired protocols of the connector.
    acquired_protocols_per_host : `dict` of (``ConnectionKey``, `set` of ``HttpReadWriteProtocol``) items
        Acquired protocols for each host.
    alive_protocols_per_host : `dict` of (``ConnectionKey``, `list` of `tuple` (``HttpReadWriteProtocol``, `float`)) items
        Alive, not used protocols for each host. Each element of the values stores when the connection was last used
        as well.
    cleanup_handle : `None`, ``TimerWeakHandle``
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
        '__weakref__', 'acquired_protocols', 'acquired_protocols_per_host', 'alive_protocols_per_host',
        'cleanup_handle', 'closed',  'cookies', 'force_close', 'loop'
    )
    
    def __new__(cls, loop, force_close = False):
        """
        Creates a new connector bound to the given loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the connector is bound to.
        force_close : `bool` = `False`, Optional
            Whether after each request (and between redirects) the connections should be closed. Defaults to `False`.
        """
        self = object.__new__(cls)
        self.loop = loop
        self.closed = False
        self.alive_protocols_per_host = {}
        self.acquired_protocols = set()
        self.acquired_protocols_per_host = {}
        self.force_close = force_close
        self.cookies = SimpleCookie()
        self.cleanup_handle = None
        return self
    
    
    def __del__(self):
        """
        Closes the connector if not yet closed.
        """
        if (not self.closed) and self.alive_protocols_per_host:
            self.close()
    
    
    def _cleanup(self):
        """
        Cleans ups the expired connections of the connector.
        """
        handle = self.cleanup_handle
        if (handle is not None):
            # Cancelling the currently running handle does nothing.
            handle.cancel()
            self.cleanup_handle = None
        
        # Cleanup unused transports.
        alive_protocols_per_host = self.alive_protocols_per_host
        if not alive_protocols_per_host:
            return
        
        now = LOOP_TIME()
        to_remove_keys = []
        
        for key, alive_protocols_for_host in alive_protocols_per_host.items():
            for index in reversed(range(len(alive_protocols_for_host))):
                protocol, time = alive_protocols_for_host[index]
                
                if time + KEEP_ALIVE_TIMEOUT < now:
                    continue
                
                del alive_protocols_for_host[index]
                transport = protocol.get_transport()
                if key.is_ssl and (transport is not None):
                    transport.abort()
            
            if not alive_protocols_for_host:
                to_remove_keys.append(key)
        
        for key in to_remove_keys:
            del alive_protocols_per_host[key]
        
        if alive_protocols_per_host:
            self.cleanup_handle = self.loop.call_after_weak(KEEP_ALIVE_TIMEOUT, self._cleanup,)
    
    
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
                for protocol, time in alive_protocols_for_host:
                    protocol.close()
            
            for protocol in self.acquired_protocols:
                protocol.close()
        
        finally:
            self.alive_protocols_per_host.clear()
            self.acquired_protocols.clear()
    
    
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
        
        self.acquired_protocols.add(protocol)
        
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
        protocol : `None`, ``HttpReadWriteProtocol``
            Protocol connected to the respective host. Defaults to `None` if there is not any.
        """
        try:
            alive_protocols_for_host = self.alive_protocols_per_host[key]
        except KeyError:
            return None
        
        now = LOOP_TIME()
        while alive_protocols_for_host:
            protocol, time = alive_protocols_for_host.pop()
            if (protocol.get_transport() is None):
                continue
            
            if (now - time) > KEEP_ALIVE_TIMEOUT:
                transport = protocol.get_transport()
                protocol.close()
                if key.is_ssl and (transport is not None):
                    transport.abort()
            else:
                if not alive_protocols_for_host:
                    del self.alive_protocols_per_host[key]
                
                return protocol
        
        del self.alive_protocols_per_host[key]
    
    
    def release_acquired_protocols(self, key, protocol):
        """
        Removes the given acquired protocol from the connector.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.
        protocol : ``HttpReadWriteProtocol``
            The connected protocol to the respective host.
        """
        if self.closed:
            return
        
        self.acquired_protocols.discard(protocol)
        
        acquired_protocols_per_host = self.acquired_protocols_per_host
        try:
            acquired_protocols_for_host = acquired_protocols_per_host[key]
        except KeyError:
            pass
        else:
            try:
                acquired_protocols_for_host.remove(protocol)
            except KeyError:
                pass
            else:
                if not acquired_protocols_for_host:
                    del acquired_protocols_per_host[key]
    
    
    def release(self, key, protocol, should_close = False):
        """
        Releases the given protocol from the connector. If the connection should not be closed, not closes it, instead
        stores it for future reuse.
        
        Parameters
        ----------
        key : ``ConnectionKey``
            A key which contains information about the host.
        protocol : ``HttpReadWriteProtocol``
            Protocol of the released connection.
        should_close : `bool`
            Whether the respective connection should be closed.
        """
        if self.closed:
            return
        
        self.release_acquired_protocols(key, protocol)
        
        if should_close or self.force_close or protocol.should_close():
            transport = protocol.get_transport()
            protocol.close()
            if key.is_ssl and (transport is not None):
                transport.abort()
        else:
            try:
                alive_protocols_for_host = self.alive_protocols_per_host[key]
            except KeyError:
                alive_protocols_for_host = self.alive_protocols_per_host[key] = []
            
            alive_protocols_for_host.append((protocol, LOOP_TIME()))
            
            if self.cleanup_handle is None:
                self.cleanup_handle = self.loop.call_after_weak(KEEP_ALIVE_TIMEOUT, self._cleanup,)
    
    
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
        protocol : ``HttpReadWriteProtocol``
            The created protocol connected to the respective host.
        
        Raises
        ------
        NotImplementedError
            ``ConnectorBase`` do not implements ``.create_connection``. Subclasses should do it.
        """
        raise NotImplementedError


class HostInfo:
    """
    Resolved information about a host.
    
    Attributes
    ----------
    hostname : `str`
        The hosts' name.
    host : `str`
        The host's ip address.
    port : `int`
        Port to connect to the host.
    family : `AddressFamily`, `int`
        Address family.
    protocol : `int`
        Protocol type.
    flags : `int`
        Bit-mask for `get_address_info`.
    """
    __slots__ = ('hostname', 'host', 'port', 'family', 'protocol', 'flags', )
    
    def __repr__(self):
        """Returns the host info's representation."""
        return (
            f'<{self.__class__.__name__}, hostname = {self.hostname!r}, host = {self.host!r}, port = {self.port!r}, '
            f'family = {self.family!r}, protocol = {self.protocol!r}, flags = {self.flags!r}>'
        )
    
    @classmethod
    def from_ip(cls, host, port, family):
        """
        Creates a host info instance from the given parameters.
        
        Parameters
        ----------
        host : `str`
            The host's ip address.
        port : `int`
            Port to connect to the host.
        family : `AddressFamily`, `int`
            Address family.
        """
        self = object.__new__(cls)
        self.hostname = host
        self.host = host
        self.port = port
        self.family = family
        self.protocol = 0
        self.flags = 0
        return self
    
    
    @classmethod
    def from_address_info(cls, host, address_info):
        """
        Creates a host info instance from the given parameters.
        
        Parameters
        ----------
        host : `str`
            The host's ip address.
        address_info : `tuple` (`AddressFamily`, `int`, `SocketKind`, `int`, `int`, `str`, `tuple` (`str, `int`))
            An address info returned by `get_address_info`.
        """
        self = object.__new__(cls)
        self.hostname = host
        address = address_info[4]
        self.host = address[0]
        self.port = address[1]
        self.family = address_info[0]
        self.protocol = address_info[2]
        self.flags = module_socket.AI_NUMERICHOST
        
        return self
    
    def __eq__(self, other):
        """Returns whether the two host info's are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.hostname != other.hostname:
            return False
        
        if self.host != other.host:
            return False
        
        if self.port != other.port:
            return False
        
        if self.family != other.family:
            return False
        
        if self.protocol != other.protocol:
            return False
        
        if self.flags != other.flags:
            return False
        
        return True
    
    def __hash__(self):
        """Returns the host info's hash value."""
        return hash(self.hostname) ^ hash(self.host) ^ (self.port << 17 ) ^ hash(self.family) ^ hash(self.protocol) ^ \
               hash(self.flags)


class HostInfoCont:
    """
    ``HostInfo`` container, which rotates it's hosts.
    
    Attributes
    ----------
    index : `int`
        Index to determine since the next yielded addresses will start. Used for cycle host infos.
    timestamp : `int`
        Monotonic time determining when the container was created.
    host_infos : `list` of ``HostInfo``
        A list of the contained host information.
    """
    __slots__ = ('host_infos', 'index', 'timestamp')
    
    def __new__(cls, host, address_infos):
        """
        Creates a new host container from the given parameters.
        
        Parameters
        ----------
        host : `str`
            The host's name.
        address_infos : `list` of tuple` \
                (`AddressFamily`, `int`, `SocketKind`, `int`, `int`, `str`, `tuple` (`str, `int`))
            Address infos returned by `get_address_info`.
        """
        self = object.__new__(cls)
        self.index = 0
        self.timestamp = LOOP_TIME()
        self.host_infos = [HostInfo.from_address_info(host, address_info) for address_info in address_infos]
        
        return self
    
    @property
    def expired(self):
        """
        Returns whether the host info container expired.
        
        Returns
        -------
        expired : `bool`
        """
        if (self.timestamp + DNS_CACHE_TIMEOUT) < LOOP_TIME():
            return True
        
        return False
    
    def next_addresses(self):
        """
        Gets the next cycled addresses from the container.
        
        Returns
        -------
        result : `list` of ``HostInfo``
        """
        result = []
        
        host_infos = self.host_infos
        index = self.index
        limit = len(host_infos)
        left = limit
        
        while True:
            host_info = host_infos[index]
            result.append(host_info)
            index += 1
            if index == limit:
                index = 0
            
            left -= 1
            if left:
                continue
            
            break
        
        self.index = index
        return result

    def __repr__(self):
        """Returns the host info container's representation."""
        return f'<{self.__class__.__name__} host_infos={self.host_infos!r}, index={self.index!r}, ' \
            f'timestamp={self.timestamp!r}>'
    
    
class TCPConnector(ConnectorBase):
    """
    Base connector class.
    
    Attributes
    ----------
    acquired_protocols : `set` of ``HttpReadWriteProtocol``
        Acquired protocols of the connector.
    acquired_protocols_per_host : `dict` of (``ConnectionKey``, `set` of ``HttpReadWriteProtocol``) items
        Acquired protocols for each host.
    alive_protocols_per_host : `dict` of (``ConnectionKey``, `list` of `tuple` (``HttpReadWriteProtocol``, `float`)) items
        Alive, not used protocols for each host. Each element of the values stores when the connection was last used
        as well.
    cleanup_handle : `None`, ``TimerWeakHandle``
        Weak handle, which cleans up the timed out connections of the connector.
    closed : `bool`
        Whether the connector is closed.
    cookies : `http.cookies.SimpleCookie`
        Cookies of the connection.
    force_close : `bool`
        Whether after each request (and between redirects) the connections should be closed.
    loop : ``EventThread``
        The event loop to what the connector is bound to.
    cached_hosts : `dict` of (`tuple` (`str`, `int`), ``HostInfoCont``) items
        Cached resolved host information.
    dns_events : `dict` of (`tuple` (`str`, `int`), ``Task`` of ``.resolve``) items
        Active host info resolving events of the connector.
    family : `AddressFamily`, `int`
        Address family of the created socket if any.
    local_address : `None`, `tuple` ((`None`, `str`), (`None`, `int`))
        Can be given as a `tuple` (`local_host`, `local_port`) to bind created sockets locally.
    ssl : `ssl.SSLContext`, `bool`, ``Fingerprint``, `NoneType`
        Whether and what type of ssl should the connector use.
    
    Notes
    -----
    Connectors support weakreferencing.
    """
    __slots__ = ('cached_hosts', 'dns_events', 'family', 'local_address',  'ssl', )

    def __new__(cls, loop, family = 0, ssl = None, local_address = None, force_close = False):
        """
        Creates a new ``TCPConnector`` with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the connector is bound to.
        family : `AddressFamily`, `int` = `0`, Optional
            Address family of the created socket if any
        ssl : `ssl.SSLContext`, `bool`, ``Fingerprint``, `NoneType` = `None`, Optional
            Whether and what type of ssl should the connector use.
        local_address : `None`, `tuple` of ((`None`, `str`), (`None`, `int`)) = `None`, Optional
            Can be given as a `tuple` (`local_host`, `local_port`) to bind created sockets locally.
        force_close : `bool` = `False`, Optional
            Whether after each request (and between redirects) the connections should be closed.
        """
        if not isinstance(ssl, SSL_ALLOWED_TYPES):
            raise TypeError(
                f'`ssl` can be any of {SSL_ALLOWED_TYPES!r}, got {ssl.__class__.__name__}; {ssl!r}.'
            )
        
        self = ConnectorBase.__new__(cls, loop, force_close,)
        
        self.ssl = ssl
        self.cached_hosts = {}
        self.dns_events = {}
        self.family = family
        self.local_address = local_address
        
        return self
    
    
    def close(self):
        """
        Closes the connector, it's dns lookup events and it's connections.
        """
        for event in self.dns_events.values():
            event.cancel()
        
        ConnectorBase.close(self)
    
    
    async def resolve(self, host, port):
        """
        Resolves a host and returns it's result.
        
        This method is a coroutine.
        
        Parameters
        ----------
        host : `None`, `str`
            To what network interfaces should the connection be bound.
        port : `None`, `int`
            The port of the `host`.
        
        Returns
        -------
        result : ``HostInfoCont``, ``BaseException``
            A host info container containing the resolved addresses or the cached exception.
        """
        try:
            infos = await self.loop.get_address_info(host, port, type = module_socket.SOCK_STREAM, family = self.family)
        except BaseException as err:
            return err
        
        return HostInfoCont(host, infos,)
    
    
    async def resolver_task(self, key):
        """
        Resolves addresses for the given `host` - `port` key.
        
        If there is a ``.resolve`` task for the given `key`, then awaits on that's result instead.
        
        This method is a coroutine.
        
        Parameters
        ----------
        key : `tuple`, ((`None`, `str`), (`None`, `int`))
            A tuple containing a `host`, `port` par to resolve.
        
        Returns
        -------
        result : ``HostInfoCont``, ``BaseException``
            A host info container containing the resolved addresses or the cached exception.
        """
        try:
            event = self.dns_events[key]
        except KeyError:
            event = Task(self.loop, self.resolve(*key))
            self.dns_events[key] = event
            host_info = await event
            if type(host_info) is HostInfoCont:
                self.cached_hosts[key] = host_info
            del self.dns_events[key]
        else:
            host_info = await event
        
        return host_info
    
    
    async def resolve_host_iterator(self, request):
        """
        Yields host infos to which the request can connect to.
        
        This method is a coroutine generator.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request, which requires a connection.
        
        Yields
        ------
        host_info : ``HostInfo``
            Resolved host information.
        
        Raises
        ------
        ConnectionError
            No hosts were resolved.
        BaseException
            Any other cached exception.
        """
        host = request.url.raw_host
        port = request.port
        
        if is_ip_address(host):
            yield HostInfo.from_ip(host, port, self.family)
            return
        
        key = (host, port)
        try:
            host_infos = self.cached_hosts[key]
        except KeyError:
            pass
        else:
            expired = host_infos.expired
            if expired:
                task = shield(self.resolver_task(key), self.loop)
            
            address = host_infos.next_addresses()
            for host_info in address:
                yield host_info
            
            if expired:
                host_infos = await task
                if (type(host_infos) is not HostInfoCont):
                    if isinstance(host_infos, OSError):
                        raise ConnectionError(request.connection_key, host_infos) from host_infos
                    else:
                        raise host_infos
                
                for host_info in host_infos.next_addresses():
                    if host_info in address:
                        continue
                    
                    yield host_info
            
            return
        
        task = shield(self.resolver_task(key), self.loop)
        
        host_infos = await task
        if (type(host_infos) is not HostInfoCont):
            if isinstance(host_infos, OSError):
                raise ConnectionError(request.connection_key, host_infos) from host_infos
            else:
                raise host_infos
        
        for host_info in host_infos.next_addresses():
            yield host_info
    
    
    async def create_connection(self, request):
        """
        Creates connection for the request and returns the created protocol.
        
        This method is a coroutine.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        protocol : ``HttpReadWriteProtocol``
        
        Raises
        ------
        ssl.SSLError
        ssl.CertificateError
        OSError
        RuntimeError
            If transport does not expose socket instance.
        """
        if request.proxy_url is None:
            coroutine = self.create_direct_connection(request)
        else:
            coroutine = self.create_proxy_connection(request)
        
        return await coroutine
    
    def get_ssl_context(self, request):
        """
        Gets ssl context for the respective request.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        ssl_context : `None`, `ssl.SSLContext`
            Returns `None` if the request is not `ssl`.
        """
        if not request.is_ssl():
            return None
        
        if module_ssl is None:
            raise RuntimeError('SSL is not supported.')
        
        ssl_context = request.ssl
        if (ssl_context is not None):
            if isinstance(ssl_context, module_ssl.SSLContext):
                return ssl_context
            
            return SSL_CONTEXT_UNVERIFIED # not verified or fingerprinted
        
        ssl_context = self.ssl
        if ssl_context is None:
            return SSL_CONTEXT_VERIFIED
        
        if isinstance(ssl_context, module_ssl.SSLContext):
            return ssl_context
        
        return SSL_CONTEXT_UNVERIFIED
    
    
    def get_fingerprint(self, request):
        """
        Gets fingerprint for the respective request.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        fingerprint : `None`, ``Fingerprint``
        """
        maybe_fingerprint = request.ssl
        if isinstance(maybe_fingerprint, Fingerprint):
            return maybe_fingerprint
        
        maybe_fingerprint = self.ssl
        if isinstance(maybe_fingerprint, Fingerprint):
            return maybe_fingerprint
    
    
    async def create_direct_connection(self, request):
        """
        Creates a direct connection for the given request and returns the created protocol.
        
        This method is a coroutine.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        protocol : ``HttpReadWriteProtocol``
        
        Raises
        ------
        ssl.SSLError
        ssl.CertificateError
        OSError
        """
        ssl_context = self.get_ssl_context(request)
        fingerprint = self.get_fingerprint(request)
        
        last_error = None
        
        async for host_info in self.resolve_host_iterator(request):
            try:
                protocol = await self.loop.create_connection_to(
                    partial_func(HttpReadWriteProtocol, self.loop),
                    host_info.host,
                    host_info.port,
                    ssl = ssl_context,
                    socket_family = host_info.family,
                    socket_protocol = host_info.protocol,
                    socket_flags = host_info.flags,
                    local_address = self.local_address,
                    server_host_name = (host_info.hostname if ssl_context else None),
                )
            except SSL_EXCEPTION_TYPES as err:
                err.key = request.connection_key
                raise
            
            except OSError as err:
                last_error = OSError(request.connection_key, err)
                last_error.__cause__ = err
                continue
            
            if request.is_ssl() and fingerprint:
                try:
                    fingerprint.check(protocol)
                except ValueError as err:
                    protocol.close_transport(force = True)
                    last_error = err
                    continue
            
            return protocol
        
        raise last_error
    
    
    async def create_proxy_connection(self, request):
        """
        Creates a proxy connection for the given request and returns the created protocol.
        
        This method is a coroutine.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        protocol : ``HttpReadWriteProtocol``
        
        Raises
        ------
        ssl.SSLError
        ssl.CertificateError
        OSError
        RuntimeError
            If transport does not expose socket instance.
        """
        headers = IgnoreCaseMultiValueDictionary()
        
        headers[HOST] = request.headers[HOST]
        
        proxy_request = ClientRequest(self.loop, METHOD_GET, request.proxy_url, headers, None, None, None,
            request.proxy_auth, None, None, request.ssl)
        
        # create connection to proxy server
        protocol = await self.create_direct_connection(proxy_request)
        
        # Many HTTP proxies has buggy keep-alive support. Let's not reuse connection but close it after processing
        # every response.
        protocol.close()
        
        auth = proxy_request.headers.pop(AUTHORIZATION, None)
        if auth is not None:
            if not request.is_ssl():
                request.headers[PROXY_AUTHORIZATION] = auth
            else:
                proxy_request.headers[PROXY_AUTHORIZATION] = auth
        
        if request.is_ssl():
            ssl_context = self.get_ssl_context(request)
            proxy_request.method = METHOD_CONNECT
            proxy_request.url = request.url
            connection = Connection(self, request.connection_key, protocol)
            
            response = await proxy_request.send(connection)
            try:
                connection.protocol = None
                try:
                    if response.status != 200:
                        raise ProxyError(response.status, response.reason, response.headers)
                    
                    raw_socket = protocol.get_extra_info('socket', None)
                    if raw_socket is None:
                        raise RuntimeError('Transport does not expose socket instance.')
                    
                    # Duplicate the socket, so now we can close proxy transport
                    raw_socket = raw_socket.dup()
                finally:
                    protocol.close_transport()
                
                try:
                    protocol = await self.loop.create_connection_with(
                        partial_func(HttpReadWriteProtocol, self.loop),
                        ssl = ssl_context,
                        socket = raw_socket,
                        server_host_name = request.host,
                    )
                except SSL_EXCEPTION_TYPES as err:
                    err.key = request.connection_key
                    raise
                
                except OSError as err:
                    raise OSError(request.connection_key, err) from err
            
            finally:
                response.close()
        
        return protocol
