import vampytest

from ..layer import Layer
from ..parse_result import ParseResult
from ..token import Token
from ..token_types import (
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE
)
from ..utils import get_highlight_parse_result


def test__get_highlight_parse_result():
    """
    Tests whether ``get_highlight_parse_result`` works as intended.
    """
    content = '{}'
    
    layers = [
        Layer(-1, 0, 1),
    ]
    tokens = [
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, 0, 0, 0, 1),
        Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, 1, 0, 1, 1),
    ]
    
    parse_result = ParseResult(layers, tokens)
    
    output = get_highlight_parse_result(content)
    vampytest.assert_instance(output, ParseResult)
    
    vampytest.assert_eq(
        output,
        parse_result,
    )
