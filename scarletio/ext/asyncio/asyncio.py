__all__ = (
    'ALL_COMPLETED', 'AbstractChildWatcher', 'AbstractEventLoop', 'AbstractEventLoopPolicy', 'AbstractServer',
    'Barrier', 'BrokenBarrierError', 'BaseEventLoop', 'BaseProactorEventLoop', 'BaseProtocol', 'BaseSelectorEventLoop',
    'BaseTransport', 'BoundedSemaphore', 'BufferedProtocol', 'CancelledError', 'Condition', 'DatagramProtocol',
    'DatagramTransport', 'DefaultEventLoopPolicy', 'Event', 'FIRST_COMPLETED', 'FIRST_EXCEPTION', 'FastChildWatcher',
    'Future', 'Handle', 'IncompleteReadError', 'InvalidStateError', 'IocpProactor', 'LifoQueue', 'LimitOverrunError',
    'Lock', 'MultiLoopChildWatcher', 'PIPE', 'PidfdChildWatcher', 'PipeHandle', 'Popen', 'PriorityQueue',
    'ProactorEventLoop', 'Protocol', 'Queue', 'QueueEmpty', 'QueueFull', 'ReadTransport', 'Runner', 'SafeChildWatcher',
    'SelectorEventLoop', 'Semaphore', 'SendfileNotAvailableError', 'StreamReader', 'StreamReaderProtocol',
    'StreamWriter', 'SubprocessProtocol', 'SubprocessTransport', 'Task', 'ThreadedChildWatcher', 'Timeout',
    'TimeoutError', 'TimerHandle', 'Transport', 'WindowsProactorEventLoopPolicy', 'WindowsSelectorEventLoopPolicy',
    'WriteTransport', '_enter_task', '_get_running_loop', '_leave_task', '_register_task', '_set_running_loop',
    '_unregister_task', 'all_tasks', 'as_completed', 'coroutine', 'create_subprocess_exec', 'create_subprocess_shell',
    'create_eager_task_factory', 'create_task', 'current_task', 'create_eager_task_factory', 'ensure_future', 'gather',
    'get_child_watcher', 'get_event_loop', 'get_event_loop_policy', 'get_running_loop', 'iscoroutine',
    'iscoroutinefunction', 'isfuture', 'new_event_loop', 'open_connection', 'pipe', 'run', 'run_coroutine_threadsafe',
    'set_child_watcher', 'set_event_loop', 'set_event_loop_policy', 'shield', 'sleep', 'staggered_race',
    'start_server', 'start_unix_server', 'timeout', 'timeout_at', 'to_thread', 'wait', 'wait_for', 'wrap_future'
)

import os, signal, sys
import socket as module_socket
from collections import deque
from functools import partial, partial as partial_func
from enum import Enum
from stat import S_ISSOCK
from subprocess import DEVNULL, PIPE, STDOUT
from threading import current_thread, main_thread
from types import GeneratorType
from warnings import warn

try:
    import ssl
except ImportError:
    ssl = None

from ...core import (
    AbstractProtocolBase, AsyncLifoQueue, AsyncProcess, AsyncQueue, CancelledError, DatagramSocketTransportLayer,
    Event as HataEvent, EventThread, Executor, Future as HataFuture, Handle, InvalidStateError, Lock as HataLock,
    LOOP_TIME, ReadProtocolBase, Server, SSLBidirectionalTransportLayer, Task as HataTask, TaskGroup, TimerHandle,
    shield as scarletio_shield, skip_ready_cycle, sleep as scarletio_sleep
)
from ...core.event_loop.event_loop_functionality_helpers import _is_stream_socket, _set_reuse_port
from ...core.top_level import get_event_loop as scarletio_get_event_loop, write_exception_async
from ...utils import (
    IS_UNIX, KeepType, WeakReferer, WeakValueDictionary, alchemy_incendiary, is_coroutine, is_coroutine_function
)


__path__ = os.path.dirname(__file__)


