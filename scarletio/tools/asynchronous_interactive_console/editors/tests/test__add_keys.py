import vampytest

from ..editor_advanced import _add_keys, KeyNode


def test__add_keys():
    """
    Tests whether ``_add_keys`` works as intended.
    """
    node_0 = KeyNode()
    node_0_sub_0 = node_0.add_character_sub_node('a')
    node_0_sub_0_0 = node_0_sub_0.add_character_sub_node('b')
    node_0_sub_0_1 = node_0_sub_0.add_character_sub_node('v')
    
    node_0_sub_0_0.set_end()
    node_0_sub_0_1.set_end()
    
    node_1 = KeyNode()
    _add_keys(node_1, ['ab', 'av'])
    vampytest.assert_eq(node_0, node_1)
