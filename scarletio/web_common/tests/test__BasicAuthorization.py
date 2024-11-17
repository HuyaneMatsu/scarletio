import vampytest

from base64 import b64encode as base64_encode

from ..basic_authorization import BasicAuthorization


def _assert_fields_set(basic_authorization):
    """
    Asserts whether every fields are set of the given basic authorization.
    
    Parameters
    ----------
    basic_authorization : ``BasicAuthorization``
        Basic authorization to check.
    """
    vampytest.assert_instance(basic_authorization, BasicAuthorization)
    vampytest.assert_instance(basic_authorization.encoding, str)
    vampytest.assert_instance(basic_authorization.password, str)
    vampytest.assert_instance(basic_authorization.user_id, str)


def test__BasicAuthorization__new__min_fields():
    """
    Tests whether ``BasicAuthorization.__new__`` works as intended.
    
    Case: Minimal fields given.
    """
    user_id = 'orin'
    
    basic_authorization = BasicAuthorization(user_id)
    _assert_fields_set(basic_authorization)
    
    vampytest.assert_eq(basic_authorization.user_id, user_id)
    

def test__BasicAuthorization__new__all_fields():
    """
    Tests whether ``BasicAuthorization.__new__`` works as intended.
    
    Case: All fields given.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_authorization = BasicAuthorization(user_id, password, encoding = encoding)
    _assert_fields_set(basic_authorization)
    
    vampytest.assert_eq(basic_authorization.encoding, encoding)
    vampytest.assert_eq(basic_authorization.password, password)
    vampytest.assert_eq(basic_authorization.user_id, user_id)


def test__BasicAuthorization__repr():
    """
    Tests whether ``BasicAuthorization.__repr__`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_authorization = BasicAuthorization(user_id, password, encoding = encoding)
    
    output = repr(basic_authorization)
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
def test__BasicAuthorization__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``BasicAuthorization.__eq__`` works as intended.
    
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
    basic_authorization_0 = BasicAuthorization(**keyword_parameters_0)
    basic_authorization_1 = BasicAuthorization(**keyword_parameters_1)
    
    output = basic_authorization_0 == basic_authorization_1
    vampytest.assert_instance(output, bool)
    return output


def test__BasicAuthorization__hash():
    """
    Tests whether ``BasicAuthorization.__hash__`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    basic_authorization = BasicAuthorization(user_id, password, encoding = encoding)
    
    output = hash(basic_authorization)
    vampytest.assert_instance(output, int)


def test__BasicAuthorization__from_header__min_fields():
    """
    Tests whether ``BasicAuthorization.from_headers`` works as intended.
    
    Case: Minimal fields given.
    """
    user_id = 'orin'
    
    token = base64_encode(user_id.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_authorization = BasicAuthorization.from_header(header_value)
    _assert_fields_set(basic_authorization)
    
    vampytest.assert_eq(basic_authorization.user_id, user_id)


def test__BasicAuthorization__from_header__all_fields():
    """
    Tests whether ``BasicAuthorization.from_headers`` works as intended.
    
    Case: All fields given.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    token = base64_encode(f'{user_id}:{password}'.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_authorization = BasicAuthorization.from_header(header_value, encoding = encoding)
    _assert_fields_set(basic_authorization)
    
    vampytest.assert_eq(basic_authorization.encoding, encoding)
    vampytest.assert_eq(basic_authorization.password, password)
    vampytest.assert_eq(basic_authorization.user_id, user_id)


def test__BasicAuthorization__to_header():
    """
    Tests whether ``BasicAuthorization.from_headers`` works as intended.
    """
    encoding = 'utf-8'
    password = 'fish'
    user_id = 'orin'
    
    token = base64_encode(f'{user_id}:{password}'.encode()).decode()
    header_value = f'Basic {token}'
    
    basic_authorization = BasicAuthorization(user_id, password, encoding = encoding)
    
    output = basic_authorization.to_header()
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(output, header_value)
