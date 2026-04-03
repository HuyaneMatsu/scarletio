import vampytest

from ..helpers import is_ipv4_address


def _iter_options__passing():
    # None
    yield None, False
    
    # Valid ipv4 addresses
    yield '0.0.0.0', True
    yield b'0.0.0.0', True
    yield '127.0.0.1', True
    yield b'127.0.0.1', True
    yield '255.255.255.255', True
    yield b'255.255.255.255', True
    
    # Valid ipv6 addresses
    yield '::8', False
    yield b'::8', False
    yield '0:0:0:0:0:0:0:0', False
    yield b'0:0:0:0:0:0:0:0', False
    yield '2001:db8:3333:4444:5555:6666:7777:8888', False
    yield b'2001:db8:3333:4444:5555:6666:7777:8888', False
    yield 'FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF', False
    yield b'FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF', False
    
    # host name
    yield 'localhost', False
    yield b'localhost', False
    yield 'www.orindance.party', False
    yield b'www.orindance.party', False
    
    # value out of range
    yield '300.300.300.300', False
    yield b'300.300.300.300', False
    
    # with port
    yield '127.0.0.1:80', False
    yield b'127.0.0.1:80', False
    yield '[0:0:0:0:0:0:0:0]:80', False
    yield b'[0:0:0:0:0:0:0:0]:80', False
    
    # Too many double colons,
    yield '2001::3333:4444::6666:7777:8888', False
    yield b'2001::3333:4444::6666:7777:8888', False


def _iter_options__type_error():
    yield 123
    yield object()


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__type_error()).raising(TypeError))
def test__is_ipv4_address(input_value):
    """
    Tests whether ``is_ipv4_address`` works as intended.
    
    Parameters
    ----------
    input_value : `bool`
        Value to test on.
    
    Returns
    -------
    output : `bool`
    
    Raises
    ------
    TypeError
    """
    output = is_ipv4_address(input_value)
    vampytest.assert_instance(output, bool)
    return output
