from ssl import SSLContext, create_default_context as create_default_ssl_context

import vampytest

from ...web_common import URL

from ..connection_key import ConnectionKey
from ..proxy import Proxy
from ..ssl_fingerprint import SSLFingerprint


def _assert_fields_set(connection_key):
    """
    Tests whether every fields of the given connection key are received.
    
    Parameters
    ----------
    connection_key : ``ConnectionKey``
        The connect key to check.
    """
    vampytest.assert_instance(connection_key, ConnectionKey)
    vampytest.assert_instance(connection_key.host, str)
    vampytest.assert_instance(connection_key.port, int)
    vampytest.assert_instance(connection_key.proxy, Proxy, nullable = True)
    vampytest.assert_instance(connection_key.secure, bool)
    vampytest.assert_instance(connection_key.ssl_context, SSLContext, nullable = True)
    vampytest.assert_instance(connection_key.ssl_fingerprint, SSLFingerprint, nullable = True)


def test__ConnectionKey__new():
    """
    Tests whether ``ConnectionKey.__new__`` works as intended.
    """
    host = '1.1.1.1'
    port = 96
    proxy = Proxy(URL('https://orindance.party/'))
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    connection_key = ConnectionKey(
        host,
        port,
        proxy,
        secure,
        ssl_context,
        ssl_fingerprint,
    )
    
    _assert_fields_set(connection_key)
    
    vampytest.assert_eq(connection_key.host, host)
    vampytest.assert_eq(connection_key.port, port)
    vampytest.assert_eq(connection_key.proxy, proxy)
    vampytest.assert_eq(connection_key.secure, secure)
    vampytest.assert_eq(connection_key.ssl_context, ssl_context)
    vampytest.assert_eq(connection_key.ssl_fingerprint, ssl_fingerprint)


def test__ConnectionKey__repr():
    """
    Tests whether ``ConnectionKey.__repr__`` works as intended.
    """
    host = '1.1.1.1'
    port = 96
    proxy = Proxy(URL('https://orindance.party/'))
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    connection_key = ConnectionKey(
        host,
        port,
        proxy,
        secure,
        ssl_context,
        ssl_fingerprint,
    )
    
    output = repr(connection_key)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    host = '1.1.1.1'
    port = 96
    proxy = Proxy(URL('https://orindance.party/'))
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    keyword_parameters = {
        'host': host,
        'port': port,
        'proxy': proxy,
        'secure': secure,
        'ssl_context': ssl_context,
        'ssl_fingerprint': ssl_fingerprint,
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
            'host': '2.1.1.1',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'port': 97,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'proxy': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'secure': False,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ssl_context': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ssl_fingerprint': None,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ConnectionKey__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``ConnectionKey.__eq__`` works as intended.
    
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
    connection_key_0 = ConnectionKey(**keyword_parameters_0)
    connection_key_1 = ConnectionKey(**keyword_parameters_1)
    
    output = connection_key_0 == connection_key_1
    vampytest.assert_instance(output, bool)
    return output


def test__ConnectionKey__hash():
    """
    Tests whether ``ConnectionKey.__hash__`` works as intended.
    """
    host = '1.1.1.1'
    port = 96
    proxy = Proxy(URL('https://orindance.party/'))
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    connection_key = ConnectionKey(
        host,
        port,
        proxy,
        secure,
        ssl_context,
        ssl_fingerprint,
    )
    
    output = hash(connection_key)
    vampytest.assert_instance(output, int)


def test__ConnectionKey__copy_proxyless():
    """
    Tests whether ``ConnectionKey.copy_proxyless`` works as intended.
    """
    host = '1.1.1.1'
    port = 96
    proxy = Proxy(URL('https://orindance.party/'))
    secure = True
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    
    connection_key = ConnectionKey(
        host,
        port,
        proxy,
        secure,
        ssl_context,
        ssl_fingerprint,
    )
    
    copy = connection_key.copy_proxyless()
    _assert_fields_set(copy)
    vampytest.assert_is_not(copy, connection_key)
    
    vampytest.assert_eq(
        copy,
        ConnectionKey(
            host,
            port,
            None,
            secure,
            ssl_context,
            ssl_fingerprint,
        )
    )
