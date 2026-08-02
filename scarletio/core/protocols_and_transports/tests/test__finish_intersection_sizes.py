import vampytest

from ..protocol import _finish_intersection_sizes


def _iter_options():
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [1],
        (-1, None),
    )
    
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [2],
        (-1, None),
    )
    
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [3],
        (-1, None),
    )
    
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [4],
        (3, None),
    )
    
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [5],
        (-1, None),
    )
    
    yield (
        b'abc nyan nyan',
        b'abc abc',
        [1, 2, 3, 4, 5, 6],
        (3, None),
    )
    
    yield (
        b'abc',
        b' abc abc',
        [1],
        (-1, [1]),
    )
    
    yield (
        b'\nnyan',
        b'\r\n',
        [1],
        (1, None),
    )
    
    yield (
        b'nyan',
        b'\r\n',
        [1],
        (-1, None),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__finish_intersection_sizes(chunk, boundary, intersection_sizes):
    """
    Tests whether ``_finish_intersection_sizes`` works as intended.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    intersection_sizes : `list<int>`
        Detected intersection sizes of on the previous chunk.
        The processed ones are removed from it while the too low values to finish processing on are left in it.
    
    Returns
    -------
    output : `(int, None | list<int>)`
    """
    output = _finish_intersection_sizes(chunk, boundary, intersection_sizes)
    vampytest.assert_instance(output, tuple)
    return output
