import vampytest

from ..utils import get_highlight_parse_result, search_line_end_index_in_tokens


def test__search_line_end_index_in_tokens():
    """
    Tests whether ``search_line_end_index_in_tokens`` works as intended.
    """
    parse_result = get_highlight_parse_result('shrimp\nfry + 5\ncooked')
    
    output = search_line_end_index_in_tokens(parse_result.tokens, 1)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 8)
