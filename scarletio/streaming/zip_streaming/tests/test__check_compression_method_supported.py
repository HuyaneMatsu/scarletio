import vampytest

from ..compression import check_compression_method_supported
from ..constants import (
    COMPRESSION_METHOD_BZIP2, COMPRESSION_METHOD_DEFLATE, COMPRESSION_METHOD_LZMA, COMPRESSION_METHOD_NONE
)


def _iter_options__passing():
    yield COMPRESSION_METHOD_NONE
    yield COMPRESSION_METHOD_DEFLATE


def _iter_options__runtime_error():
    yield COMPRESSION_METHOD_BZIP2
    yield COMPRESSION_METHOD_LZMA
    yield -1


@vampytest.call_from(_iter_options__passing())
@vampytest._(vampytest.call_from(_iter_options__runtime_error()).raising(RuntimeError))
def test__check_compression_method_supported(compression_method):
    """
    Tests whether ``check_compression_method_supported`` works as intended.
    
    Parameters
    ----------
    compression_method : `int`
        The compression method to check.
    
    Raises
    ------
    RuntimeError
    """
    check_compression_method_supported(compression_method)
