__all__ = ()

import zlib

try:
    import brotli
except ImportError:
    brotli = None
    COMPRESSION_ERRORS = zlib.error
    BROTLI_DECOMPRESSOR = None
    BROTLI_COMPRESSOR = None
else:
    COMPRESSION_ERRORS = (zlib.error, brotli.error)
    
    if hasattr(brotli, 'Error'):
        # brotlipy case
        BROTLI_DECOMPRESSOR = brotli.Decompressor
        BROTLI_COMPRESSOR = brotli.Compressor
    else:
        # brotli case
        class BROTLI_DECOMPRESSOR:
            __slots__ = ('_decompressor', )
            def __init__(self):
                self._decompressor = brotli.Decompressor()
            
            def decompress(self, value):
                return self._decompressor.process(value)
        
        class BROTLI_COMPRESSOR:
            __slots__ = ('_compressor', )
            def __init__(self):
                self._compressor = brotli.Compressor()
            
            def compress(self, value):
                return self._compressor.process(value)


ZLIB_DECOMPRESSOR = zlib.decompressobj
ZLIB_COMPRESSOR = zlib.compressobj
