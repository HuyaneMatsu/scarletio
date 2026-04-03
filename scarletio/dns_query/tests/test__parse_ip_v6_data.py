import vampytest

from ..building_and_parsing import parse_ip_v6_data


def _iter_options():
    yield (
        None,
        None,
    )
    
    yield (
        b'',
        None,
    )
    
    yield (
        b'aaaaaaaaaaaaaaa',
        None,
    )
    
    yield (
        b'aaaaaaaaaaaaaaaa',
        (
            (24929 << (16 * 7)) |
            (24929 << (16 * 6)) |
            (24929 << (16 * 5)) |
            (24929 << (16 * 4)) |
            (24929 << (16 * 3)) |
            (24929 << (16 * 2)) |
            (24929 << (16 * 1)) |
            (24929 << (16 * 0))
        ),
    )
    
    yield (
        b'aaaaaaaaaaaaaaaaa',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_ip_v6_data(data):
    """
    Tests whether ``parse_ip_v6_data`` works as intended.
    
    Parameters
    ----------
    data : `None | bytes`
        Data to parse from.
    
    Returns
    --------
    output : `None | int`
    """
    output = parse_ip_v6_data(data)
    vampytest.assert_instance(output, int, nullable = True)
    return output
