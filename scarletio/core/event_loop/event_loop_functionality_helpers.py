__all__ = ()

import socket as module_socket
import sys
from threading import current_thread
from types import MethodType

from ...utils import DOCS_ENABLED, WeakReferer, docs_property, include

from ..traps import Future, Task, TaskGroup


EventThread = include('EventThread')

_HAS_IPv6 = hasattr(module_socket, 'AF_INET6')

def _ip_address_info(host, port, family, type_, protocol):
    """
    Gets the address info for the given parameters.
    
    Parameters
    ----------
    host : `str`, `bytes`
        The host ip address.
    port : `int`
        The host port.
    family : `AddressFamily`, `int`
        Address family.
    type_ : `SocketKind`, `int`
        Socket type.
    protocol : `int`
        Protocol type.
    
    Returns
    -------
    result : `None`, `tuple` ((`AddressFamily`, `int`), (`SocketKind`, `int`), `int`, `str`, `tuple` (`str, `int`))
        If everything is correct, returns a `tuple` of 5 elements:
        - `family` : Address family.
        - `type_` : Socket type.
        - `protocol` : Protocol type.
        - `canonical_name` : Represents the canonical name of the host. (Always empty string.)
        - `socket_address` : Socket address containing the `host` and the `port`.
    """
    # Try to skip get_address_info if `host` is already an IP. Users might have handled name resolution in their own
    # code and pass in resolved IP-s.
    if not hasattr(module_socket, 'inet_pton'):
        return
    
    if protocol not in (0, module_socket.IPPROTO_TCP, module_socket.IPPROTO_UDP) or (host is None):
        return
    
    if type_ == module_socket.SOCK_STREAM:
        protocol = module_socket.IPPROTO_TCP
    elif type_ == module_socket.SOCK_DGRAM:
        protocol = module_socket.IPPROTO_UDP
    else:
        return
    
    if port is None:
        port = 0
    elif type(port) is int:
        # Has the most chance.
        pass
    elif isinstance(port, bytes) and port == b'':
        port = 0
    elif isinstance(port, str) and port == '':
        port = 0
    else:
        # If port's a service name like "http", don't skip get_address_info.
        try:
            port = int(port)
        except (TypeError, ValueError):
            return
    
    if family == module_socket.AF_UNSPEC:
        address_families = [module_socket.AF_INET]
        if _HAS_IPv6:
            address_families.append(module_socket.AF_INET6)
    else:
        address_families = [family]
    
    if isinstance(host, bytes):
        host = host.decode('idna')
    
    if '%' in host:
        return
    
    for family in address_families:
        try:
            module_socket.inet_pton(family, host)
            # The host has already been resolved.
        except OSError:
            pass
        else:
            return family, type_, protocol,'', (host, port)
    
    # `host` is not an IP address.
    return None


def _is_datagram_socket(socket):
    """
    Returns whether the given socket is datagram socket.
    
    Parameters
    ----------
    socket : `socket.socket`
        The socket to check.
    
    Returns
    -------
    is_datagram_socket : `bool`
    """
    return (socket.type & module_socket.SOCK_DGRAM) == module_socket.SOCK_DGRAM


def _is_stream_socket(socket):
    """
    Returns whether the given socket is stream socket.
    
    Parameters
    ----------
    socket : `socket.socket`
        The socket to check.
    
    Returns
    -------
    is_stream_socket : `bool`
    """
    return (socket.type & module_socket.SOCK_STREAM) == module_socket.SOCK_STREAM


def _set_reuse_port(socket):
    """
    Tells to the kernel to allow this endpoint to be bound to the same port as an other existing endpoint already
    might be bound to.
    
    Parameters
    ----------
    socket : `socket.socket`.
        The socket to set reuse to.
    
    Raises
    ------
    ValueError
        `reuse_port` is not supported by socket module.
    """
    if not hasattr(module_socket, 'SO_REUSEPORT'):
        raise ValueError(
            '`reuse_port` not supported by socket module.'
        )
    else:
        try:
            socket.setsockopt(module_socket.SOL_SOCKET, module_socket.SO_REUSEPORT, 1)
        except OSError:
            raise ValueError(
                '`reuse_port` not supported by socket module, `SO_REUSEPORT` defined but not implemented.'
            )

_OLD_ASYNC_GENERATOR_HOOKS = sys.get_asyncgen_hooks()

def _async_generator_first_iteration_hook(async_generator):
    """
    Adds asynchronous generators to their respective event loop. These async gens are shut down, when the loop is
    stopped.
    
    Parameters
    ----------
    async_generator : `async_generator`
    """
    loop = current_thread()
    if isinstance(loop, EventThread):
        if loop._async_generators_shutdown_called:
            return
        
        loop._async_generators.add(async_generator)
        return
    
    first_iteration = _OLD_ASYNC_GENERATOR_HOOKS.firstiter
    if first_iteration is not None:
        first_iteration(async_generator)


def _async_generator_finalizer_hook(async_generator):
    """
    Removes asynchronous generator from their respective event loop.
    
    Parameters
    ----------
    async_generator : `async_generator`
    """
    loop = current_thread()
    if isinstance(loop, EventThread):
        loop._async_generators.discard(async_generator)
        if not loop.running:
            return
            
        Task(loop, async_generator.aclose())
        loop.wake_up()
        return
    
    finalizer = _OLD_ASYNC_GENERATOR_HOOKS.finalizer
    if finalizer is not None:
        finalizer(async_generator)

sys.set_asyncgen_hooks(firstiter = _async_generator_first_iteration_hook, finalizer = _async_generator_finalizer_hook)


class EventThreadRunDescriptor:
    if DOCS_ENABLED:
        __class_doc__ = ("""
        Descriptor which decides, exactly which function of the ``EventThread`` is called, when using it's `.run`
        method.
        
        If called from class, returns `self`. If called from a non yet running event loop, returns that's `.runner`. If
        called from an already stopped event loop, raises `RuntimeError`.
        """)
        
        __instance_doc__ = ("""
        ``EventThread.run`` is an overloaded method, with two usages. The first is when the thread starts up, it will
        run the thread's "runner", ``EvenThread.runner``. The other one usage is, when the event loop is running, then
        it returns it's "caller", ``EvenThread.caller``.
        
        If the event loop is already closed, raises ``RuntimeError``.
        """)
        
        __doc__ = docs_property()
    
    def __get__(self, obj, type_):
        if obj is None:
            return self
        
        if obj.running:
            return obj.caller
        
        if not obj.started:
            if obj._started.is_set():
                obj.started = True
                return obj.runner
            else:
                obj._do_start()
                return obj.caller
        
        if not obj._is_stopped:
            return obj.caller
        
        raise RuntimeError(f'The {obj.__class__.__name__} is already stopped.')
    
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')


def _iter_futures_of(value):
    """
    Iterates over the identified futures of the given value.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    value : `object`
        The value to check.
    
    Yields
    ------
    future : ``Future``
    """
    while True:
        # direct instance.
        if isinstance(value, Future):
            yield value
            return
        
        
        if isinstance(value, TaskGroup):
            yield from value.iter_futures()
            return
        
        # Method?
        if isinstance(value, MethodType):
            instance = value.__self__
            if isinstance(instance, WeakReferer):
                instance = instance()
                if instance is None:
                    return
            
            value = instance
            continue
        
        # Not method, gin-heh
        return
