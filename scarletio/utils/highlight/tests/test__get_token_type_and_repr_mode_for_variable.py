import vampytest

from ..token_types import (
    TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED,
    TOKEN_TYPE_NUMERIC_FLOAT, TOKEN_TYPE_NUMERIC_INTEGER, TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_UNICODE
)

from ..utils import get_token_type_and_repr_mode_for_variable


class CustomType():
    __slots__ = ()
    pass


def _iter_options():
    yield True, (TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, False)
    yield KeyError, (TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, True)
    yield map, (TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, True)
    yield {}, (TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, False)
    yield 12.65, (TOKEN_TYPE_NUMERIC_FLOAT, False)
    yield 26, (TOKEN_TYPE_NUMERIC_INTEGER, False)
    yield b'hey', (TOKEN_TYPE_STRING_BINARY, False)
    yield 'hey', (TOKEN_TYPE_STRING_UNICODE, False)
    yield CustomType, (TOKEN_TYPE_IDENTIFIER_VARIABLE, True)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_token_type_and_repr_mode_for_variable(variable):
    """
    Tests whether ``get_token_type_and_repr_mode_for_variable`` works as intended.
    
    Parameters
    ----------
    variable : `object`
        The variable to get token type for.
    
    Returns
    -------
    output : `(int, bool)`
    """
    output = get_token_type_and_repr_mode_for_variable(variable)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], int)
    vampytest.assert_instance(output[1], bool)
    return output
