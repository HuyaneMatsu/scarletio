import vampytest

from ...top_level import get_event_loop

from ..protocol import _read_until_by_chunk, ReadProtocolBase


def _iter_options():
    yield (
        0,
        [
            b'rawr\r\nnyan\r\na',
        ],
        b'\r\n',
        (
            6,
            [
                b'rawr\r\nnyan\r\na',
            ],
            b'rawr',
        ),
    )
    
    yield (
        0,
        [
            b'rawr\r\n',
        ],
        b'\r\n',
        (
            0,
            [],
            b'rawr',
        ),
    )
    
    yield (
        1,
        [
            b'rawr\r\nnyan\r\na',
        ],
        b'\r\n',
        (
            6,
            [
                b'rawr\r\nnyan\r\na',
            ],
            b'awr',
        ),
    )
    
    yield (
        3,
        [
            b'rawr\r\nnyan\r\na',
        ],
        b'\r\n',
        (
            6,
            [
                b'rawr\r\nnyan\r\na',
            ],
            b'r',
        ),
    )
    
    yield (
        4,
        [
            b'rawr\r\nnyan\r\na',
        ],
        b'\r\n',
        (
            6,
            [
                b'rawr\r\nnyan\r\na',
            ],
            b'',
        ),
    )
    
    yield (
        5,
        [
            b'rawr\r\nnyan\r\na',
        ],
        b'\r\n',
        (
            12,
            [
                b'rawr\r\nnyan\r\na',
            ],
            b'\nnyan'
        ),
    )
    
    yield (
        5,
        [
            b'rawr\r\nnyan\r\n',
        ],
        b'\r\n',
        (
            0,
            [],
            b'\nnyan'
        ),
    )
    
    yield (
        0,
        [
            b'\r\n',
            b'nyan',
        ],
        b'\r\n',
        (
            0,
            [
                b'nyan',
            ],
            b'',
        ),
    )
    
    yield (
        0,
        [
            b'rawr',
            b'\r\n',
            b'nyan',
        ],
        b'\r\n',
        (
            0,
            [
                b'nyan',
            ],
            b'rawr',
        ),
    )
    
    yield (
        0,
        [
            b'rawr',
            b'\r',
            b'\n',
            b'nyan',
        ],
        b'\r\n',
        (
            0,
            [
                b'nyan',
            ],
            b'rawr',
        ),
    )
    
    yield (
        2,
        [
            b'rawr',
            b'\r',
            b'\n',
            b'nyan',
        ],
        b'\r\n',
        (
            0,
            [
                b'nyan',
            ],
            b'wr',
        ),
    )
    
    yield (
        4,
        [
            b'rawr\r\n',
            b'nyan',
        ],
        b'\r\n',
        (
            0,
            [
                b'nyan',
            ],
            b'',
        ),
    )
    
    yield (
        0,
        [
            b'rawr\r',
            b'\nnyan',
        ],
        b'\r\n',
        (
            1,
            [
                b'\nnyan',
            ],
            b'rawr',
        ),
    )
    
    yield (
        2,
        [
            b'rawr\r',
            b'\nnyan',
        ],
        b'\r\n',
        (
            1,
            [
                b'\nnyan',
            ],
            b'wr',
        ),
    )
    
    yield (
        4,
        [
            b'rawr\r',
            b'\nnyan',
        ],
        b'\r\n',
        (
            1,
            [
                b'\nnyan',
            ],
            b'',
        ),
    )
    
    yield (
        2,
        [
            b'rawr',
            b'\r\nnyan',
        ],
        b'\r\n',
        (
            2,
            [
                b'\r\nnyan',
            ],
            b'wr',
        ),
    )
    
    yield (
        4,
        [
            b'rawr',
            b'\r\nnyan',
        ],
        b'\r\n',
        (
            2,
            [
                b'\r\nnyan',
            ],
            b'',
        ),
    )
    
    yield (
        0,
        [
            b'\r\n17\r\n',
        ],
        b'\r\n',
        (
            2,
            [
                b'\r\n17\r\n',
            ],
            b'',
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
async def test__read_until_by_chunk(offset, chunks, boundary):
    """
    Tests whether ``_read_until_by_chunk`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    offset : `int`
        Offset of the first chunk.
    
    chunks : `list<bytes>`
        Chunks to serve from-
    
    boundary : `bytes`
        The boundary to read until. Consumed but not returned.
    
    Returns
    -------
    output : `(int, list<bytes>, bytes)`
    """
    event_loop = get_event_loop()
    
    read_protocol = ReadProtocolBase(event_loop)
    read_protocol._offset = offset
    read_protocol._chunks.extend(chunks)
    read_protocol._at_eof = True
    
    parts = []
    async for part in _read_until_by_chunk(read_protocol, boundary):
        parts.append(part)
    
    for part in parts:
        vampytest.assert_instance(part, bytes, memoryview)
    
    return read_protocol._offset, [*read_protocol._chunks], b''.join(parts)
