import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..constants import KEEP_ALIVE_CONNECTION_TIMEOUT_KEY, KEEP_ALIVE_MAX_REQUESTS_KEY
from ..headers import CONNECTION, CONTENT_ENCODING, KEEP_ALIVE, TRANSFER_ENCODING, UPGRADE
from ..helpers import HttpVersion
from ..http_message import RawMessage
from ..keep_alive_info import KeepAliveInfo


def _assert_fields_set(message):
    """
    Asserts whether every fields are set of the message.
    
    Parameters
    ----------
    message : ``RawMessage``
        The message to test.
    """
    vampytest.assert_instance(message, RawMessage)
    vampytest.assert_instance(message._cache_encoding, str, nullable = True)
    vampytest.assert_instance(message._cache_flags, int)
    vampytest.assert_instance(message._cache_keep_alive, KeepAliveInfo, nullable = True)
    vampytest.assert_instance(message.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(message.version, HttpVersion)


def test__RawMessage__new():
    """
    Tests whether ``RawMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    _assert_fields_set(message)
    
    vampytest.assert_eq(message.headers, headers)
    vampytest.assert_eq(message.version, version)


def test__RawMessage__repr():
    """
    Tests whether ``RawMessage.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = repr(message)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    keyword_parameters = {
        'headers': headers,
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
            'version': HttpVersion(1, 2),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__RawMessage__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``RawMessage.__eq__`` works as intended.
    
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
    message_0 = RawMessage(**keyword_parameters_0)
    message_1 = RawMessage(**keyword_parameters_1)
    
    output = message_0 == message_1
    vampytest.assert_instance(output, bool)
    return output


def test__RawMessage__upgraded__false():
    """
    Tests whether ``RawMessage.upgraded`` works as intended.
    
    Case: false, missing connection.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
        (UPGRADE, 'yukari'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.upgraded
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__RawMessage__upgraded__false_missing_upgrade():
    """
    Tests whether ``RawMessage.upgraded`` works as intended.
    
    Case: false missing upgrade.
    """
    headers = IgnoreCaseMultiValueDictionary([
        (CONNECTION, 'upgrade'),
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.upgraded
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__RawMessage__upgraded__true():
    """
    Tests whether ``RawMessage.upgraded`` works as intended.
    
    Case: true.
    """
    headers = IgnoreCaseMultiValueDictionary([
        (CONNECTION, 'upgrade'),
        (UPGRADE, 'yukari'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.upgraded
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__RawMessage__upgraded__set():
    """
    Tests whether ``RawMessage.upgraded`` works as intended.
    
    Case: setting it.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    message.upgraded = True
    
    output = message.upgraded
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__RawMessage__chunked__false():
    """
    Tests whether ``RawMessage.chunked`` works as intended.
    
    Case: false.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.chunked
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__RawMessage__chunked__true():
    """
    Tests whether ``RawMessage.chunked`` works as intended.
    
    Case: true.
    """
    headers = IgnoreCaseMultiValueDictionary([
        (TRANSFER_ENCODING, 'chunked'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.chunked
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__RawMessage__chunked__set():
    """
    Tests whether ``RawMessage.chunked`` works as intended.
    
    Case: setting it.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    message.chunked = True
    
    output = message.chunked
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__RawMessage__encoding__missing():
    """
    Tests whether ``RawMessage.encoding`` works as intended.
    
    Case: missing.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.encoding
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(message._cache_encoding, output)
    vampytest.assert_eq(output, None)


def test__RawMessage__encoding__has():
    """
    Tests whether ``RawMessage.encoding`` works as intended.
    
    Case: has.
    """
    headers = IgnoreCaseMultiValueDictionary([
        (CONTENT_ENCODING, 'utf-8'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    output = message.encoding
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(message._cache_encoding, output)
    vampytest.assert_eq(output, 'utf-8')


def test__RawMessage__encoding__set():
    """
    Tests whether ``RawMessage.encoding`` works as intended.
    
    Case: set.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    message.encoding = 'utf-8'
    
    output = message.encoding
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(output, 'utf-8')


def _iter_options__keep_alive():
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
            'version': HttpVersion(1, 1),
        },
        KeepAliveInfo.create_default(),
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                ('hey', 'mister'),
            ]),
            'version': HttpVersion(1, 0),
        },
        None,
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                (CONNECTION, 'close'),
            ]),
            'version': HttpVersion(1, 1),
        },
        None,
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                (CONNECTION, 'close'),
            ]),
            'version': HttpVersion(1, 0),
        },
        None,
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                (CONNECTION, 'keep-alive'),
            ]),
            'version': HttpVersion(1, 1),
        },
        KeepAliveInfo.create_default(),
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                (CONNECTION, 'keep-alive'),
            ]),
            'version': HttpVersion(1, 0),
        },
        KeepAliveInfo.create_default(),
    )
    
    yield (
        {
            'headers': IgnoreCaseMultiValueDictionary([
                (KEEP_ALIVE, f'{KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5,{KEEP_ALIVE_MAX_REQUESTS_KEY}=1000'),
            ]),
            'version': HttpVersion(1, 1),
        },
        KeepAliveInfo(5.0, 1000),
    )


@vampytest._(vampytest.call_from(_iter_options__keep_alive()).returning_last())
def test__RawMessage__keep_alive(keyword_parameters):
    """
    Tests whether ``RawMessage.keep_alive`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create the instance with.
    
    Returns
    -------
    output : `bool`
    """
    message = RawMessage(**keyword_parameters)
    
    output = message.keep_alive
    vampytest.assert_instance(output, KeepAliveInfo, nullable = True)
    vampytest.assert_eq(message._cache_keep_alive, output)
    return output


def test__RawMessage__keep_alive__set():
    """
    Tests whether ``RawMessage.keep_alive`` works as intended.
    
    Case: setting it.
    """
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    version = HttpVersion(1, 1)
    
    message = RawMessage(
        version,
        headers,
    )
    
    message.keep_alive = KeepAliveInfo(10.0, 20)
    
    output = message.keep_alive
    vampytest.assert_instance(output, KeepAliveInfo, nullable = True)
    vampytest.assert_eq(message._cache_keep_alive, output)
    vampytest.assert_eq(output, KeepAliveInfo(10.0, 20))
