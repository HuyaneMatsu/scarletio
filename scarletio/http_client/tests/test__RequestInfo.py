import vampytest

from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import URL
from ...web_common.headers import METHOD_GET, METHOD_PUT

from ..request_info import RequestInfo


def _assert_fields_set(request_info):
    """
    Asserts whether every fields are set of the given reqtest info.
    
    Parameters
    ----------
    request_info : ``RequestInfo``
    """
    vampytest.assert_instance(request_info, RequestInfo)
    vampytest.assert_instance(request_info.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(request_info.method, str)
    vampytest.assert_instance(request_info.original_url, URL)
    vampytest.assert_instance(request_info.url, URL)
    

def test__RequestInfo__new():
    """
    Tests whether ``RequestInfo.__new__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    method = METHOD_GET
    original_url = URL('https://orindance.party/#3d')
    url = URL('https://orindance.party/')
    
    request_info = RequestInfo(
        headers,
        method,
        original_url,
        url,
    )
    _assert_fields_set(request_info)
    
    vampytest.assert_eq(request_info.headers, headers)
    vampytest.assert_eq(request_info.method, method)
    vampytest.assert_eq(request_info.original_url, original_url)
    vampytest.assert_eq(request_info.url, url)


def test__RequestInfo__repr():
    """
    Tests whether ``RequestInfo.__repr__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    method = METHOD_GET
    original_url = URL('https://orindance.party/#3d')
    url = URL('https://orindance.party/')
    
    request_info = RequestInfo(
        headers,
        method,
        original_url,
        url,
    )
    
    output = repr(request_info)
    vampytest.assert_instance(output, str)



def _iter_options__eq():
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    method = METHOD_GET
    original_url = URL('https://orindance.party/#3d')
    url = URL('https://orindance.party/')
    
    keyword_parameters = {
        'headers': headers,
        'method': method,
        'original_url': original_url,
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
            'headers': IgnoreCaseMultiValueDictionary([('hey', 'sister')]),
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'method': METHOD_PUT,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'original_url': URL('https://orindance.party/#2d'),
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'url': URL('https://orindance.party/miau'),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__RequestInfo__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``RequestInfo.__eq__`` works as intended.
    
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
    connection_key_0 = RequestInfo(**keyword_parameters_0)
    connection_key_1 = RequestInfo(**keyword_parameters_1)
    
    output = connection_key_0 == connection_key_1
    vampytest.assert_instance(output, bool)
    return output


def test__RequestInfo__hash():
    """
    Tests whether ``RequestInfo.__hash__`` works as intended.
    """
    headers = IgnoreCaseMultiValueDictionary([('hey', 'mister')])
    method = METHOD_GET
    original_url = URL('https://orindance.party/#3d')
    url = URL('https://orindance.party/')
    
    request_info = RequestInfo(
        headers,
        method,
        original_url,
        url,
    )
    
    output = hash(request_info)
    vampytest.assert_instance(output, int)
