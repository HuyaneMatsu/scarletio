__all__ = (
    'BROTLI_COMPRESSOR', 'BROTLI_DECOMPRESSOR', 'COMPRESSION_ERRORS', 'ZLIB_DECOMPRESSOR', 'ZLIB_COMPRESSOR',
    'ZLIB_MAX_WBITS', 'get_decompressor_for'
)

import zlib

from .exceptions import ContentEncodingError


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

ZLIB_MAX_WBITS = zlib.MAX_WBITS

def get_decompressor_for(content_encoding):
    """
    Gets decompress object for the given content-encoding if applicable.
    
    Parameters
    ----------
    content_encoding : `None`, `str`
        Content encoding of a respective http message.
    
    Returns
    -------
    decompressor : `None`, `ZLIB_DECOMPRESSOR`, `BROTLI_DECOMPRESSOR`
    
    Raises
    ------
    ContentEncodingError
        - `'content_encoding'` was given as `'br'` meanwhile brotli or brotlipy are not installed.
        - `'content_encoding'` is not an from the expected values.
    """
    if (content_encoding is None):
        decompressor = None
    
    elif content_encoding == 'gzip':
        decompressor = ZLIB_DECOMPRESSOR(wbits = 16 + ZLIB_MAX_WBITS)
    
    elif content_encoding == 'deflate':
        decompressor = ZLIB_DECOMPRESSOR(wbits = -ZLIB_MAX_WBITS)
    
    elif content_encoding == 'br':
        if BROTLI_DECOMPRESSOR is None:
            raise ContentEncodingError(
                'Can not decode content-encoding: brotli (br). Please install `brotlipy`.'
            )
        decompressor = BROTLI_DECOMPRESSOR()
    
    elif content_encoding == 'identity':
        # I assume this is no encoding
        decompressor = None
    
    else:
        raise ContentEncodingError(
            f'Can not decode content-encoding: {content_encoding!r}.'
        )
    
    return decompressor
