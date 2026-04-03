import vampytest

from ....utils import MultiValueDictionary

from ..url import URL

from ..url_fragment import URLFragment
from ..url_host_info import URLHostInfo
from ..url_path import URLPath
from ..url_query import URLQuery
from ..url_user_info import URLUserInfo


def _assert_fields_set(url):
    """
    Asserts whether the given url has all of its fields set.
    
    Parameters
    ----------
    url : ``URL``
        The url to test.
    """
    vampytest.assert_instance(url, URL)
    vampytest.assert_instance(url._cache, dict, nullable = True)
    vampytest.assert_instance(url._fragment, URLFragment, nullable = True)
    vampytest.assert_instance(url._host, URLHostInfo, nullable = True)
    vampytest.assert_instance(url._path, URLPath, nullable = True)
    vampytest.assert_instance(url._port, int, nullable = True)
    vampytest.assert_instance(url._query, URLQuery, nullable = True)
    vampytest.assert_instance(url._scheme, str, nullable = True)
    vampytest.assert_instance(url._user, URLUserInfo, nullable = True)



def test__URL__new__empty_string():
    """
    Tests whether ``URL.__new__`` works as intended.
    
    Case: empty string.
    """
    url = URL()
    _assert_fields_set(url)


def test__URL__new__string():
    """
    Tests whether ``URL.__new__`` works as intended.
    
    Case: string.
    """
    value = 'https://orindance.party/'
    
    url = URL(value)
    _assert_fields_set(url)


def test__URL__new__url():
    """
    Tests whether ``URL.__new__`` works as intended.
    
    Case: url.
    """
    value = 'https://orindance.party/'
    
    url_0 = URL(value)
    url_1 = URL(url_0)
    
    vampytest.assert_is(url_0, url_1)


def _iter_options__value_encoded():
    yield (
        '',
        True,
        '',
    )
    
    yield (
        '',
        False,
        '',
    )
    
    yield (
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
        True,
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
    )
    
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        False,
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
    )
    
    yield (
        'https://orindance.party./',
        False,
        'https://orindance.party./',
    )
    
    yield (
        'https://orindance.party../',
        False,
        'https://orindance.party./',
    )
    
    yield (
        'https://localhost./',
        False,
        'https://localhost./',
    )
    
    yield (
        'https://localhost../',
        False,
        'https://localhost./',
    )


@vampytest._(vampytest.call_from(_iter_options__value_encoded()).returning_last())
def test__URL__value_encoded(input_value, encoded):
    """
    Tests whether ``URL.value_encoded`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value, encoded)
    output = url.value_encoded
    vampytest.assert_instance(output, str)
    return output


def _iter_options__value_decoded():
    yield (
        '',
        True,
        '',
    )
    
    yield (
        '',
        False,
        '',
    )
    
    yield (
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
        True,
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
    )
    
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        False,
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
    )
    
    yield (
        'https://orindance.party./',
        False,
        'https://orindance.party./',
    )
    
    yield (
        'https://orindance.party../',
        False,
        'https://orindance.party./',
    )
    
    yield (
        'https://localhost./',
        False,
        'https://localhost./',
    )
    
    yield (
        'https://localhost../',
        False,
        'https://localhost./',
    )


@vampytest._(vampytest.call_from(_iter_options__value_decoded()).returning_last())
def test__URL__value_decoded(input_value, encoded):
    """
    Tests whether ``URL.value_decoded`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value, encoded)
    output = url.value_decoded
    vampytest.assert_instance(output, str)
    return output


def _iter_options__str():
    yield (
        '',
        True,
        '',
    )
    
    yield (
        '',
        False,
        '',
    )
    
    yield (
        'https://orindance.party',
        False,
        'https://orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        True,
        'https://orindance.party/',
    )
    
    yield (
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
        True,
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
    )
    
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        False,
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
    )


@vampytest._(vampytest.call_from(_iter_options__str()).returning_last())
def test__URL__str(input_value, encoded):
    """
    Tests whether ``URL.__str__`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value, encoded)
    output = str(url)
    vampytest.assert_instance(output, str)
    return output


def _in_url(value):
    return ''.join([URL.__name__, '(', repr(value), ')'])


