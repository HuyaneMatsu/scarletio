import vampytest

from ..parser_context import HighlightParserContext
from ..token import Token
from ..token_types import TOKEN_TYPE_LINEBREAK, TOKEN_TYPE_STRING_UNICODE


def _iter_options__try_match_string():
    yield '\'hello\'', [Token(TOKEN_TYPE_STRING_UNICODE, '\'hello\'')]
    yield '\'\'\'hello\'\'\'', [Token(TOKEN_TYPE_STRING_UNICODE, '\'\'\'hello\'\'\'')]
    yield (
        '\'\'\'\nhello\n\'\'\'',
        [
            Token(TOKEN_TYPE_STRING_UNICODE, '\'\'\''),
            Token(TOKEN_TYPE_LINEBREAK, '\n'),
            Token(TOKEN_TYPE_STRING_UNICODE, 'hello'),
            Token(TOKEN_TYPE_LINEBREAK, '\n'),
            Token(TOKEN_TYPE_STRING_UNICODE, '\'\'\''),
        ],
    )
    yield '\'\'', [Token(TOKEN_TYPE_STRING_UNICODE, '\'\'')]


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
    context = HighlightParserContext(input_string.splitlines(keepends = True))
    context.match()
    return context.tokens
