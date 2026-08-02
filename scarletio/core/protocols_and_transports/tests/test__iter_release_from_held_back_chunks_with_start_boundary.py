import vampytest

from ..protocol import _iter_release_from_held_back_chunks_with_start_boundary


def _iter_options():
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        b'rawrnyanpyon',
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        b'awrnyanpyon',
    )
    
    yield (
        2,
        [b'rawr', b'nyan', b'pyon'],
        b'wrnyanpyon',
    )
    
    yield (
        3,
        [b'rawr', b'nyan', b'pyon'],
        b'rnyanpyon',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_release_from_held_back_chunks_with_start_boundary(held_back_offset, held_back):
    """
    Tests whether ``_iter_release_from_held_back_chunks_with_start_boundary`` works as intended.
    
    Parameters
    ----------
    held_back_offset : `int`
        Offset applied from the start.
    
    held_back : `list<bytes>`
        Held back chunks.
    
    Returns
    -------
    output : `bytes`
    """
    parts = [*_iter_release_from_held_back_chunks_with_start_boundary(held_back_offset, held_back)]
    for part in parts:
        vampytest.assert_instance(part, bytes, memoryview)
    return b''.join(parts)
