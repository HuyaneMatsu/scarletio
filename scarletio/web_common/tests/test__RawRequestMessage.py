import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..helpers import HttpVersion
from ..http_message import RawRequestMessage


def _assert_fields_set(message):
    """
    Asserts whether every fields are set of the message.
    
    Parameters
    ----------
    message : ``RawRequestMessage``
        The message to test.
    """
    vampytest.assert_instance(message, RawRequestMessage)
    vampytest.assert_instance(message._cache_encoding, str, nullable = True)
    vampytest.assert_instance(message._cache_flags, int)
    vampytest.assert_instance(message.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(message.method, str)
    vampytest.assert_instance(message.path, str)
    vampytest.assert_instance(message.version, HttpVersion)


def test__RawRequestMessage__new():
    """
    Tests whether ``RawRequestMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    method = 'GET'
    path = 'orin'
    version = HttpVersion(1, 1)
    
    message = RawRequestMessage(
        version,
        path,
        method,
        headers,
    )
    _assert_fields_set(message)
    
    vampytest.assert_eq(message.headers, headers)


def test__RawRequestMessage__repr():
    """
    Tests whether ``RawRequestMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    method = 'GET'
    path = 'orin'
    version = HttpVersion(1, 1)
    
    message = RawRequestMessage(
        version,
        path,
        method,
        headers,
    )
    
    output = repr(message)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    method = 'GET'
    path = 'orin'
    version = HttpVersion(1, 1)
    
    keyword_parameters = {
        'headers': headers,
        'method': method,
        'path': path,
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
            'method': 'PUT',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'path': 'okuu',
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
def test__RawRequestMessage__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``RawRequestMessage.__eq__`` works as intended.
    
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
    message_0 = RawRequestMessage(**keyword_parameters_0)
    message_1 = RawRequestMessage(**keyword_parameters_1)
    
    output = message_0 == message_1
    vampytest.assert_instance(output, bool)
    return output
