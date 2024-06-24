import vampytest

from ..line_render_intermediate import LineRenderIntermediate
from ..terminal_control_commands import COMMAND_UP


def _assert_fields_set(line):
    """
    Asserts whether every fields set of the given line.
    
    Parameters
    ----------
    line : ``LineRenderIntermediate``
    """
    vampytest.assert_instance(line, LineRenderIntermediate)
    vampytest.assert_instance(line.parts, list)


def test__LineRenderIntermediate__new():
    """
    Tests whether ``LineRenderIntermediate.__new__`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    
    line = LineRenderIntermediate(prefix_length, prefix)
    _assert_fields_set(line)
    
    vampytest.assert_eq(line.parts, [(prefix_length, prefix)])


def test__LineRenderIntermediate__add_command():
    """
    Tests whether ``LineRenderIntermediate.add_command`` works as intended.
    """
    value = COMMAND_UP
    
    line = LineRenderIntermediate(0, '')
    line.add_command(value)
    
    vampytest.assert_eq(line.parts, [(0, ''), (0, value)])


def test__LineRenderIntermediate__add_part():
    """
    Tests whether ``LineRenderIntermediate.add_part`` works as intended.
    """
    value = 'miau'
    
    line = LineRenderIntermediate(0, '')
    line.add_part(value)
    
    vampytest.assert_eq(line.parts, [(0, ''), (len(value), value)])


def test__LineRenderIntermediate__repr():
    """
    Tests whether ``LineRenderIntermediate.__repr__`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    
    line = LineRenderIntermediate(prefix_length, prefix)
    
    output = repr(line)
    vampytest.assert_instance(output, str)


def test__LineRenderIntermediate__eq():
    """
    Tests whether ``LineRenderIntermediate.__repr__`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    
    line_0 = LineRenderIntermediate(prefix_length, prefix)
    line_1 = LineRenderIntermediate(prefix_length, prefix)
    
    vampytest.assert_eq(line_0, line_1)
    vampytest.assert_ne(line_0, object())
    
    line_0.add_part('miau')
    vampytest.assert_ne(line_0, line_1)

def test__LineRenderIntermediate__iter_parts():
    """
    Tests whether ``LineRenderIntermediate.iter_parts`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    value_0 = COMMAND_UP
    value_1 = 'miau'
    
    line = LineRenderIntermediate(prefix_length, prefix)
    line.add_command(value_0)
    line.add_part(value_1)
    
    output = [*line.iter_parts()]
    
    vampytest.assert_eq(
        output,
        [prefix, value_0, value_1],
    )


def test__LineRenderIntermediate__iter_items():
    """
    Tests whether ``LineRenderIntermediate.iter_items`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    value_0 = COMMAND_UP
    value_1 = 'miau'
    
    line = LineRenderIntermediate(prefix_length, prefix)
    line.add_command(value_0)
    line.add_part(value_1)
    
    output = [*line.iter_items()]
    
    vampytest.assert_eq(
        output,
        [(prefix_length, prefix), (0, value_0), (len(value_1), value_1)],
    )


def test__LineRenderIntermediate__get_length():
    """
    Tests whether ``LineRenderIntermediate.get_length`` works as intended.
    """
    prefix_length = 8
    prefix = 'In [0]: '
    value_0 = COMMAND_UP
    value_1 = 'miau'
    
    line = LineRenderIntermediate(prefix_length, prefix)
    line.add_command(value_0)
    line.add_part(value_1)
    
    output = line.get_length()
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, prefix_length + len(value_1))
