import vampytest

from ..protocol import _iter_release_from_held_back_chunks_unused


def _iter_options():
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        0,
        (
            [],
            b'rawrnyanpyon',
        ),
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        0,
        (
            [],
            b'awrnyanpyon',
        ),
    )
    
    yield (
        2,
        [b'rawr', b'nyan', b'pyon'],
        0,
        (
            [],
            b'wrnyanpyon',
        ),
    )
    
    yield (
        3,
        [b'rawr', b'nyan', b'pyon'],
        0,
        (
            [],
            b'rnyanpyon',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        1,
        (
            [b'pyon'],
            b'rawrnyan',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        2,
        (
            [b'pyon'],
            b'rawrnyan',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        3,
        (
            [b'pyon'],
            b'rawrnyan',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        4,
        (
            [b'pyon'],
            b'rawrnyan',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        5,
        (
            [b'nyan', b'pyon'],
            b'rawr',
        ),
    )
    
    yield (
        0,
        [b'rawr', b'nyan', b'pyon'],
        10,
        (
            [b'rawr', b'nyan', b'pyon'],
            b'',
        ),
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        1,
        (
            [b'pyon'],
            b'awrnyan',
        ),
    )
    
    yield (
        1,
        [b'rawr', b'nyan', b'pyon'],
        9,
        (
            [b'rawr', b'nyan', b'pyon'],
            b'',
        ),
    )
    
    yield (
        3,
        [b'rawr', b'nyan', b'pyon'],
        9,
        (
            [b'rawr', b'nyan', b'pyon'],
            b'',
        ),
    )

@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def _iter_release_from_held_back_chunks_unused(held_back_offset, held_back, kept_bytes):
    """
    tests whether ``_iter_release_from_held_back_chunks_unused`` works as intended.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    held_back_offset : `int`
        Offset applied from the start.
    
    held_back : `list<bytes>`
        Held back chunks.
    
    kept_bytes : `int`
        The lower threshold of bytes to keep from the end.
    
    Returns
    -------
    output : `(list<bytes>, bytes)`
    """
    held_back = held_back.copy()
    parts = [*_iter_release_from_held_back_chunks_unused(held_back_offset, held_back, kept_bytes)]
    for part in parts:
        vampytest.assert_instance(part, bytes, memoryview)
    return (held_back, b''.join(parts))
