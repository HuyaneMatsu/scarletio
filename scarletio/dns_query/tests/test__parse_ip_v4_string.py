import vampytest

from ..helpers import parse_ip_v4_string


def _iter_options():
    yield (
        'empty string',
        '',
        (
            False,
            0,
        ),
    )
    
    yield (
        'full',
        f'{56:d}.{12:d}.{255:d}.{1:d}',
        (
            True,
            (
                (56 << (8 * 3)) |
                (12 << (8 * 2)) |
                (255 << (8 * 1)) |
                (1 << (8 * 0))
            ),
        ),
    )
    
    yield (
        'max',
        f'{255:d}.{255:d}.{255:d}.{255:d}',
        (
            True,
            (
                (255 << (8 * 3)) |
                (255 << (8 * 2)) |
                (255 << (8 * 1)) |
                (255 << (8 * 0))
            ),
        ),
    )
    
    yield (
        'min',
        f'{0:d}.{0:d}.{0:d}.{0:d}',
        (
            True,
            (
                (0 << (8 * 3)) |
                (0 << (8 * 2)) |
                (0 << (8 * 1)) |
                (0 << (8 * 0))
            ),
        ),
    )
    
    yield (
        '3 fields',
        f'{127:d}.{0:d}.{1:d}',
        (
            False,
            0,
        ),
    )
    
    yield (
        '5 fields',
        f'{127:d}.{0:d}.{0:d}.{0:d}.{1:d}',
        (
            False,
            0,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__parse_ip_v4_string(ip_string):
    """
    Tests whether ``parse_ip_v4_string`` works as intended.
    
    Parameters
    ----------
    ip_string : `str`
        Value to test with.
    
    Returns
    -------
    output : `(bool, int)`
    """
    output = parse_ip_v4_string(ip_string)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], bool)
    vampytest.assert_instance(output[1], int)
    return output
