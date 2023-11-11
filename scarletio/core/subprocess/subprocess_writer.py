__all__ = ()

from ...utils import copy_docs

from ..protocols_and_transports import AbstractTransportLayerBase
from ..traps import skip_ready_cycle


class SubprocessWriter(AbstractTransportLayerBase):
    """
    Writer interface for subprocess calls.
    
    Attributes
    ----------
    _loop : ``EventThread``
        The respective event loop of the stream.
    _transport : ``UnixWritePipeTransport``, `object`
        Asynchronous transport implementation.
    _protocol : ``AsyncProcess``, `object`
        Asynchronous protocol implementation.
    """
    __slots__ = ('_loop', '_transport', '_protocol', )
    
    def __new__(cls, loop, transport, protocol):
        """
        Writer used as ``AsyncProcess.stdin``.
        
        Parameters
        ----------
        loop : ``EventThread``
            The respective event loop of the stream.
        transport : ``UnixWritePipeTransportLayer``
            Asynchronous transport implementation.
        protocol : ``AsyncProcess``
            Asynchronous protocol implementation.
        """
        self = object.__new__(cls)
        
        self._transport = transport
        self._protocol = protocol
        self._loop = loop
        
        return self
    
    
    @copy_docs(AbstractTransportLayerBase.write)
    def write(self, data):
        self._transport.write(data)
    
    
    @copy_docs(AbstractTransportLayerBase.writelines)
    def writelines(self, lines):
        self._transport.writelines(lines)
    
    
    @copy_docs(AbstractTransportLayerBase.write_eof)
    def write_eof(self):
        return self._transport.write_eof()
    
    
    @copy_docs(AbstractTransportLayerBase.can_write_eof)
    def can_write_eof(self):
        return self._transport.can_write_eof()
    
    
    @copy_docs(AbstractTransportLayerBase.close)
    def close(self):
        return self._transport.close()
    
    
    @copy_docs(AbstractTransportLayerBase.is_closing)
    def is_closing(self):
        return self._transport.is_closing()
    
    
    @copy_docs(AbstractTransportLayerBase.get_extra_info)
    def get_extra_info(self, name, default = None):
        return self._transport.get_extra_info(name, default)
    
    
    async def drain(self):
        """
        Blocks till the write buffer is drained.
        
        This method is a coroutine.
        
        Raises
        ------
        BaseException
            Connection lost exception if applicable.
        """
        if self._transport.is_closing():
            # skip 1 loop
            await skip_ready_cycle()
        
        await self._protocol._drain_helper()