def _iter_options__repr():
    yield (
        '',
        True,
        _in_url(''),
    )
    
    yield (
        '',
        False,
        _in_url(''),
    )
    
    yield (
        'https://orindance.party',
        False,
        _in_url('https://orindance.party/'),
    )
    
    yield (
        'https://orindance.party',
        True,
        _in_url('https://orindance.party/'),
    )
    
    yield (
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
        True,
        _in_url('https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű'),
    )
    
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        False,
        _in_url('https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű'),
    )


@vampytest._(vampytest.call_from(_iter_options__repr()).returning_last())
def test__URL__repr(input_value, encoded):
    """
    Tests whether ``URL.__repr__`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `repr`
    """
    url = URL(input_value, encoded)
    output = repr(url)
    vampytest.assert_instance(output, str)
    return output


def test__URL__hash():
    """
    Tests whether ``URL.__hash__`` works as intended.
    """
    input_value = 'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű'
    url = URL(input_value, False)
    output = hash(url)
    vampytest.assert_instance(output, int)


def _iter_options__bool():
    yield (
        '',
        True,
        False,
    )
    
    yield (
        '',
        False,
        False,
    )
    
    yield (
        'https://hey%C5%B1:mister%C5%B1@orindance.party:69/mia%C5%B1/u%C5%B1/?nyan%C5%B1=true%C5%B1#there%C5%B1',
        True,
        True,
    )
    
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        False,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__bool()).returning_last())
def test__URL__bool(input_value, encoded):
    """
    Tests whether ``URL.__bool__`` works as intended.
    
    Parameters
    ----------
    input_value : `bool`
        Value to create url from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `bool`
    """
    url = URL(input_value, encoded)
    output = bool(url)
    vampytest.assert_instance(output, bool)
    return output


def test__URL__sorting():
    """
    Tests whether ``URL`` sorting works as intended.
    """
    url_0 = URL('https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű')
    url_1 = URL('https://heyű:misterű@orindance.party:69/miaűű/uű/?nyanű=trueű#thereű')
    url_2 = URL('https://heyű:misterű@orindance.party:69/miaűűű/uű/?nyanű=trueű#thereű')
    
    input_value = [
        url_0,
        url_1,
        url_2,
        url_2,
        url_1,
        url_0,
    ]
    
    expected_output = [
        url_2,
        url_2,
        url_1,
        url_1,
        url_0,
        url_0,
    ]
    
    vampytest.assert_eq(
        sorted(input_value),
        expected_output,
    )


def test__Url__truediv():
    """
    Tests whether ``Url.__truediv__`` works as intended.
    """
    url = URL('https://heyű:misterű@orindance.party:69')
    
    output = url / 'hey'
    
    vampytest.assert_instance(output, URL)
    vampytest.assert_eq(
        output,
        URL('https://heyű:misterű@orindance.party:69/hey')
    )
    
    url = output
    
    output = url / 'mister'
    
    vampytest.assert_instance(output, URL)
    vampytest.assert_eq(
        output,
        URL('https://heyű:misterű@orindance.party:69/hey/mister')
    )


def _iter_options__is_absolute():
    yield (
        '',
        False,
    )
    
    yield (
        'https://orindance.party',
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__is_absolute()).returning_last())
def test__Url__is_absolute(input_value):
    """
    Tests whether ``Url.is_absolute`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    is_absolute : `bool`
    """
    url = URL(input_value)
    output = url.is_absolute()
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__is_default_port():
    yield (
        '',
        False,
    )
    
    yield (
        'https://orindance.party',
        True,
    )
    
    yield (
        'http://orindance.party',
        True,
    )
    
    yield (
        'wss://orindance.party',
        True,
    )
    
    yield (
        'ws://orindance.party',
        True,
    )
    
    yield (
        'https://orindance.party:443',
        True,
    )
    
    yield (
        'http://orindance.party:80',
        True,
    )
    
    yield (
        'wss://orindance.party:443',
        True,
    )
    
    yield (
        'ws://orindance.party:80',
        True,
    )
    
    yield (
        'osd://orindance.party',
        False,
    )
    
    yield (
        'http://orindance.party:99',
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__is_default_port()).returning_last())
def test__Url__is_default_port(input_value):
    """
    Tests whether ``Url.is_default_port`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    is_default_port : `bool`
    """
    url = URL(input_value)
    output = url.is_default_port()
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__is_host_ip_v4():
    yield (
        '',
        False,
    )
    
    yield (
        'https://orindance.party',
        False,
    )
    
    yield (
        '1.1.1.1',
        True,
    )
    
    yield (
        '[::2]',
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__is_host_ip_v4()).returning_last())
def test__Url__is_host_ip_v4(input_value):
    """
    Tests whether ``Url.is_host_ip_v4`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    is_host_ip_v4 : `bool`
    """
    url = URL(input_value)
    output = url.is_host_ip_v4()
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__is_host_ip_v6():
    yield (
        '',
        False,
    )
    
    yield (
        'https://orindance.party',
        False,
    )
    
    yield (
        '1.1.1.1',
        False,
    )
    
    yield (
        '[::2]',
        True,
    )


