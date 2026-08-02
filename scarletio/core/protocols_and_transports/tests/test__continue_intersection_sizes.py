import vampytest

from ..protocol import _continue_intersection_sizes


def _iter_options():
    yield (
        b'abc',
        b' abc abc',
        [1],
        [4],
    )
    
    yield (
        b'abc',
        b' abc abc',
        [1, 2, 3, 4, 5, 6],
        [4, 8],
    )
    
    yield (
        b'dddd',
        b' abc abc',
        [2],
        None,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__continue_intersection_sizes(chunk, boundary, intersection_sizes):
    """
    Tests whether ``_continue_intersection_sizes`` works as intended.
    
    Parameters
    ----------
    chunk : `bytes`
        Data chunk to process. Must have length > 0.
    
    boundary : `bytes`
        Boundary to check intersection with.
    
    intersection_sizes : `list<int>`
        Detected the non matched intersection sizes. The matched ones are updated.
    
    Returns
    -------
    output : `None | list<int>`
    """
    output = _continue_intersection_sizes(chunk, boundary, intersection_sizes)
    vampytest.assert_instance(output, list, nullable = True)
    return output
