import vampytest

from ....highlight import Token
from ....highlight.token_types import (
    TOKEN_TYPE_SPACE, TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_COMMENT
)

from ..expression_info import get_shared_indentation_length


def _iter_options():
    yield (
        'Empty, start',
        [],
        0,
        0,
        0,
    )
    
    yield (
        'Empty',
        [
            Token(TOKEN_TYPE_SPACE, 0, 0, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 4, 0, 4, 20),
            Token(TOKEN_TYPE_LINE_BREAK, 24, 0, 24, 1),
            Token(TOKEN_TYPE_SPACE, 25, 1, 0, 4),
            Token(TOKEN_TYPE_LINE_BREAK, 29, 1, 4, 1),
            Token(TOKEN_TYPE_SPACE, 30, 2, 0, 4),
        ],
        4,
        4,
        0,
    )
    
    yield (
        'empty lines',
        [
            Token(TOKEN_TYPE_LINE_BREAK, 0, 0, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 1, 1, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 2, 2, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 3, 3, 0, 1),
        ],
        1,
        3,
        0,
    )
    
    yield (
        'same space length',
        [
            Token(TOKEN_TYPE_COMMENT, 0, 0, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 1, 0, 1, 1),
            Token(TOKEN_TYPE_SPACE, 2, 1, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 6, 1, 4, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 7, 1, 5, 1),
            Token(TOKEN_TYPE_SPACE, 8, 2, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 12, 2, 4, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 13, 2, 5, 1),
            Token(TOKEN_TYPE_COMMENT, 14, 3, 0, 1),
        ],
        1,
        8,
        4,
    )
    
    yield (
        'less space length',
        [
            Token(TOKEN_TYPE_COMMENT, 0, 0, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 1, 0, 1, 1),
            Token(TOKEN_TYPE_SPACE, 2, 1, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 6, 1, 4, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 7, 1, 5, 1),
            Token(TOKEN_TYPE_SPACE, 8, 2, 0, 2),
            Token(TOKEN_TYPE_COMMENT, 10, 2, 2, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 11, 2, 3, 1),
            Token(TOKEN_TYPE_COMMENT, 13, 3, 0, 1),
        ],
        1,
        8,
        2,
    )
    
    yield (
        'more space length',
        [
            Token(TOKEN_TYPE_COMMENT, 0, 0, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 1, 0, 1, 1),
            Token(TOKEN_TYPE_SPACE, 2, 1, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 6, 1, 4, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 7, 1, 5, 1),
            Token(TOKEN_TYPE_SPACE, 8, 2, 0, 6),
            Token(TOKEN_TYPE_COMMENT, 14, 2, 6, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 15, 2, 7, 1),
            Token(TOKEN_TYPE_COMMENT, 17, 3, 0, 1),
        ],
        1,
        8,
        4,
    )
    
    yield (
        'less space but empty line',
        [
            Token(TOKEN_TYPE_COMMENT, 0, 0, 0, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 1, 0, 1, 1),
            Token(TOKEN_TYPE_SPACE, 2, 1, 0, 4),
            Token(TOKEN_TYPE_COMMENT, 6, 1, 4, 1),
            Token(TOKEN_TYPE_LINE_BREAK, 7, 1, 5, 1),
            Token(TOKEN_TYPE_SPACE, 8, 2, 0, 2),
            Token(TOKEN_TYPE_LINE_BREAK, 10, 2, 2, 1),
            Token(TOKEN_TYPE_COMMENT, 11, 3, 0, 1),
        ],
        1,
        7,
        4,
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__get_shared_indentation_length(tokens, token_start_index, token_end_index):
    """
    Tests whether ``get_shared_indentation_length`` works as intended.
    
    Parameters
    ----------
    tokens : ``list<Token>``
        Tokens to iterate over.
    
    token_start_index : `int`
        First token of the area.
    
    token_end_index : `int`
        Last token of the area.
    
    Returns
    -------
    output : `int`
    """
    output = get_shared_indentation_length(tokens, token_start_index, token_end_index)
    vampytest.assert_instance(output, int)
    return output
