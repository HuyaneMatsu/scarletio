import vampytest

from ..utils import get_highlight_parse_result, search_layer_index


def test__search_layer_index():
    """
    Tests whether ``search_layer_index`` works as intended.
    """
    parse_result = get_highlight_parse_result('(shrimp)\n(fry + (5))\n(cooked)')
    
    output = search_layer_index(parse_result.layers, 10)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)
