import vampytest

from ..protocol import _merge_intersection_sizes


def _iter_options():
    yield None, None, None
    yield [1], None, [1]
    yield None, [2], [2]
    yield [1], [2], [1, 2]


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__merge_intersection_sizes(intersection_sizes_0, intersection_sizes_1):
    """
    Tests whether ``_merge_intersection_sizes`` works as intended.
    
    Parameters
    ----------
    intersection_sizes_0 : `None | list<int>`
        Intersection sizes to merge.
    
    intersection_sizes_1 : `None | list<int>`
        Intersection sizes to merge.
    
    Returns
    -------
    output : `None | list<int>``
    """
    output = _merge_intersection_sizes(intersection_sizes_0, intersection_sizes_1)
    vampytest.assert_instance(output, list, nullable = True)
    return output
