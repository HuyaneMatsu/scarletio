__all__ = ()

from zlib import DEFLATED, Z_FINISH, compressobj as create_zlib_compressor, crc32 as compute_crc32

from ...utils import RichAttributeErrorBaseType, copy_docs

from .constants import (
    COMPRESSION_METHOD_BZIP2, COMPRESSION_METHOD_DEFLATE, COMPRESSION_METHOD_LZMA, COMPRESSION_METHOD_NONE
)


class CompressorBase(RichAttributeErrorBaseType):
    """
    Base compressor type that does passthrough processing.
    """
    __slots__ = ()
    
    def __new__(cls):
        """Creates a new compressor instance."""
        return object.__new__(cls)
    
    
    def process(self, file_state, chunk):
        """
        Processes a single chunk of data. Updates crc, compresses the data and updates the compressed size counter.
        
        Parameters
        ----------
        file_state : ``FileState``
            The respective file's state.
        
        chunk : `bytes | memoryview`
            The chunk of data to process.
        
        Returns
        -------
        chunk : `bytes | memoryview`
        """
        file_state.crc = compute_crc32(chunk, file_state.crc)
        file_state.size_uncompressed = file_state.size_compressed = file_state.size_uncompressed + len(chunk)
        return chunk
    
    
    def tail(self, file_state):
        """
        Flushes the compressor if applicable and increases the compressed size counter.
        
        Returns
        -------
        chunk : `bytes | memoryview`
        """
        return b''
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return f'<{type(self).__name__}>'


class CompressorZlibDeflate(CompressorBase):
    """
    Zlib deflate compressor.
    
    Attributes
    ----------
    compressor : `Compress`
        Zlib compressor.
    """
    __slots__ = ('compressor',)
    
    @copy_docs(CompressorBase.__new__)
    def __new__(cls):
        self = object.__new__(cls)
        self.compressor = create_zlib_compressor(5, DEFLATED, -15)
        return self
    
    
    @copy_docs(CompressorBase.process)
    def process(self, file_state, chunk):
        file_state.crc = compute_crc32(chunk, file_state.crc)
        file_state.size_uncompressed += len(chunk)
        chunk = self.compressor.compress(chunk)
        file_state.size_compressed += len(chunk)
        return chunk
    
    
    @copy_docs(CompressorBase.tail)
    def tail(self, file_state):
        chunk = self.compressor.flush(Z_FINISH)
        file_state.size_compressed += len(chunk)
        return chunk


def check_compression_method_supported(compression_method):
    """
    Checks whether the selected compression method is supported.
    
    Parameters
    ----------
    compression_method : `int`
        The compression method to check.
    
    Raises
    ------
    RuntimeError
    """
    if compression_method == COMPRESSION_METHOD_NONE:
        return
    
    if compression_method == COMPRESSION_METHOD_DEFLATE:
        return
    
    if compression_method == COMPRESSION_METHOD_BZIP2:
        raise RuntimeError('`bzip2` compression not supported.')
    
    if compression_method == COMPRESSION_METHOD_LZMA:
        raise RuntimeError('`lzma` compression not supported.')
    
    raise RuntimeError(f'Unknown compression method: {compression_method!r}.')


def select_compressor_type(compression_method):
    """
    Selects the compressor type for the given compression method.
    
    Parameters
    ----------
    compression_method : `int`
        The compression method to check.
    
    Returns
    -------
    compressor_type : `type<CompressorBase>`
    """
    if compression_method == COMPRESSION_METHOD_NONE:
        return CompressorBase
    
    if compression_method == COMPRESSION_METHOD_DEFLATE:
        return CompressorZlibDeflate
    
    return CompressorBase
