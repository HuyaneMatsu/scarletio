import vampytest

from ..protocol import _get_end_intersection_sizes


def _iter_options():
    yield 'hey mister', 0, 'mister, water heater for sale', [6]
    yield 'hey mister', 0, 'r mister, water heater for sale', [1]
    yield 'hey mister', 5, 'mister, water heater for sale', None
    yield 'hey mister', 5, 'r mister, water heater for sale', [1]
    yield 'ay aya', 0, 'ayaya', [3, 1]


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
