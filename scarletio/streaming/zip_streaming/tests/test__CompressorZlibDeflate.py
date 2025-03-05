import vampytest

from zlib import compressobj as create_zlib_compressor

from ..compression import CompressorZlibDeflate
from ..file import ZipStreamFile
from ..file_state import ZipStreamFileState

from .resources import AsyncGenerator


def _assert_fields_set(compressor_base):
    """
    Asserts whether the given compressor base has all of its fields set.
    
    Parameters
    ----------
    compressor_base : ``CompressorZlibDeflate``
        The compressor to test.
    """
    vampytest.assert_instance(compressor_base, CompressorZlibDeflate)
    vampytest.assert_instance(compressor_base.compressor, type(create_zlib_compressor()))


def test__CompressorZlibDeflate():
    """
    Tests whether ``CompressorZlibDeflate`` works as intended.
    """
    async_generator = AsyncGenerator([b'aya' * 33, b'mister' * 5])
    name = 'koishi'
    
    file = ZipStreamFile(name, async_generator)
    file_state = ZipStreamFileState(file, None)
    
    compressor = CompressorZlibDeflate()
    _assert_fields_set(compressor)
    
    chunks = []
    
    coroutine_generator = file.async_generator.__aiter__()
    while True:
        coroutine = coroutine_generator.asend(None)
        
        try:
            while True:
                coroutine.send(None)
        except StopIteration as exception:
            chunk = exception.value
        
        except StopAsyncIteration:
            break
        
        chunk = compressor.process(file_state, chunk)
        chunks.append(chunk)
    
    chunks.append(compressor.tail(file_state))
    
    vampytest.assert_eq(
        chunks,
        [
            b'',
            b'',
            b'K\xacLL\xa41\xca\xcd,.I-\xc2E\x02\x00',
        ],
    )
    
    vampytest.assert_eq(file_state.size_compressed, 16)
    vampytest.assert_eq(file_state.size_uncompressed, async_generator.get_data_size())
    vampytest.assert_eq(file_state.crc, 428089206)
