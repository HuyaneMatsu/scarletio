import vampytest

from ..constants import (
    HOST_FLAG_EXTERNAL_IP_V4, HOST_FLAG_EXTERNAL_IP_V6, HOST_FLAG_EXTERNAL_NAME, HOST_FLAG_LOCAL_IP_V4,
    HOST_FLAG_LOCAL_NAME, HOST_FLAG_UNAMBIGUOUS
)
from ..url_host_info import URLHostInfo
from ..url_host_part import URLHostPart


def _assert_fields_set(url_host_info):
    """
    Asserts whether the given url host info has all of its fields set.
    
    Parameters
    ----------
    url_host_info : ``URLHostInfo``
        The url host info to test.
    """
    vampytest.assert_instance(url_host_info, URLHostInfo)
    vampytest.assert_instance(url_host_info._flags, int)
    vampytest.assert_instance(url_host_info._main_domain, URLHostPart, nullable = True)
    vampytest.assert_instance(url_host_info._sub_domain, URLHostPart, nullable = True)
    vampytest.assert_instance(url_host_info._top_level_domain, URLHostPart, nullable = True)


def test__URLHostInfo__new():
    """
    Tests whether ``URLHostInfo.__new__`` works as intended.
    """
    with vampytest.assert_raises(RuntimeError):
        URLHostInfo()


def test__URLHostInfo__repr__all_fields():
    """
    Tests whether ``URLHostInfo.__repr__`` works as intended.
    
    Case: all fields filled.
    """
    host_main_domain = 'koishi'
    host_sub_domain = 'eye'
    host_top_level_domain = 'kokoro'
    
    url_host_info = URLHostInfo._create_from_decoded(
        HOST_FLAG_EXTERNAL_NAME, host_main_domain, host_sub_domain, host_top_level_domain
    )
    
    output = repr(url_host_info)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(url_host_info).__name__, output)
    vampytest.assert_in(f'main_domain_decoded = {host_main_domain!r}', output)
    vampytest.assert_in(f'sub_domain_decoded = {host_sub_domain!r}', output)
    vampytest.assert_in(f'top_level_domain_decoded = {host_top_level_domain!r}', output)


def test__URLHostInfo__repr__no_fields():
    """
    Tests whether ``URLHostInfo.__repr__`` works as intended.
    
    Case: no fields filled.
    """
    host_main_domain = None
    host_sub_domain = None
    host_top_level_domain = None
    
    url_host_info = URLHostInfo._create_from_decoded(
        HOST_FLAG_EXTERNAL_NAME, host_main_domain, host_sub_domain, host_top_level_domain
    )
    
    output = repr(url_host_info)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(url_host_info).__name__, output)
    vampytest.assert_not_in('main_domain_decoded', output)
    vampytest.assert_not_in('sub_domain_decoded', output)
    vampytest.assert_not_in('top_level_domain', output)


def _iter_options__eq():
    main_domain_decoded = 'koishiű'
    main_domain_encoded = 'xn--koishi-nnb'
    sub_domain_decoded = 'satoriű'
    sub_domain_encoded = 'xn--satori-nnb'
    top_level_domain_decoded = 'kokoroű'
    top_level_domain_encoded = 'xn--kokoro-nnb'
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (main_domain_decoded, None, None),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (main_domain_encoded, None, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (main_domain_encoded, None, None),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (main_domain_encoded, None, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (main_domain_decoded, None, None),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (main_domain_decoded, None, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (main_domain_decoded, None, None),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        ('orin', None, None),
        False,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, None),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, None, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, sub_domain_decoded, None),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, sub_domain_encoded, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, sub_domain_encoded, None),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, sub_domain_encoded, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, sub_domain_decoded, None),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, sub_domain_decoded, None),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, sub_domain_decoded, None),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, 'orin', None),
        False,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, top_level_domain_decoded),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, None, top_level_domain_encoded),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, None, top_level_domain_encoded),
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        (None, None, top_level_domain_encoded),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, top_level_domain_decoded),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, top_level_domain_decoded),
        True,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, top_level_domain_decoded),
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        (None, None, 'orin'),
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__URLHostInfo__eq(constructor_0, parameters_0, constructor_1, parameters_1):
    """
    Tests whether ``URLHostInfo.__eq__`` works as intended.
    
    Parameters
    ----------
    constructor_0 : `FunctionType`
        Constructor to call.
    
    parameters_0 : `(object, object, object)`
        Parameter to call the constructor with.
    
    constructor_1 : `FunctionType`
        Constructor to call.
    
    parameters_1 : `(object, object, object)`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `bool`
    """
    url_host_info_0 = constructor_0(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, *parameters_0)
    url_host_info_1 = constructor_1(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, *parameters_1)
    output = url_host_info_0 == url_host_info_1
    vampytest.assert_instance(output, bool)
    return output


