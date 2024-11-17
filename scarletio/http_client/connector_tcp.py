__all__ = ('ConnectorTCP',)

from functools import partial as partial_func
from http import HTTPStatus
from socket import AddressFamily, SOCK_STREAM as SOCKET_TYPE_STREAM
from ssl import (
    CertificateError as SSLCertificateError, SSLContext, SSLError, create_default_context as create_default_ssl_context
)
from warnings import warn

from ..core import CancelledError, Future, SSLBidirectionalTransportLayer, Task
from ..utils import CauseGroup, IgnoreCaseMultiValueDictionary
from ..web_common.exceptions import ProxyError
from ..web_common.headers import METHOD_CONNECT
from ..web_common.helpers import is_ip_address, set_tcp_nodelay
from ..web_common.http_protocol import HttpReadWriteProtocol

from .client_request import ClientRequest
from .connection import Connection
from .connector_base import ConnectorBase
from .constants import SSL_CONTEXT_UNVERIFIED
from .host_info import HostInfo
from .host_info_basket import HostInfoBasket
from .ssl_fingerprint import SSLFingerprint


class ConnectorTCP(ConnectorBase):
    """
    Tcp connector.
    
    Attributes
    ----------
    cookies : `http.cookies.SimpleCookie`
        Cookies of the connection.
    
    clean_up_handle : `None | TimerWeakHandle`
        Weak handle, which cleans up the timed out connections of the connector.
    
    closed : `bool`
        Whether the connector is closed.
    
    family : `AddressFamily`
        Address family of the created socket if any.
    
    force_close : `bool`
        Whether after each request (and between redirects) the connections should be closed.
    
    host_info_basket_cache : `dict<(None | str, None | int), HostInfoBasket)`
        Cached resolved host information.
    
    local_address : `None | (None | str, None | int))`
        Can be given as a `tuple` (`local_host`, `local_port`) to bind created sockets locally.
    
    loop : ``EventThread``
        The event loop to what the connector is bound to.
    
    protocols_by_host : `dict<ConnectionKey, ConnectionBasket>`
        Protocols for each host.
    
    resolve_host_tasks_and_waiters : `dict<(None | str, None | int), \
            (Task<.resolve>, list<Future<(None | HostInfoBasket, None | BaseException)>>)>`
        Active host info resolving tasks and waiters.
    
    ssl_context : `None | SSLContext`
        The connection's ssl type.
    
    ssl_fingerprint : `None | SSLFingerprint`
        Alternative way to accept ssl or to block it depending whether the fingerprint is the same or changed.
    
    Notes
    -----
    Connectors support weakreferencing.
    """
    __slots__ = (
        'family', 'host_info_basket_cache', 'local_address', 'resolve_host_tasks_and_waiters', 'ssl_context',
        'ssl_fingerprint'
    )
    
    def __new__(
        cls,
        loop,
        *deprecated,
        family = AddressFamily.AF_UNSPEC,
        force_close = False,
        local_address = None,
        ssl = ...,
        ssl_context = None,
        ssl_fingerprint = None,
    ):
        """
        Creates a new tcp connector with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the connector is bound to.
        
        family : `AddressFamily` = `AddressFamily.AF_UNSPEC`, Optional (keyword only)
            Address family of the created socket if any
        
        force_close : `bool` = `False`, Optional (keyword only)
            Whether after each request (and between redirects) the connections should be closed.
        
        local_address : `None | (None | str, None | int)` = `None`, Optional (keyword only)
            Can be given as a `tuple` (`local_host`, `local_port`) to bind created sockets locally.
        
        ssl_context : `None | SSLContext`, Optional (Keyword only)
            SSL context to be used by the connector.
        
        ssl_fingerprint : `None | SSLFingerprint`, Optional (Keyword only)
            SSL finger print to use by the connector.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        """
        # deprecated
        deprecated_length = len(deprecated)
        if deprecated_length:
            warn(
                (
                    f'The `force_close`, `proxy_headers`, `local_address` and `ssl` parameters in '
                    f'`{cls.__name__}.__new__` are moved to be keyword only. '
                    f'Support for positional is deprecated and will be removed in 2025 August.'
                ),
                FutureWarning,
                stacklevel = 2,
            )
            
            family = deprecated[0]
            
            if deprecated_length > 1:
                ssl = deprecated[1]
            
            if deprecated_length > 2:
                local_address = deprecated[2]
            
            if deprecated_length > 3:
                force_close = deprecated[3]
        
        
        if (ssl is not ...):
            warn(
                (
                    f'`{cls.__name__}.__new__`\'s `ssl` parameter is deprecated '
                    f'and scheduled for removal in 2025 August. '
                    f'Please use either the `ssl_context` or the `ssl_fingerprint` parameters depending on your needs.'
                ),
                FutureWarning,
                stacklevel = 3,
            )
            
            if ssl is None:
                ssl_context = None
                ssl_fingerprint = None
            
            elif isinstance(ssl, SSLContext):
                ssl_context = ssl
                ssl_fingerprint = None
            
            elif isinstance(ssl, SSLFingerprint):
                ssl_context = None
                ssl_fingerprint = ssl
            
            elif isinstance(ssl, bool):
                ssl_context = create_default_ssl_context()
                ssl_fingerprint = None
                
            else:
                raise TypeError(
                    f'`ssl` can be `None`, `bool`, `{SSLContext.__name__}`, `{SSLFingerprint.__name__}`. '
                    f'Got {type(ssl).__name__}; {ssl!r}.'
                )
        
        
        self = ConnectorBase.__new__(cls, loop, force_close = force_close)
        
        self.family = family
        self.host_info_basket_cache = {}
        self.local_address = local_address
        self.resolve_host_tasks_and_waiters = {}
        self.ssl_context = ssl_context
        self.ssl_fingerprint = ssl_fingerprint
        
        return self
    
    
    def close(self):
        """
        Closes the connector, it's dns lookup events and it's connections.
        """
        for task, waiters in self.resolve_host_tasks_and_waiters.values():
            task.cancel()
        
        ConnectorBase.close(self)
    
    
    async def resolve_host(self, host, port, waiters):
        """
        Resolves a host and returns it's result.
        
        This method is a coroutine.
        
        Parameters
        ----------
        host : `None | str`
            To what network interfaces should the connection be bound.
        port : `None | int`
            The port of the `host`.
        
        Returns
        -------
        result : `(None | HostInfoBasket, None | BaseException)`
            A host info container containing the resolved addresses. And an occurred exception if any.
        """
        result = (None, None)
        
        try:
            try:
                infos = await self.loop.get_address_info(host, port, type = SOCKET_TYPE_STREAM, family = self.family)
            except GeneratorExit:
                raise
            
            except CancelledError:
                raise
            
            except BaseException as exception:
                result = (None, exception)
            
            else:
                result = (HostInfoBasket.from_address_infos(host, infos), None)
        
        finally:
            try:
                del self.resolve_host_tasks_and_waiters[host, port]
            except KeyError:
                pass
            
            for waiter in waiters:
                waiter.set_result_if_pending(result)
    
    
    def get_resolve_host_waiter(self, host, port):
        """
        Resolves addresses for the given `host` and `port`.
        Returns a future that can be awaited to retrieve the result.
        
        Parameters
        ----------
        host : `None | str`
            To what network interfaces should the connection be bound.
        port : `None | int`
            The port of the `host`.
        
        Returns
        -------
        waiter : `Future<(HostInfoBasket, BaseException)>`
            A waiter future that can be awaited to retrieve the resolve's result.
        """
        try:
            task, waiters = self.resolve_host_tasks_and_waiters[host, port]
        except KeyError:
            waiters = []
            task = Task(self.loop, self.resolve_host(host, port, waiters))
            self.resolve_host_tasks_and_waiters[host, port] = (task, waiters)
        
        waiter = Future(self.loop)
        waiters.append(waiter)
        
        return waiter
    
    
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
        
        # If host is an ip return
        if is_ip_address(host):
            yield HostInfo.from_ip(host, port, self.family)
            return
        
        # Strip extra dots from the end, keep one.
        # This is actually done now in url parsing because double dot is invalid.
        
        # Get old host info basket
        try:
            old_host_info_basket = self.host_info_basket_cache[host, port]
        except KeyError:
            old_host_info_basket = None
            expired = True
        else:
            expired = old_host_info_basket.is_expired()
        
        # if old host info basket expired create new resolve task.
        if expired:
            waiter = self.get_resolve_host_waiter(host, port)
        
        if (old_host_info_basket is not None):
            for host_info in old_host_info_basket.iter_next_rotation():
                yield host_info
        
        if not expired:
            return
        
        new_host_info_basket, exception = await waiter
        
        # Yield host infos that we did not yield before.
        if (new_host_info_basket is not None):
            for host_info in new_host_info_basket.iter_next_rotation():
                if (old_host_info_basket is None) or (host_info not in old_host_info_basket):
                    yield host_info
            
            return
        
        # Raise any occurred exception.
        if (exception is not None):
            if not isinstance(exception, OSError):
                raise exception
            
            raise ConnectionError(request.connection_key, 'Resolve task failed.') from exception
            
        # If neither host info basket & exception is returned then the resolve task was cancelled.
        raise ConnectionError(request.connection_key, 'Resolve task cancelled.')
    
    
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
        if request.proxy is None:
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
        ssl_context : `None | SSLContext`
            Returns `None` if the request is not `ssl`.
        """
        if not request.is_secure():
            return None
        
        ssl_context = request.ssl_context
        if (ssl_context is not None):
            return ssl_context
        
        ssl_context = self.ssl_context
        if (ssl_context is not None):
            return ssl_context
        
        return SSL_CONTEXT_UNVERIFIED
    
    
    def get_ssl_fingerprint(self, request):
        """
        Gets fingerprint for the respective request.
        
        Parameters
        ----------
        request : ``ClientRequest``
            Respective request.
        
        Returns
        -------
        fingerprint : `None | SSLFingerprint`
        """
        if not request.is_secure():
            return None
        
        ssl_fingerprint = request.ssl_fingerprint
        if (ssl_fingerprint is not None):
            return ssl_fingerprint
        
        ssl_fingerprint = self.ssl_fingerprint
        if (ssl_fingerprint is not None):
            return ssl_fingerprint
    
    
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
        ssl_fingerprint = self.get_ssl_fingerprint(request)
        
        causes = None
        
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
                    server_host_name = (None if (ssl_context is None) else host_info.host_name.rstrip('.')),
                )
            except (SSLCertificateError, SSLError) as err:
                err.key = request.connection_key
                raise
            
            except OSError as exception:
                if (causes is None):
                    causes = []
                
                causes.append(exception)    
                continue
            
            if (ssl_fingerprint is not None):
                try:
                    ssl_fingerprint.check(protocol)
                except ValueError as exception:
                    protocol.close_transport(force = True)
                    
                    if (causes is None):
                        causes = []
                    
                    causes.append(exception)    
                    continue
            
            return protocol
        
        raise OSError(request.connection_key) from (None if causes is None else CauseGroup(*causes))
    
    
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
        ProxyError
        RuntimeError
            If transport does not expose socket instance.
        """
        proxy = request.proxy
        
        proxy_request = ClientRequest(
            self.loop,
            METHOD_CONNECT,
            proxy.url,
            IgnoreCaseMultiValueDictionary(proxy.headers),
            None,
            None,
            None,
            proxy.authorization,
            request.url,
            None,
            proxy.ssl_context,
            proxy.ssl_fingerprint,
        )
        
        # create connection to proxy server
        protocol = await self.create_direct_connection(proxy_request)
        ssl_context = self.get_ssl_context(request)
        connection = Connection(self, request.connection_key.copy_proxyless(), protocol, 0)
        set_tcp_nodelay(connection.get_transport(), True)
        
        response = proxy_request.begin(connection)
        try:
            await response.start_processing()
        except:
            connection.close()
            raise
        
        try:
            connection.detach()
            response.close()
            
            try:
                status = response.status
                if status != 200:
                    reason = response.reason
                    if reason is None:
                        reason = HTTPStatus(status).phrase
                    
                    raise ProxyError(status, reason, response.headers)
            except:
                protocol.close()
                raise
            
            if not request.is_secure():
                return protocol
            
            underlying_transport = protocol._transport
            protocol = HttpReadWriteProtocol(self.loop)
            
            try:
                underlying_transport.pause_reading()
                waiter = Future(self.loop)
                ssl_protocol = SSLBidirectionalTransportLayer(
                    self.loop,
                    protocol,
                    ssl_context,
                    waiter,
                    False,
                    request.host,
                    False,
                )
                underlying_transport.set_protocol(ssl_protocol)
                ssl_protocol.connection_made(underlying_transport)
                underlying_transport.resume_reading()
                
                try:
                    await waiter
                except:
                    underlying_transport.close()
                    raise
            
            except (SSLCertificateError, SSLError) as exception:
                exception.key = request.connection_key
                raise
            
            except OSError as exception:
                raise OSError(request.connection_key, exception) from exception
            
            else:
                protocol.connection_made(ssl_protocol)
        
        except:
            response.close()
            raise
        
        return protocol
