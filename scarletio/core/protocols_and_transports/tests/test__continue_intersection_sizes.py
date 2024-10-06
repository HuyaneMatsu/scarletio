import vampytest

from ..protocol import _continue_intersection_sizes


def _iter_options():
    yield 'ayaya', 'ayayaya', [3, 1], None
    yield 'yaya', 'ayayayaya', [3, 1], [7, 5]
    yield ', water heater for', 'mister, water heater for sale', [6], [24]


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
