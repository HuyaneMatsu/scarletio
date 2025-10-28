import vampytest

from ..rendering import (
    _produce_attribute_name, _produce_attribute_name_only, _produce_file_location, _produce_grave_wrapped,
    _produce_variable_attribute_access, _produce_variable_attribute_access_only, _produce_variable_name,
    _produce_variable_name_only
)


def _iter_options__produce_file_location():
    # default
    yield 'koishi.py', 56, 'watch', False, '  File "koishi.py", line 57, in watch\n'
    
    # expression line count > 1
    yield 'koishi.py', 56, 'watch', True, '  File "koishi.py", around line 57, in watch\n'
    
    # `"` in file name
    yield 'koi"shi.py', 56, 'watch', False, '  File "koi\\"shi.py", line 57, in watch\n'
    
    # no file name
    yield '', 56, 'watch', False, '  File unknown location, line 57, in watch\n'
    
    # no function name
    yield 'koishi.py', 56, '', False, '  File "koishi.py", line 57\n'


@vampytest._(vampytest.call_from(_iter_options__produce_file_location()).returning_last())
def test__produce_file_location(file_name, line_index, name, multi_line):
    """
    Tests whether ``_produce_file_location`` works as intended.
    
    Parameters
    ----------
    file_name : `str`
        Path of the respective file.
    
    line_index : int`
        The respective line's index.
    
    name : `str`
        The respective functions name.
    
    multi_line : `int`
        Whether the expression expands over multiple lines.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_file_location(file_name, line_index, name, multi_line)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_variable_name_only():
    # default
    yield 'koishi', 'koishi'


@vampytest._(vampytest.call_from(_iter_options__produce_variable_name_only()).returning_last())
def test__produce_variable_name_only(variable_name):
    """
    Tests whether ``_produce_variable_name_only`` works as intended.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_variable_name_only(variable_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_attribute_name_only():
    # default
    yield 'koishi', '.koishi'


@vampytest._(vampytest.call_from(_iter_options__produce_attribute_name_only()).returning_last())
def test__produce_attribute_name_only(attribute_name):
    """
    Tests whether ``_produce_attribute_name_only`` works as intended.
    
    Parameters
    ----------
    attribute_name : `str`
        Attribute name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_attribute_name_only(attribute_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_variable_attribute_access_only():
    # default
    yield 'satori', 'koishi', 'satori.koishi'


@vampytest._(vampytest.call_from(_iter_options__produce_variable_attribute_access_only()).returning_last())
def test__produce_variable_attribute_access_only(variable_name, attribute_name):
    """
    Tests whether ``_produce_variable_attribute_access_only`` works as intended.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to render.
    attribute_name : `str`
        Attribute name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_variable_attribute_access_only(variable_name, attribute_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_grave_wrapped():
    # default
    yield [(0, 'satori')], '`satori`'
    
    # no length
    yield [], '``'
    
    # extra long
    yield [(0, 'satori'), (0, ' '), (0, 'mister')], '`satori mister`'


@vampytest._(vampytest.call_from(_iter_options__produce_grave_wrapped()).returning_last())
def test__produce_grave_wrapped(producer):
    """
    Tests whether ``_produce_grave_wrapped`` works as intended.
    
    Parameters
    ----------
    producer : `iterable<(int, str)>`
        The producer to wrap into grave characters.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_grave_wrapped(producer)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_variable_name():
    # default
    yield 'koishi', '`koishi`'


@vampytest._(vampytest.call_from(_iter_options__produce_variable_name()).returning_last())
def test__produce_variable_name(variable_name):
    """
    Tests whether ``_produce_variable_name`` works as intended.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_variable_name(variable_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_attribute_name():
    # default
    yield 'koishi', '`.koishi`'


@vampytest._(vampytest.call_from(_iter_options__produce_attribute_name()).returning_last())
def test__produce_attribute_name(attribute_name):
    """
    Tests whether ``_produce_attribute_name`` works as intended.
    
    Parameters
    ----------
    attribute_name : `str`
        Attribute name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_attribute_name(attribute_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string


def _iter_options__produce_variable_attribute_access():
    # default
    yield 'satori', 'koishi', '`satori.koishi`'


@vampytest._(vampytest.call_from(_iter_options__produce_variable_attribute_access()).returning_last())
def test__produce_variable_attribute_access(variable_name, attribute_name):
    """
    Tests whether ``_produce_variable_attribute_access`` works as intended.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to render.
    attribute_name : `str`
        Attribute name to render.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_variable_attribute_access(variable_name, attribute_name)]
    
    for item in output:
        vampytest.assert_instance(item, tuple)
        vampytest.assert_eq(len(item), 2)
        vampytest.assert_instance(item[0], int)
        vampytest.assert_instance(item[1], str)
    
    output_string = ''.join([item[1] for item in output])
    return output_string
