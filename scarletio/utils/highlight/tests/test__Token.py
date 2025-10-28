import vampytest

from ..token import Token
from ..token_types import TOKEN_TYPE_NUMERIC_FLOAT, TOKEN_TYPE_NUMERIC_INTEGER


def _assert_fields_set(token):
    """
    Asserts whether every fields of the given token are correctly set.
    """
    vampytest.assert_instance(token, Token)
    vampytest.assert_instance(token.content_character_index, int)
    vampytest.assert_instance(token.length, int)
    vampytest.assert_instance(token.line_character_index, int)
    vampytest.assert_instance(token.line_index, int)
    vampytest.assert_instance(token.type, int)


def test__Token__new():
    """
    Tests whether ``Token.__new__`` works as intended.
    """
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    token = Token(
        token_type,
        content_character_index,
        line_index,
        line_character_index,
        length,
    )
    _assert_fields_set(token)
    
    vampytest.assert_eq(token.type, token_type)
    vampytest.assert_eq(token.content_character_index, content_character_index)
    vampytest.assert_eq(token.length, length)
    vampytest.assert_eq(token.line_character_index, line_character_index)
    vampytest.assert_eq(token.line_index, line_index)


def test__Token__repr():
    """
    Tests whether ``Token.__repr__`` works as intended.
    """
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    token = Token(
        token_type,
        content_character_index,
        line_index,
        line_character_index,
        length,
    )
    
    output = repr(token)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    token_type = TOKEN_TYPE_NUMERIC_FLOAT
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    keyword_parameters = {
        'token_type': token_type,
        'content_character_index': content_character_index,
        'line_index': line_index,
        'line_character_index': line_character_index,
        'length': length,
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
            'token_type': TOKEN_TYPE_NUMERIC_INTEGER,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'content_character_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'line_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'line_character_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'length': 10,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Token__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Token.__eq__`` works as intended.
    
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
    token_0 = Token(**keyword_parameters_0)
    token_1 = Token(**keyword_parameters_1)
    
    output = token_0 == token_1
    vampytest.assert_instance(output, bool)
    return output
