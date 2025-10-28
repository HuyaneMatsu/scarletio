import vampytest

from ..layer import Layer
from ..parse_result import ParseResult
from ..token import Token
from ..token_types import (
    TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN
)


def _assert_fields_set(parse_result):
    """
    Asserts whether the parse result has all of its fields set.
    
    Parameters
    ----------
    parse_result : ``ParseResult``
        Instance to check.
    """
    vampytest.assert_instance(parse_result, ParseResult)
    vampytest.assert_instance(parse_result.layers, list)
    vampytest.assert_instance(parse_result.tokens, list)


def test__ParseResult__new():
    """
    Tests whether ``ParseResult.__new__`` works as intended.
    """
    layers = [
        Layer(-1, 0, 1),
    ]
    tokens = [
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, 0, 0, 0, 1),
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, 1, 0, 1, 1),
    ]
    
    parse_result = ParseResult(layers, tokens)
    _assert_fields_set(parse_result)
    vampytest.assert_eq(parse_result.layers, layers)
    vampytest.assert_eq(parse_result.tokens, tokens)


def test__ParseResult__repr():
    """
    Tests whether ``ParseResult.__repr__`` works as intended.
    """
    layers = [
        Layer(-1, 0, 1),
    ]
    tokens = [
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, 0, 0, 0, 1),
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, 1, 0, 1, 1),
    ]
    
    parse_result = ParseResult(layers, tokens)
    
    output = repr(parse_result)
    vampytest.assert_instance(output, str)


def test__ParseResult__iter():
    """
    Tests whether ``ParseResult.__iter__`` works as intended.
    """
    layers = [
        Layer(-1, 0, 1),
    ]
    tokens = [
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, 0, 0, 0, 1),
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, 1, 0, 1, 1),
    ]
    
    parse_result = ParseResult(layers, tokens)
    
    vampytest.assert_eq(
        [*parse_result],
        [layers, tokens],
    )


def _iter_options__eq():
    layers = [
        Layer(-1, 0, 1),
    ]
    tokens = [
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, 0, 0, 0, 1),
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, 1, 0, 1, 1),
    ]
    
    keyword_parameters = {
        'layers': layers,
        'tokens': tokens,
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
            'layers': [],
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'tokens': [
                *tokens,
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, 2, 0, 2, 1),
            ],
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ParseResult__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``ParseResult.__eq__`` works as intended.
    
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
    parse_result_0 = ParseResult(**keyword_parameters_0)
    parse_result_1 = ParseResult(**keyword_parameters_1)
    
    output = parse_result_0 == parse_result_1
    vampytest.assert_instance(output, bool)
    return output
