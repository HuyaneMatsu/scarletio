import vampytest

from base64 import b64decode as base64_decode, b64encode as base64_encode

from ..basic_auth import BasicAuth


def _assert_fields_set(basic_auth):
    """
    Asserts whether every fields are set of the given basic authorization.
    
    Parameters
    ----------
    basic_auth : ``BasicAuth``
        Basic authorization to check.
    """
    vampytest.assert_instance(basic_auth, BasicAuth)
    vampytest.assert_instance(basic_auth.encoding, str)
    vampytest.assert_instance(basic_auth.password, str)
    vampytest.assert_instance(basic_auth.user_id, str)


def test__BasicAuth__new__min_fields():
    """
    Tests whether ``BasicAuth.__new__`` works as intended.
    
    Case: Minimal fields given.
    """
    user_id = 'orin'
    
    basic_auth = BasicAuth(user_id)
    _assert_fields_set(basic_auth)
    
    vampytest.assert_eq(basic_auth.user_id, user_id)
    

def test__BasicAuth__new__all_fields():
    """
    Tests whether ``BasicAuth.__new__`` works as intended.
    
    Case: All fields given.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_auth = BasicAuth(user_id, password, encoding = encoding)
    _assert_fields_set(basic_auth)
    
    vampytest.assert_eq(basic_auth.encoding, encoding)
    vampytest.assert_eq(basic_auth.password, password)
    vampytest.assert_eq(basic_auth.user_id, user_id)


def test__BasicAuth__repr():
    """
    Tests whether ``BasicAuth.__repr__`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_auth = BasicAuth(user_id, password, encoding = encoding)
    
    output = repr(basic_auth)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    keyword_parameters = {
        'encoding': encoding,
        'password': password,
        'user_id': user_id,
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
            'encoding': 'utf-32',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'password': 'skull',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'user_id': 'okuu',
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__BasicAuth__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``BasicAuth.__eq__`` works as intended.
    
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
    basic_auth_0 = BasicAuth(**keyword_parameters_0)
    basic_auth_1 = BasicAuth(**keyword_parameters_1)
    
    output = basic_auth_0 == basic_auth_1
    vampytest.assert_instance(output, bool)
    return output


def test__BasicAuth__hash():
    """
    Tests whether ``BasicAuth.__hash__`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_auth = BasicAuth(user_id, password, encoding = encoding)
    
    output = hash(basic_auth)
    vampytest.assert_instance(output, int)


def test__BasicAuth__from_header__min_fields():
    """
    Tests whether ``BasicAuth.from_headers`` works as intended.
    
    Case: Minimal fields given.
    """
    user_id = 'orin'
    
    token = base64_encode(user_id.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_auth = BasicAuth.from_header(header_value)
    _assert_fields_set(basic_auth)
    
    vampytest.assert_eq(basic_auth.user_id, user_id)


def test__BasicAuth__from_header__all_fields():
    """
    Tests whether ``BasicAuth.from_headers`` works as intended.
    
    Case: All fields given.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    token = base64_encode(f'{user_id}:{password}'.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_auth = BasicAuth.from_header(header_value, encoding = encoding)
    _assert_fields_set(basic_auth)
    
    vampytest.assert_eq(basic_auth.encoding, encoding)
    vampytest.assert_eq(basic_auth.password, password)
    vampytest.assert_eq(basic_auth.user_id, user_id)


def test__BasicAuth__to_header():
    """
    Tests whether ``BasicAuth.from_headers`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    token = base64_encode(f'{user_id}:{password}'.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_auth = BasicAuth(user_id, password, encoding = encoding)
    
    output = basic_auth.to_header()
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, header_value)
