from ssl import SSLContext, create_default_context as create_default_ssl_context

import vampytest

from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import BasicAuthorization, URL

from ..ssl_fingerprint import SSLFingerprint
from ..proxy import Proxy


def _assert_fields_set(proxy):
    """
    Asserts whether every fields of the given proxy are set.
    
    Parameters
    ----------
    proxy : ``Proxy``
        The proxy to test.
    """
    vampytest.assert_instance(proxy, Proxy)
    vampytest.assert_instance(proxy._hash_cache, int, nullable = True)
    vampytest.assert_instance(proxy.authorization, BasicAuthorization, nullable = True)
    vampytest.assert_instance(proxy.headers, IgnoreCaseMultiValueDictionary, nullable = True)
    vampytest.assert_instance(proxy.ssl_context, SSLContext, nullable = True)
    vampytest.assert_instance(proxy.ssl_fingerprint, SSLFingerprint, nullable = True)
    vampytest.assert_instance(proxy.url, URL)


def test__Proxy__new():
    """
    Tests whether ``Proxy.__new__`` works as intended.
    """
    authorization = BasicAuthorization('koishi', 'eye')
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    url = URL('https://orindance.party/#mister')
    
    proxy = Proxy(
        url,
        authorization = authorization,
        headers = headers,
        ssl_context = ssl_context,
        ssl_fingerprint = ssl_fingerprint,
    )
    _assert_fields_set(proxy)
    
    vampytest.assert_eq(proxy.authorization, authorization)
    vampytest.assert_eq(proxy.headers, headers)
    vampytest.assert_eq(proxy.ssl_context, ssl_context)
    vampytest.assert_eq(proxy.ssl_fingerprint, ssl_fingerprint)
    vampytest.assert_eq(proxy.url, url)


def test__Proxy__repr():
    """
    Tests whether ``Proxy.__repr__`` works as intended.
    """
    authorization = BasicAuthorization('koishi', 'eye')
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    url = URL('https://orindance.party/#mister')
    
    proxy = Proxy(
        url,
        authorization = authorization,
        headers = headers,
        ssl_context = ssl_context,
        ssl_fingerprint = ssl_fingerprint,
    )
    
    output = repr(proxy)
    vampytest.assert_instance(output, str)


def test__Proxy__hash():
    """
    Tests whether ``Proxy.__hash__`` works as intended.
    """
    authorization = BasicAuthorization('koishi', 'eye')
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    url = URL('https://orindance.party/#mister')
    
    proxy = Proxy(
        url,
        authorization = authorization,
        headers = headers,
        ssl_context = ssl_context,
        ssl_fingerprint = ssl_fingerprint,
    )
    
    output = hash(proxy)
    vampytest.assert_instance(output, int)


def _iter_options__eq():
    authorization = BasicAuthorization('koishi', 'eye')
    headers = IgnoreCaseMultiValueDictionary([
        ('hey', 'mister'),
    ])
    ssl_context = create_default_ssl_context()
    ssl_fingerprint = SSLFingerprint(b'a' * 32)
    url = URL('https://orindance.party/#mister')
    
    keyword_parameters = {
        'authorization': authorization,
        'headers': headers,
        'ssl_context': ssl_context,
        'ssl_fingerprint': ssl_fingerprint,
        'url': url,
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
            'authorization': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'headers': None,
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
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'url': URL('https://orindance.party/#sister'),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Proxy__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Proxy.__eq__`` works as intended.
    
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
    proxy_0 = Proxy(**keyword_parameters_0)
    proxy_1 = Proxy(**keyword_parameters_1)
    
    output = proxy_0 == proxy_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__host():
    yield(
        URL('https://orindance.party/'),
        'orindance.party',
    )
    
    yield(
        URL('http://1.1.1.1/'),
        '1.1.1.1',
    )
    
    yield(
        URL('https://orindance.party:99/'),
        'orindance.party',
    )
    
    yield(
        URL('https://1.1.1.1:99/'),
        '1.1.1.1',
    )


@vampytest._(vampytest.call_from(_iter_options__host()).returning_last())
def test__ClientResponse__host(url):
    """
    Tests whether ``Proxy.host`` works as intended.
    
    
    Parameters
    ----------
    url : ``URL``
        Url to create proxy with.
    
    Returns
    -------
    output : `str`
    """
    # Construct
    proxy = Proxy(
        url,
    )
    
    output = proxy.host
    vampytest.assert_instance(output, str)
    return output


def _iter_options__port():
    yield(
        URL('https://orindance.party/'),
        443,
    )
    
    yield(
        URL('http://1.1.1.1/'),
        80,
    )
    
    yield(
        URL('https://orindance.party:99/'),
        99,
    )
    
    yield(
        URL('https://1.1.1.1:99/'),
        99,
    )


@vampytest._(vampytest.call_from(_iter_options__port()).returning_last())
def test__ClientResponse__port(url):
    """
    Tests whether ``Proxy.port`` works as intended.
    
    Parameters
    ----------
    url : ``URL``
        Url to create proxy with.
    
    Returns
    -------
    output : `int`
    """
    proxy = Proxy(
        url,
    )
    
    output = proxy.port
    vampytest.assert_instance(output, int)
    return output


def _iter_options__is_secure():
    yield (
        URL('http://orindance.party/'),
        None,
        False,
    )
    
    yield (
        URL('ws://orindance.party/'),
        None,
        False,
    )
    
    yield (
        URL('https://orindance.party/'),
        None,
        True,
    )
    
    yield (
        URL('wss://orindance.party/'),
        None,
        True,
    )
    
    yield (
        URL('orindance.party/'),
        create_default_ssl_context(),
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__is_secure()).returning_last())
def test__Proxy__is_secure(url, ssl_context):
    """
    Tests whether ``Proxy.is_secure`` works as intended.
    
    Parameters
    ----------
    url : ``URL``
        Url to create proxy with.
    
    ssl_context : `None | SSLContext`
        Ssl context to create the proxy with.
    
    Returns
    -------
    output : `bool`
    """
    proxy = Proxy(
        url,
        ssl_context = ssl_context,
    )
    
    output = proxy.is_secure()
    vampytest.assert_instance(output, bool)
    return output