# Additions to EventThread
@KeepType(EventThread)
class EventThread:
    
    call_soon_threadsafe = EventThread.call_soon_thread_safe
    
    
    def getaddrinfo(self, host, port, *, family = 0, type = 0, proto = 0, flags = 0):
        return self.get_address_info(host, port, family = family, type = type, protocol = proto, flags = flags)
    
    
    getnameinfo = EventThread.get_name_info
    sock_recv = EventThread.socket_receive
    sock_sendall = EventThread.socket_send_all
    sock_connect = EventThread.socket_connect
    sock_accept = EventThread.socket_accept
    
    
    # Required by aio-http 3.6
    def is_running(self):
        return self.running
    
    
    # Required by aio-http 3.6
    def get_debug(self):
        return False
    
    
    EventThread.get_debug = get_debug
    del get_debug
    
    
    # Required by aio-http 3.6
    def is_closed(self):
        return (not self.running)
    
    
    # Required by dead.py 3.8
    def add_signal_handler(self, sig, callback, *args):
        pass
    
    
    # Required by aio-http 3.8
    def remove_signal_handler(self, sig):
        pass
    
    
    # Required by aio-http 3.8
    async def shutdown_asyncgens(self):
        pass
    
    
    # Required by dead.py 3.8
    def run_forever(self):
        local_thread = current_thread()
        if isinstance(local_thread, EventThread):
            raise RuntimeError('Cannot call `loop.run_until_complete` inside of a loop')
        
        self.wake_up()
        self.join()
    
    
    # Required by dead.py 3.8
    def run_until_complete(self, future):
        local_thread = current_thread()
        if isinstance(local_thread, EventThread):
            raise RuntimeError('Cannot call `loop.run_until_complete` inside of a loop')
        
        self.run(future)
    
    
    # Required by dead.py 3.8
    def close(self):
        self.stop()
    
    
    def call_exception_handler(self, context):
        message = context.pop('message')
        exception = context.pop('exception', None)
        in_ = []
        for key, value in context.items():
            in_.append(key)
            in_.append(': ')
            in_.append(repr(value))
            in_.append(', ')
        
        if in_:
            del in_[-1]
            in_ = ''.join(in_)
        else:
            in_ = None
        
        extracted = [
            'Unexpected exception occurred',
        ]
        
        if (in_ is not None):
            extracted.append('at ')
            extracted.append(in_)
        
        extracted.append(': ')
        extracted.append(message)
        extracted.append('\n')
        
        if exception is None:
            extracted.append('*no exception provided*\n')
            sys.stderr.write(''.join(extracted))
        else:
            write_exception_async(exception, extracted, loop = self)
    
    
    async def create_connection(
        self,
        protocol_factory,
        host = None,
        port = None,
        *,
        ssl = None,
        family = 0,
        proto = 0,
        flags = 0,
        sock = None,
        local_addr = None, server_hostname = None,
        ssl_handshake_timeout = None,
        happy_eyeballs_delay = None,
        interleave = None,
        all_errors = False,
    ):
        if sock is None:
            return await self._asyncio_create_connection_to(
                protocol_factory,
                host,
                port,
                ssl = ssl,
                socket_family = family,
                socket_protocol = proto,
                socket_flags = flags,
                local_address = local_addr,
                server_host_name = server_hostname,
            )
        else:
            return await self._asyncio_create_connection_with(
                protocol_factory,
                sock,
                ssl = ssl,
                server_host_name = server_hostname,
            )
    
    
    async def _asyncio_create_connection_to(
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
        server_host_name = None
    ):
        ssl, server_host_name = self._create_connection_shared_precheck(ssl, server_host_name, host)
        
        future_1 = self._ensure_resolved(
            (host, port),
            family = socket_family,
            type = module_socket.SOCK_STREAM,
            protocol = socket_protocol,
            flags = socket_flags,
        )
        
        if local_address is not None:
            future_2 = self._ensure_resolved(
                local_address,
                family = socket_family,
                type = module_socket.SOCK_STREAM,
                protocol = socket_protocol,
                flags = socket_flags,
            )
        
        else:
            future_2 = None
        
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
            raise OSError('`get_address_info` returned empty list')
        
        if (future_2 is None):
            local_address_infos = None
        
        else:
            local_address_infos = future_2.get_result()
            if not local_address_infos:
                raise OSError('`get_address_info` returned empty list')
        
        exceptions = []
        for socket_family, socket_type, socket_protocol, socket_address_canonical_name, socket_address in infos:
            
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
                            err = OSError(err.errno, f'Error while attempting to bind on address '
                                f'{local_address!r}: {err.strerror.lower()}.')
                            exceptions.append(err)
                    else:
                        socket.close()
                        socket = None
                        continue
                
                await self.socket_connect(socket, socket_address)
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
                raise OSError(f'Multiple exceptions: {", ".join(exception_representations)}')
        
        return await self._asyncio_create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def _asyncio_create_connection_with(self, protocol_factory, socket, *, ssl = None, server_host_name = None):
        ssl, server_host_name = self._create_connection_shared_precheck(ssl, server_host_name, None)
        
        if not _is_stream_socket(socket):
            raise ValueError(f'A stream socket was expected, got {socket!r}.')
        
        return await self._asyncio_create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def _asyncio_create_connection_transport(self, socket, protocol_factory, ssl, server_host_name, server_side):
        socket.setblocking(False)
        
        protocol = protocol_factory()
        waiter = HataFuture(self)
        
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
        
        return transport, protocol
    
    
    async def create_datagram_endpoint(
        self,
        protocol_factory,
        local_addr = None,
        remote_addr = None,
        *,
        family = 0,
        proto = 0,
        flags = 0,
        reuse_address = None,
        reuse_port = None,
        allow_broadcast = None,
        sock = None,
    ):
        
        if sock is None:
            return await self._asyncio_create_datagram_connection_to(
                protocol_factory,
                local_addr,
                remote_addr,
                socket_family = family,
                socket_protocol = proto,
                socket_flags = flags,
                reuse_port = reuse_port,
                allow_broadcast = allow_broadcast,
            )
        
        else:
            return await self._asyncio_create_datagram_connection_with(protocol_factory, sock)


    async def _asyncio_create_datagram_connection_to(
        self,
        protocol_factory,
        local_address,
        remote_address, *,
        socket_family = 0,
        socket_protocol = 0,
        socket_flags = 0,
        reuse_port = False,
        allow_broadcast = False,
    ):
        address_info = []
        
        if (local_address is None) and (remote_address is None):
            if socket_family == 0:
                raise ValueError(f'Unexpected address family: {socket_family!r}.')
            
            address_info.append((socket_family, socket_protocol, None, None))
        
        elif hasattr(module_socket, 'AF_UNIX') and socket_family == module_socket.AF_UNIX:
            if __debug__:
                if (local_address is not None):
                    if not isinstance(local_address, bytes):
                        raise TypeError(
                            f'`local_address` can be `None`, `str` if `socket_family` is `AF_UNIX`, got '
                            f'{local_address.__class__.__name__}; {local_address!r}.'
                        )
                
                if (remote_address is not None):
                    if not isinstance(remote_address, str):
                        raise TypeError(
                            f'`remote_address` can be `None`, `str` if `socket_family` is `AF_UNIX`, got '
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
                    iterated_socket_canonical_name,
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
                    raise OSError('`get_address_info` returned empty list')
                
                
                for (
                    iterated_socket_family,
                    iterated_socket_type,
                    iterated_socket_protocol,
                    iterated_canonical_name,
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
        
        return await self._asyncio_create_datagram_connection(protocol_factory, socket, remote_address)
    

    async def _asyncio_create_datagram_connection_with(self, protocol_factory, socket):
        if socket.type != module_socket.SOCK_DGRAM:
            raise ValueError(f'A UDP socket was expected, got {socket!r}.')
        
        socket.setblocking(False)
        
        return await self._asyncio_create_datagram_connection(protocol_factory, socket, None)
    
    
    async def _asyncio_create_datagram_connection(self, protocol_factory, socket, address):
        protocol = protocol_factory()
        waiter = HataFuture(self)
        transport = DatagramSocketTransportLayer(self, None, socket, protocol, waiter, address)
        
        try:
            await waiter
        except:
            transport.close()
            raise
        
        return transport, protocol
    
    
    async def create_unix_connection(
        self,
        protocol_factory,
        path = None,
        *,
        ssl = None,
        sock = None,
        server_hostname = None,
        ssl_handshake_timeout = None,
    ):
        if sock is None:
            return await self._asyncio_create_unix_connection_to(
                protocol_factory, path, ssl = ssl, server_host_name = server_hostname
            )
        
        else:
            return await self._asyncio_create_unix_connection_with(
                protocol_factory, sock, ssl = ssl, server_host_name = server_hostname
            )
    
    
    async def _asyncio_create_unix_connection_to(self, protocol_factory, path, *, ssl = None, server_host_name = None):
        ssl, server_host_name = self._create_unix_connection_shared_precheck(ssl, server_host_name)
        
        path = os.fspath(path)
        socket = module_socket.socket(module_socket.AF_UNIX, module_socket.SOCK_STREAM, 0)
        
        try:
            socket.setblocking(False)
            await self.socket_connect(socket, path)
        except:
            socket.close()
            raise
        
        return await self._asyncio_create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def _asyncio_create_unix_connection_with(
        self, protocol_factory, socket, *, ssl = None, server_host_name = None
    ):
        ssl, server_host_name = self._create_unix_connection_shared_precheck(ssl, server_host_name)
        
        if socket.family not in (module_socket.AF_UNIX, module_socket.SOCK_STREAM):
            raise ValueError(f'A UNIX Domain Stream Socket was expected, got {socket!r}.')
        
        socket.setblocking(False)
    
        return await self._asyncio_create_connection_transport(socket, protocol_factory, ssl, server_host_name, False)
    
    
    async def create_server(
        self,
        protocol_factory,
        host = None,
        port = None,
        *,
        family = module_socket.AF_UNSPEC,
        flags = module_socket.AI_PASSIVE,
        sock = None,
        backlog = 100,
        ssl = None,
        reuse_address = None,
        reuse_port = None,
        ssl_handshake_timeout = None,
        start_serving = True,
    ):
        if sock is None:
            server = await self.create_server_to(
                protocol_factory,
                host,
                port,
                socket_family = family,
                socket_flags = flags,
                backlog = backlog,
                ssl = ssl,
                reuse_port = reuse_port,
            )
        
        else:
            server =  await self.create_server_with(protocol_factory, sock, backlog = backlog, ssl = ssl)
        
        if start_serving:
            await server.start()
        
        return server
    
    
    async def create_unix_server(
        self,
        protocol_factory,
        path = None,
        *,
        sock = None,
        backlog = 100,
        ssl = None,
        ssl_handshake_timeout = None,
        start_serving = True,
    ):
        
        if sock is None:
            server = await self.create_unix_server_to(protocol_factory, path, backlog = backlog, ssl = ssl)
        
        else:
            server = await self.create_unix_server_with(protocol_factory, sock, backlog = backlog, ssl = ssl)
        
        if start_serving:
            await server.start()
        
        return server
    
    
    call_later = EventThread.call_after


    async def sock_sendto(self, sock, data, address):
        """
        Send data to the socket.

        The socket must be connected to a remote socket. This method continues
        to send data from data until either all data has been sent or an
        error occurs. None is returned on success. On error, an exception is
        raised, and there is no way to determine how much data, if any, was
        successfully processed by the receiving end of the connection.
        """
        if ssl is not None and isinstance(sock, ssl.SSLSocket):
            raise TypeError("Socket cannot be of type SSLSocket")
        
        try:
            return sock.sendto(data, address)
        except (BlockingIOError, InterruptedError):
            pass

        future = HataFuture(self)
        file_descriptor = sock.fileno()
        handle = self.add_writer(file_descriptor, self._sock_sendto, future, sock, data, address)
        future.add_done_callback(partial_func(self._sock_write_done, file_descriptor, handle = handle))
        return await future
    
    
    def _sock_sendto(self, future, sock, data, address):
        if future.done():
            return
        
        try:
            n = sock.sendto(data, 0, address)
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            future.set_exception(exc)
        else:
            future.set_result(n)
    
    
    def _sock_write_done(self, file_descriptor, future, handle = None):
        if handle is None or not handle.cancelled():
            self.remove_writer(file_descriptor)


    def _sock_read_done(self, file_descriptor, future, handle = None):
        if handle is None or not handle.cancelled():
            self.remove_reader(file_descriptor)
    
    
    async def sock_recvfrom(self, sock, bufsize):
        """
        Receive a datagram from a datagram socket.

        The return value is a tuple of (bytes, address) representing the
        datagram received and the address it came from.
        The maximum amount of data to be received at once is specified by
        nbytes.
        """
        if ssl is not None and isinstance(sock, ssl.SSLSocket):
            raise TypeError("Socket cannot be of type SSLSocket")

        try:
            return sock.recvfrom(bufsize)
        except (BlockingIOError, InterruptedError):
            pass
        
        future = HataFuture(self)
        file_descriptor = sock.fileno()
        self._ensure_fd_no_transport(file_descriptor)
        handle = self._add_reader(file_descriptor, self._sock_recvfrom, future, sock, bufsize)
        future.add_done_callback(partial_func(self._sock_read_done, file_descriptor, handle = handle))
        return await future


    def _sock_recvfrom(self, future, sock, bufsize):
        if future.done():
            return
        
        try:
            result = sock.recvfrom(bufsize)
        except (BlockingIOError, InterruptedError):
            return  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            future.set_exception(exc)
        else:
            future.set_result(result)


    async def sock_recvfrom_into(self, sock, buf, nbytes = 0):
        """
        Receive data from the socket.

        The received data is written into *buf* (a writable buffer).
        The return value is a tuple of (number of bytes written, address).
        """
        if ssl is not None and isinstance(sock, ssl.SSLSocket):
            raise TypeError("Socket cannot be of type SSLSocket")
    
        if not nbytes:
            nbytes = len(buf)

        try:
            return sock.recvfrom_into(buf, nbytes)
        except (BlockingIOError, InterruptedError):
            pass
        
        future = HataFuture(self)
        file_descriptor = sock.fileno()
        handle = self.add_reader(file_descriptor, self._sock_recvfrom_into, future, sock, buf, nbytes)
        future.add_done_callback(partial_func(self._sock_read_done, file_descriptor, handle = handle))
        return await future


    def _sock_recvfrom_into(self, fut, sock, buf, bufsize):
        if fut.done():
            return
        try:
            result = sock.recvfrom_into(buf, bufsize)
        except (BlockingIOError, InterruptedError):
            return  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(result)


    async def start_tls(
        self,
        transport,
        protocol,
        sslcontext,
        *,
        server_side = False,
        server_hostname = None,
        ssl_handshake_timeout = None,
        ssl_shutdown_timeout = None,
    ):
        """
        Upgrade transport to TLS.

        Return a new transport that *protocol* should start using
        immediately.
        """
        if ssl is None:
            raise RuntimeError('Python ssl module is not available')

        if not isinstance(sslcontext, ssl.SSLContext):
            raise TypeError(
                f'sslcontext is expected to be an instance of ssl.SSLContext, got {sslcontext!r}'
            )

        if not getattr(transport, '_start_tls_compatible', False):
            raise TypeError(
                f'transport {transport!r} is not supported by start_tls()'
            )

        waiter = HataFuture(self)
        ssl_protocol = SSLBidirectionalTransportLayer(
            self,
            protocol,
            sslcontext,
            waiter,
            server_side,
            server_hostname,
            False,
        )

        transport.pause_reading()

        transport.set_protocol(ssl_protocol)
        connection_made_callback = self.call_soon(ssl_protocol.connection_made, transport)
        resume_callback = self.call_soon(transport.resume_reading)

        try:
            await waiter
        except:
            transport.close()
            connection_made_callback.cancel()
            resume_callback.cancel()
            raise

        return ssl_protocol._transport
    
    
    _scarletio_connect_accepted_socket = EventThread.connect_accepted_socket
    
    async def connect_accepted_socket(
        self,
        protocol_factory,
        sock,
        *,
        ssl = None,
        ssl_handshake_timeout = None,
        ssl_shutdown_timeout = None,
    ):
        return await self._scarletio_connect_accepted_socket(protocol_factory, sock, ssl = ssl)


async def in_coro(future):
    return await future


# Required by aio-http 3.7
def asyncio_run_in_executor(self, executor, func = ..., *args):
    # We ignore the executor parameter.
    # First handle if the call is from hata. If called from hata, needs to return a `Future`.
    if func is ...:
        return Executor.run_in_executor(self, executor)
    
    # if the call is from async-io it needs to return a coroutine
    if args:
        func = alchemy_incendiary(func, args)
    
    return in_coro(Executor.run_in_executor(self, func))

EventThread.run_in_executor = asyncio_run_in_executor
del asyncio_run_in_executor


# required by anyio
def asyncio_create_task(self, coroutine):
    return Task(coroutine, self)

EventThread.create_task = asyncio_create_task
del asyncio_create_task

# We accept different names, so we need to define a dodge system, so here we go
scarletio_EventThread_subprocess_shell = EventThread.subprocess_shell

async def asyncio_subprocess_shell(
    self,
    *args,
    preexecution_function = None,
    creation_flags = 0,
    preexec_fn = None,
    creationflags = 0,
    startupinfo = None,
    startup_info = None,
    **kwargs,
):
    
    if preexec_fn is not None:
        preexecution_function = preexec_fn
    
    if creationflags != 0:
        creation_flags = creationflags
    
    if startupinfo is not None:
        startup_info = startupinfo
    
    return await scarletio_EventThread_subprocess_shell(
        self,
        *args,
        preexecution_function = preexecution_function,
        creation_flags = creation_flags,
        startupinfo = startup_info,
        **kwargs,
    )

EventThread.subprocess_shell = asyncio_subprocess_shell
del asyncio_subprocess_shell


scarletio_EventThread_subprocess_exec = EventThread.subprocess_exec

async def asyncio_subprocess_exec(
    self,
    *args,
    preexecution_function = None,
    creation_flags = 0,
    preexec_fn = None,
    creationflags = 0,
    startupinfo = None,
    startup_info = None,
    **kwargs,
):
    
    if preexec_fn is not None:
        preexecution_function = preexec_fn
    
    if creationflags != 0:
        creation_flags = creationflags
    
    if startupinfo is not None:
        startup_info = startupinfo
    
    return await scarletio_EventThread_subprocess_exec(
        self,
        *args,
        preexecution_function = preexecution_function,
        creation_flags = creation_flags,
        startup_info = startup_info,
        **kwargs,
    )

EventThread.subprocess_exec = asyncio_subprocess_exec
del asyncio_subprocess_exec


@KeepType(ReadProtocolBase)
class ReadProtocolBase:
    async def readexactly(self, n):
        return await self.read_exactly(n)


@KeepType(HataFuture)
class HataFuture:
    @property
    def done(self):
        return self.is_done
    
    @property
    def cancelled(self):
        return self.is_cancelled
    
    @property
    def pending(self):
        return self.is_pending
    
    @property
    def result(self):
        return self.get_result
    
    @property
    def exception(self):
        return self.get_exception


@KeepType(HataTask)
class HataTask:
    @property
    def _log_destroy_pending(self):
        return False
    
    @_log_destroy_pending.setter
    def _log_destroy_pending(self, value):
        pass


@KeepType(HataLock)
class HataLock:
    def locked(self):
        return self.is_locked()

# Reimplement async-io features

# asyncio.base_events
# include: BaseEventLoop, _run_until_complete_cb
BaseEventLoop = EventThread

def _run_until_complete_cb(future): # needed by anyio
    future._loop.stop()

# async-io.base_futures
# *none*

# async-io.base_subprocess
# *none*

# async-io.base_tasks
# *none*

# async-io.constants
# *none*

# async-io.coroutines
# include: coroutine, iscoroutinefunction, iscoroutine
from types import coroutine
iscoroutinefunction = is_coroutine_function


if sys.version_info >= (3, 12, 0):
    def iscoroutine(coroutine):
        if isinstance(coroutine, GeneratorType):
            return False
        
        return is_coroutine(coroutine)
else:
    iscoroutine = is_coroutine

# asyncio.events
# include: AbstractEventLoopPolicy, AbstractEventLoop, AbstractServer, Handle, TimerHandle, get_event_loop_policy,
#    set_event_loop_policy, get_event_loop, set_event_loop, new_event_loop, get_child_watcher, set_child_watcher,
#    _set_running_loop, get_running_loop, _get_running_loop

class AbstractEventLoopPolicy:
    def __new__(cls):
        raise NotImplementedError

AbstractEventLoop = EventThread
AbstractServer = Server

def get_event_loop_policy():
    raise NotImplementedError

def set_event_loop_policy():
    raise NotImplementedError

def get_event_loop():
    """
    Return a hata event loop.
    
    When called from a coroutine or a callback (e.g. scheduled with call_soon or similar API), this function will
    always return the running event loop.
    
    If there is no running event loop set, the function will return the result of
    `get_event_loop_policy().get_event_loop()` call.
    """
    return scarletio_get_event_loop()

def set_event_loop(loop):
    """Set the event loop."""
    pass

def new_event_loop():
    """Equivalent to calling get_event_loop_policy().new_event_loop()."""
    return EventThread()

def get_child_watcher():
    """Equivalent to calling get_event_loop_policy().get_child_watcher()."""
    raise NotImplementedError

def set_child_watcher(watcher):
    """Equivalent to calling get_event_loop_policy().set_child_watcher(watcher)."""
    raise NotImplementedError

def _set_running_loop(loop):
    """
    Set the running event loop.
    
    This is a low-level function intended to be used by event loops.
    This function is thread-specific.
    """
    assert current_thread() is loop

def get_running_loop():
    """
    Return the running event loop.  Raise a RuntimeError if there is none.
    This function is thread-specific.
    """
    loop = _get_running_loop()
    if loop is None:
        raise RuntimeError('no current event loop')
    
    return loop

def _get_running_loop():
    """
    Return the running event loop or None.
    This is a low-level function intended to be used by event loops.
    This function is thread-specific.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        return local_thread

class SendfileNotAvailableError(RuntimeError):
    """
    Sendfile syscall is not available.
    
    Raised if OS does not support sendfile syscall for given socket or file type.
    """

# asyncio.exceptions
# include: CancelledError, InvalidStateError, TimeoutError, IncompleteReadError, LimitOverrunError,
#    SendfileNotAvailableError, BrokenBarrierError
TimeoutError = TimeoutError

class IncompleteReadError(EOFError):
    """
    Incomplete read error. Attributes:
    
    - partial: read bytes string before the end of stream was reached
    - expected: total number of expected bytes (or None if unknown)
    """
    def __init__(self, partial, expected):
        EOFError.__init__(self, f'{len(partial)} bytes read on a total of {expected!r} expected bytes')
        self.partial = partial
        self.expected = expected

    def __reduce__(self):
        return type(self), (self.partial, self.expected)


class LimitOverrunError(Exception):
    """
    Reached the buffer limit while looking for a separator.
    
    Attributes:
    - consumed: total number of to be consumed bytes.
    """
    def __init__(self, message, consumed):
        Exception.__init__(self, message)
        self.consumed = consumed

    def __reduce__(self):
        return type(self), (self.args[0], self.consumed)


class BrokenBarrierError(RuntimeError):
    """Barrier is broken by barrier.abort() call."""


# asyncio.format_helpers
# *none*

# asyncio.futures
# Include: Future, wrap_future, isfuture

class Future:
    """
    This class is *almost* compatible with concurrent.futures.Future.
    
    Differences:
    
    - This class is not thread-safe.
    
    - result() and exception() do not take a timeout parameter and
      raise an exception when the future isn't done yet.
    
    - Callbacks registered with add_done_callback() are always called
      via the event loop's call_soon().
    
    - This class is not compatible with the wait() and as_completed()
      methods in the concurrent.futures package.
    
    (In Python 3.4 or later we may be able to unify the implementations.)
    """
    def __new__(cls, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        
        return HataFuture(loop)
    
    def __instancecheck__(cls, instance):
        return isinstance(instance, HataFuture) or isinstance(instance, cls)

    def __subclasscheck__(cls, klass):
        return issubclass(klass, HataFuture) or (klass is cls)

# get_loop is new in python 3.7 and required by aiosqlite
def asyncio_get_loop(self):
    return self._loop

HataFuture.get_loop = asyncio_get_loop
del asyncio_get_loop


def wrap_future(future, *, loop = None):
    raise NotImplementedError

def isfuture(obj):
    """
    Check for a Future.
    
    This returns True when obj is a Future instance or is advertising itself as duck-type compatible by setting
    _asyncio_future_blocking.
    See comment in Future for more details.
    """
    return isinstance(obj, HataFuture)

# asyncio.locks
# Include: Lock, Event, Condition, Semaphore, BoundedSemaphore, Barrier

class Lock(HataLock):
    """
    Primitive lock objects.
    
    A primitive lock is a synchronization primitive that is not owned by a particular coroutine when locked.
    A primitive lock is in one of two states, 'locked' or 'unlocked'.
    
    It is created in the unlocked state. It has two basic methods,acquire() and release(). When the state is unlocked,
    acquire()changes the state to locked and returns immediately. When the state is locked, acquire() blocks until a
    call to release() in an other coroutine changes it to unlocked, then the acquire() call resets it to locked and
    returns. The release() method should only be called in the locked state; it changes the state to unlocked and
    returns immediately. If an attempt is made to release an unlocked lock, a RuntimeError will be raised.
    
    When more than one coroutine is blocked in acquire() waiting for the state to turn to unlocked, only one coroutine
    proceeds when a release() call resets the state to unlocked; first coroutine which is blocked in acquire() is being
    processed.
    
    acquire() is a coroutine and should be called with 'await'.
    
    Locks also support the asynchronous context management protocol. 'async with lock' statement should be used.
    
    Usage:
    
        ```py
        lock = Lock()
        ...
        await lock.acquire()
        try:
            ...
        finally:
            lock.release()
        ```
    
    Context manager usage:
        ```py
        lock = Lock()
        ...
        async with lock:
             ...
         ```
     
    Lock objects can be tested for locking state:
    
        ```py
        if not lock.locked():
           await lock.acquire()
        else:
           # lock is acquired
           ...
        ```
    """
    # Required by dead.py
    __slots__ = ('__weakref__', )
    
    def __new__(cls, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        
        return HataLock.__new__(cls, loop)
    
    def __instancecheck__(cls, instance):
        return isinstance(instance, HataLock)
    
    def __subclasscheck__(cls, klass):
        return issubclass(klass, HataLock) or (klass is cls)


class Event:
    """
    Asynchronous equivalent to threading.Event.
    
    Class implementing event objects. An event manages a flag that can be set to true with the set() method and reset
    to false with the clear() method. The wait() method blocks until the flag is true. The flag is initially false.
    """
    def __new__(cls, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        
        return HataEvent(loop)
    
    def __instancecheck__(cls, instance):
        return isinstance(instance, HataEvent)
    
    def __subclasscheck__(cls, klass):
        return issubclass(klass, HataEvent) or (klass is cls)


class Condition:
    """
    Asynchronous equivalent to threading.Condition.
    
    This class implements condition variable objects. A condition variable allows one or more coroutines to wait until
    they are notified by another coroutine.
    
    A new Lock object is created and used as the underlying lock.
    """
    __slots__ = ('_lock', '_loop', '_waiters')
    
    def __new__(cls, lock = None, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        else:
            warn(
                'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
                DeprecationWarning,
                stacklevel = 2,
            )
        
        
        if lock is None:
            lock = Lock(loop = loop)
        elif lock._loop is not loop:
            raise RuntimeError(
                f'The lock\'s loop must match with the loop parameter; got lock.loop = {lock._loop!r}; loop = {loop!r}.'
            )
        
        self = object.__new__(cls)
        self._loop = loop
        self._lock = lock
        self._waiters = deque()
        return self
    
    
    def locked(self):
        return self._lock.is_locked()
    
    
    async def acquire(self):
        await self._lock.acquire()
        return True
    
    
    def release(self):
        return self._lock.release()
    
    
    async def __aenter__(self):
        await self._lock.acquire()
        return None
    
    
    async def __aexit__(self, exception_type, exception, exception_traceback):
        self._lock.release()
        return False
    
    
    def __repr__(self):
        repr_parts = ['<', self.__class__.__name__, ' ']
        
        if not self._lock.is_locked():
            repr_parts.append('un')
        repr_parts.append('locked')
        
        waiter_count = len(self._waiters)
        if waiter_count:
            repr_parts.append(', waiters: ')
            repr_parts.append(str(waiter_count))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    async def wait(self):
        """
        Wait until notified.

        If the calling coroutine has not acquired the lock when this method is called, a RuntimeError is raised.

        This method releases the underlying lock, and then blocks until it is awakened by a notify() or notify_all()
        call for the same condition variable in another coroutine. Once awakened, it re-acquires the lock and returns
        True.
        """
        if not self._lock.is_locked():
            raise RuntimeError(f'cannot wait on un-acquired lock; self = {self!r}.')
        
        self._lock.release()
        try:
            future = self._loop.create_future()
            self._waiters.append(future)
            try:
                await future
            finally:
                self._waiters.remove(future)
        except GeneratorExit:
            self._lock._waiters.appendleft(self._loop.create_future())
            raise
        
        except BaseException as err:
            exception = err
        else:
            exception = None
        
        try:
            await self._lock.acquire()
        except BaseException as err:
            self._lock._waiters.appendleft(self._loop.create_future())
            raise err from exception
        
        if (exception is not None):
            raise exception
        
        return True
    
    
    async def wait_for(self, predicate):
        """
        Wait until a predicate becomes true.

        The predicate should be a callable which result will be interpreted as a boolean value. The final predicate
        value is the return value.
        """
        result = predicate()
        while not result:
            await self.wait()
            result = predicate()
        
        return result
    
    
    def notify(self, n = 1):
        """
        By default, wake up one coroutine waiting on this condition, if any. If the calling coroutine has not acquired
        the lock when this method is called, a RuntimeError is raised.

        This method wakes up at most n of the coroutines waiting for the condition variable; it is a no-op if no
        coroutines are waiting.

        Note: an awakened coroutine does not actually return from its wait() call until it can reacquire the lock.
        Since notify() does not release the lock, its caller should.
        """
        if not self._lock.is_locked():
            raise RuntimeError(f'cannot wait on un-acquired lock; self = {self!r}.')

        index = 0
        for future in self._waiters:
            if index >= n:
                break
            
            index += future.set_result_if_pending(False)
    
    
    def notify_all(self):
        """
        Wake up all threads waiting on this condition. This method acts like notify(), but wakes up all waiting threads
        instead of one. If the calling thread has not acquired the lock when this method is called, a RuntimeError is
        raised.
        """
        self.notify(len(self._waiters))


class Semaphore:
    """
    A Semaphore implementation.
    
    A semaphore manages an internal counter which is decremented by each acquire() call and incremented by each
    release() call. The counter can never go below zero; when acquire() finds that it is zero, it blocks, waiting until
    some other coroutine calls release().
    
    Semaphores also support the context management protocol.
    
    The optional parameter gives the initial value for the internal counter; it defaults to 1. If the value given is
    less than 0, ValueError is raised.
    """
    __slots__ = ('_loop', '_value', '_waiters')
    
    def __new__(cls, value = 1, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        else:
            warn(
                'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
                DeprecationWarning,
                stacklevel = 2,
            )
        
        if value < 0:
            raise ValueError(f'Semaphore initial value must be >= 0; value = {value!r}')
        
        self = object.__new__(cls)
        self._loop = loop
        self._value = value
        self._waiters = deque()
        return self
    
    
    def __repr__(self):
        repr_parts = ['<', self.__class__.__name__]
        
        if self.locked():
            repr_parts.append(' locked')
        else:
            repr_parts.append(' unlocked, value:')
            repr_parts.append(repr(self._value))
        
        waiter_count = len(self._waiters)
        if waiter_count:
            repr_parts.append(', waiters:')
            repr_parts.append(waiter_count)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def _wake_up_next(self):
        while self._waiters:
            waiter = self._waiters.popleft()
            if waiter.set_result_if_pending(None) == 1:
                return
    
    
    def locked(self):
        """Returns True if semaphore can not be acquired immediately."""
        return self._value == 0
    
    
    async def acquire(self):
        """
        Acquire a semaphore.
        
        If the internal counter is larger than zero on entry, decrement it by one and return True immediately.
        If it is zero on entry, block, waiting until some other coroutine has called release() to make it larger than
        0, and then return True.
        """
        while self._value <= 0:
            future = HataFuture(self._loop)
            self._waiters.append(future)
            
            try:
                await future
            except:
                future.cancel()
                
                if (self._value > 0) and (not future.cancelled()):
                    self._wake_up_next()
                
                raise
        
        self._value -= 1
        return True
    
    
    def release(self):
        """
        Release a semaphore, incrementing the internal counter by one. When it was zero on entry and another
        coroutine is waiting for it to become larger than zero again, wake up that coroutine.
        """
        self._value += 1
        self._wake_up_next()
    
    async def __aenter__(self):
        await self.acquire()
        return None
    
    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        self.release()
        return False


class BoundedSemaphore(Semaphore):
    """
    A bounded semaphore implementation.
    
    This raises ValueError in release() if it would increase the value above the initial value.
    """
    __slots__ = ('_bound_value',)
    
    def __new__(cls, value = 1, *, loop = None):
        self = Semaphore.__new__(cls, value = value, loop = loop)
        self._bound_value = value
        return self
    
    def release(self):
        if self._value >= self._bound_value:
            raise ValueError('BoundedSemaphore released too many times')
        
        return Semaphore.release(self)


class _BarrierState(Enum):
    FILLING = 'filling'
    DRAINING = 'draining'
    RESETTING = 'resetting'
    BROKEN = 'broken'


class Barrier:
    """
    Asyncio equivalent to threading.Barrier

    Implements a Barrier primitive.
    Useful for synchronizing a fixed number of tasks at known synchronization
    points. Tasks block on 'wait()' and are simultaneously awoken once they
    have all made their call.
    """
    def __init__(self, parties):
        """Create a barrier, initialised to 'parties' tasks."""
        if parties < 1:
            raise ValueError('Parties must be > 0.')

        self._cond = Condition()

        self._parties = parties
        self._state = _BarrierState.FILLING
        self._count = 0


    def __repr__(self):
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append('[')
        repr_parts.append(self._state.value)
        
        repr_parts.append(', waiters: ')
        repr_parts.append(repr(self.n_waiting))
        repr_parts.append('/')
        repr_parts.append(repr(self.parties))
        repr_parts.append(']>')
        
        return ''.join(repr_parts)


    async def __aenter__(self):
        return await self.wait()


    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        pass


    async def wait(self):
        """
        Wait for the barrier.

        When the specified number of tasks have started waiting, they are all
        simultaneously awoken.
        Returns an unique and individual index number from 0 to 'parties-1'.
        """
        async with self._cond:
            await self._block()
            try:
                index = self._count
                self._count += 1
                if index + 1 == self._parties:
                    await self._release()
                else:
                    await self._wait()
                return index
            finally:
                self._count -= 1
                self._exit()


    async def _block(self):
        await self._cond.wait_for(
            lambda: self._state not in (
                _BarrierState.DRAINING, _BarrierState.RESETTING
            )
        )

        if self._state is _BarrierState.BROKEN:
            raise BrokenBarrierError("Barrier aborted")


    async def _release(self):
        self._state = _BarrierState.DRAINING
        self._cond.notify_all()


    async def _wait(self):
        await self._cond.wait_for(lambda: self._state is not _BarrierState.FILLING)

        if self._state in (_BarrierState.BROKEN, _BarrierState.RESETTING):
            raise BrokenBarrierError("Abort or reset of barrier")


    def _exit(self):
        if self._count == 0:
            if self._state in (_BarrierState.RESETTING, _BarrierState.DRAINING):
                self._state = _BarrierState.FILLING
            self._cond.notify_all()


    async def reset(self):
        """
        Reset the barrier to the initial state.

        Any tasks currently waiting will get the BrokenBarrier exception
        raised.
        """
        async with self._cond:
            if self._count > 0:
                if self._state is not _BarrierState.RESETTING:
                    self._state = _BarrierState.RESETTING
            else:
                self._state = _BarrierState.FILLING
            self._cond.notify_all()


    async def abort(self):
        """
        Place the barrier into a 'broken' state.

        Useful in case of error.  Any currently waiting tasks and tasks
        attempting to 'wait()' will have BrokenBarrierError raised.
        """
        async with self._cond:
            self._state = _BarrierState.BROKEN
            self._cond.notify_all()


    @property
    def parties(self):
        """Return the number of tasks required to trip the barrier."""
        return self._parties


    @property
    def n_waiting(self):
        """Return the number of tasks currently waiting at the barrier."""
        if self._state is _BarrierState.FILLING:
            return self._count
        return 0


    @property
    def broken(self):
        """Return True if the barrier is in a broken state."""
        return self._state is _BarrierState.BROKEN


# asyncio.proactor_events
# Include: BaseProactorEventLoop

BaseProactorEventLoop = EventThread # Note, that hata has no proactor event_loop implemented.

# asyncio.protocols
# Include: BaseProtocol, Protocol, DatagramProtocol, SubprocessProtocol, BufferedProtocol

class BaseProtocol:
    """
    Common base class for protocol interfaces.
    
    Usually user implements protocols that derived from BaseProtocol like Protocol or ProcessProtocol.
    
    The only case when BaseProtocol should be implemented directly is write-only transport like write pipe.
    """
    __slots__ = ()
    
    def connection_made(self, transport):
        pass
    
    def connection_lost(self, exception):
        pass
    
    def pause_writing(self):
        pass
    
    def resume_writing(self):
        pass

class Protocol(BaseProtocol):
    """
    Interface for stream protocol.
    
    The user should implement this interface. They can inherit from this class but don't need to. The implementations
    here do Nothing (they don't raise exceptions).
    
    When the user wants to requests a transport, they pass a protocol factory to a utility function
    (e.g., EventLoop.create_connection()).
    
    When the connection is made successfully, connection_made() is called with a suitable transport object.
    Then data_received() will be called 0 or more times with data (bytes) received from the transport; finally,
    connection_lost() will be called exactly once with either an exception object or None as an parameter.
    
    State machine of calls:
    
      start -> CM [-> DR*] [-> ER?] -> CL -> end
    
    - CM: connection_made()
    - DR: data_received()
    - ER: eof_received()
    - CL: connection_lost()
    """

    __slots__ = ()

    def data_received(self, data):
        pass

    def eof_received(self):
        pass

class DatagramProtocol(BaseProtocol):
    """Interface for datagram protocol."""

    __slots__ = ()

    def datagram_received(self, data, addr):
        pass

    def error_received(self, exc):
        pass

class SubprocessProtocol(BaseProtocol):
    """Interface for protocol for subprocess calls."""

    __slots__ = ()

    def pipe_data_received(self, fd, data):
        pass

    def pipe_connection_lost(self, fd, exception):
        pass

    def process_exited(self):
        pass


class BufferedProtocol(BaseProtocol):
    """
    Interface for stream protocol with manual buffer control.
    
    Important: this has been added to asyncio in Python 3.7 *on a provisional basis*!  Consider it as an experimental
    API that might be changed or removed in Python 3.8.
    
    Event methods, such as `create_server` and `create_connection`, accept factories that return protocols that
    implement this interface. The idea of BufferedProtocol is that it allows to manually allocate and control the
    receive buffer. Event loops can then use the buffer provided by the protocol to avoid unnecessary data copies.
    This can result in noticeable performance improvement for protocols that receive big amounts of data.
    Sophisticated protocols can allocate the buffer only once at creation time.
    
    State machine of calls:
    
      start -> CM [-> GB [-> BU?]]* [-> ER?] -> CL -> end
      
    - CM: connection_made()
    - GB: get_buffer()
    - BU: buffer_updated()
    - ER: eof_received()
    - CL: connection_lost()
    """

    __slots__ = ()

    def get_buffer(self, sizehint):
        pass

    def buffer_updated(self, nbytes):
        pass

    def eof_received(self):
        pass

# asyncio.queues
# Include Queue, PriorityQueue, LifoQueue, QueueFull, QueueEmpty

class QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""
    def __init__(cls, *args):
        pass

class QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""
    def __init__(self, *args):
        pass

class Queue(AsyncQueue):
    def __new__(cls, maxsize = 0, *, loop = None):
        if loop is None:
            loop = get_event_loop()
        
        if maxsize:
            max_length = maxsize
        else:
            max_length = None
        
        return AsyncQueue.__new__(cls, loop, max_length = max_length)
    
    async def put(self, element):
        """
        Put an item into the queue.
        
        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.
        """
        await self.set_result_wait(element)
    
    def put_nowait(self, element):
        if len(self) == self.max_length:
            raise QueueFull()
        
        self.set_result(element)
    
    async def get(self):
        return await self.get_result()
    
    def get_nowait(self):
        try:
            return self.result_no_wait()
        except IndexError:
            raise QueueEmpty


def PriorityQueue(maxsize = 0, *, loop = None):
    """
    A subclass of Queue; retrieves entries in priority order (lowest first).

    Entries are typically tuples of the form: (priority number, data).
    """
    raise NotImplementedError


class LifoQueue(AsyncLifoQueue):
    def __new__(cls, maxsize = 0, *, loop = None):
        """A subclass of Queue that retrieves most recently added entries first."""
        if loop is None:
            loop = get_event_loop()
        
        if maxsize:
            max_length = maxsize
        else:
            max_length = None
        
        return AsyncLifoQueue.__new__(cls, loop, max_length = max_length)
    
    def put_nowait(self, element):
        if len(self) == self.max_length:
            raise QueueFull()
        
        self.set_result(element)
    
    async def get(self):
        return await self.get_result()
    
    
    def get_nowait(self):
        try:
            return self.result_no_wait()
        except IndexError:
            raise QueueEmpty


# asyncio.runners
# Include: run, Runner

def run(main, *, debug = None, loop_factory = None):
    """
    Execute the coroutine and return the result.
    
    This function runs the passed coroutine, taking care of managing the asyncio event loop and finalizing asynchronous
    generators.
    
    This function cannot be called when another asyncio event loop is running in the same thread.
    
    If debug is True, the event loop will be run in debug mode.
    
    This function always creates a new event loop and closes it at the end. It should be used as a main entry point for
    asyncio programs, and should ideally only be called once.
    
    Example:
    
        ```py
        async def main():
            await asyncio.sleep(1)
            print('hello')
        
        asyncio.run(main())
        ```
    """
    local_loop = current_thread()
    if isinstance(local_loop, EventThread):
        raise RuntimeError('asyncio.run() cannot be called from a running event loop.')
    
    if not iscoroutine(main):
        raise ValueError(f'A coroutine was expected, got {main!r}.')
    
    if (loop_factory is not None):
        loop = loop_factory()
    
    else:
        try:
            loop = scarletio_get_event_loop()
        except RuntimeError:
            pass
        else:
            # Required by anyio
            main = Task(in_coro(main), loop = loop)
            
            loop.run(main)
            return
    
    loop = EventThread()
    
    # Required by anyio
    main = Task(in_coro(main), loop = loop)
    
    try:
        loop.run(main)
    finally:
        loop.stop()


class _RunnerState(Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    CLOSED = "closed"


class Runner:
    """
    A context manager that controls event loop life cycle.

    The context manager always creates a new event loop,
    allows to run async functions inside it,
    and properly finalizes the loop at the context manager exit.

    If debug is True, the event loop will be run in debug mode.
    If loop_factory is passed, it is used for new event loop creation.

    asyncio.run(main(), debug=True)

    is a shortcut for

    with asyncio.Runner(debug=True) as runner:
        runner.run(main())

    The run() method can be called multiple times within the runner's context.

    This can be useful for interactive console (e.g. IPython),
    unittest runners, console tools, -- everywhere when async code
    is called from existing sync framework and where the preferred single
    asyncio.run() call doesn't work.
    """
    def __init__(self, *, debug = None, loop_factory = None):
        self._state = _RunnerState.CREATED
        self._loop_factory = loop_factory
        self._loop = None
        self._interrupt_count = 0
        self._set_event_loop = False
    
    
    def __enter__(self):
        self._lazy_init()
        return self
    
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()
    
    
    def close(self):
        """Shutdown and close event loop."""
        if self._state is not _RunnerState.INITIALIZED:
            return
        
        loop = self._loop
        try:
            try:
                for task in loop.get_tasks():
                    task.cancel()
            finally:
                task = None
            
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            if self._set_event_loop:
                set_event_loop(None)
            
            loop.close()
            self._loop = None
            self._state = _RunnerState.CLOSED
    
    
    def get_loop(self):
        """Return embedded event loop."""
        self._lazy_init()
        return self._loop
    
    
    def run(self, coro, *, context = None):
        """Run a coroutine inside the embedded event loop."""
        if not iscoroutine(coro):
            raise ValueError(f"A coroutine was expected, got {coro!r}.")

        if _get_running_loop() is not None:
            # fail fast with short traceback
            raise RuntimeError(f"{type(self).__name__}.run() cannot be called from a running event loop.")

        self._lazy_init()

        task = self._loop.create_task(coro)

        if (current_thread() is main_thread()) and signal.getsignal(signal.SIGINT) is signal.default_int_handler:
            sigint_handler = partial_func(self._on_sigint, main_task = task)
            try:
                signal.signal(signal.SIGINT, sigint_handler)
            except ValueError:
                sigint_handler = None
        else:
            sigint_handler = None

        self._interrupt_count = 0
        try:
            return self._loop.run_until_complete(task)
        except CancelledError as err:
            if self._interrupt_count > 0:
                raise KeyboardInterrupt from err
            
            raise
        
        finally:
            if (sigint_handler is not None) and signal.getsignal(signal.SIGINT) is sigint_handler:
                signal.signal(signal.SIGINT, signal.default_int_handler)
    
    
    def _lazy_init(self):
        if self._state is _RunnerState.CLOSED:
            raise RuntimeError(f"{type(self).__name__} is closed")
        
        if self._state is _RunnerState.INITIALIZED:
            return
        
        loop_factory = self._loop_factory
        if loop_factory is not None:
            loop = loop_factory()
        else:
            loop = new_event_loop()
            if not self._set_event_loop:
                set_event_loop(self._loop)
                self._set_event_loop = True
        
        self._loop = loop
        self._state = _RunnerState.INITIALIZED
    
    
    def _on_sigint(self, signum, frame, main_task):
        self._interrupt_count += 1
        if self._interrupt_count == 1 and not main_task.is_done():
            main_task.cancel()
            self._loop.wake_up()
            return
        
        raise KeyboardInterrupt


# asyncio.selector_events
# Include: BaseSelectorEventLoop

BaseSelectorEventLoop = EventThread

# asyncio.sslproto
# *none*

# asyncio.staggered_race
# Include: staggered_race

async def staggered_race(coroutine_functions, delay, *, loop = None):
    """
    Run coroutines with staggered start times and take the first to finish.
    
    This method takes an iterable of coroutine functions. The first one is started immediately. From then on, whenever
    the immediately preceding one fails (raises an exception), or when *delay* seconds has passed, the next coroutine
    is started. This continues until one of the coroutines complete successfully, in which case all others are
    cancelled, or until all coroutines fail.
    
    The coroutines provided should be well-behaved in the following way:
    
    * They should only `return` if completed successfully.
    
    * They should always raise an exception if they did not complete successfully. In particular, if they handle
    cancellation, they should probably reraise, like this::
    
        ```py
        try:
            # do work
        except asyncio.CancelledError:
            # undo partially completed work
            raise
        ```
    
    Args:
        coroutine_functions: an iterable of coroutine functions, i.e. callables that return a coroutine object when
        called. Use `functools.partial` or lambdas to pass parameters.
        
        delay: amount of time, in seconds, between starting coroutines. If `None`, the coroutines will run
        sequentially.
        
        loop: the event loop to use.
    
    Returns:
        tuple *(winner_result, winner_index, exceptions)* where
        
        - *winner_result*: the result of the winning coroutine, or `None` if no coroutines won.
        - *winner_index*: the index of the winning coroutine in `coroutine_functions`, or `None` if no coroutines won.
            If the winning coroutine may return None on success, *winner_index* can be used to definitively determine
            whether any coroutine won.
        - *exceptions*: list of exceptions returned by the coroutines. `len(exceptions)` is equal to the number of
            coroutines actually started, and the order is the same as in `coroutine_functions`. The winning coroutine's
            entry is `None`.
    """
    raise NotImplementedError

# asyncio.streams
# Include: StreamReader, StreamWriter, StreamReaderProtocol, open_connection, start_server, start_unix_server

_DEFAULT_LIMIT = 1 << 16

def protocol_itself_factory(protocol):
    """
    Uses to return the protocol itself when calling ``EventThread.open_connection``. This function is wrapped as a
    partial function when used.
    
    > Only available for `asyncio` extension.
    
    Parameters
    ----------
    protocol : ``StreamReaderProtocol``
        The protocol to return
    
    Returns
    -------
    protocol : ``StreamReaderProtocol``
    """
    return protocol


async def open_connection(host = None, port = None, *, loop = None, limit = _DEFAULT_LIMIT, **kwds):
    """
    A wrapper for create_connection() returning a (reader, writer) pair.
    
    The reader returned is a StreamReader instance; the writer is a StreamWriter instance.
    
    The parameters are all the usual parameters to create_connection() except protocol_factory; most common are
    positional host and port, with various optional keyword parameters following.
    
    Additional optional keyword parameters are loop (to set the event loop instance to use) and limit (to set the buffer
    limit passed to the StreamReader).
    
    (If you want to customize the StreamReader and/or StreamReaderProtocol classes, just copy the code -- there's
    really nothing special here except some convenience.)
    """
    if loop is None:
        loop = get_event_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    reader = StreamReader(limit = limit, loop = loop)
    protocol = StreamReaderProtocol(reader, loop = loop)
    transport, _ = await loop.create_connection(partial_func(protocol_itself_factory, protocol), host, port, **kwds)
    writer = StreamWriter(transport, protocol, reader, loop)
    return reader, writer


async def start_server(client_connected_cb, host = None, port = None, *, loop = None, limit = _DEFAULT_LIMIT, **kwds):
    """
    Start a socket server, call back for each client connected. The first parameter, `client_connected_cb`, takes two
    parameters: client_reader, client_writer. client_reader is a StreamReader object, while client_writer is a
    StreamWriter object. This parameter can either be a plain callback function or a coroutine; if it is a coroutine,
    it will be automatically converted into a Task.
    
    The rest of the parameters are all the usual parameters to loop.create_server() except protocol_factory; most common
    are positional host and port, with various optional keyword parameters following.  The return value is the same as
    loop.create_server().
    
    Additional optional keyword parameters are loop (to set the event loop instance to use) and limit (to set the buffer
    limit passed to the StreamReader).
    
    The return value is the same as loop.create_server(), i.e. a Server object which can be used to stop the service.
    """
    if loop is None:
        loop = get_event_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    def factory():
        reader = StreamReader(limit = limit, loop = loop)
        protocol = StreamReaderProtocol(reader, client_connected_cb, loop = loop)
        return protocol
    
    return await loop.create_server(factory, host, port, **kwds)


async def start_unix_server(client_connected_cb, path = None, *, loop = None, limit = _DEFAULT_LIMIT, **kwds):
    """
    Similar to `start_server` but works with UNIX Domain Sockets.
    """
    if loop is None:
        loop = get_event_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    def factory():
        reader = StreamReader(limit = limit, loop = loop)
        protocol = StreamReaderProtocol(reader, client_connected_cb, loop = loop)
        return protocol

    return await loop.create_unix_server(factory, path, **kwds)


class FlowControlMixin(Protocol):
    """
    Reusable flow control logic for StreamWriter.drain().
    
    This implements the protocol methods pause_writing(), resume_writing() and connection_lost().  If the subclass
    overrides these it must call the super methods.
    
    StreamWriter.drain() must wait for _drain_helper() coroutine.
    """
    def __init__(self, loop = None):
        if loop is None:
            loop = get_event_loop()
        
        self._loop = loop
        self._paused = False
        self._drain_waiter = None
        self._connection_lost = False
    
    def pause_writing(self):
        assert not self._paused
        self._paused = True
    
    def resume_writing(self):
        assert self._paused
        self._paused = False
        
        waiter = self._drain_waiter
        if waiter is not None:
            self._drain_waiter = None
            waiter.set_result_if_pending(None)
    
    def connection_lost(self, exception):
        self._connection_lost = True
        if not self._paused:
            return
        waiter = self._drain_waiter
        if waiter is None:
            return
        self._drain_waiter = None
        
        if exception is None:
            waiter.set_result_if_pending(None)
        else:
            waiter.set_exception_if_pending(exception)
    
    async def _drain_helper(self):
        if self._connection_lost:
            raise ConnectionResetError('Connection lost')
        if not self._paused:
            return
        waiter = self._drain_waiter
        assert waiter is None or waiter.cancelled()
        waiter = self._loop.create_future()
        self._drain_waiter = waiter
        await waiter
    
    def _get_close_waiter(self, stream):
        raise NotImplementedError

class StreamReaderProtocol(FlowControlMixin, Protocol):
    """
    Helper class to adapt between Protocol and StreamReader. (This is a helper class instead of making StreamReader
    itself a Protocol subclass, because the StreamReader has other potential uses, and to prevent the user of the
    StreamReader to accidentally call inappropriate methods of the protocol.)
    """
    def __init__(self, stream_reader, client_connected_cb = None, loop = None):
        FlowControlMixin.__init__(self, loop = loop)
        if stream_reader is not None:
            self._stream_reader_wr = WeakReferer(stream_reader)
        else:
            self._stream_reader_wr = None
        
        if client_connected_cb is not None:
            self._strong_reader = stream_reader
        
        self._reject_connection = False
        self._stream_writer = None
        self._transport = None
        self._client_connected_cb = client_connected_cb
        self._over_ssl = False
        self._closed = self._loop.create_future()
    
    @property
    def _stream_reader(self):
        if self._stream_reader_wr is None:
            return None
        return self._stream_reader_wr()
    
    def connection_made(self, transport):
        if self._reject_connection:
            transport.abort()
            return
        
        self._transport = transport
        reader = self._stream_reader
        if reader is not None:
            reader.set_transport(transport)
        
        self._over_ssl = (transport.get_extra_info('sslcontext') is not None)
        if self._client_connected_cb is not None:
            self._stream_writer = StreamWriter(transport, self, reader, self._loop)
            res = self._client_connected_cb(reader, self._stream_writer)
            if iscoroutine(res):
                self._loop.create_task(res)
            self._strong_reader = None
    
    def connection_lost(self, exception):
        reader = self._stream_reader
        if reader is not None:
            if exception is None:
                reader.feed_eof()
            else:
                reader.set_exception(exception)
        
        closed = self._closed
        if exception is None:
            closed.set_result_if_pending(None)
        else:
            closed.set_exception_if_pending(exception)
        
        FlowControlMixin.connection_lost(self, exception)
        self._stream_reader_wr = None
        self._stream_writer = None
        self._transport = None
    
    def data_received(self, data):
        reader = self._stream_reader
        if reader is not None:
            reader.feed_data(data)
    
    def eof_received(self):
        reader = self._stream_reader
        if reader is not None:
            reader.feed_eof()
        
        if self._over_ssl:
            return False
        return True
    
    def _get_close_waiter(self, stream):
        return self._closed
    
    def __del__(self):
        closed = self._closed
        if closed.done() and not closed.cancelled():
            closed.get_exception()


class StreamWriter:
    def __init__(self, transport, protocol, reader, loop):
        self._transport = transport
        self._protocol = protocol
        assert reader is None or isinstance(reader, StreamReader)
        self._reader = reader
        self._loop = loop
        self._complete_fut = self._loop.create_future()
        self._complete_fut.set_result(None)

    def __repr__(self):
        result = [
            '<',
            self.__class__.__name__,
            'transport = ',
            repr(self._transport)
        ]
        
        reader = self._reader
        if reader is not None:
            result.append(' reader = ')
            result.append(repr(reader))
        
        result.append('>')
        
        return ''.join(result)
    
    @property
    def transport(self):
        return self._transport

    def write(self, data):
        self._transport.write(data)

    def writelines(self, data):
        self._transport.writelines(data)

    def write_eof(self):
        return self._transport.write_eof()

    def can_write_eof(self):
        return self._transport.can_write_eof()

    def close(self):
        return self._transport.close()

    def is_closing(self):
        return self._transport.is_closing()

    async def wait_closed(self):
        await self._protocol._get_close_waiter(self)

    def get_extra_info(self, name, default = None):
        return self._transport.get_extra_info(name, default)

    async def drain(self):
        if self._reader is not None:
            exception = self._reader.exception()
            if exception is not None:
                raise exception
        
        if self._transport.is_closing():
            await skip_ready_cycle()
        
        await self._protocol._drain_helper()


    async def start_tls(
        self,
        sslcontext,
        *,
        server_hostname = None,
        ssl_handshake_timeout = None,
        ssl_shutdown_timeout = None
    ):
        """Upgrade an existing stream-based connection to TLS."""
        protocol = self._protocol
        server_side = protocol._client_connected_cb is not None
        
        await self.drain()
        
        new_transport = await self._loop.start_tls(
            self._transport,
            protocol,
            sslcontext,
            server_side = server_side,
            server_hostname = server_hostname,
            ssl_handshake_timeout = ssl_handshake_timeout,
            ssl_shutdown_timeout = ssl_shutdown_timeout,
        )
        
        self._transport = new_transport
        protocol._replace_transport(new_transport)


class StreamReader:
    def __init__(self, limit = _DEFAULT_LIMIT, loop = None):
        if limit <= 0:
            raise ValueError('Limit cannot be <= 0')

        self._limit = limit
        if loop is None:
            loop = get_event_loop()
        
        self._loop = loop
        self._buffer = bytearray()
        self._eof = False
        self._waiter = None
        self._exception = None
        self._transport = None
        self._paused = False
    
    def __repr__(self):
        result = [
            '<',
            self.__class__.__name__,
        ]
        
        buffer = self._buffer
        if buffer:
            result.append(' ')
            result.append(repr(len(buffer)))
            result.append(' bytes')
        
        if self._eof:
            result.append(' eof')
        
        limit = self._limit
        if limit != _DEFAULT_LIMIT:
            result.append(' limit = ')
            result.append(repr(limit))
        
        waiter = self._waiter
        if waiter is not None:
            result.append(' waiter = ')
            result.append(repr(waiter))
        
        exception = self._exception
        if exception is not None:
            result.append(' exception = ')
            result.append(repr(exception))
        
        
        transport = self._transport
        if transport is not None:
            result.append(' transport')
            result.append(repr(transport))
        
        if self._paused:
            result.append(' paused')
        
        result.append('>')
        
        return ''.join(result)
    
    def exception(self):
        return self._exception
    
    def set_exception(self, exception):
        self._exception = exception
        
        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            waiter.set_exception_if_pending(exception)
    
    def _wake_up_waiter(self):
        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            waiter.set_result_if_pending(None)
    
    def set_transport(self, transport):
        assert self._transport is None, 'Transport already set'
        self._transport = transport
    
    def _maybe_resume_transport(self):
        if self._paused and len(self._buffer) <= self._limit:
            self._paused = False
            self._transport.resume_reading()
    
    def feed_eof(self):
        self._eof = True
        self._wake_up_waiter()
    
    def at_eof(self):
        return self._eof and not self._buffer
    
    def feed_data(self, data):
        assert not self._eof, 'feed_data after feed_eof'
        
        if not data:
            return
        
        self._buffer.extend(data)
        self._wake_up_waiter()
        
        if (self._transport is not None) and (not self._paused) and (len(self._buffer) > (self._limit << 1)):
            try:
                self._transport.pause_reading()
            except NotImplementedError:
                self._transport = None
            else:
                self._paused = True
    
    async def _wait_for_data(self, func_name):
        if self._waiter is not None:
            raise RuntimeError(f'{func_name}() called while another coroutine is already waiting for incoming data')
        
        assert not self._eof, '_wait_for_data after EOF'
        
        if self._paused:
            self._paused = False
            self._transport.resume_reading()
        
        self._waiter = self._loop.create_future()
        try:
            await self._waiter
        finally:
            self._waiter = None
    
    async def readline(self):
        sep = b'\n'
        seplen = len(sep)
        try:
            line = await self.readuntil(sep)
        except IncompleteReadError as err:
            return err.partial
        except LimitOverrunError as err:
            if self._buffer.startswith(sep, err.consumed):
                del self._buffer[:err.consumed + seplen]
            else:
                self._buffer.clear()
            self._maybe_resume_transport()
            raise ValueError(err.args[0])
        return line
    
    async def readuntil(self, separator = b'\n'):
        seplen = len(separator)
        if seplen == 0:
            raise ValueError('Separator should be at least one-byte string')
        
        exception = self._exception
        if exception is not None:
            raise exception
        
        offunctionset = 0
        
        while True:
            buflen = len(self._buffer)
            
            if buflen - offunctionset >= seplen:
                isep = self._buffer.find(separator, offunctionset)
                
                if isep != -1:
                    break
                
                offunctionset = buflen + 1 - seplen
                if offunctionset > self._limit:
                    raise LimitOverrunError('Separator is not found, and chunk exceed the limit', offunctionset)
            
            if self._eof:
                chunk = bytes(self._buffer)
                self._buffer.clear()
                raise IncompleteReadError(chunk, None)
            
            await self._wait_for_data('readuntil')
        
        if isep > self._limit:
            raise LimitOverrunError('Separator is found, but chunk is longer than limit', isep)
        
        chunk = self._buffer[:isep + seplen]
        del self._buffer[:isep + seplen]
        self._maybe_resume_transport()
        return bytes(chunk)

    async def read(self, n=-1):
        exception = self._exception
        if exception is not None:
            raise exception
        
        if n == 0:
            return b''
        
        if n < 0:
            blocks = []
            while True:
                block = await self.read(self._limit)
                if not block:
                    break
                blocks.append(block)
            return b''.join(blocks)

        if not self._buffer and not self._eof:
            await self._wait_for_data('read')
        
        data = bytes(self._buffer[:n])
        del self._buffer[:n]
        
        self._maybe_resume_transport()
        return data

    async def readexactly(self, n):
        if n < 0:
            raise ValueError('readexactly size can not be less than zero')
        
        exception = self._exception
        if exception is not None:
            raise exception
        
        if n == 0:
            return b''
        
        while len(self._buffer) < n:
            if self._eof:
                incomplete = bytes(self._buffer)
                self._buffer.clear()
                raise IncompleteReadError(incomplete, n)

            await self._wait_for_data('readexactly')

        if len(self._buffer) == n:
            data = bytes(self._buffer)
            self._buffer.clear()
        else:
            data = bytes(self._buffer[:n])
            del self._buffer[:n]
        self._maybe_resume_transport()
        return data
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        val = await self.readline()
        if val == b'':
            raise StopAsyncIteration
        return val

# asyncio.subprocess
# Include: DEVNULL, PIPE, Process, STDOUT, create_subprocess_exec, create_subprocess_shell, Process

if IS_UNIX:
    async def create_subprocess_shell(
        cmd,
        stdin = None,
        stdout = None,
        stderr = None,
        loop = None,
        limit = _DEFAULT_LIMIT,
        **kwargs,
    ):
        if loop is None:
            loop = get_event_loop()
        else:
            warn(
                'The loop parameter is deprecated since Python 3.8 and scheduled for removal in Python 3.10.',
                DeprecationWarning,
                stacklevel = 2,
            )
        
        if stdin is None:
            stdin = PIPE
        
        if stdout is None:
            stdout = PIPE
        
        if stderr is None:
            stderr = PIPE
        
        return await loop.subprocess_shell(cmd, stdin = stdin, stdout = stdout, stderr = stderr, **kwargs)
    
    
    async def create_subprocess_exec(
        program,
        *args,
        stdin = None,
        stdout = None,
        stderr = None,
        loop = None,
        limit = _DEFAULT_LIMIT,
        **kwargs,
    ):
        
        if loop is None:
            loop = get_event_loop()
        else:
            warn(
                'The loop parameter is deprecated since Python 3.8 and scheduled for removal in Python 3.10.',
                DeprecationWarning,
                stacklevel = 2,
            )
            
        if stdin is None:
            stdin = PIPE
        
        if stdout is None:
            stdout = PIPE
        
        if stderr is None:
            stderr = PIPE
        
        return await loop.subprocess_exec(program, *args, stdin = stdin, stdout = stdout, stderr = stderr, **kwargs)

else:
    async def create_subprocess_shell(
        cmd,
        stdin = None,
        stdout = None,
        stderr = None,
        loop = None,
        limit = _DEFAULT_LIMIT,
        **kwargs,
    ):
        raise NotImplementedError
    
    async def create_subprocess_exec(
        program,
        *args,
        stdin = None,
        stdout = None,
        stderr = None,
        loop = None,
        limit = _DEFAULT_LIMIT,
        **kwargs,
    ):
        raise NotImplementedError

# Required by anyio
Process = AsyncProcess

# asyncio.tasks
# Include: Task, create_task, FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED, wait, wait_for, as_completed, sleep,
#    gather, shield, ensure_future, run_coroutine_threadsafe, current_task, all_tasks, _register_task,
#    _unregister_task, _enter_task, _leave_task, create_eager_task_factory, eager_task_factory

class TaskMeta(type):
    def __new__(cls, class_name, class_parents, class_attributes, ignore = False):
        if ignore:
            return type.__new__(cls, class_name, class_parents, class_attributes)
        
        class_attributes['__init__'] = cls._subclass_init
        class_attributes['__new__'] = cls._subclass_new
        
        return type.__new__(type, class_name, class_parents, class_attributes)
    
    # Required by dead.py
    def _subclass_init(self, *args, **kwargs):
        pass
    
    # Required by dead.py
    def _subclass_new(cls, *args, coro = None, loop = None, **kwargs):
        self = Task.__new__(cls, coro, loop = loop)
        self.__init__(*args, coro = coro, loop = loop, **kwargs)
        return self

class Task(HataTask, metaclass = TaskMeta, ignore = True):
    __slots__ = (
        '__weakref__', # Required by anyio
    )
    
    def __new__(cls, coroutine, loop = None, name = None, eager_start = False):
        """A coroutine wrapped in a Future."""
        if not iscoroutine(coroutine):
            raise TypeError(f'a coroutine was expected, got {coroutine!r}')
        
        if loop is None:
            loop = get_event_loop()
        
        return HataTask.__new__(cls, loop, coroutine)
    
    # Required by aiohttp 3.6
    def current_task(loop = None):
        if loop is None:
            loop = get_event_loop()
        else:
            if not isinstance(loop, EventThread):
                raise TypeError(
                    f'`loop` can be `{EventThread.__name__}`, got {loop.__class__.__name__}; {loop!r}.'
                )
        
        task = loop.current_task
        if (task is not None):
            task = TaskWrapper(task)
        
        return task
    
    # Required by anyio
    def get_coro(self):
        return self._coroutine
    
    
    def cancelling(self):
        """
        Return the count of the task's cancellation requests.

        This count is incremented when .cancel() is called
        and may be decremented using .uncancel().
        """
        return 1 if self.is_cancelling() else 0
    
    
    def uncancel(self):
        """
        Decrement the task's count of cancellation requests.

        This should be called by the party that called `cancel()` on the task
        beforehand.

        Returns the remaining number of cancellation requests.
        """
        return 0


def create_task(coroutine, *, name = None):
    """
    Schedule the execution of a coroutine object in a spawn task.
    
    Return a Task object.
    """
    loop = get_running_loop()
    return Task(loop, coroutine)


FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'


async def wait(futures, *, loop = None, timeout = None, return_when = ALL_COMPLETED):
    """
    Wait for the Futures and coroutines given by functions to complete.
    
    The sequence futures must not be empty.
    
    Coroutines will be wrapped in Tasks.
    
    Returns two sets of Future: (done, pending).
    
    Usage:
        ```py
        done, pending = await asyncio.wait(functions)
        ```
    
    Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs are returned in the second
    set.
    """
    if isfuture(futures) or iscoroutine(futures):
        raise TypeError(f'expect a list of futures, not {type(futures).__name__}')
    
    if not futures:
        raise ValueError('Set of coroutines/Futures is empty.')
    
    if return_when not in (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        raise ValueError(f'Invalid return_when value: {return_when}')
    
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    futures = {*futures}
    
    if any(iscoroutine(future) for future in futures):
        warn(
            (
                'The explicit passing of coroutine objects to asyncio.wait() is deprecated since Python 3.8, '
                'and scheduled for removal in Python 3.11.'
            ),
            DeprecationWarning,
            stacklevel = 2,
        )
    
    task_group = TaskGroup(
        loop,
        (loop.ensure_future(future) for future in futures),
    )
    
    if return_when == FIRST_COMPLETED:
        waiter_future = task_group.wait_first()
    elif return_when == FIRST_EXCEPTION:
        waiter_future = task_group.wait_first()
    else:
        waiter_future = task_group.wait_all()
    
    if timeout is not None:
        waiter_future.apply_timeout(timeout)
    
    try: 
        await waiter_future
    except TimeoutError:
        pass
    
    return task_group.done, task_group.pending


async def wait_for(future, timeout, *, loop = None):
    """
    Wait for the single Future or coroutine to complete, with timeout.
    
    Coroutine will be wrapped in Task.
    
    Returns result of the Future or coroutine. When a timeout occurs, it cancels the task and raises TimeoutError. To
    avoid the task cancellation, wrap it in shield().
    
    If the wait is cancelled, the task is also cancelled.
    
    This function is a coroutine.
    """
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    if timeout is None:
        return await future
    
    future = loop.ensure_future(future)
    if timeout <= 0.0:
        if future.done():
            return future.get_result()
    
    future.apply_timeout(timeout)
    return await future


async def _as_completed_task(task_group, waiter_futures, timeout_future):
    index = 0
    limit = len(waiter_futures)
    
    async for future in task_group.exhaust():
        if future is timeout_future:
            future.cancel()
            task_group.cancel_pending()
            
            while True:
                waiter_futures[index].set_exception_if_pending(TimeoutError())
                
                index += 1
                if index == limit:
                    break
                
                continue
            return
        
        try:
            result = future.get_result()
        except BaseException as err:
            waiter_futures[index].set_exception_if_pending(err)
        else:
            waiter_futures[index].set_result_if_pending(result)
        
        index += 1
        if index == limit:
            if (timeout_future is not None):
                timeout_future.cancel()
            
            return
        
        continue


def as_completed(futures, *, loop = None, timeout = None):
    """
    Return an iterator whose values are coroutines.
    
    When waiting for the yielded coroutines you'll get the results (or exceptions!) of the original Futures (or
    coroutines), in the order in which and as soon as they complete.
    
    This differs from PEP 3148; the proper way to use this is:
        ```py
        for function in as_completed(functions):
            result = await f  # The 'await' may raise.
            # Use result.
        ```
    
    If a timeout is specified, the 'await' will raise TimeoutError when the timeout occurs before all Futures are done.
    
    Note: The futures 'f' are not necessarily members of functions.
    """
    if isfuture(futures) or iscoroutine(futures):
        raise TypeError(
            f'expect a list of futures, not {type(futures).__name__}.'
        )
    
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    tasks = {loop.ensure_future(coroutine_or_future) for coroutine_or_future in {*futures}}
    
    if not tasks:
        return []
    
    waiter_futures = [HataFuture(loop) for _ in range(len(tasks))]
    waited_futures = waiter_futures[::-1]
    
    if timeout is None:
        timeout_future = None
    else:
        timeout_future = HataFuture(loop)
        timeout_future.apply_timeout(timeout)
        tasks.add(timeout_future)
    
    task_group = TaskGroup(loop, tasks)
    Task(_as_completed_task(task_group, waiter_futures, timeout_future), loop)
    
    async def wait_for_one():
        return await waited_futures.pop()
    
    for _ in range(len(waiter_futures)):
        yield wait_for_one()


async def sleep(delay, result = None, *, loop = None):
    """Coroutine that completes after a given time (in seconds)."""
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    if delay <= 0.0:
        await skip_ready_cycle()
        return result
    
    await scarletio_sleep(delay, loop)
    return result


def ensure_future(coroutine_or_future, *, loop = None):
    """
    Wrap a coroutine or an awaitable in a future.
    
    If the parameter is a Future, it is returned directly.
    """
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    return loop.ensure_future(coroutine_or_future)

class _gatherer_done_callback_return_exceptions:
    __slots__ = ('task_group', 'future', )
    
    def __init__(self, task_group, future):
        self.task_group = task_group
        self.future = future
    
    def __call__(self, gatherer):
        self.task_group.cancel_pending()
        
        future = self.future
        if future.done():
            return
        
        gatherer.cancel()
        results = []
        
        try:
            gatherer.get_result()
        except BaseException as err:
            future.set_exception_if_pending(err)
            return
        
        for done_future in self.task_group.done:
            try:
                result = done_future.get_result()
            except BaseException as err:
                result = err
            
            results.append(result)
        
        future.set_result(results)


class _gatherer_done_callback_raise:
    __slots__ = ('task_group', 'future', )
    
    def __init__(self, task_group, future):
        self.task_group = task_group
        self.future = future
    
    
    def __call__(self, gatherer):
        future = self.future
        if future.done():
            return
        
        try:
            gatherer.get_result()
        except BaseException as err:
            future.set_exception_if_pending(err)
            return
        
        results = []
        
        iterator = iter(self.task_group.done)
        for done_future in iterator:
            try:
                result = done_future.get_result()
            except BaseException as err:
                exception = err
                
                # Silence the rest of the futures, so we do not get not retrieved warning.
                for future_to_silence in iterator:
                    future_to_silence.silence()
                
                for future_to_silence in self.task_group.pending:
                    future_to_silence.silence()
                    
                break
            else:
                results.append(result)
        else:
            # should not happen
            exception = None
        
        if exception is None:
            future.set_result(results)
        else:
            future.set_exception(exception)


class _gatherer_cancel_callback:
    __slots__ = ('task_group', 'gatherer',)
    
    def __init__(self, task_group, gatherer):
        self.task_group = task_group
        self.gatherer = gatherer
    
    def __call__(self, future):
        gatherer = self.gatherer
        if gatherer.done():
            return
        
        if not future.cancelled():
            return
        
        self.task_group.cancel_all()
        gatherer.cancel()

        
def gather(*coroutines_or_futures, loop = None, return_exceptions = False):
    """
    Return a future aggregating results from the given coroutines/futures. Coroutines will be wrapped in a future and
    scheduled in the event loop. They will not necessarily be scheduled in the same order as passed in.
    
    All futures must share the same event loop. If all the tasks are done successfully, the returned future's result
    is the list of results (in the order of the original sequence, not necessarily the order of results arrival). If
    *return_exceptions* is True, exceptions in the tasks are treated the same as successful results, and gathered in
    the result list; otherwise, the first raised exception will be immediately propagated to the returned future.
    
    Cancellation: if the outer Future is cancelled, all children (that have not completed yet) are also cancelled.
    If any child is cancelled, this is treated as if it raised CancelledError -- the outer Future is *not* cancelled
    in this case. (This is to prevent the cancellation of one child to cause other children to be cancelled.)
    
    If *return_exceptions* is False, cancelling gather() after it has been marked done won't cancel any submitted
    awaitables. For instance, gather can be marked done after propagating an exception to the caller, therefore,
    calling ``gather.cancel()`` after catching an exception (raised by one of the awaitables) from gather won't cancel
    any other awaitables.
    """
    # Remove duplicates. This is not an asyncio behavior, but should be.
    coroutines_or_futures = {*coroutines_or_futures}
    
    if loop is None:
        detected_loops = None
        for future in coroutines_or_futures:
            if isinstance(future, HataFuture):
                if detected_loops is None:
                    detected_loops = set()
                detected_loops.add(future._loop)
        
        if detected_loops is None:
            loop = get_running_loop()
        
        else:
            if len(detected_loops) > 1:
                raise ValueError(
                    'The given futures are bound to multiple event loops; {detected_loops!r}.'
                )
            
            loop = detected_loops.pop()
            detected_loops = None
    
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )
    
    
    future = HataFuture(loop)
    
    if not coroutines_or_futures:
        future.set_result([])
        return future
    
    tasks = []
    for coroutine in coroutines_or_futures:
        task = loop.ensure_future(coroutine)
        tasks.append(task)
    
    task_group = TaskGroup(loop, tasks)
    
    if return_exceptions:
        waiter = task_group.wait_all()
        gatherer_done_callback_type = _gatherer_done_callback_return_exceptions
    else:
        waiter = task_group.wait_exception_or_cancellation()
        gatherer_done_callback_type = _gatherer_done_callback_raise
    
    future.add_done_callback(_gatherer_cancel_callback(task_group, waiter))
    waiter.add_done_callback(gatherer_done_callback_type(task_group, future))
    return future


def shield(arg, *, loop = None):
    """
    Wait for a future, shielding it from cancellation.
    
    The statement
        ```py
        res = await shield(something())
        ```
    
    is exactly equivalent to the statement
        ```py
        res = await something()
        ```
        
    *except* that if the coroutine containing it is cancelled, the task running in something() is not cancelled. From
    the POV of something(), the cancellation did not happen. But its caller is still cancelled, so the yield-from
    expression still raises CancelledError. Note: If something() is cancelled by other means this will still cancel
    shield().
    
    If you want to completely ignore cancellation (not recommended) you can combine shield() with a try/except clause,
    as follows:
        ```py
        try:
            res = await shield(something())
        except CancelledError:
            res = None
        ```
    """
    if loop is None:
        loop = get_running_loop()
    else:
        warn(
            'The loop parameter is deprecated since Python 3.8, and scheduled for removal in Python 3.10.',
            DeprecationWarning,
            stacklevel = 2,
        )

    return scarletio_shield(arg, loop)


def run_coroutine_threadsafe(coroutine, loop):
    """
    Submit a coroutine object to a given event loop.
    
    Return a concurrent.futures.Future to access the result.
    """
    return loop.create_task_thread_safe(coroutine)

def _register_task(task):
    """Register a new task in asyncio as executed by loop."""

def _enter_task(loop, task):
    pass


def _leave_task(loop, task):
    pass

def _unregister_task(task):
    """Unregister a task."""

def all_tasks(loop = None):
    """Return a set of all tasks for the loop."""
    # We could do this, but we will not.
    return {}


TASK_WRAPPER_CACHE = WeakValueDictionary()


def current_task(loop = None):
    """Return a currently executed task."""
    if loop is None:
        loop = get_running_loop()
    
    task = loop.current_task
    if task is None:
        return None
    
    try:
        task_wrapper = TASK_WRAPPER_CACHE[task]
    except KeyError:
        task_wrapper = TaskWrapper(task)
        TASK_WRAPPER_CACHE[task] = task_wrapper
    
    return task_wrapper


class TaskWrapperCallback:
    __slots__ = ('task_wrapper_additional_attributes', )
    
    def __new__(cls, task_wrapper_additional_attributes):
        self = object.__new__(cls)
        self.task_wrapper_additional_attributes = task_wrapper_additional_attributes
        return self
    
    def __call__(self, task):
        pass


class TaskWrapper:
    __slots__ = ('__weakref__', '_additional_attributes', '_task', )
    
    def __new__(cls, task):
        for callback in task._callbacks:
            if isinstance(callback, TaskWrapperCallback):
                additional_attributes = callback.task_wrapper_additional_attributes
                break
        else:
            additional_attributes = None
        
        self = object.__new__(cls)
        object.__setattr__(self, '_task', task)
        object.__setattr__(self, '_additional_attributes', additional_attributes)
        return self
    
    
    def __getattr__(self, attribute_name):
        additional_attributes = object.__getattribute__(self, '_additional_attributes')
        if (additional_attributes is not None):
            try:
                return additional_attributes[attribute_name]
            except KeyError:
                pass
        
        return getattr(object.__getattribute__(self, '_task'), attribute_name)
    
    
    def __setattr__(self, attribute_name, attribute_value):
        task = object.__getattribute__(self, '_task')
        
        descriptor = getattr(type(task), attribute_name, None)
        if (descriptor is not None):
            setter = getattr(descriptor, '__set__', None)
            if (setter is not None):
                setter(descriptor, task, type(task))
                return
        
        additional_attributes = object.__getattribute__(self, '_additional_attributes')
        if (additional_attributes is None):
            additional_attributes = {}
            object.__setattr__(self, '_additional_attributes', additional_attributes)
            task.add_done_callback(TaskWrapperCallback(additional_attributes))
        
        additional_attributes[attribute_name] = attribute_value
    
    
    def __repr__(self):
        return (
            f'<{self.__class__.__name__} '
                f'task={object.__getattribute__(self, "_task")!r}, '
                f'additional_attributes={object.__getattribute__(self, "_additional_attributes")!r}'
            f'>'
        )
    
    
    def __iter__(self):
        return object.__getattribute__(self, '_task').__iter__()
    
    
    def __await__(self):
        return object.__getattribute__(self, '_task').__await__()
    
    
    def __instancecheck__(cls, instance):
        return isinstance(instance, HataTask) or isinstance(instance, cls)
    
    
    def __subclasscheck__(cls, klass):
        return issubclass(klass, HataTask) or (klass is cls)
    
    
    def __hash__(self):
        """Returns the task wrapper's representation."""
        return hash(self._task)
    
    
    def __eq__(self, other):
        """Returns whether the two tasks are equal."""
        if isinstance(other, type(self)):
            other_task = other._task
        
        elif isinstance(other, HataTask):
            other_task = other
        
        else:
            return NotImplemented
        
        return self._task == other_task


def create_eager_task_factory(custom_task_constructor):
    """
    Create a function suitable for use as a task factory on an event-loop.
    
    Example usage:

        loop.set_task_factory(
            asyncio.create_eager_task_factory(my_task_constructor))
    
    Now, tasks created will be started immediately (rather than being first
    scheduled to an event loop). The constructor argument can be any callable
    that returns a Task-compatible object and has a signature compatible
    with `Task.__init__`; it must have the `eager_start` keyword argument.

    Most applications will use `Task` for `custom_task_constructor` and in
    this case there's no need to call `create_eager_task_factory()`
    directly. Instead the  global `eager_task_factory` instance can be
    used. E.g. `loop.set_task_factory(asyncio.eager_task_factory)`.
    """
    def factory(loop, coro, *, name = None, context = None):
        return custom_task_constructor(coro, loop = loop, name = name, context = context, eager_start = True)
    return factory


eager_task_factory = create_eager_task_factory(Task)


# asyncio.threads
# Include: to_thread

async def to_thread(func, *args, **kwargs):
    """
    Asynchronously run function *func* in a separate thread.
    
    Any *args and **kwargs supplied for this function are directly passed to *func*. Also, the current
    `contextvars.Context` is propagated, allowing context variables from the main thread to be accessed in the separate
    thread.
    
    Return a coroutine that can be awaited to get the eventual result of *func*.
    """
    loop = get_running_loop()
    return await loop.run_in_executor(alchemy_incendiary(func, args, kwargs))

# asyncio.transports
# Include: BaseTransport, ReadTransport, WriteTransport, Transport, DatagramTransport, SubprocessTransport

class BaseTransport:
    __slots__ = ('_extra',)

    def __init__(self, extra = None):
        if extra is None:
            extra = {}
        self._extra = extra

    def get_extra_info(self, name, default = None):
        return self._extra.get(name, default)

    def is_closing(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def set_protocol(self, protocol):
        raise NotImplementedError

    def get_protocol(self):
        raise NotImplementedError


class ReadTransport(BaseTransport):
    __slots__ = ()

    def is_reading(self):
        raise NotImplementedError

    def pause_reading(self):
        raise NotImplementedError

    def resume_reading(self):
        raise NotImplementedError


class WriteTransport(BaseTransport):
    __slots__ = ()

    def set_write_buffer_limits(self, high = None, low = None):
        raise NotImplementedError

    def get_write_buffer_size(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

    def writelines(self, list_of_data):
        data = b''.join(list_of_data)
        self.write(data)

    def write_eof(self):
        raise NotImplementedError

    def can_write_eof(self):
        raise NotImplementedError

    def abort(self):
        raise NotImplementedError


class Transport(ReadTransport, WriteTransport):
    """Interface representing a bidirectional transport.
    
    There may be several implementations, but typically, the user does not implement new transports; rather, the
    platform provides some useful transports that are implemented using the platform's best practices.
    
    The user never instantiates a transport directly; they call a utility function, passing it a protocol factory and
    other information necessary to create the transport and protocol.  (E.g. EventLoop.create_connection() or
    EventLoop.create_server().)
    
    The utility function will asynchronously create a transport and a protocol and hook them up by calling the
    protocol's connection_made() method, passing it the transport.
    
    The implementation here raises NotImplemented for every method except writelines(), which calls write() in a loop.
    """

    __slots__ = ()


class DatagramTransport(BaseTransport):
    __slots__ = ()

    def sendto(self, data, addr = None):
        raise NotImplementedError

    def abort(self):
        raise NotImplementedError


class SubprocessTransport(BaseTransport):

    __slots__ = ()

    def get_pid(self):
        raise NotImplementedError

    def get_returncode(self):
        raise NotImplementedError

    def get_pipe_transport(self, fd):
        raise NotImplementedError

    def send_signal(self, signal):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError


class _FlowControlMixin(Transport):
    """
    All the logic for (write) flow control in a mix-in base class.
    
    The subclass must implement get_write_buffer_size(). It must call_maybe_pause_protocol() whenever the write buffer
    size increases, and _maybe_resume_protocol() whenever it decreases.  It may also override set_write_buffer_limits()
    (e.g. to specify different defaults).
    
    The subclass constructor must call super().__init__(extra).  This will call set_write_buffer_limits().
    
    The user may call set_write_buffer_limits() and get_write_buffer_size(), and their protocol's pause_writing() and
    resume_writing() may be called.
    """

    __slots__ = ('_loop', '_protocol_paused', '_high_water', '_low_water')
    
    def __init__(self, extra = None, loop = None):
        Transport.__init__(extra)
        assert loop is not None
        self._loop = loop
        self._protocol_paused = False
        self._set_write_buffer_limits()

    def _maybe_pause_protocol(self):
        size = self.get_write_buffer_size()
        if size <= self._high_water:
            return
        if not self._protocol_paused:
            self._protocol_paused = True
            try:
                self._protocol.pause_writing()
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as err:
                write_exception_async(err, 'protocol.pause_writing() failed\n', loop = self)
    

    def _maybe_resume_protocol(self):
        if self._protocol_paused and (self.get_write_buffer_size() <= self._low_water):
            self._protocol_paused = False
            try:
                self._protocol.resume_writing()
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as err:
                write_exception_async(err, 'protocol.resume_writing() failed\n', loop = self)
    
    def get_write_buffer_limits(self):
        return (self._low_water, self._high_water)
    
    def _set_write_buffer_limits(self, high = None, low = None):
        if high is None:
            if low is None:
                high = 64 * 1024
            else:
                high = 4 * low
        if low is None:
            low = high >>2

        if not high >= low >= 0:
            raise ValueError(f'high ({high!r}) must be >= low ({low!r}) must be >= 0')

        self._high_water = high
        self._low_water = low

    def set_write_buffer_limits(self, high = None, low = None):
        self._set_write_buffer_limits(high = high, low = low)
        self._maybe_pause_protocol()

    def get_write_buffer_size(self):
        raise NotImplementedError

# asyncio.trsock
# *none*

# asyncio.unix_events
# Include: SelectorEventLoop, AbstractChildWatcher, SafeChildWatcher, FastChildWatcher, PidfdChildWatcher,
#    MultiLoopChildWatcher, ThreadedChildWatcher, DefaultEventLoopPolicy

class AbstractChildWatcher:
    """
    Abstract base class for monitoring child processes.
    
    Objects derived from this class monitor a collection of subprocesses and report their termination or interruption
    by a signal.
    
    New callbacks are registered with .add_child_handler(). Starting a new process must be done within a 'with' block
    to allow the watcher to suspend its activity until the new process if fully registered (this is needed to prevent a
    race condition in some implementations).
    
    Example:
        ```py
        with watcher:
            proc = subprocess.Popen("sleep 1")
            watcher.add_child_handler(proc.pid, callback)
        ```
    
    Notes:
        Implementations of this class must be thread-safe. Since child watcher objects may catch the SIGCHLD signal
        and call waitpid(-1), there should be only one active object per process.
    """
    def __new__(cls):
        raise NotImplementedError


class PidfdChildWatcher(AbstractChildWatcher):
    """
    Child watcher implementation using Linux's pid file descriptors.
    
    This child watcher polls process file descriptors (pidfds) to await child process termination. In some respects,
    PidfdChildWatcher is a "Goldilocks" child watcher implementation. It doesn't require signals or threads, doesn't
    interfere with any processes launched outside the event loop, and scales linearly with the number of subprocesses
    launched by the event loop. The main disadvantage is that pidfds are specific to Linux, and only work on recent
    (5.3+) kernels.
    """

class BaseChildWatcher(AbstractChildWatcher):
    pass


class SafeChildWatcher(BaseChildWatcher):
    """
    'Safe' child watcher implementation.
    
    This implementation avoids disrupting other code spawning processes by polling explicitly each process in the
    SIGCHLD handler instead of calling os.waitpid(-1).
    
    This is a safe solution but it has a significant overhead when handling a big number of children (O(n) each time
    SIGCHLD is raised)
    """

class FastChildWatcher(BaseChildWatcher):
    """
    'Fast' child watcher implementation.
    
    This implementation reaps every terminated processes by calling os.waitpid(-1) directly, possibly breaking other
    code spawning processes and waiting for their termination.
    
    There is no noticeable overhead when handling a big number of children (O(1) each time a child terminates).
    """

class MultiLoopChildWatcher(AbstractChildWatcher):
    """
    A watcher that doesn't require running loop in the main thread.
    
    This implementation registers a SIGCHLD signal handler on instantiation (which may conflict with other code that
    install own handler for this signal).
    
    The solution is safe but it has a significant overhead when handling a big number of processes (*O(n)* each time a
    SIGCHLD is received).
    """

class ThreadedChildWatcher(AbstractChildWatcher):
    """
    Threaded child watcher implementation.
    
    The watcher uses a thread per process for waiting for the process finish.
    
    It doesn't require subscription on POSIX signal but a thread creation is not free.
    
    The watcher has O(1) complexity, its performance doesn't depend on amount of spawn processes.
    """

class DefaultEventLoopPolicy(AbstractEventLoopPolicy):
    pass

SelectorEventLoop = EventThread

# asyncio.windows_events
# include: SelectorEventLoop, ProactorEventLoop, IocpProactor, DefaultEventLoopPolicy, WindowsSelectorEventLoopPolicy,
#     WindowsProactorEventLoopPolicy

# SelectorEventLoop included already
ProactorEventLoop = EventThread

class IocpProactor:
    """Proactor implementation using IOCP."""

    def __new__(cls, concurrency = 0xffffffff):
        raise NotImplementedError

# DefaultEventLoopPolicy included already

class WindowsSelectorEventLoopPolicy(AbstractEventLoopPolicy):
    pass

class WindowsProactorEventLoopPolicy(AbstractEventLoopPolicy):
    pass

# asyncio.windows_utils
# Include : pipe, Popen, PIPE, PipeHandle

BUFSIZE = 8192

def pipe(*, duplex = False, overlapped = (True, True), bufunctionsize = BUFSIZE):
    raise NotImplementedError

class PipeHandle:
    """
    Wrapper for an overlapped pipe handle which is vaguely file-object like.
    
    The IOCP event loop can use these instead of socket objects.
    """
    def __new__(cls, handle):
        raise NotImplementedError

class Popen:
    """
    Replacement for subprocess.Popen using overlapped pipe handles.
    
    The stdin, stdout, stderr are None or instances of PipeHandle.
    """
    def __new__(cls, args, stdin = None, stdout = None, stderr = None, **kwds):
        raise NotImplementedError

# asyncio.timeouts
# Includes: Timeout, timeout, timeout_at


class _TimeoutState(Enum):
    CREATED = "created"
    ENTERED = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    EXITED = "finished"


class Timeout:
    """
    Asynchronous context manager for cancelling overdue coroutines.

    Use `timeout()` or `timeout_at()` rather than instantiating this class directly.
    """

    def __init__(self, when):
        """
        Schedule a timeout that will trigger at a given loop time.

        - If `when` is `None`, the timeout will never trigger.
        - If `when < loop.time()`, the timeout will trigger on the next
          iteration of the event loop.
        """
        self._state = _TimeoutState.CREATED
        self._timeout_handler = None
        self._task = None
        self._when = when


    def when(self):
        """Return the current deadline."""
        return self._when


    def reschedule(self, when):
        """Reschedule the timeout."""
        if self._state is not _TimeoutState.ENTERED:
            if self._state is _TimeoutState.CREATED:
                raise RuntimeError("Timeout has not been entered.")
            raise RuntimeError(f"Cannot change state of {self._state.value} {type(self).__name__}.")

        self._when = when

        if self._timeout_handler is not None:
            self._timeout_handler.cancel()

        if when is None:
            self._timeout_handler = None
        else:
            loop = get_event_loop()
            if when <= LOOP_TIME():
                self._timeout_handler = loop.call_soon(self._on_timeout)
            else:
                self._timeout_handler = loop.call_at(when, self._on_timeout)


    def expired(self):
        """Is timeout expired during execution?"""
        return self._state in (_TimeoutState.EXPIRING, _TimeoutState.EXPIRED)


    def __repr__(self):
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' [')
        repr_parts.append(self._state.value)
        repr_parts.append(']')
        
        if self._state is _TimeoutState.ENTERED:
            when = round(self._when, 3) if self._when is not None else None
            repr_parts.append(' when = ')
            repr_parts.append(repr(when))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


    async def __aenter__(self):
        if self._state is not _TimeoutState.CREATED:
            raise RuntimeError("Timeout has already been entered.")
        
        loop = get_event_loop()
        task = loop.current_task
        if task is None:
            raise RuntimeError("Timeout should be used inside a task.")
        
        self._state = _TimeoutState.ENTERED
        self._task = task
        self.reschedule(self._when)
        return self


    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        assert self._state in (_TimeoutState.ENTERED, _TimeoutState.EXPIRING)

        if self._timeout_handler is not None:
            self._timeout_handler.cancel()
            self._timeout_handler = None

        if self._state is _TimeoutState.EXPIRING:
            self._state = _TimeoutState.EXPIRED
            
            if isinstance(exception_type, CancelledError):
                # Since there are no new cancel requests, we're handling this.
                raise TimeoutError from exception_value
        
        elif self._state is _TimeoutState.ENTERED:
            self._state = _TimeoutState.EXITED

        return False

    def _on_timeout(self):
        assert self._state is _TimeoutState.ENTERED
        self._task.cancel()
        self._state = _TimeoutState.EXPIRING
        # drop the reference early
        self._timeout_handler = None


def timeout(delay):
    """
    Timeout async context manager.

    Useful in cases when you want to apply timeout logic around block
    of code or in cases when asyncio.wait_for is not suitable. For example:

    >>> async with asyncio.timeout(10):  # 10 seconds timeout
    ...     await long_running_task()


    delay - value in seconds or None to disable timeout logic

    long_running_task() is interrupted by raising asyncio.CancelledError,
    the top-most affected timeout() context manager converts CancelledError
    into TimeoutError.
    """
    return Timeout(LOOP_TIME() + delay if delay is not None else None)


def timeout_at(when):
    """
    Schedule the timeout at absolute time.

    Like timeout() but argument gives absolute time in the same clock system
    as loop.time().

    Please note: it is not POSIX time but a time with
    undefined starting base, e.g. the time of the system power on.

    >>> async with asyncio.timeout_at(loop.time() + 10):
    ...     await long_running_task()


    when - a deadline when timeout occurs or None to disable timeout logic

    long_running_task() is interrupted by raising asyncio.CancelledError,
    the top-most affected timeout() context manager converts CancelledError
    into TimeoutError.
    """
    return Timeout(when)
