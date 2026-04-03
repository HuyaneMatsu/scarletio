__all__ = ()

from ...utils import copy_docs

from ..protocols_and_transports import AbstractProtocolBase


class SubprocessWritePipeProtocol(AbstractProtocolBase):
    """
    Asynchronous subprocess write pipe protocol.
    
    Attributes
    ----------
    _disconnected : `bool`
        Whether the protocol is disconnected.
    _file_descriptor : `int`
        The used socket's file descriptor number.
    _transport : ``UnixWritePipeTransport``, `object`
        Asynchronous transport implementation.
    _process : ``AsyncProcess``
        The parent process of the pipe protocol.
    """
    __slots__ = ('_disconnected', '_file_descriptor', '_transport', '_process', )
    
    def __new__(cls, process, file_descriptor):
        """
        Creates a new ``SubprocessWritePipeProtocol`` with the given parameters.
        
        Parameters
        ----------
        process : ``AsyncProcess``
            The parent process of the pipe protocol.
        file_descriptor : `int`
            The used socket's file descriptor number.
        """
        self = object.__new__(cls)
        self._process = process
        self._file_descriptor = file_descriptor
        self._transport = None
        self._disconnected = False
        return self
    
    
    @copy_docs(AbstractProtocolBase.connection_made)
    def connection_made(self, transport):
        self._transport = transport
    
    
    def __repr__(self):
        """Returns the subprocess write protocol's representation."""
        return f'<{self.__class__.__name__} file_descriptor = {self._file_descriptor} pipe = {self._transport!r}>'
    
    
    @copy_docs(AbstractProtocolBase.connection_lost)
    def connection_lost(self, exception):
        process = self._process
        if (process is not None):
            self._process = None
            process._pipe_connection_lost(self._file_descriptor, exception)
            self._disconnected = True
    
    
    @copy_docs(AbstractProtocolBase.pause_writing)
    def pause_writing(self):
        self._process.pause_writing()
    
    
    @copy_docs(AbstractProtocolBase.resume_writing)
    def resume_writing(self):
        self._process.resume_writing()


    @copy_docs(AbstractProtocolBase.get_transport)
    def get_transport(self):
        return self._transport


class SubprocessReadPipeProtocol(SubprocessWritePipeProtocol):
    """
    Asynchronous subprocess read pipe protocol.
    
    Attributes
    ----------
    _disconnected : `bool`
        Whether the protocol is disconnected.
    _file_descriptor : `int`
        The used socket's file descriptor number.
    _transport : ``UnixWritePipeTransport``, `object`
        Asynchronous transport implementation.
    _process : ``AsyncProcess``
        The parent process of the pipe protocol.
    """
    __slots__ = ()
    
    @copy_docs(AbstractProtocolBase.data_received)
    def data_received(self, data):
        self._process._pipe_data_received(self._file_descriptor, data)
    
    
    @copy_docs(AbstractProtocolBase.eof_received)
    def eof_received(self):
        return False
