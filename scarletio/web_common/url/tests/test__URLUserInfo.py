import vampytest

from ..url_part_base import URLPartBase
from ..url_user_info import URLUserInfo


def _assert_fields_set(url_user_info):
    """
    Asserts whether the given url user info has all of its fields set.
    
    Parameters
    ----------
    url_user_info : ``URLUserInfo``
        The url user info to test.
    """
    vampytest.assert_instance(url_user_info, URLUserInfo)
    vampytest.assert_instance(url_user_info._name, URLPartBase, nullable = True)
    vampytest.assert_instance(url_user_info._password, URLPartBase, nullable = True)


def test__URLUserInfo__new():
    """
    Tests whether ``URLUserInfo.__new__`` works as intended.
    """
    with vampytest.assert_raises(RuntimeError):
        URLUserInfo()


def test__URLUserInfo__repr__all_fields():
    """
    Tests whether ``URLUserInfo.__repr__`` works as intended.
    
    Case: all fields filled.
    """
    user_name = 'koishi'
    user_password = 'eye'
    
    url_user_info = URLUserInfo.create_from_decoded(user_name, user_password)
    
    output = repr(url_user_info)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(url_user_info).__name__, output)
    vampytest.assert_in(f'name_decoded = {user_name!r}', output)
    vampytest.assert_in(f'password_decoded = {user_password!r}', output)


def test__URLUserInfo__repr__no_fields():
    """
    Tests whether ``URLUserInfo.__repr__`` works as intended.
    
    Case: no fields filled.
    """
    user_name = None
    user_password = None
    
    url_user_info = URLUserInfo.create_from_decoded(user_name, user_password)
    
    output = repr(url_user_info)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(url_user_info).__name__, output)
    vampytest.assert_not_in('name_decoded', output)
    vampytest.assert_not_in('password_decoded', output)


def _iter_options__eq():
    name_decoded = 'koishi '
    name_encoded = 'koishi%20'
    password_decoded = 'satori '
    password_encoded = 'satori%20'
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (name_decoded, None),
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (name_encoded, None),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (name_encoded, None),
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (name_encoded, None),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (name_decoded, None),
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (name_decoded, None),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (name_decoded, None),
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        ('orin', None),
        False,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, None),
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (None, None),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, password_decoded),
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (None, password_encoded),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (None, password_encoded),
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        (None, password_encoded),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, password_decoded),
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, password_decoded),
        True,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, password_decoded),
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        (None, 'orin'),
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__URLUserInfo__eq(constructor_0, parameters_0, constructor_1, parameters_1):
    """
    Tests whether ``URLUserInfo.__eq__`` works as intended.
    
    Parameters
    ----------
    constructor_0 : `FunctionType`
        Constructor to call.
    
    parameters_0 : `(object, object)`
        Parameter to call the constructor with.
    
    constructor_1 : `FunctionType`
        Constructor to call.
    
    parameters_1 : `(object, object)`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `bool`
    """
    url_user_info_0 = constructor_0(URLUserInfo, *parameters_0)
    url_user_info_1 = constructor_1(URLUserInfo, *parameters_1)
    output = url_user_info_0 == url_user_info_1
    vampytest.assert_instance(output, bool)
    return output


def test__URLUserInfo__create_from_encoded():
    """
    Tests whether ``URLUserInfo.create_from_encoded`` works as intended.
    """
    name_encoded = 'koishi%20'
    password_encoded = 'satori%20'
    
    url_user_info = URLUserInfo.create_from_encoded(name_encoded, password_encoded)
    _assert_fields_set(url_user_info)
    
    vampytest.assert_eq(url_user_info.name_encoded, name_encoded)
    vampytest.assert_eq(url_user_info.password_encoded, password_encoded)


def test__URLUserInfo__create_from_decoded():
    """
    Tests whether ``URLUserInfo.create_from_decoded`` works as intended.
    """
    name_decoded = 'koishi '
    password_decoded = 'satori '
    
    url_user_info = URLUserInfo.create_from_decoded(name_decoded, password_decoded)
    _assert_fields_set(url_user_info)
    
    vampytest.assert_eq(url_user_info.name_decoded, name_decoded)
    vampytest.assert_eq(url_user_info.password_decoded, password_decoded)


def _iter_options__decoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        decoded,
        decoded,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        encoded,
        decoded,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLUserInfo__name_decoded(constructor, parameter):
    """
    Tests whether ``URLUserInfo.name_decoded`` works as intended.
    
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
    part =  constructor(URLUserInfo, parameter, None)
    
    output = part.name_decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLUserInfo__password_decoded(constructor, parameter):
    """
    Tests whether ``URLUserInfo.password_decoded`` works as intended.
    
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
    url_user_info =  constructor(URLUserInfo, None, parameter)
    
    output = url_user_info.password_decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__encoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        decoded,
        encoded,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        encoded,
        encoded,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLUserInfo.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLUserInfo__name_encoded(constructor, parameter):
    """
    Tests whether ``URLUserInfo.name_encoded`` works as intended.
    
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
    url_user_info =  constructor(URLUserInfo, parameter, None)
    
    output = url_user_info.name_encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLUserInfo__password_encoded(constructor, parameter):
    """
    Tests whether ``URLUserInfo.password_encoded`` works as intended.
    
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
    url_user_info =  constructor(URLUserInfo, None, parameter)
    
    output = url_user_info.password_encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    return output
