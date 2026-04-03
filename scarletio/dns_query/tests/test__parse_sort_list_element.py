import vampytest

from ..constants import IP_TYPE_IP_V4, IP_TYPE_IP_V6
from ..resolve_configuration import SortListElement, parse_sort_list_element


def _iter_options():
    yield (
        '/',
        None,
    )
    
    yield (
        'nyan',
        None,
    )
    
    yield (
        '/nyan',
        None,
    )
    
    yield (
        'nyan/',
        None,
    )
    
    yield (
        'nyan/nyan',
        None,
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            0xffffffff,
        ),
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            0xffffffff,
        ),
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/nyan',
        None,
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/{2:d}.{2:d}.{2:d}.{2:d}',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            (
                (2 << 24) |
                (2 << 16) |
                (2 << 8) |
                (2 << 0)
            ),
        ),
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}',
        None,
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/8',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            0xff000000,
        ),
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/32',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            0xffffffff,
        ),
    )
    
    yield (
        f'{1:d}.{1:d}.{1:d}.{1:d}/500',
        SortListElement(
            IP_TYPE_IP_V4,
            (
                (1 << 24) |
                (1 << 16) |
                (1 << 8) |
                (1 << 0)
            ),
            0xffffffff,
        ),
    )
    
    
    
    
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            0xffffffffffffffffffffffffffffffff,
        ),
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            0xffffffffffffffffffffffffffffffff,
        ),
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/nyan',
        None,
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}:{2:x}',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            (
                (2 << (16 * 7)) |
                (2 << (16 * 6)) |
                (2 << (16 * 5)) |
                (2 << (16 * 4)) |
                (2 << (16 * 3)) |
                (2 << (16 * 2)) |
                (2 << (16 * 1)) |
                (2 << (16 * 0))
            ),
        ),
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/{2:d}.{2:d}.{2:d}.{2:d}',
        None,
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/8',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            0xff000000000000000000000000000000,
        ),
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/128',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            0xffffffffffffffffffffffffffffffff,
        ),
    )
    
    yield (
        f'{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}:{1:x}/500',
        SortListElement(
            IP_TYPE_IP_V6,
            (
                (1 << (16 * 7)) |
                (1 << (16 * 6)) |
                (1 << (16 * 5)) |
                (1 << (16 * 4)) |
                (1 << (16 * 3)) |
                (1 << (16 * 2)) |
                (1 << (16 * 1)) |
                (1 << (16 * 0))
            ),
            0xffffffffffffffffffffffffffffffff,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_sort_list_element(string):
    """
    Tests whether ``parse_sort_list_element`` works as intended.
    
    Parameters
    ----------
    string : `str`
        String to parse. Should not be empty.
    
    Returns
    -------
    output : ``None | SortListElement``
    """
    output = parse_sort_list_element(string)
    vampytest.assert_instance(output, SortListElement, nullable = True)
    return output