def _iter_options__is_host_ip():
    yield (
        '',
        False,
    )
    
    yield (
        'https://orindance.party',
        False,
    )
    
    yield (
        '1.1.1.1',
        True,
    )
    
    yield (
        '[::2]',
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__is_host_ip()).returning_last())
def test__Url__is_host_ip(input_value):
    """
    Tests whether ``Url.is_host_ip`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    is_host_ip : `bool`
    """
    url = URL(input_value)
    output = url.is_host_ip()
    vampytest.assert_instance(output, bool)
    return output


@vampytest._(vampytest.call_from(_iter_options__is_host_ip_v6()).returning_last())
def test__Url__is_host_ip_v6(input_value):
    """
    Tests whether ``Url.is_host_ip_v6`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    is_host_ip_v6 : `bool`
    """
    url = URL(input_value)
    output = url.is_host_ip_v6()
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__origin__passing():
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        'https://orindance.party:69/',
    )


def _iter_options__origin__value_error():
    yield ''


@vampytest._(vampytest.call_from(_iter_options__origin__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__origin__value_error()).raising(ValueError))
def test__URL__origin(input_value):
    """
    Tests whether ``URL.origin`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value)
    output = url.origin()
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__relative__passing():
    yield (
        'https://heyű:misterű@orindance.party:69/miaű/uű/?nyanű=trueű#thereű',
        '/miaű/uű/?nyanű=trueű#thereű',
    )


def _iter_options__relative__value_error():
    yield ''


@vampytest._(vampytest.call_from(_iter_options__relative__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__relative__value_error()).raising(ValueError))
def test__URL__relative(input_value):
    """
    Tests whether ``URL.relative`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to create url from.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value)
    output = url.relative()
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__scheme():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party',
        'https',
    )
    
    yield (
        'osd://orindance.party',
        'osd',
    )


@vampytest._(vampytest.call_from(_iter_options__scheme()).returning_last())
def test__Url__scheme(input_value):
    """
    Tests whether ``Url.scheme`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.scheme
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__raw_user():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://heyű:misterű@orindance.party',
        'hey%C5%B1',
    )
    
    yield (
        'https://:misterű@orindance.party',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__raw_user()).returning_last())
def test__Url__raw_user(input_value):
    """
    Tests whether ``Url.raw_user`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_user
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__user():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://heyű:misterű@orindance.party',
        'heyű',
    )
    
    yield (
        'https://:misterű@orindance.party',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__user()).returning_last())
def test__Url__user(input_value):
    """
    Tests whether ``Url.user`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.user
    vampytest.assert_instance(output, str, nullable = True)
    return output



def _iter_options__raw_password():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://heyű:misterű@orindance.party',
        'mister%C5%B1',
    )
    
    yield (
        'https://heyű:@orindance.party',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__raw_password()).returning_last())
def test__Url__raw_password(input_value):
    """
    Tests whether ``Url.raw_password`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_password
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__password():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://heyű:misterű@orindance.party',
        'misterű',
    )
    
    yield (
        'https://heyű:@orindance.party',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__password()).returning_last())
