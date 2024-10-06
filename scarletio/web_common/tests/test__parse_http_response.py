import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..exceptions import PayloadError
from ..helpers import HttpVersion, parse_http_response
from ..http_message import RawResponseMessage


def _iter_options__passing():
    yield (
        b'HTTP/1.1 500 An error haz Okuued',
        RawResponseMessage(
            HttpVersion(1, 1),
            500,
            'An error haz Okuued',
            IgnoreCaseMultiValueDictionary(),
        ),
    )
    
    yield (
        b'HTTP/1.1 500',
        RawResponseMessage(
            HttpVersion(1, 1),
            500,
            None,
            IgnoreCaseMultiValueDictionary(),
        ),
    )
    
    yield (
        (
            b'HTTP/1.1 500\r\n'
            b'hey: mister'
        ),
        RawResponseMessage(
            HttpVersion(1, 1),
            500,
            None,
            IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
        ),
    )


def _iter_options__payload_error():
    yield b'MIAU/1.1 500'


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__payload_error()).raising(PayloadError))
def test__parse_http_response(data):
    """
    Tests whether ``parse_http_response`` works as intended.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    output : ``RawResponseMessage``
    
    Raises
    ------
    PayloadError
    """
    output = parse_http_response(data)
    vampytest.assert_instance(output, RawResponseMessage)
    return output
