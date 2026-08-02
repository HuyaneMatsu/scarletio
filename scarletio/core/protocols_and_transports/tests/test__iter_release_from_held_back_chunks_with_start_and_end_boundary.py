import vampytest

from ..protocol import _iter_release_from_held_back_chunks_with_start_and_end_boundary


def _iter_options():
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        0,
        b'rawrnyanpyon',
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        0,
        b'awrnyanpyon',
    )
    
    yield (
        2,
        [b'rawr', b'nyan', b'pyon'],
        0,
        b'wrnyanpyon',
    )
    
    yield (
        3,
        [b'rawr', b'nyan', b'pyon'],
        0,
        b'rnyanpyon',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        1,
        b'rawrnyanpyo',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        2,
        b'rawrnyanpy',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        3,
        b'rawrnyanp',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        4,
        b'rawrnyan',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        5,
        b'rawrnya',
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        10,
        b'ra',
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        1,
        b'awrnyanpyo',
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        9,
        b'aw',
    )
    
    yield (
        3,
        [b'rawr', b'nyan', b'pyon'],
        9,
        b'',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_release_from_held_back_chunks_with_start_and_end_boundary(held_back_offset, held_back, dropped_bytes):
    """
    Tests whether ``_iter_release_from_held_back_chunks_with_start_and_end_boundary`` works as intended.
    
    Parameters
    ----------
    held_back_offset : `int`
        Offset applied from the start.
    
    held_back : `list<bytes>`
        Held back chunks.
    
    dropped_bytes : `int`
        Offset applies from the end.
    
    Returns
    -------
    output : `bytes`
    """
    parts = [*_iter_release_from_held_back_chunks_with_start_and_end_boundary(held_back_offset, held_back, dropped_bytes)]
    for part in parts:
        vampytest.assert_instance(part, bytes, memoryview)
    return b''.join(parts)
