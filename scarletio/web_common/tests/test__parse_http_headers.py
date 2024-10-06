import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..exceptions import PayloadError
from ..helpers import parse_http_headers


def _iter_options__passing():
    # no headers
    yield (
        b'',
        0,
        IgnoreCaseMultiValueDictionary(),
    )
    
    # 1 header
    yield (
        b'hey mister: sister',
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister'),
        ]),
    )
    
    # 1 header & offset
    yield (
        (
            b'miau\r\n'
            b'hey mister: sister'
        ),
        6,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister'),
        ]),
    )
    
    # 2 headers
    yield (
        (
            b'hey mister: sister\r\n'
            b'hey: mister'
        ),
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister'),
            ('hey', 'mister'),
        ]),
    )
    
    # 1 header twice (different)
    yield (
        (
            b'hey mister: sister\r\n'
            b'hey mister: water heater for sale'
        ),
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister'),
            ('hey mister', 'water heater for sale'),
        ]),
    )
    
    # 1 header continuous (+1 line)
    yield (
        (
            b'hey mister: sister\r\n'
            b'            water heater for sale'
        ),
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister water heater for sale'),
        ]),
    )
    
    # 1 header continuous (+2 line)
    yield (
        (
            b'hey mister: sister\r\n'
            b'            water\r\n'
            b'            heater for sale'
        ),
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister water heater for sale'),
        ]),
    )
    
    # 2 header continuous (+1 line x 2)
    yield (
        (
            b'hey mister: sister\r\n'
            b'            water\r\n'
            b'hey sister: heater\r\n'
            b'            for sale'
        ),
        0,
        IgnoreCaseMultiValueDictionary([
            ('hey mister', 'sister water'),
            ('hey sister', 'heater for sale'),
        ]),
    )
 

def _iter_options__payload_error():
    yield b'ayaya', 0


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__payload_error()).raising(PayloadError))
def test__parse_http_headers(data, offset):
    """
    Tests whether ``parse_http_headers`` works as intended.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    offset : `int`
        Position to start parsing at.
    
    Returns
    -------
    headers : ``IgnoreCaseMultiValueDictionary``
    
    raises
    ------
    PayloadError
    """
    output = parse_http_headers(data, offset)
    vampytest.assert_instance(output, IgnoreCaseMultiValueDictionary)
    return output
