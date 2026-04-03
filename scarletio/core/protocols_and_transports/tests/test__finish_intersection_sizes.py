import vampytest

from ..protocol import _finish_intersection_sizes


def _iter_options():
    yield 'ayaya', 'ayaya', [3, 1], (-1, None)
    yield 'yayaya', 'ayaya', [3, 1], (2, None)
    yield ', water heater for sale', 'mister, water heater for sale', [6], (23, None)
    yield 'ister, water heater for sale', 'mister, water heater for sale', [1], (28, None)
    yield ', water heater for', 'mister, water heater for sale', [6], (-1, [6])


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
