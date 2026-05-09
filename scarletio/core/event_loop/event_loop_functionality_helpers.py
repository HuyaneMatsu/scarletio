__all__ = ()

import sys
from socket import (
    SOCK_DGRAM as SOCKET_TYPE_DATAGRAM, SOCK_STREAM as SOCKET_TYPE_STREAM, SOL_SOCKET as SOCKET_OPTION_LEVEL_SOCKET,
    SO_REUSEPORT as SOCKET_OPTION_REUSE_PORT
)
from ssl import SSLContext, create_default_context as create_default_ssl_context
from threading import current_thread
from types import MethodType
from warnings import warn

from ...utils import DOCS_ENABLED, WeakReferer, docs_property, include

from ..traps import Future, Task, TaskGroup


EventThread = include('EventThread')


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
    return (socket.type & SOCKET_TYPE_DATAGRAM) == SOCKET_TYPE_DATAGRAM


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
    return (socket.type & SOCKET_TYPE_STREAM) == SOCKET_TYPE_STREAM


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
    try:
        socket.setsockopt(SOCKET_OPTION_LEVEL_SOCKET, SOCKET_OPTION_REUSE_PORT, 1)
    except OSError as exception:
        raise ValueError(
            '`reuse_port` not supported by socket module, the option is defined but not implemented.'
        ) from exception


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
        __type_doc__ = ("""
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
        
        raise RuntimeError(f'The {type(obj).__name__} is already stopped.')
    
    
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


def _ssl_deprecation_precheck(ssl):
    """
    Validates the given ssl value and raises if it is given as invalid type.
    
    Parameters
    ----------
    ssl : `None | bool | SSLContext`
        Ssl to validate and convert to an ssl context.
    
    Returns
    -------
    ssl_context : `None | SSLContext`
    """
    warn(
        (
            f'`ssl` parameter is deprecated, please use `ssl_context` instead.'
        ),
        FutureWarning,
        stacklevel = 3,
    )
    
    if ssl is None:
        ssl_context = None
    elif isinstance(ssl, SSLContext):
        ssl_context = ssl
    elif isinstance(ssl, bool):
        if ssl:
            ssl_context = create_default_ssl_context()
        else:
            ssl_context = None
    else:
        raise TypeError(f'`ssl` if unexpected type: {type(ssl).__name__}; ssl = {ssl!r}.')
    
    return ssl_context


def _create_connection_shared_precheck(ssl_context, server_host_name, host):
    """
    Shared precheck by ``.create_connection_to`` and by ``.create_connection_with``.
    
    Parameters
    ----------
    ssl : `None | SSLContext`
        Ssl context to use.
    
    server_host_name : `None | str`
        Overwrites the host name that the target server’s certificate will be matched against.
        Should only be passed if `ssl_context` is not `None`. By default the value of the host parameter is used.
        If host is empty, there is no default and you must pass a value for `server_host_name`.
        If `server_host_name` is an empty string, host name matching is disabled
        (which is a serious security risk, allowing for potential man-in-the-middle attacks).
    
    host : `None | str`
        To what network interfaces should the connection be bound.
    
    Returns
    -------
    server_host_name : `None | str`
    """
    if (server_host_name is None):
        if (ssl_context is not None):
            # Use host as default for server_host_name.
            if host is None:
                raise ValueError('You must set `server_host_name` when using `ssl_context` without a `host`.')
            
            server_host_name = host
    else:
        if ssl_context is None:
            raise ValueError('`server_host_name` is only meaningful with `ssl_context`.')
    
    return server_host_name

    
def _create_unix_connection_shared_precheck( ssl_context, server_host_name):
    """
    Shared precheck used by ``.create_unix_connection_to` and by ``.create_unix_connection_with``.
    
    Parameters
    ----------
    ssl_context : `None | SSLContext`
        Ssl context to use.
    
    server_host_name : `None | str`
        Overwrites the host name that the target server’s certificate will be matched against.
        Should only be passed if `ssl_context` is not `None`.
    
    Returns
    -------
    server_host_name : `None | str`
    
    Raises
    ------
    ValueError
        - If `server_host_name` parameter is given, but `ssl_context` isn't.
        - If `ssl_context` parameter is given, but `server_host_name` is not.
    """
    if (ssl_context is None):
        if server_host_name is not None:
            raise ValueError('`server_host_name` is only meaningful with `ssl_context`.')
    else:
        if server_host_name is None:
            raise ValueError('`server_host_name` parameter is required with `ssl_context`.')
    
    return server_host_name