def test__URLHostInfo__create_from_local_ip_v4_decoded():
    """
    Tests whether ``URLHostInfo.create_from_local_ip_v4_decoded`` works as intended.
    """
    local_ip_v4 = 'xn--koishi-nnb'
    
    url_host_info = URLHostInfo.create_from_local_ip_v4_decoded(local_ip_v4)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_decoded, local_ip_v4)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_LOCAL_IP_V4)


def test__URLHostInfo__create_from_local_ip_v4_encoded():
    """
    Tests whether ``URLHostInfo.create_from_local_ip_v4_encoded`` works as intended.
    """
    local_ip_v4 = 'koishiű'
    
    url_host_info = URLHostInfo.create_from_local_ip_v4_encoded(local_ip_v4)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_encoded, local_ip_v4)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_LOCAL_IP_V4)


def test__URLHostInfo__create_from_local_name_decoded():
    """
    Tests whether ``URLHostInfo.create_from_local_name_decoded`` works as intended.
    """
    local_host = 'xn--koishi-nnb'
    unambiguous = True
    
    url_host_info = URLHostInfo.create_from_local_name_decoded(local_host, unambiguous)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_decoded, local_host)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_LOCAL_NAME | HOST_FLAG_UNAMBIGUOUS)


def test__URLHostInfo__create_from_local_name_encoded():
    """
    Tests whether ``URLHostInfo.create_from_local_name_encoded`` works as intended.
    """
    local_host = 'koishiű'
    unambiguous = True
    
    url_host_info = URLHostInfo.create_from_local_name_encoded(local_host, unambiguous)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_encoded, local_host)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_LOCAL_NAME | HOST_FLAG_UNAMBIGUOUS)


def test__URLHostInfo__create_from_external_ip_v4_decoded():
    """
    Tests whether ``URLHostInfo.create_from_external_ip_v4_decoded`` works as intended.
    """
    external_ip_v4 = 'xn--koishi-nnb'
    
    url_host_info = URLHostInfo.create_from_external_ip_v4_decoded(external_ip_v4)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_decoded, external_ip_v4)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_IP_V4)


def test__URLHostInfo__create_from_external_ip_v4_encoded():
    """
    Tests whether ``URLHostInfo.create_from_external_ip_v4_encoded`` works as intended.
    """
    external_ip_v4 = 'koishiű'
    
    url_host_info = URLHostInfo.create_from_external_ip_v4_encoded(external_ip_v4)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_encoded, external_ip_v4)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_IP_V4)


def test__URLHostInfo__create_from_external_ip_v6_decoded():
    """
    Tests whether ``URLHostInfo.create_from_external_ip_v6_decoded`` works as intended.
    """
    external_ip_v6 = 'xn--koishi-nnb'
    
    url_host_info = URLHostInfo.create_from_external_ip_v6_decoded(external_ip_v6)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_decoded, external_ip_v6)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_IP_V6)


def test__URLHostInfo__create_from_external_ip_v6_encoded():
    """
    Tests whether ``URLHostInfo.create_from_external_ip_v6_encoded`` works as intended.
    """
    external_ip_v6 = 'koishiű'
    
    url_host_info = URLHostInfo.create_from_external_ip_v6_encoded(external_ip_v6)
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_encoded, external_ip_v6)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_IP_V6)


def test__URLHostInfo__create_from_external_name_decoded():
    """
    Tests whether ``URLHostInfo.create_from_external_name_decoded`` works as intended.
    """
    host_main_domain = 'xn--koishi-nnb'
    host_sub_domain = 'eye '
    host_top_level_domain = 'kokoro '
    unambiguous = True
    
    url_host_info = URLHostInfo.create_from_external_name_decoded(
        host_sub_domain, host_main_domain, host_top_level_domain, unambiguous
    )
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_decoded, host_main_domain)
    vampytest.assert_eq(url_host_info.sub_domain_decoded, host_sub_domain)
    vampytest.assert_eq(url_host_info.top_level_domain_decoded, host_top_level_domain)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_NAME | HOST_FLAG_UNAMBIGUOUS)


