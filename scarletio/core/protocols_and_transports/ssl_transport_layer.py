__all__ = ('SSLBidirectionalTransportLayer',)

import reprlib
from collections import deque
from ssl import SSLError, create_default_context as create_default_ssl_context

from ...utils import copy_docs

from .abstract import AbstractBidirectionalTransportLayerBase
from .extra_info import (
    EXTRA_INFO_NAME_CIPHER, EXTRA_INFO_NAME_COMPRESSION, EXTRA_INFO_NAME_PEER_CERTIFICATION,
    EXTRA_INFO_NAME_SSL_CONTEXT, EXTRA_INFO_NAME_SSL_OBJECT, get_has_extra_info, set_extra_info
)
from .ssl_pipe import SSLPipe
from .transport_layer import TransportLayerBase


class SSLBidirectionalTransportLayer(TransportLayerBase, AbstractBidirectionalTransportLayerBase):
    """
    Asynchronous SSL protocol implementation on top of a `socket`. Uses `MemoryBIO`-s for incoming and
    outgoing data.
    
    Attributes
    ----------
    _extra : `None`, `dict` of (`str`, `object`) items
        Optional transport information.
    _loop : ``EventThread``
        The event loop to what the transport is bound to.
    _call_connection_made : `bool`
        Whether the the ``.app_protocol``'s `.connection_made` should be called when handshake is completed.
    _closing : `bool`
        Whether the ssl protocol is shut or shutting down.
    _connection_made_waiter : `None`, ``Future``
        A waiter future, what's result is set when connection is made, aka handshake is completed, or if when the
        connection is lost, depending which happens first.
        
        After the future's result or exception is set, the attribute is set as `None`.
    _in_handshake : `bool`
        Whether the ssl transport is in handshaking.
    _protocol : ``AbstractTransportLayerBase``
        Asynchronous protocol implementation.
    _server_host_name : `None`, `str`
        The ssl protocol's server hostname if applicable.
    _server_side : `bool`
        Whether the ssl protocol is server side.
    _session_established : `bool`
        Whether the session is established. Is set after handshake and is set back to `False` when the connection is
        lost.
    _ssl_context : `ssl.SSLContext`
        The connection's ssl type.
    _ssl_pipe : `None`, ``SSLPipe``
        Ssl pipe set meanwhile the protocol is connected to feed the ssl data to.
    _transport : `None`, ``AbstractTransportLayerBase``
        Asynchronous transport implementation.
    _write_backlog : `deque` of `tuple` (`bytes-like`, `int`)
        Ensured data queued up to be written. Each element contains a tuple of the data to write and an offset till
        write from.
    """
    __slots__ = (
        '_call_connection_made', '_closing', '_connection_made_waiter', '_in_handshake', '_protocol',
        '_server_host_name', '_server_side', '_session_established', '_ssl_context', '_ssl_pipe', '_transport',
        '_write_backlog'
    )
    
    def __new__(cls, loop, protocol, ssl_context, connection_made_waiter, server_side, server_host_name,
            call_connection_made):
        """
        Creates a new ``SSLProtocol``.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop of the protocol.
        protocol : ``AbstractTransportLayerBase``
            Asynchronous protocol implementation.
        ssl_context : `None`, `ssl.SSLContext`
            The connection ssl type. If SSl was given as `True` when creating a connection at this point we get it as
            `None`, so we create a default ssl context.
            
            Note, that if the connection is server side, a valid `ssl_context` should be given.
        connection_made_waiter : `None`, ``Future``
            A waiter future, what's result is set when connection is made, aka handshake is completed, or if when the
            connection is lost, depending which happens first.
            
            After the future's result or exception is set, the attribute is set as `None`.
        server_side : `bool`
            Whether the ssl protocol is server side.
        server_host_name : `None`, `str`
            The ssl protocol's server hostname if applicable.
            
            If we are the `server_side`, then this parameter is forced to `None` (wont raise).
        call_connection_made : `bool`
            Whether the the `protocol`'s `.connection_made` should be called when handshake is completed.
        
        Raises
        ------
        ValueError
            If the protocol is server side, but `ssl_context` is not given.
        """
        if ssl_context is None:
            if server_side:
                raise ValueError('Server side SSL needs a valid `SSLContext`.')
            
            ssl_context = create_default_ssl_context()
            if (server_host_name is None) or (not server_host_name):
                ssl_context.check_hostname = False
        
        if server_side:
            server_host_name = None
        
        extra = set_extra_info(None, EXTRA_INFO_NAME_SSL_CONTEXT, ssl_context)
        self = TransportLayerBase.__new__(cls, loop, extra)
        
        self._server_side = server_side
        self._server_host_name = server_host_name
        self._ssl_context = ssl_context
        self._write_backlog = deque()
        self._connection_made_waiter = connection_made_waiter
        self._protocol = protocol
        self._ssl_pipe = None
        self._session_established = False
        self._in_handshake = False
        self._closing = False
        self._transport = None
        self._call_connection_made = call_connection_made
        
        return self
    
    
    def __repr__(self):
        """Returns the ssl protocol transport's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
        ]
        
        if self._closing:
            repr_parts.append(' closing')
            field_added = True
        else:
            field_added = False
        
        transport = self._transport
        if (transport is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' transport = ')
            repr_parts.append(transport.__class__.__name__)
        
        protocol = self._protocol
        if (protocol is not None):
            if field_added:
                repr_parts.append(',')
            
            repr_parts.append(' protocol = ')
            repr_parts.append(protocol.__class__.__name__)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def _wake_up_connection_made_waiter(self, exception = None):
        """
        Wakes up the ssl protocol's ``._connection_made_waiter`` if applicable.
        
        Called when connection is made closed or lost, depending, which happens first. If connection is made or closed,
        then the connection made waiter's result is set as `None`, if the connection is lost, then the respective
        exception is thrown into it if any.
        
        Parameters
        ----------
        exception : `None`, ``BaseException`` = `None`, Optional
            Exception to throw into ``._connection_made_waiter`` if any.
        """
        connection_made_waiter = self._connection_made_waiter
        if (connection_made_waiter is not None):
            self._connection_made_waiter = None
            if connection_made_waiter.is_pending():
                if exception is None:
                    connection_made_waiter.set_result(None)
                else:
                    connection_made_waiter.set_exception(exception)
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.connection_made)
    def connection_made(self, transport):
        self._transport = transport
        self._ssl_pipe = SSLPipe(self._ssl_context, self._server_side, self._server_host_name)
        
        self._in_handshake = True
        # `(b'', 1)` is a special value in ``._process_write_backlog`` to do the SSL handshake
        self._write_backlog.append((b'', 1))
        self._loop.call_soon(self._process_write_backlog)
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.connection_lost)
    def connection_lost(self, exception):
        if self._session_established:
            self._session_established = False
            app_protocol = self._protocol
            self._loop.call_soon(type(app_protocol).connection_lost, app_protocol, exception)
        
        self._transport = None
        self._wake_up_connection_made_waiter(exception)
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.pause_writing)
    def pause_writing(self):
        self._protocol.pause_writing()
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.resume_writing)
    def resume_writing(self):
        self._protocol.resume_writing()
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.data_received)
    def data_received(self, data):
        try:
            ssl_data, application_data = self._ssl_pipe.feed_ssl_data(data)
        except SSLError:
            self.abort()
            return
        
        for chunk in ssl_data:
            self._transport.write(chunk)
        
        for chunk in application_data:
            if chunk:
                self._protocol.data_received(chunk)
                continue
            
            self.close()
            break
    
    
    @copy_docs(AbstractBidirectionalTransportLayerBase.eof_received)
    def eof_received(self):
        try:
            self._wake_up_connection_made_waiter(ConnectionResetError)
            if not self._in_handshake:
                # has no effect whatever it returns when we use ssl
                self._protocol.eof_received()
        finally:
            self._transport.close()
        
        return False
    
    
    @copy_docs(TransportLayerBase.get_extra_info)
    def get_extra_info(self, name, default = None):
        info, present = get_has_extra_info(self._extra, name)
        if not present:
            transport = self._transport
            if transport is not None:
                info = transport.get_extra_info(name, default)
            else:
                info = default
        
        return info
    
    
    def _write_application_data(self, data):
        """
        Writes data to the ``SSLProtocol`` to be sent.
        
        Parameters
        ----------
        data : `bytes-like`
            The data to write.
        """
        self._write_backlog.append((data, 0))
        self._process_write_backlog()
    
    
    def _handshake_completed(self, handshake_exception):
        """
        Called when ssl handshake is completed.
        
        Parameters
        ----------
        handshake_exception : `None`, `BaseException`
            Exception occurred when processing backlog meanwhile handshaking.
        """
        self._in_handshake = False
        ssl_object = self._ssl_pipe._ssl_object
        
        if (handshake_exception is None):
            try:
                peer_certification = ssl_object.getpeercert()
            except BaseException as err:
                handshake_exception = err
            else:
                handshake_exception = None
        
        if (handshake_exception is not None):
            self._transport.close()
            self._wake_up_connection_made_waiter(handshake_exception)
            raise
        
        # Add extra info that becomes available after handshake.
        extra = self._extra
        extra = set_extra_info(extra, EXTRA_INFO_NAME_PEER_CERTIFICATION, peer_certification)
        extra = set_extra_info(extra, EXTRA_INFO_NAME_CIPHER, ssl_object.cipher())
        extra = set_extra_info(extra, EXTRA_INFO_NAME_COMPRESSION, ssl_object.compression())
        extra = set_extra_info(extra, EXTRA_INFO_NAME_SSL_OBJECT, ssl_object)
        self._extra = extra
        
        if self._call_connection_made:
            self._protocol.connection_made(self)
        
        self._wake_up_connection_made_waiter()
        self._session_established = True
        
        # Don's call it immediately, other tasks might be scheduled already.
        self._loop.call_soon(self._process_write_backlog)
    
    
    def _process_write_backlog(self):
        """
        Try to make progress on the write backlog.
        
        Feeds data to ``.ssl_pipe`` till it is full.
        """
        transport = self._transport
        if transport is None:
            return
        
        write_backlog = self._write_backlog
        try:
            for _ in range(len(write_backlog)):
                data, offset = write_backlog[0]
                if data:
                    ssl_data, offset = self._ssl_pipe.feed_application_data(data, offset)
                else:
                    # If data is given as empty bytes means we either have handshake complete or there is no more data
                    # to write
                    if offset:
                        ssl_data = self._ssl_pipe.do_handshake(self._handshake_completed)
                    else:
                        ssl_data = self._ssl_pipe.shutdown(self._finalize)
                    
                    offset = 1
                
                for chunk in ssl_data:
                    transport.write(chunk)
                
                if offset < len(data):
                    write_backlog[0] = (data, offset)
                    # A short write means that a write is blocked on a read, we need to enable reading if it is paused!
                    assert self._ssl_pipe._need_ssl_data
                    if transport._paused:
                        transport.resume_reading()
                    
                    break
                
                # An entire chunk from the backlog was processed. We can delete it and reduce the outstanding buffer
                # size.
                del self._write_backlog[0]
        
        except BaseException as err:
            if self._in_handshake:
                self._handshake_completed(err)
            else:
                self._fatal_error(err, 'Fatal error on SSL transport.')
            
            if not isinstance(err, Exception):
                # BaseException
                raise
    
    
    @copy_docs(TransportLayerBase._fatal_error)
    def _fatal_error(self, exception, message = 'Fatal error on transport.'):
        TransportLayerBase._fatal_error(self, exception, message)
        
        transport = self._transport
        if (transport is not None):
            transport._force_close(exception)
    
    
    def _finalize(self):
        """
        Closes the ``SSLProtocol``'s transport.
        
        Called after shutdown or abortion.
        """
        transport = self._transport
        if (transport is not None):
            transport.close()
    
    
    def __del__(self):
        """
        Closes the ssl protocol transport if not yet closed.
        """
        self.close()
    
    
    @copy_docs(TransportLayerBase.get_protocol)
    def get_protocol(self):
        return self._protocol
    
    
    @copy_docs(TransportLayerBase.set_protocol)
    def set_protocol(self, protocol):
        self._protocol = protocol
    
    
    @copy_docs(TransportLayerBase.is_closing)
    def is_closing(self):
        return self._closing
    
    
    @copy_docs(TransportLayerBase.close)
    def close(self):
        if not self._closing:
            self._closing = True
            self._write_application_data(b'')
    
    
    @copy_docs(TransportLayerBase.abort)
    def abort(self):
        transport = self._transport
        if (transport is not None):
            try:
                transport.abort()
            finally:
                self._finalize()


    @copy_docs(TransportLayerBase.write)
    def write(self, data):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f'`data` can be `bytes-like`, got {data.__class__.__name__}; {reprlib.repr(data)}.'
            )
        
        if data:
            self._write_application_data(data)
    
    
    @copy_docs(TransportLayerBase.write_eof)
    def write_eof(self):
        pass
    
    
    @copy_docs(TransportLayerBase.can_write_eof)
    def can_write_eof(self):
        return False
    
    
    @copy_docs(TransportLayerBase.pause_reading)
    def pause_reading(self):
        transport = self._transport
        if transport is None:
            return False
        
        return transport.pause_reading()
    
    
    @copy_docs(TransportLayerBase.resume_reading)
    def resume_reading(self):
        transport = self._transport
        if transport is None:
            return False
            
        transport.resume_reading()
        return True
    
    
    @copy_docs(TransportLayerBase.get_write_buffer_size)
    def get_write_buffer_size(self):
        transport = self._transport
        if transport is None:
            write_buffer_size = 0
        else:
            write_buffer_size = transport.get_write_buffer_size()
        
        return write_buffer_size
    
    
    @copy_docs(TransportLayerBase.get_write_buffer_limits)
    def get_write_buffer_limits(self):
        transport = self._transport
        if transport is None:
            return 16384, 65536
        
        return transport.get_write_buffer_limits()
    
    
    @copy_docs(TransportLayerBase.set_write_buffer_limits)
    def set_write_buffer_limits(self, low = None, high = None):
        transport = self._transport
        if (transport is not None):
            transport.set_write_buffer_limits(high, low)
