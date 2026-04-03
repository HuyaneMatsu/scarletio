__all__ = ()

from .compressors import ZLIB_COMPRESSOR, ZLIB_MAX_WBITS


WRITE_CHUNK_LIMIT = 65536


class HTTPStreamWriter:
    """
    Http writer used by ``ClientRequest``.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether ``.write_eof`` was called.
    size : `int`
        The amount of written data in bytes. If reaches a limit, drain lock is awaited.
    chunked : `bool`
        Whether the http message's content is chunked.
    compressor : `None`, `ZLIB_COMPRESSOR`, `BROTLI_COMPRESSOR`
        Decompressor used to compress the sent data. Defaults to `None` if no compression is given.
    protocol : `AbstractProtocolBase`
        Asynchronous transport implementation.
    transport : `None`, ``AbstractTransportLayerBase``
        Asynchronous transport implementation. Set as `None` if at eof.
    """
    __slots__ = ('_at_eof', 'size', 'chunked', 'compressor', 'protocol', 'transport', )
    
    def __init__(self, protocol, compression, chunked):
        """
        Creates a new ``HTTPStreamWriter`` with the given parameter.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            Asynchronous protocol implementation.
        compression : `None`, `str`
            The compression's type to encode the written content with.
        chunked : `bool`
            Whether the given data should be written with chunking.
        """
        if (compression is None):
            compressor = None
        elif compression == 'gzip':
            compressor = ZLIB_COMPRESSOR(wbits = 16 + ZLIB_MAX_WBITS)
        elif compression == 'deflate':
            compressor = ZLIB_COMPRESSOR(wbits = ZLIB_MAX_WBITS)
        else:
            compressor = None
        
        self.compressor = compressor
        
        self.protocol = protocol
        self.transport = protocol.get_transport()
        
        self.chunked = chunked
        self.size = 0
        
        self._at_eof = False
    
    
    def _write(self, chunk):
        """
        Writes the given chunk of data to the writer's ``.transport``.
        
        Parameters
        ----------
        chunk : `bytes-like`
            The data to write.
        
        Raises
        ------
        ConnectionResetError
            Cannot write to closing transport.
        """
        size = len(chunk)
        self.size += size
        
        transport = self.transport
        if (transport is None) or transport.is_closing():
            raise ConnectionResetError('Cannot write to closing transport.')
        
        transport.write(chunk)
    
    
    async def write(self, chunk):
        """
        Writes the given chunk of data to the writer's ``.transport``.
        
        Compresses and "chunks" the `chunk` if applicable. If after writing the respective buffer limit is reached,
        waits for drain lock.
        
        This method is a coroutine.
        
        Parameters
        ----------
        chunk : `bytes-like`
            The data to write.
        
        Raises
        ------
        ConnectionResetError
            Cannot write to closing transport.
        """
        compressor = self.compressor
        if (compressor is not None):
            chunk = compressor.compress(chunk)
        
        if not chunk:
            return
        
        if self.chunked:
            chunk = b''.join([format(len(chunk), 'x').encode('ascii'), b'\r\n', chunk, b'\r\n'])
        
        self._write(chunk)
        
        if self.size > WRITE_CHUNK_LIMIT:
            self.size = 0
            
            await self.drain()
    
    
    async def write_eof(self, chunk = b''):
        """
        Write end of stream to the writer's ``.transport`` and marks it as it is at eof.
        
        If the writer is already at eof, does nothing.
        
        This method is a coroutine.
        
        Parameters
        ----------
        chunk : `bytes-like` = `b''`, Optional
            The data to write.
        """
        if self._at_eof:
            return
        
        compressor = self.compressor
        if compressor is None:
            if self.chunked:
                if chunk:
                    chunk = b''.join([format(len(chunk), 'x').encode('ascii'), b'\r\n', chunk, b'\r\n0\r\n\r\n'])
                else:
                    chunk = b'0\r\n\r\n'
        else:
            if chunk:
                chunk = compressor.compress(chunk)
                chunk = chunk + compressor.flush()
            else:
                chunk = compressor.flush()
            
            if chunk and self.chunked:
                chunk = b''.join([format(len(chunk), 'x').encode('ascii'), b'\r\n', chunk, b'\r\n0\r\n\r\n'])
        
        if chunk:
            self._write(chunk)
        
        await self.drain()
        
        self._at_eof = True
        self.transport = None
    
    
    async def drain(self):
        """
        Flushes the write buffer.
        """
        protocol = self.protocol
        if (protocol.get_transport() is not None):
            await protocol._drain_helper()