def test__URLHostInfo__create_from_external_name_encoded():
    """
    Tests whether ``URLHostInfo.create_from_external_name_encoded`` works as intended.
    """
    host_main_domain = 'xn--koishi-nnb'
    host_sub_domain = 'xn--eye-nnb'
    host_top_level_domain = 'xn--kokoro-nnb'
    unambiguous = True
    
    url_host_info = URLHostInfo.create_from_external_name_encoded(
        host_sub_domain, host_main_domain, host_top_level_domain, unambiguous
    )
    _assert_fields_set(url_host_info)
    
    vampytest.assert_eq(url_host_info.main_domain_encoded, host_main_domain)
    vampytest.assert_eq(url_host_info.sub_domain_encoded, host_sub_domain)
    vampytest.assert_eq(url_host_info.top_level_domain_encoded, host_top_level_domain)
    vampytest.assert_eq(url_host_info._flags, HOST_FLAG_EXTERNAL_NAME | HOST_FLAG_UNAMBIGUOUS)


def _iter_options__decoded():
    decoded = 'koishiű'
    encoded = 'xn--koishi-nnb'
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        decoded,
        decoded,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        encoded,
        decoded,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLHostInfo__main_domain_decoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.main_domain_decoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    part =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, parameter, None, None)
    
    output = part.main_domain_decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLHostInfo__sub_domain_decoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.sub_domain_decoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    url_host_info =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, None, parameter, None)
    
    output = url_host_info.sub_domain_decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLHostInfo__top_level_domain_decoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.top_level_domain_decoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    url_host_info =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, None, None, parameter)
    
    output = url_host_info.top_level_domain_decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__encoded():
    decoded = 'koishiű'
    encoded = 'xn--koishi-nnb'
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        decoded,
        encoded,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        encoded,
        encoded,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLHostInfo.__dict__['_create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLHostInfo__main_domain_encoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.main_domain_encoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    url_host_info =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, parameter, None, None)
    
    output = url_host_info.main_domain_encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLHostInfo__sub_domain_encoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.sub_domain_encoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    url_host_info =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, None, parameter, None)
    
    output = url_host_info.sub_domain_encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLHostInfo__top_level_domain_encoded(constructor, parameter):
    """
    Tests whether ``URLHostInfo.top_level_domain_encoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    url_host_info =  constructor(URLHostInfo, HOST_FLAG_EXTERNAL_NAME, None, None, parameter)
    
    output = url_host_info.top_level_domain_encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__checks():
    # create_from_local_ip_v4_decoded
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v4,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v6,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_name,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_local,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_external,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_unambiguous,
        False,
    )
    
    # create_from_local_name_decoded
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False,),
        URLHostInfo.is_ip_v4,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_ip_v6,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_ip,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_name,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_local,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_external,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, False),
        URLHostInfo.is_unambiguous,
        False,
    )
    
    # unambiguous
    yield (
        URLHostInfo.__dict__['create_from_local_name_decoded'].__func__,
        (None, True),
        URLHostInfo.is_unambiguous,
        True,
    )
    
    # create_from_external_ip_v4_decoded
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v4,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v6,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_name,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_local,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_external,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v4_decoded'].__func__,
        (None,),
        URLHostInfo.is_unambiguous,
        False,
    )
    
    # create_from_external_ip_v6_decoded
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v4,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip_v6,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_ip,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_name,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_local,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_external,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_ip_v6_decoded'].__func__,
        (None,),
        URLHostInfo.is_unambiguous,
        False,
    )
    
    # create_from_external_ip_v6_decoded
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_ip_v4,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_ip_v6,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_ip,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_name,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_local,
        False,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_external,
        True,
    )
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, False),
        URLHostInfo.is_unambiguous,
        False,
    )
    
    # unambiguous
    yield (
        URLHostInfo.__dict__['create_from_external_name_decoded'].__func__,
        (None, None, None, True),
        URLHostInfo.is_unambiguous,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__checks()).returning_last())
def test__URLHostInfo__checks(constructor, parameters, check):
    """
    Tests whether ``URLHostInfo``'s properties works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameters : `tuple<object>`
        Parameters to call the constructor with.
    
    check : `FunctionType`
        The check to call
    
    Returns
    -------
    output : `bool`
    """
    url_host_info =  constructor(URLHostInfo, *parameters)
    
    output = check(url_host_info)
    
    vampytest.assert_instance(output, bool)
    return output