def test__Url__password(input_value):
    """
    Tests whether ``Url.password`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.password
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__raw_host():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        'orindance.party',
    )
    
    yield (
        'https://orindanceű.party',
        'xn--orindance-e8b.party',
    )
    
    yield (
        'https://nyan.nyanű.orindance.party',
        'nyan.xn--nyan-t8a.orindance.party',
    )
    
    yield (
        'https://hey:mister@1.1.1.1:8000',
        '1.1.1.1',
    )


@vampytest._(vampytest.call_from(_iter_options__raw_host()).returning_last())
def test__Url__raw_host(input_value):
    """
    Tests whether ``Url.raw_host`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_host
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__host():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        'orindance.party',
    )
    
    yield (
        'https://orindanceű.party',
        'orindanceű.party',
    )
    
    yield (
        'https://nyan.nyanű.orindance.party',
        'nyan.nyanű.orindance.party',
    )
    
    yield (
        'https://hey:mister@1.1.1.1:8000',
        '1.1.1.1',
    )


@vampytest._(vampytest.call_from(_iter_options__host()).returning_last())
def test__Url__host(input_value):
    """
    Tests whether ``Url.host`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.host
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__raw_sub_domain():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://orindanceű.party',
        None,
    )
    
    yield (
        'https://nyan.nyanű.orindance.party',
        'nyan.xn--nyan-t8a',
    )
    
    yield (
        'https://hey:mister@1.1.1.1:8000',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__raw_sub_domain()).returning_last())
def test__Url__raw_sub_domain(input_value):
    """
    Tests whether ``Url.raw_sub_domain`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_sub_domain
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__sub_domain():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://orindanceű.party',
        None,
    )
    
    yield (
        'https://nyan.nyanű.orindance.party',
        'nyan.nyanű',
    )
    
    yield (
        'https://hey:mister@1.1.1.1:8000',
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__sub_domain()).returning_last())
def test__Url__sub_domain(input_value):
    """
    Tests whether ``Url.sub_domain`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.sub_domain
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__port():
    yield (
        '',
        None,
    )
    
    yield (
        'osd://orindance.party',
        None,
    )
    
    yield (
        'https://orindanceű.party',
        443,
    )
    
    yield (
        'https://hey:mister@1.1.1.1:8000',
        8000,
    )


@vampytest._(vampytest.call_from(_iter_options__port()).returning_last())
def test__Url__port(input_value):
    """
    Tests whether ``Url.port`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | int`
    """
    url = URL(input_value)
    output = url.port
    vampytest.assert_instance(output, int, nullable = True)
    return output


def _iter_options__raw_path():
    yield (
        '',
        '/',
    )
    
    yield (
        'https://orindance.party',
        '/',
    )
    
    yield (
        'https://orindance.party/',
        '/',
    )
    
    yield (
        'https://orindance.party/heyű/mister',
        '/hey%C5%B1/mister',
    )


@vampytest._(vampytest.call_from(_iter_options__raw_path()).returning_last())
def test__Url__raw_path(input_value):
    """
    Tests whether ``Url.raw_path`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_path
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__path():
    yield (
        '',
        '/',
    )
    
    yield (
        'https://orindance.party',
        '/',
    )
    
    yield (
        'https://orindance.party/',
        '/',
    )
    
    yield (
        'https://orindance.party/heyű/mister',
        '/heyű/mister',
    )


@vampytest._(vampytest.call_from(_iter_options__path()).returning_last())
def test__Url__path(input_value):
    """
    Tests whether ``Url.path`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.path
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__query():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party?',
        None,
    )
    
    yield (
        'https://orindance.party?&&&',
        None,
    )
    
    yield (
        'https://orindance.party/?heyű=mister',
        MultiValueDictionary([
            ('heyű', 'mister'),
        ])
    )


@vampytest._(vampytest.call_from(_iter_options__query()).returning_last())
def test__Url__query(input_value):
    """
    Tests whether ``Url.query`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | MultiValueDictionary<str, str>`
    """
    url = URL(input_value)
    output = url.query
    vampytest.assert_instance(output, MultiValueDictionary, nullable = True)
    return output


def _iter_options__raw_query_string():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party?',
        None,
    )
    
    yield (
        'https://orindance.party?&&&',
        None,
    )
    
    yield (
        'https://orindance.party/?heyű=mister',
        'hey%C5%B1=mister',
    )


@vampytest._(vampytest.call_from(_iter_options__raw_query_string()).returning_last())
def test__Url__raw_query_string(input_value):
    """
    Tests whether ``Url.raw_query_string`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_query_string
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__query_string():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party?',
        None,
    )
    
    yield (
        'https://orindance.party?&&&',
        None,
    )
    
    yield (
        'https://orindance.party/?heyű=mister',
        'heyű=mister',
    )


@vampytest._(vampytest.call_from(_iter_options__query_string()).returning_last())
def test__Url__query_string(input_value):
    """
    Tests whether ``Url.query_string`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.query_string
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__raw_fragment():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party#',
        None,
    )
    
    yield (
        'https://orindance.party###',
        '##',
    )
    
    yield (
        'https://orindance.party#hey',
        'hey',
    )
    
    yield (
        'https://orindance.party/#heyű',
        'hey%C5%B1',
    )


