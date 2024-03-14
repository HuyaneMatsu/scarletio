__all__ = ()

from ssl import CertificateError, MemoryBIO, SSLError, SSL_ERROR_SYSCALL, SSL_ERROR_WANT_READ, SSL_ERROR_WANT_WRITE


SSL_PIPE_STATE_UNWRAPPED = 0
SSL_PIPE_STATE_DO_HANDSHAKE = 1
SSL_PIPE_STATE_WRAPPED = 2
SSL_PIPE_STATE_SHUTDOWN = 3

SSL_PIPE_STATE_VALUE_TO_NAME = {
    SSL_PIPE_STATE_UNWRAPPED: 'unwrapped',
    SSL_PIPE_STATE_DO_HANDSHAKE: 'do_handshake',
    SSL_PIPE_STATE_WRAPPED: 'wrapped',
    SSL_PIPE_STATE_SHUTDOWN: 'shutdown',
}

MAX_SIZE = 262144

class SSLPipe:
    """
    An SSL pipe.
    
    Allows you to communicate with an SSL/TLS protocol instance through memory buffers. It can be used to implement a
    security layer for an existing connection where you don't have access to the connection's file descriptor, or for
    some reason you don't want to use it.
    
    An ``SSLPipe`` can be in `wrapped` and `unwrapped` mode. In unwrapped mode, data is passed through untransformed.
    In wrapped mode, application level data is encrypted to SSL record level data and vice versa. The SSL record level
    is the lowest level in the SSL protocol suite and is what travels as-is over the wire.
    
    An ``SSLPipe`` initially is in `unwrapped` mode. To start SSL, call ``.do_handshake``, to shutdown SSL, call
    ``.unwrap``.
    
    Attributes
    ----------
    _handshake_callback : `None`, `callable`
        A Callback which will be called when handshake is completed. Set by ``.do_handshake``.
        
        Should accept the following parameters:
        +-----------------------+---------------------------+
        | Respective name       | Value                     |
        +=======================+===========================+
        | handshake_exception   | `None`, `BaseException` |
        +-----------------------+---------------------------+
        
        If the handshake is successful, then the `handshake_exception` is given as `None`, else as an exception
        instance.
    _incoming : `MemoryBIO`
        Does the incoming data encryption/decryption.
    _need_ssl_data : `bool`
        Whether more record level data is needed to complete a handshake that is currently in progress.
    _outgoing : `MemoryBIO`
        Does the outgoing data encryption/decryption.
    _server_host_name : `None`, `str`
        The ssl protocol's server hostname if applicable.
    _server_side : `bool`
        Whether the ssl protocol is server side.
    _shutdown_callback : `None`, `callable`
        A callback which will be called when the shutdown is completed. Set by ``.shutdown``.
        
        Should accept no parameters.
    _ssl_context : `SSLContext`
        The SSL pipe's SSL type.
    _ssl_object : `None`, `ssl.SSLObject`
        SSL object connecting ``._incoming`` and ``._outgoing`` memory bios set at ``.do_handshake``.
    _state : `int`
        The state of the ``SSLPipe``.
        
        Can be set as one of:
        
        +-------------------------------+-----------+
        | Respective name               | Value     |
        +===============================+===========+
        | SSL_PIPE_STATE_UNWRAPPED      | `0`       |
        +-------------------------------+-----------+
        | SSL_PIPE_STATE_DO_HANDSHAKE   | `1`       |
        +-------------------------------+-----------+
        | SSL_PIPE_STATE_WRAPPED        | `2`       |
        +-------------------------------+-----------+
        | SSL_PIPE_STATE_SHUTDOWN       | `3`       |
        +-------------------------------+-----------+
        
        Note, that ``.state`` is checked by memory address and not by value.
    """
    __slots__ = (
        '_handshake_callback', '_incoming', '_need_ssl_data', '_outgoing', '_server_host_name', '_server_side',
        '_shutdown_callback', '_ssl_context', '_ssl_object', '_state'
    )
    
    def __init__(self, context, server_side, server_host_name):
        """
        Creates a new ``SSLPipe`` with the given parameters.
        
        Parameters
        ----------
        context : `SSLContext`
            The SSL pipe's SSL type.
        server_side : `bool`
            Whether the ssl protocol is server side.
        server_host_name : `None`, `str`
            The ssl protocol's server hostname if applicable.

        """
        self._ssl_context = context
        self._server_side = server_side
        self._server_host_name = server_host_name
        self._state = SSL_PIPE_STATE_UNWRAPPED
        self._incoming = MemoryBIO()
        self._outgoing = MemoryBIO()
        self._ssl_object = None
        self._need_ssl_data = False
        self._handshake_callback = None
        self._shutdown_callback = None
    
    
    def is_wrapped(self):
        """
        Returns whether a security layer is currently is effect.
        
        In handshake or on in shutdown is always `False`.
        
        Returns
        -------
        is_wrapped : `bool`
        """
        return (self._state == SSL_PIPE_STATE_WRAPPED)
    
    
    def do_handshake(self, callback = None):
        """
        Starts the SSL handshake.
        
        Parameters
        ----------
        callback : `None`, `callable` = `None`, Optional
            A Callback which will be called when handshake is completed.
            
            Should accept the following parameters:
            +-----------------------+---------------------------+
            | Respective name       | Value                     |
            +=======================+===========================+
            | handshake_exception   | `None`, `BaseException`   |
            +-----------------------+---------------------------+
            
            If the handshake is successful, then the `handshake_exception` is given as `None`, else as an exception
            instance.
            
        Returns
        -------
        ssl_data : `list` of `bytes`
            A list of SSL data. Always an empty list is returned.
        
        Raises
        ------
        RuntimeError
            If the handshake is in progress or is already completed.
        """
        if self._state != SSL_PIPE_STATE_UNWRAPPED:
            raise RuntimeError('Handshake in progress or completed.')
        
        self._ssl_object = self._ssl_context.wrap_bio(
            self._incoming, self._outgoing, server_side = self._server_side, server_hostname = self._server_host_name
        )
        
        self._state = SSL_PIPE_STATE_DO_HANDSHAKE
        self._handshake_callback = callback
        ssl_data, application_data = self.feed_ssl_data(b'', only_handshake = True)
        
        return ssl_data
    
    
    def shutdown(self, callback = None):
        """
        Starts the SSL shutdown process.
        
        Parameters
        ----------
        callback : `None`, `callable` = `None`, Optional
            A callback which will be called when the shutdown is completed.
            
            Should accept no parameters.
        
        Returns
        -------
        ssl_data : `list` of `bytes`
            A list of SSL data.
        
        Raises
        ------
        RuntimeError
            - If the security layer is not yet present.
            - If shutdown is already in progress.
        """
        state = self._state
        if state == SSL_PIPE_STATE_UNWRAPPED:
            raise RuntimeError('No security layer present.')
        
        if state == SSL_PIPE_STATE_SHUTDOWN:
            raise RuntimeError('Shutdown in progress.')
        
        self._state = SSL_PIPE_STATE_SHUTDOWN
        self._shutdown_callback = callback
        ssl_data, application_data = self.feed_ssl_data(b'')
        return ssl_data
    
    
    def feed_eof(self):
        """
        Sends an eof.
        
        Raises
        ------
        SSLError
            If the eof was unexpected. The raised ssl error has `errno` set as `SSL_ERROR_EOF`.
        """
        self._incoming.write_eof()
        # Ignore return.
        self.feed_ssl_data(b'')
    
    
    def feed_ssl_data(self, data, only_handshake = False):
        """
        Feed SSL record level data into the pipe.
        
        Parameters
        ----------
        data : `bytes`
            If empty `bytes` is given, then it will get ssl_data for the handshake initialization.
        
        Returns
        -------
        ssl_data : `list` of `bytes`
            Contains the SSL data that needs to be sent to the remote SSL.
        application_data : `list` of `bytes`
            Plaintext data that needs to be forwarded to the application.
            
            Might contain an empty `bytes`, what indicates that ``.shutdown`` should be called.
        """
        state = self._state
        ssl_data = []
        application_data = []
        
        if state == SSL_PIPE_STATE_UNWRAPPED:
            # If unwrapped, pass plaintext data straight through.
            if data:
                application_data.append(data)
            
            return ssl_data, application_data
        
        self._need_ssl_data = False
        if data:
            self._incoming.write(data)
        
        try:
            if state == SSL_PIPE_STATE_DO_HANDSHAKE:
                # Call do_handshake() until it doesn't raise anymore.
                self._ssl_object.do_handshake()
                self._state = state = SSL_PIPE_STATE_WRAPPED
                
                handshake_callback = self._handshake_callback
                if (handshake_callback is not None):
                    handshake_callback(None)
                
                if only_handshake:
                    return ssl_data, application_data
                # Handshake done: execute the wrapped block
            
            if state == SSL_PIPE_STATE_WRAPPED:
                # Main state: read data from SSL until close_notify.
                while True:
                    chunk = self._ssl_object.read(MAX_SIZE)
                    application_data.append(chunk)
                    if not chunk:  # close_notify
                        break
            
            elif state == SSL_PIPE_STATE_SHUTDOWN:
                # Call shutdown() until it doesn't raise anymore.
                self._ssl_object.unwrap()
                self._ssl_object = None
                self._state = SSL_PIPE_STATE_UNWRAPPED
                
                shutdown_callback = self._shutdown_callback
                if (shutdown_callback is not None):
                    shutdown_callback()
            
            elif state == SSL_PIPE_STATE_UNWRAPPED:
                # Drain possible plaintext data after close_notify.
                application_data.append(self._incoming.read())
        
        except (SSLError, CertificateError) as err:
            err_number = getattr(err, 'errno', None)
            if err_number not in (SSL_ERROR_WANT_READ, SSL_ERROR_WANT_WRITE, SSL_ERROR_SYSCALL):
                if self._state == SSL_PIPE_STATE_DO_HANDSHAKE:
                    handshake_callback = self._handshake_callback
                    if (handshake_callback is not None):
                        handshake_callback(err)
                raise
            
            self._need_ssl_data = (err_number == SSL_ERROR_WANT_READ)

        # Check for record level data that needs to be sent back. Happens for the initial handshake and renegotiation.
        if self._outgoing.pending:
            ssl_data.append(self._outgoing.read())
        
        return ssl_data, application_data
    
    
    def feed_application_data(self, data, offset):
        """
        Feed plaintext data into the pipe.
        
        If the returned `offset` is less than the returned data's total length in bytes, that case is called
        `short write`. If `short-write` happens, than the same `data` should be passed to ``.feed_application_data``
        next time. (This is an OpenSSL requirement.) A further particularity is that a short write will always have
        `offset = 0`, because the `_ssl` module does not enable partial writes. And even though the offset is `0`,
        there will still be encrypted data in ssl_data.
        
        Returns
        -------
        ssl_data : `list` of `bytes-like`
            Containing record level data that needs to be sent to the remote SSL instance.
        offset : `int`
            The number of the processed plaintext data in bytes. Might be less than the total length of the returned
            data.
        
        Raises
        ------
        SSLError
            Any unexpected SSL error.
        """
        ssl_data = []
        if self._state == SSL_PIPE_STATE_UNWRAPPED:
            # pass through data in unwrapped mode
            if offset < len(data):
                ssl_data.append(memoryview(data)[offset:])
            offset = len(data)
        else:
            view = memoryview(data)
            while True:
                self._need_ssl_data = False
                try:
                    if offset < len(view):
                        offset += self._ssl_object.write(view[offset:])
                except SSLError as err:
                    # It is not allowed to call `.write` after ``.unwrap`` until the close_notify is acknowledged. We
                    # return the condition to the caller as a short write.
                    if err.reason == 'PROTOCOL_IS_SHUTDOWN':
                        err.errno = SSL_ERROR_WANT_READ
                        need_ssl_data = True
                    else:
                        errno = getattr(err, 'errno', None)
                        if errno is None:
                            raise
                        
                        if errno == SSL_ERROR_WANT_READ:
                            need_ssl_data = True
                        elif errno == SSL_ERROR_WANT_WRITE or errno == SSL_ERROR_SYSCALL:
                            need_ssl_data = False
                        else:
                            raise
                    
                    self._need_ssl_data = need_ssl_data
    
                # See if there's any record level data back for us.
                if self._outgoing.pending:
                    ssl_data.append(self._outgoing.read())
                
                if offset == len(view) or self._need_ssl_data:
                    break
        
        return ssl_data, offset
