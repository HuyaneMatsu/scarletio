import vampytest

from ..building_and_parsing import parse_domain_name_pointer_data


def _iter_options():
    yield None, None
    yield b'', None
    yield b'\05aaaaa\01b\00', 'aaaaa.b'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_domain_name_pointer_data(data):
    """
    Tests whether ``parse_domain_name_pointer_data`` works as intended.
    
    Parameters
    ----------
    data : `None | bytes`
        Data to parse from.
    
    Returns
    --------
    output : `None | str`
    """
    output = parse_domain_name_pointer_data(data)
    vampytest.assert_instance(output, str, nullable = True)
    return output
