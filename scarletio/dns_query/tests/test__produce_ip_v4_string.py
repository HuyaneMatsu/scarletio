import vampytest

from ..helpers import produce_ip_v4_string


def _iter_options():
    yield (
        'full',
        (
            (56 << (8 * 3)) |
            (12 << (8 * 2)) |
            (255 << (8 * 1)) |
            (1 << (8 * 0))
        ),
        f'{56:d}.{12:d}.{255:d}.{1:d}',
    )
    
    yield (
        'max',
        (
            (255 << (8 * 3)) |
            (255 << (8 * 2)) |
            (255 << (8 * 1)) |
            (255 << (8 * 0))
        ),
        f'{255:d}.{255:d}.{255:d}.{255:d}',
    )
    
    yield (
        'min',
        (
            (0 << (8 * 3)) |
            (0 << (8 * 2)) |
            (0 << (8 * 1)) |
            (0 << (8 * 0))
        ),
        f'{0:d}.{0:d}.{0:d}.{0:d}',
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__produce_ip_v4_string(ip_value):
    """
    Tests whether ``produce_ip_v4_string`` works as intended.
    
    Parameters
    ----------
    ip_value : `int`
        Ip value.
    
    Returns
    -------
    output : `str`
    """
    output = [*produce_ip_v4_string(ip_value)]
    for element in output:
        vampytest.assert_instance(element, str)
    
    return ''.join(output)
