import vampytest

from ..building_and_parsing import parse_ip_v4_data


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
        b'aaa',
        None,
    )
    
    yield (
        b'aaaa',
        (
            (97 << (8 * 3)) |
            (97 << (8 * 2)) |
            (97 << (8 * 1)) |
            (97 << (8 * 0))
        ),
    )
    
    yield (
        b'ayaya',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_ip_v4_data(data):
    """
    Tests whether ``parse_ip_v4_data`` works as intended.
    
    Parameters
    ----------
    data : `None | bytes`
        Data to parse from.
    
    Returns
    --------
    output : `None | int`
    """
    output = parse_ip_v4_data(data)
    vampytest.assert_instance(output, int, nullable = True)
    return output
