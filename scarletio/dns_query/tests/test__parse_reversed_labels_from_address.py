import vampytest

from ..helpers import parse_reversed_labels_from_address


def _iter_options():
    yield (
        '127.0.0.1',
        (b'1', b'0', b'0', b'127', b'in-addr', b'arpa'),
    )
    
    yield (
        f'{5612:x}:{12:x}:{255:x}:{1:x}:{0:x}:{2666:x}:{2626:x}:{2366:x}',
        (
            b'e', b'3', b'9', b'0', b'2', b'4', b'a', b'0', b'a', b'6', b'a', b'0', b'0', b'0', b'0', b'0', b'1', b'0',
            b'0', b'0', b'f', b'f', b'0', b'0', b'c', b'0', b'0', b'0', b'c', b'e', b'5', b'1', b'ip6', b'arpa'
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_reversed_labels_from_address(address):
    """
    Tests whether ``parse_reversed_labels_from_address`` works as intended.
    
    Parameters
    ----------
    address : `str`
        The address to parse.
    
    Returns
    -------
    output : `None | tuple<bytes>`
    """
    output = parse_reversed_labels_from_address(address)
    vampytest.assert_instance(output, tuple, nullable = True)
    if (output is not None):
        for element in output:
            vampytest.assert_instance(element, bytes)
    
    return output
