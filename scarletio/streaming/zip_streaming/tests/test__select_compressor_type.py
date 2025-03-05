import vampytest

from ..compression import CompressorBase, CompressorZlibDeflate, select_compressor_type
from ..constants import COMPRESSION_METHOD_DEFLATE, COMPRESSION_METHOD_NONE


def _iter_options():
    yield COMPRESSION_METHOD_NONE, CompressorBase
    yield COMPRESSION_METHOD_DEFLATE, CompressorZlibDeflate


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__select_compressor_type(compression_method):
    """
    Tests whether ``select_compressor_type`` works as intended.
    
    Parameters
    ----------
    compression_method : `int`
        The compression method to check.
    
    Returns
    -------
    output : `type<CompressorBase>`
    """
    output = select_compressor_type(compression_method)
    vampytest.assert_subtype(output, CompressorBase)
    return output