@vampytest._(vampytest.call_from(_iter_options__raw_fragment()).returning_last())
def test__Url__raw_fragment(input_value):
    """
    Tests whether ``Url.raw_fragment`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.raw_fragment
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__fragment():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party#',
        None,
    )
    
    yield (
        'https://orindance.party###',
        '##',
    )
    
    yield (
        'https://orindance.party#hey',
        'hey',
    )
    
    yield (
        'https://orindance.party/#heyű',
        'heyű',
    )


@vampytest._(vampytest.call_from(_iter_options__fragment()).returning_last())
def test__Url__fragment(input_value):
    """
    Tests whether ``Url.fragment`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    url = URL(input_value)
    output = url.fragment
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__parts():
    yield (
        '',
        None,
    )
    
    yield (
        'https://orindance.party',
        None,
    )
    
    yield (
        'https://orindance.party/',
        None,
    )
    
    yield (
        'https://orindance.party//',
        ('',),
    )
    
    yield (
        'https://orindance.party/heyű/mister',
        ('heyű', 'mister'),
    )
    
    yield (
        'https://orindance.party/heyű/mister/',
        ('heyű', 'mister', ''),
    )


@vampytest._(vampytest.call_from(_iter_options__parts()).returning_last())
def test__Url__parts(input_value):
    """
    Tests whether ``Url.parts`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `None | tuple`
    """
    url = URL(input_value)
    output = url.parts
    vampytest.assert_instance(output, tuple, nullable = True)
    return output


def _iter_options__parent():
    yield (
        '',
        '',
    )
    
    yield (
        'https://orindance.party',
        'https://orindance.party/',
    )
    
    yield (
        'https://orindance.party/',
        'https://orindance.party/',
    )
    
    yield (
        'https://orindance.party/heyű/mister',
        'https://orindance.party/heyű',
    )


@vampytest._(vampytest.call_from(_iter_options__parent()).returning_last())
def test__Url__parent(input_value):
    """
    Tests whether ``Url.parent`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value)
    output = url.parent
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__name():
    yield (
        '',
        '',
    )
    
    yield (
        'https://orindance.party',
        '',
    )
    
    yield (
        'https://orindance.party/',
        '',
    )
    
    yield (
        'https://orindance.party/heyű/misterű',
        'misterű',
    )


@vampytest._(vampytest.call_from(_iter_options__name()).returning_last())
def test__Url__name(input_value):
    """
    Tests whether ``Url.name`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    Returns
    -------
    output : `str`
    """
    url = URL(input_value)
    output = url.name
    vampytest.assert_instance(output, str)
    return output


def _iter_options__with_scheme__passing():
    yield (
        'https://orindance.party',
        None,
        'orindance.party/',
    )
    
    yield (
        'https://orindance.party/hey',
        '',
        'orindance.party/hey',
    )
    
    yield (
        'https://orindance.party/hey',
        'mister',
        'mister://orindance.party/hey',
    )


def _iter_options__with_scheme__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_scheme__value_error():
    yield (
        '',
        'mister',
    )


@vampytest._(vampytest.call_from(_iter_options__with_scheme__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_scheme__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_scheme__value_error()).raising(ValueError))
def test__Url__with_scheme(input_value, scheme):
    """
    Tests whether ``Url.with_scheme`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    scheme : `object`
        New scheme for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_scheme(scheme)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_user__passing():
    yield (
        'https://hey:mister@orindance.party',
        None,
        'https://:mister@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        None,
        'https://orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        None,
        'https://:mister@orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        None,
        'https://orindance.party/',
    )
    
    yield (
        'https://hey:mister@orindance.party',
        '',
        'https://:mister@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        '',
        'https://orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        '',
        'https://:mister@orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        '',
        'https://orindance.party/',
    )
    
    yield (
        'https://hey:mister@orindance.party',
        'sister',
        'https://sister:mister@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        'sister',
        'https://sister:@orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        'sister',
        'https://sister:mister@orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        'sister',
        'https://sister:@orindance.party/',
    )


def _iter_options__with_user__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_user__value_error():
    yield (
        '',
        'mister',
    )


@vampytest._(vampytest.call_from(_iter_options__with_user__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_user__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_user__value_error()).raising(ValueError))
def test__Url__with_user(input_value, user):
    """
    Tests whether ``Url.with_user`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    user : `object`
        New user for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_user(user)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_password__passing():
    yield (
        'https://hey:mister@orindance.party',
        None,
        'https://hey:@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        None,
        'https://hey:@orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        None,
        'https://orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        None,
        'https://orindance.party/',
    )
    
    yield (
        'https://hey:mister@orindance.party',
        '',
        'https://hey:@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        '',
        'https://hey:@orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        '',
        'https://orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        '',
        'https://orindance.party/',
    )
    
    yield (
        'https://hey:mister@orindance.party',
        'sister',
        'https://hey:sister@orindance.party/',
    )
    
    yield (
        'https://hey:@orindance.party',
        'sister',
        'https://hey:sister@orindance.party/',
    )
    
    yield (
        'https://:mister@orindance.party',
        'sister',
        'https://:sister@orindance.party/',
    )
    
    yield (
        'https://orindance.party',
        'sister',
        'https://:sister@orindance.party/',
    )


