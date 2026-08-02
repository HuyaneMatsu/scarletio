import vampytest

from ..protocol import _get_end_intersection_sizes


def _iter_options():
    yield (
        b'abc',
        0,
        b'abc abc',
        [3],
    )
    
    yield (
        b'abc',
        1,
        b'abc abc',
        None,
    )
    
    yield (
        b'abc',
        2,
        b'abc abc',
        None,
    )
    
    yield (
        b'aab',
        1,
        b'abc abc',
        [2],
    )
    
    yield (
        b'aab',
        2,
        b'abc abc',
        None,
    )
    
    yield (
        b'aaa',
        2,
        b'abc abc',
        [1],
    )
    
    yield (
        b'abc abc',
        0,
        b'abc abc abc',
        [7, 3],
    )
    
    yield (
        b'abc abc',
        1,
        b'abc abc abc',
        [3],
    )
    
    yield (
        b'abc abc',
        2,
        b'abc abc abc',
        [3],
    )
    
    yield (
        b'abc abc',
        3,
        b'abc abc abc',
        [3],
    )
    
    yield (
        b'abc abc',
        4,
        b'abc abc abc',
        [3],
    )
    
    yield (
        b'abc abc',
        5,
        b'abc abc abc',
        None,
    )
    
    yield (
        b'nyan',
        0,
        b'\r\n',
        None,
    )
    
    yield (
        b'nyan\r',
        0,
        b'\r\n',
        [1],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_end_intersection_sizes(chunk, offset, boundary):
    """
    Tests whether ``_get_end_intersection_sizes`` works as intended.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process.
    
    offset : `int`
        Data chunk offset.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    Returns
    -------
    output : `None | list<int>`
    """
    output = _get_end_intersection_sizes(chunk, offset, boundary)
    vampytest.assert_instance(output, list, nullable = True)
    return output
