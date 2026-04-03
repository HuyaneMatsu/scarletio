import vampytest

from ..editor_advanced import _read_from_node_map, KeyNode, InputStream


def _iter_options():
    node_0 = KeyNode()
    node_0_sub_0 = node_0.add_character_sub_node('a')
    node_0_sub_0_0 = node_0_sub_0.add_character_sub_node('b')
    node_0_sub_0_1 = node_0_sub_0.add_character_sub_node('v')
    
    node_0_sub_0_0.set_end()
    node_0_sub_0_1.set_end()
    
    node_1 = KeyNode()
    
    stream_0 = InputStream('abo')
    stream_1 = InputStream('')
    
    yield node_0, stream_0, ('ab', 2)
    yield node_0, stream_1, (None, 0)
    yield node_1, stream_0, (None, 0)
    yield node_1, stream_1, (None, 0)


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__read_from_node_map(node, input_stream):
    """
    Tests whether ``_read_from_node_map`` works as intended.
    
    Parameters
    ----------
    node : `KeyNode`
        The node to read from.
    input_stream : ``InputStream``
        Stream to read from.
    
    Returns
    -------
    output : `(None | str, int)`
    """
    input_stream = input_stream.copy()
    output = _read_from_node_map(node, input_stream)
    return output, input_stream.index