def _iter_options__with_password__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_password__value_error():
    yield (
        '',
        'mister',
    )


@vampytest._(vampytest.call_from(_iter_options__with_password__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_password__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_password__value_error()).raising(ValueError))
def test__Url__with_password(input_value, password):
    """
    Tests whether ``Url.with_password`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    password : `object`
        New password for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_password(password)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_host__passing():
    yield (
        'https://hey:mister@orindance.party:8000',
        '1.1.1.1',
        'https://hey:mister@1.1.1.1:8000/',
    )


def _iter_options__with_host__type_error():
    yield (
        'https://orindance.party',
        object(),
    )
    
    yield (
        'https://orindance.party',
        None,
    )


def _iter_options__with_host__value_error():
    yield (
        'https://orindance.party',
        '',
    )
    
    yield (
        '',
        'orindance.party',
    )


@vampytest._(vampytest.call_from(_iter_options__with_host__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_host__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_host__value_error()).raising(ValueError))
def test__Url__with_host(input_value, host):
    """
    Tests whether ``Url.with_host`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    host : `object`
        New host for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_host(host)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_port__passing():
    yield (
        'https://hey:mister@orindance.party:8000',
        1000,
        'https://hey:mister@orindance.party:1000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        None,
        'https://hey:mister@orindance.party/',
    )


def _iter_options__with_port__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_port__value_error():
    yield (
        'https://orindance.party',
        -1,
    )
    
    yield (
        '',
        1000,
    )


@vampytest._(vampytest.call_from(_iter_options__with_port__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_port__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_port__value_error()).raising(ValueError))
def test__Url__with_port(input_value, port):
    """
    Tests whether ``Url.with_port`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    port : `object`
        New port for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_port(port)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_query__passing():
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        None,
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        '',
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        'hey=mister',
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        {'hey': 'mister'},
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        {'hey': 'sister'},
        'https://hey:mister@orindance.party:8000/?hey=sister',
    )


def _iter_options__with_query__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_query__value_error():
    return
    yield


