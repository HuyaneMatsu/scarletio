import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER, get_highlight_streamer, iter_split_ansi_format_codes

from ..rendering import (
    _produce_attribute_name, _produce_attribute_name_only, _produce_file_location, _produce_grave_wrapped,
    _produce_variable_attribute_access, _produce_variable_attribute_access_only, _produce_variable_name,
    _produce_variable_name_only, add_trace_title_into
)


def test__add_trace_title_into__no_highlighter():
    """
    Tests whether ``add_trace_title_into`` works as intended.
    
    Case: no highlighter.
    """
    input_value = 'koishi'
    
    highlight_streamer = get_highlight_streamer(None)
    output = add_trace_title_into(input_value, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    vampytest.assert_eq(len(output), 1)
    
    part = output[0]
    vampytest.assert_instance(part, str)
    vampytest.assert_eq(part, input_value)


def test__add_trace_title_into__with_highlighter():
    """
    Tests whether ``add_trace_title_into`` works as intended.
    
    Case: with highlighter.
    """
    input_value = 'koishi'
    
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = add_trace_title_into(input_value, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    output_string = ''.join([item[1] for item in iter_split_ansi_format_codes(output_string) if not item[0]])
    vampytest.assert_eq(output_string, input_value)


def _iter_options__produce_file_location():
    # default
    yield 'koishi.py', 56, 'watch', 1, '  File "koishi.py", line 57, in watch\n'
    
    # expression line count > 1
    yield 'koishi.py', 56, 'watch', 3, '  File "koishi.py", around line 57, in watch\n'
    
    # `"` in file name
    yield 'koi"shi.py', 56, 'watch', 1, '  File "koi\\"shi.py", line 57, in watch\n'
    
    # no file name
    yield '', 56, 'watch', 1, '  File unknown location, line 57, in watch\n'
    
    # no function name
    yield 'koishi.py', 56, '', 1, '  File "koishi.py", line 57\n'


@vampytest._(vampytest.call_from(_iter_options__produce_file_location()).returning_last())
def test__produce_file_location(file_name, line_index, name, line_count):
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
    line_count : `int`
        How much lines is the expression at the location.
    
    Returns
    -------
    output_string : `str`
    """
    output = [*_produce_file_location(file_name, line_index, name, line_count)]
    
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
