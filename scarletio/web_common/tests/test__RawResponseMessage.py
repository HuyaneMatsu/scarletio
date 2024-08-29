import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..helpers import HttpVersion
from ..http_message import RawResponseMessage


def _assert_fields_set(message):
    """
    Asserts whether every fields are set of the message.
    
    Parameters
    ----------
    message : ``RawResponseMessage``
        The message to test.
    """
    vampytest.assert_instance(message, RawResponseMessage)
    vampytest.assert_instance(message._cache_encoding, str, nullable = True)
    vampytest.assert_instance(message._cache_flags, int)
    vampytest.assert_instance(message.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(message.reason, str, nullable = True)
    vampytest.assert_instance(message.status, int)
    vampytest.assert_instance(message.version, HttpVersion)


def test__RawResponseMessage__new():
    """
    Tests whether ``RawResponseMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    reason = 'orin'
    status = 318
    version = HttpVersion(1, 1)
    
    message = RawResponseMessage(
        version,
        status,
        reason,
        headers,
    )
    _assert_fields_set(message)
    
    vampytest.assert_eq(message.headers, headers)


def test__RawResponseMessage__repr():
    """
    Tests whether ``RawResponseMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    reason = 'orin'
    status = 318
    version = HttpVersion(1, 1)
    
    message = RawResponseMessage(
        version,
        status,
        reason,
        headers,
    )
    
    output = repr(message)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    reason = 'orin'
    status = 318
    version = HttpVersion(1, 1)
    
    keyword_parameters = {
        'headers': headers,
        'reason': reason,
        'status': status,
        'version': version,
    }
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'headers': IgnoreCaseMultiValueDictionary(),
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'reason': 'okuu',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'status': 319,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'version': HttpVersion(1, 2),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__RawResponseMessage__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``RawResponseMessage.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    message_0 = RawResponseMessage(**keyword_parameters_0)
    message_1 = RawResponseMessage(**keyword_parameters_1)
    
    output = message_0 == message_1
    vampytest.assert_instance(output, bool)
    return output
