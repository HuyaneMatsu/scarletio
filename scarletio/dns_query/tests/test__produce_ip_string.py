import vampytest

from ..constants import IP_TYPE_IP_V4, IP_TYPE_IP_V6, IP_TYPE_NONE
from ..helpers import produce_ip_string


def _iter_options():
    yield (
        'none',
        IP_TYPE_NONE,
        0,
        'unknown',
    )
    
    yield (
        'ip v4',
        IP_TYPE_IP_V4,
        (
            (56 << (8 * 3)) |
            (12 << (8 * 2)) |
            (255 << (8 * 1)) |
            (1 << (8 * 0))
        ),
        f'{56:d}.{12:d}.{255:d}.{1:d}',
    )
    
    yield (
        'ip v6',
        IP_TYPE_IP_V6,
        (
            (5612 << (16 * 7)) |
            (12 << (16 * 6)) |
            (255 << (16 * 5)) |
            (1 << (16 * 4)) |
            (15 << (16 * 3)) |
            (2666 << (16 * 2)) |
            (2626 << (16 * 1)) |
            (2366 << (16 * 0))
        ),
        f'{5612:x}:{12:x}:{255:x}:{1:x}:{15:x}:{2666:x}:{2626:x}:{2366:x}',
    )
    


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__produce_ip_string(ip_type, ip_value):
    """
    Tests whether ``produce_ip_string`` works as intended.
    
    Parameters
    ----------
    ip_type : `int`
        The ip's type.
    
    ip_value : `int`
        Ip value.
    
    Returns
    -------
    output : `str`
    """
    output = [*produce_ip_string(ip_type, ip_value)]
    for element in output:
        vampytest.assert_instance(element, str)
    
    return ''.join(output)