@vampytest._(vampytest.call_from(_iter_options__with_query__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_query__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_query__value_error()).raising(ValueError))
def test__Url__with_query(input_value, query):
    """
    Tests whether ``Url.with_query`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    query : `object`
        New query for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_query(query)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_fragment__passing():
    yield (
        'https://hey:mister@orindance.party:8000#mister',
        None,
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000#mister',
        '',
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        'mister',
        'https://hey:mister@orindance.party:8000/#mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        'mister',
        'https://hey:mister@orindance.party:8000/#mister',
    )
    yield (
        'https://hey:mister@orindance.party:8000#mister',
        'sister',
        'https://hey:mister@orindance.party:8000/#sister',
    )


def _iter_options__with_fragment__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__with_fragment__value_error():
    return
    yield


@vampytest._(vampytest.call_from(_iter_options__with_fragment__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_fragment__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_fragment__value_error()).raising(ValueError))
def test__Url__with_fragment(input_value, fragment):
    """
    Tests whether ``Url.with_fragment`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    fragment : `object`
        New fragment for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_fragment(fragment)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__with_name__passing():
    yield (
        'https://hey:mister@orindance.party:8000/',
        'mister',
        'https://hey:mister@orindance.party:8000/mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000/mister',
        '',
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        '',
        'https://hey:mister@orindance.party:8000/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        'mister',
        'https://hey:mister@orindance.party:8000/mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000/hey/',
        'mister',
        'https://hey:mister@orindance.party:8000/hey/mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000/hey/mister',
        'sister',
        'https://hey:mister@orindance.party:8000/hey/sister',
    )


def _iter_options__with_name__type_error():
    yield (
        'https://orindance.party',
        object(),
    )
    
    yield (
        'https://orindance.party',
        None,
    )


def _iter_options__with_name__value_error():
    return
    yield


@vampytest._(vampytest.call_from(_iter_options__with_name__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__with_name__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__with_name__value_error()).raising(ValueError))
def test__Url__with_name(input_value, name):
    """
    Tests whether ``Url.with_name`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    name : `object`
        New name for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.with_name(name)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__join__passing():
    yield (
        'https://hey:mister@orindance.party:8000/hey/mister?size=420#right-there',
        'https://orindance.party//',
        True,
        'https://hey:mister@orindance.party:8000/hey/mister/',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000/hey/mister?size=420#right-there',
        '',
        True,
        'https://hey:mister@orindance.party:8000/hey/mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000/hey/mister',
        'https://orindance.party?size=420#right-there',
        True,
        'https://hey:mister@orindance.party:8000/hey/mister?size=420#right-there',
    )


def _iter_options__join__type_error():
    yield (
        'https://orindance.party',
        object(),
        False,
    )
    
    yield (
        'https://orindance.party',
        None,
        False,
    )
    
    yield (
        'https://orindance.party',
        '',
        False,
    )


def _iter_options__join__value_error():
    return
    yield


@vampytest._(vampytest.call_from(_iter_options__join__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__join__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__join__value_error()).raising(ValueError))
def test__Url__join(input_value, other, convert_other):
    """
    Tests whether ``Url.join`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    other : `str`
        New url to join with.
    
    convert_other : `bool`
        Whether `other` should be converted to ``URL``.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    
    if convert_other:
        other = URL(other)
    
    output = url.join(other)
    vampytest.assert_instance(output, URL)
    return output.value_decoded


def _iter_options__extend_query__passing():
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        None,
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        '',
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        'hey=mister',
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    
    yield (
        'https://hey:mister@orindance.party:8000',
        {'hey': 'mister'},
        'https://hey:mister@orindance.party:8000/?hey=mister',
    )
    yield (
        'https://hey:mister@orindance.party:8000?hey=mister',
        {'hey': 'sister'},
        'https://hey:mister@orindance.party:8000/?hey=mister&hey=sister',
    )


def _iter_options__extend_query__type_error():
    yield (
        'https://orindance.party',
        object(),
    )


def _iter_options__extend_query__value_error():
    return
    yield


@vampytest._(vampytest.call_from(_iter_options__extend_query__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__extend_query__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__extend_query__value_error()).raising(ValueError))
def test__Url__extend_query(input_value, query):
    """
    Tests whether ``Url.extend_query`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to test with.
    
    query : `object`
        New query for the url.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    TypeError
    """
    url = URL(input_value)
    output = url.extend_query(query)
    vampytest.assert_instance(output, URL)
    return output.value_decoded
