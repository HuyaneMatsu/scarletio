import vampytest

from ..parser_context import HighlightParserContext
from ..token import Token
from ..token_types import (
    TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_STRING_UNICODE, TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE,
    TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN,
    TOKEN_TYPE_IDENTIFIER_VARIABLE, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE
)


def _iter_options__try_match_string():
    yield (
        '\'hello\'',
        [
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, 0, 0, 0, 1),
            Token(TOKEN_TYPE_STRING_UNICODE, 1, 0, 1, 5),
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, 6, 0, 6, 1),
        ]
    )
    
    yield (
        '\'\'\'hello\'\'\'',
        [
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, 0, 0, 0, 3),
            Token(TOKEN_TYPE_STRING_UNICODE, 3, 0, 3, 5),
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, 8, 0, 8, 3),
        ],
    )
    
    yield (
        '\'\'\'\nhello\n\'\'\'',
        [
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, 0, 0, 0, 3),
            Token(TOKEN_TYPE_LINE_BREAK, 3, 0, 3, 1),
            Token(TOKEN_TYPE_STRING_UNICODE, 4, 1, 0, 5),
            Token(TOKEN_TYPE_LINE_BREAK, 9, 1, 5, 1),
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, 10, 2, 0, 3),
        ],
    )
    
    yield (
        '\'\'',
        [
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, 0, 0, 0, 1),
            Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, 1, 0, 1, 1),
        ],
    )
    
    yield (
        '(aya)',
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN, 0, 0, 0, 1),
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 1, 0, 1, 3),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE, 4, 0, 4, 1),
        ]
    )
    
    yield (
        '(aya',
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN, 0, 0, 0, 1),
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 1, 0, 1, 3),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE, 4, 0, 4, 0),
        ],
    )
    
    yield (
        'aya)',
        [
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 0, 0, 0, 3),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN, 3, 0, 3, 0),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE, 3, 0, 3, 1),
        ],
    )


@vampytest.skip()
@vampytest._(vampytest.call_from(_iter_options__try_match_string()).returning_last())
def test__try_match_string(input_string):
    """
    Tests whether ``_try_match_string`` works as intended.
    
    Parameters
    ----------
    input_string : `str`
        String to highlight.
    
    Returns
    -------
    tokens : `list<Token>`
    """
    context = HighlightParserContext(input_string, 0)
    context.match()
    return context.tokens
