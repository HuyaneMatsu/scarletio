import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..exceptions import PayloadError
from ..helpers import HttpVersion, parse_http_request
from ..http_message import RawRequestMessage


def _iter_options__passing():
    yield (
        b'GET /party HTTP/1.1',
        RawRequestMessage(
            HttpVersion(1, 1),
            'GET',
            '/party',
            IgnoreCaseMultiValueDictionary(),
        ),
    )
    
    yield (
        b'get /party HTTP/1.1',
        RawRequestMessage(
            HttpVersion(1, 1),
            'GET',
            '/party',
            IgnoreCaseMultiValueDictionary(),
        ),
    )
    
    yield (
        (
            b'GET /party HTTP/1.1\r\n'
            b'hey: mister'
        ),
        RawRequestMessage(
            HttpVersion(1, 1),
            'GET',
            '/party',
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
        ),
    )


def _iter_options__payload_error():
    yield b'GET /party MIAU/1.1'


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__payload_error()).raising(PayloadError))
def test__parse_http_request(data):
    """
    Tests whether ``parse_http_request`` works as intended.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    output : ``RawRequestMessage``
    
    Raises
    ------
    PayloadError
    """
    output = parse_http_request(data)
    vampytest.assert_instance(output, RawRequestMessage)
    return output
