import vampytest

from ..editor_advanced import KeyNode


def _assert_fields_set(node):
    """
    Tests whether every fields are set of the given node.
    
    Parameters
    ----------
    node : ``KeyNode``
        The node to check.
    """
    vampytest.assert_instance(node, KeyNode)
    vampytest.assert_instance(node.character_sub_nodes, dict, nullable = True)
    vampytest.assert_instance(node.end, bool)
    vampytest.assert_instance(node.matcher_sub_nodes, list, nullable = True)


def test__KeyNode__new():
    """
    Tests whether ``KeyNode.__new__`` works as intended.
    """
    node = KeyNode()
    _assert_fields_set(node)
    
    vampytest.assert_is(node.character_sub_nodes, None)
    vampytest.assert_eq(node.end, False)
    vampytest.assert_is(node.character_sub_nodes, None)


@vampytest.call_with(None)
@vampytest.call_with(object())
def test__KeyNode__eq__same_type(other):
    """
    Tests whether ``KeyNode.__eq__`` works as intended.
    
    Parameters
    ----------
    other : `object`
        Object to compare to.
    
    Returns
    -------
    output : `bool`
    """
    node = KeyNode()
    output = node == other
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def _iter_options__eq__same_type():
    node_0 = KeyNode()

    node_1 = KeyNode()
    
    yield node_0, node_1, True
    
    node_0 = KeyNode()
    node_0.add_character_sub_node('a')
    node_0.add_matcher_sub_node(str.islower)
    node_0.set_end()
    
    node_1 = KeyNode()
    node_1.add_character_sub_node('a')
    node_1.add_matcher_sub_node(str.islower)
    node_1.set_end()
    
    yield node_0, node_1, True

    node_0 = KeyNode()

    node_1 = KeyNode()
    node_1.add_character_sub_node('a')
    
    yield node_0, node_1, False

    node_0 = KeyNode()

    node_1 = KeyNode()
    node_1.add_matcher_sub_node(str.islower)
    
    yield node_0, node_1, False

    node_0 = KeyNode()

    node_1 = KeyNode()
    node_1.set_end()
    
    yield node_0, node_1, False


@vampytest._(vampytest.call_from(_iter_options__eq__same_type()).returning_last())
def test__KeyNode__eq__same_type(node_0, node_1):
    """
    Tests whether ``KeyNode.__eq__`` works as intended.
    
    Parameters
    ----------
    node_0 : ``KeyNode``
        Node to compare.
    node_1 : ``KeyNode``
        Node to compare.
    
    Returns
    -------
    output : `bool`
    """
    output = node_0 == node_1
    vampytest.assert_instance(output, bool)
    return output


def test__KeyNode__repr():
    """
    Tests whether ``KeyNode.__repr__`` works as intended.
    """
    node = KeyNode()
    node.add_character_sub_node('a')
    node.add_matcher_sub_node(str.islower)
    node.set_end()
    
    vampytest.assert_instance(repr(node), str)


def test__KeyNode__set_end():
    """
    Tests whether ``KeyNode.set_end`` works as intended.
    """
    node = KeyNode()
    node.set_end()
    vampytest.assert_instance(node.end, bool)
    vampytest.assert_eq(node.end, True)


def test__KeyNode__add_character_sub_node__first():
    """
    Tests whether ``KeyNode.add_character_sub_node`` works as intended.
    
    Case: Adding first.
    """
    core_node = KeyNode()
    
    node = core_node.add_character_sub_node('a')
    _assert_fields_set(node)
    
    vampytest.assert_eq(core_node.character_sub_nodes, {'a': KeyNode()})


def test__KeyNode__add_character_sub_node__duplicate():
    """
    Tests whether ``KeyNode.add_character_sub_node`` works as intended.
    
    Case: Adding duplicate.
    """
    core_node = KeyNode()
    
    node_0 = core_node.add_character_sub_node('a')
    node_1 = core_node.add_character_sub_node('a')
    
    vampytest.assert_is(node_0, node_1)


def test__KeyNode__add_matcher_sub_node__first():
    """
    Tests whether ``KeyNode.add_matcher_sub_node`` works as intended.
    
    Case: Adding first.
    """
    core_node = KeyNode()
    
    node = core_node.add_matcher_sub_node(str.isupper)
    _assert_fields_set(node)
    
    vampytest.assert_eq(core_node.matcher_sub_nodes, [(str.isupper, KeyNode())])


def test__KeyNode__add_matcher_sub_node__duplicate():
    """
    Tests whether ``KeyNode.add_matcher_sub_node`` works as intended.
    
    Case: Adding duplicate.
    """
    core_node = KeyNode()
    
    node_0 = core_node.add_matcher_sub_node(str.isupper)
    node_1 = core_node.add_matcher_sub_node(str.isupper)
    
    vampytest.assert_is(node_0, node_1)


def _iter_options__match():
    node = KeyNode()
    character = 'a'
    yield node, character, None
    
    node = KeyNode()
    character = 'a'
    sub_node = node.add_character_sub_node(character)
    yield node, character, sub_node

    node = KeyNode()
    character = 'a'
    node.add_character_sub_node('b')
    yield node, character, None

    node = KeyNode()
    character = 'a'
    sub_node = node.add_matcher_sub_node(str.islower)
    yield node, character, sub_node

    node = KeyNode()
    character = 'A'
    node.add_matcher_sub_node(str.islower)
    yield node, character, None

    node = KeyNode()
    character = 'A'
    node.add_character_sub_node('b')
    node.add_matcher_sub_node(str.islower)
    yield node, character, None

    node = KeyNode()
    character = 'a'
    node.add_character_sub_node('b')
    sub_node = node.add_matcher_sub_node(str.islower)
    yield node, character, sub_node


@vampytest._(vampytest.call_from(_iter_options__match()).returning_last())
def test__KeyNode__match(node, character):
    """
    Tests whether ``KeyNode.match`` works as intended.
    
    Parameters
    ----------
    node : ``KeyNode``
        Node to match with.
    character : `str`
        Character to match.
    """
    output = node.match(character)
    vampytest.assert_instance(output, KeyNode, nullable = True)
    return output
