from itertools import repeat

import vampytest

from .....utils import iter_produce_ansi_format_code

from ..display_state import CONTINUOUS_LINE_POSTFIX, DisplayState, EMPTY_LINE_PREFIX_CHARACTER
from ..line_render_intermediate import LineRenderIntermediate
from ..terminal_control_commands import (
    COMMAND_CLEAR_LINE_FROM_CURSOR, COMMAND_CLEAR_LINE_WHOLE, COMMAND_DOWN, COMMAND_FORMAT_RESET, COMMAND_START_LINE,
    COMMAND_UP, create_command_down, create_command_left, create_command_right, create_command_up
)

def _assert_fields_set(display_state):
    """
    Asserts whether every fields of the display state are set.
    
    Parameters
    ----------
    display_state : ``DisplayState``
        The display state to test. 
    """
    vampytest.assert_instance(display_state, DisplayState)
    vampytest.assert_instance(display_state.buffer, list)
    vampytest.assert_instance(display_state.cursor_index, int)
    vampytest.assert_instance(display_state.cursor_line_index, int)
    vampytest.assert_instance(display_state.content_width, int)


def test__DisplayState__new():
    """
    Tests whether ``DisplayState.__new__`` works as intended.
    """
    buffer = ['hey', 'mister']
    
    display_state = DisplayState(buffer)
    
    vampytest.assert_eq(display_state.buffer, buffer)
    vampytest.assert_eq(display_state.cursor_index, 6)
    vampytest.assert_eq(display_state.cursor_line_index, 1)
    vampytest.assert_eq(display_state.content_width, -1)


def test__DisplayState__repr():
    """
    Tests whether ``DisplayState.__repr__`` works as intended.
    """
    buffer = ['hey', 'mister']
    
    display_state = DisplayState(buffer)
    
    output = repr(display_state)
    
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(display_state).__name__, output)


def test__DisplayState__copy():
    """
    Tests whether ``DisplayState.copy`` works as intended.
    """
    buffer = ['hey', 'mister']
    cursor_index = 3
    cursor_line_index = 0
    content_width = 120
    
    
    display_state = DisplayState(buffer)
    display_state.cursor_index = cursor_index
    display_state.cursor_line_index = cursor_line_index
    display_state.content_width = content_width
    
    copy = display_state.copy()
    
    _assert_fields_set(copy)
    vampytest.assert_is_not(display_state, copy)
    
    vampytest.assert_eq(copy.buffer, buffer)
    vampytest.assert_eq(copy.cursor_index, cursor_index)
    vampytest.assert_eq(copy.cursor_line_index, cursor_line_index)
    vampytest.assert_eq(copy.content_width, -1)


def _iter_options__get_cursor_from_start_display_line_count():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        0,
    )
    
    yield (
        ['hey', 'mister'],
        {},
        8,
        0,
    )
    
    yield (
        ['hey', 'mister'],
        {
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        0,
    )
    
    # lines are longer than 1 line
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        0,
    )
    
    yield (
        ['a' * 81, 'd' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        1,
    )
    
    yield (
        ['a' * 81, 'c' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        8,
        2,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        8,
        3,
    )


@vampytest._(vampytest.call_from(_iter_options__get_cursor_from_start_display_line_count()).returning_last())
def test__DisplayState__get_cursor_from_start_display_line_count(buffer, attributes, prefix_length):
    """
    Tests whether ``DisplayState.get_cursor_from_start_display_line_count`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `int`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    output = display_state.get_cursor_from_start_display_line_count(prefix_length)
    vampytest.assert_instance(output, int)
    return output


def _iter_options__get_cursor_till_end_display_line_count():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        0,
    )
    
    yield (
        ['hey', 'mister'],
        {},
        80,
        8,
        0,
    )
    
    yield (
        ['hey', 'mister'],
        {
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        1,
    )
    
    # lines are longer than 1 line
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        3,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        2,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        1,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        0,
    )


@vampytest._(vampytest.call_from(_iter_options__get_cursor_till_end_display_line_count()).returning_last())
def test__DisplayState__get_cursor_till_end_display_line_count(buffer, attributes, new_content_width, prefix_length):
    """
    Tests whether ``DisplayState.get_cursor_till_end_display_line_count`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `int`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    output = display_state.get_cursor_till_end_display_line_count(prefix_length, new_content_width)
    vampytest.assert_instance(output, int)
    return output


def _iter_options__get_start_till_end_display_line_count():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        1,
    )
    
    yield (
        ['hey', 'mister'],
        {},
        80,
        8,
        2,
    )
    
    yield (
        ['hey', 'mister'],
        {
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        2,
    )
    
    # lines are longer than 1 line
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        4,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        4,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 80,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        4,
    )
    
    yield (
        ['a' * 81, 'b' * 81],
        {
            'cursor_index': 81,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        4,
    )


@vampytest._(vampytest.call_from(_iter_options__get_start_till_end_display_line_count()).returning_last())
def test__DisplayState__get_start_till_end_display_line_count(buffer, attributes, new_content_width, prefix_length):
    """
    Tests whether ``DisplayState.get_start_till_end_display_line_count`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `int`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    output = display_state.get_start_till_end_display_line_count(prefix_length, new_content_width)
    vampytest.assert_instance(output, int)
    return output


def _iter_options__jump_to_end():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        '',
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {},
        80,
        8,
        '',
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        create_command_down(2),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        create_command_down(1),
    )
    

@vampytest._(vampytest.call_from(_iter_options__jump_to_end()).returning_last())
def test__DisplayState__jump_to_end(buffer, attributes, new_content_width, prefix_length):
    """
    Tests whether ``DisplayState.jump_to_end`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    write_buffer = []
    display_state.jump_to_end(write_buffer, prefix_length, new_content_width)
    return ''.join(write_buffer)


def _iter_options__clear():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        COMMAND_START_LINE + COMMAND_CLEAR_LINE_WHOLE,
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {},
        80,
        8,
        '',
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        create_command_down(2) + COMMAND_START_LINE + COMMAND_UP.join(repeat(COMMAND_CLEAR_LINE_WHOLE, 3)),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        create_command_down(1) + COMMAND_START_LINE + COMMAND_UP.join(repeat(COMMAND_CLEAR_LINE_WHOLE, 3)),
    )


@vampytest._(vampytest.call_from(_iter_options__clear()).returning_last())
def test__DisplayState__clear(buffer, attributes, new_content_width, prefix_length):
    """
    Tests whether ``DisplayState.clear`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `str`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    write_buffer = []
    display_state.clear(write_buffer, prefix_length, new_content_width)
    return ''.join(write_buffer)


def _iter_options__write_cursor():
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        COMMAND_START_LINE + create_command_right(8 + 2),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        create_command_up(2) + COMMAND_START_LINE + create_command_right(8 + 0),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        8,
        create_command_up(1) + COMMAND_START_LINE + create_command_right(8 + 4),
    )


@vampytest._(vampytest.call_from(_iter_options__write_cursor()).returning_last())
def test__DisplayState__write_cursor(buffer, attributes, prefix_length):
    """
    Tests whether ``DisplayState.write_cursor`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    output : `str`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    write_buffer = []
    display_state.write_cursor(write_buffer, prefix_length)
    return ''.join(write_buffer)


def _iter_options__write():
    color_code = '\x1b[38;2;220;255;255m'
    
    yield (
        ['aa aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            COMMAND_FORMAT_RESET,
            COMMAND_START_LINE, 'In [0]: ', color_code, 'aa', COMMAND_FORMAT_RESET, ' ', color_code, 'aa', COMMAND_FORMAT_RESET
        ]),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            COMMAND_FORMAT_RESET,
            COMMAND_START_LINE, 'In [0]: ', color_code, 'hey', COMMAND_FORMAT_RESET, COMMAND_DOWN,
            COMMAND_START_LINE, '   ...: ', color_code, 'mister', COMMAND_FORMAT_RESET, COMMAND_DOWN,
            COMMAND_START_LINE, '   ...: ', color_code, 'sister', COMMAND_FORMAT_RESET,
        ]),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            COMMAND_FORMAT_RESET,
            COMMAND_START_LINE, 'In [0]: ', color_code, 'hey', COMMAND_FORMAT_RESET, COMMAND_DOWN,
            COMMAND_START_LINE, '   ...: ', color_code, 'mister', COMMAND_FORMAT_RESET, COMMAND_DOWN,
            COMMAND_START_LINE, '   ...: ', color_code, 'sister', COMMAND_FORMAT_RESET,
        ]),
    )
    
    yield (
        [''],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            COMMAND_FORMAT_RESET,
            COMMAND_START_LINE, 'In [0]: ',
        ]),
    )

    yield (
        ['a' * 81],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80 - 8 - len(EMPTY_LINE_PREFIX_CHARACTER),
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            COMMAND_FORMAT_RESET,
            COMMAND_START_LINE, 'In [0]: ', color_code, 'a' * (80 - 8 - len(EMPTY_LINE_PREFIX_CHARACTER)), CONTINUOUS_LINE_POSTFIX, COMMAND_DOWN,
            COMMAND_START_LINE, EMPTY_LINE_PREFIX_CHARACTER * 8, color_code, 'a' * (1 + 8 + len(EMPTY_LINE_PREFIX_CHARACTER)), COMMAND_FORMAT_RESET,
        ]),
    )


@vampytest._(vampytest.call_from(_iter_options__write()).returning_last())
def test__DisplayState__write(buffer, attributes, new_content_width, prefix_length, prefix_initial, prefix_continuous):
    """
    Tests whether ``DisplayState.write`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    prefix_initial : `str`
        Prefix to use for the first line.
    prefix_continuous : `str`
        Prefix to use for additional lines.
    
    Returns
    -------
    output : `str`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    write_buffer = []
    display_state.write(write_buffer, prefix_length, prefix_initial, prefix_continuous, new_content_width)
    return ''.join(write_buffer)


def _iter_options__get_line_render_intermediates():
    color_code_parts = [*iter_produce_ansi_format_code(foreground_color = (220, 255, 255))]
    format_reset_parts = [*iter_produce_ansi_format_code(reset = True)]
    
    line_0 = LineRenderIntermediate(8, 'In [0]: ')
    for part in color_code_parts:
        line_0.add_command(part)
    line_0.add_part('aa')
    for part in format_reset_parts:
        line_0.add_command(part)
    
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        [line_0],
    )
    
    line_0 = LineRenderIntermediate(8, 'In [0]: ')
    for part in color_code_parts:
        line_0.add_command(part)
    line_0.add_part('hey')
    for part in format_reset_parts:
        line_0.add_command(part)
    line_1 = LineRenderIntermediate(8, '   ...: ')
    for part in color_code_parts:
        line_1.add_command(part)
    line_1.add_part('mister')
    for part in format_reset_parts:
        line_1.add_command(part)
    line_2 = LineRenderIntermediate(8, '   ...: ')
    for part in color_code_parts:
        line_2.add_command(part)
    line_2.add_part('sister')
    for part in format_reset_parts:
        line_2.add_command(part)
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        [line_0, line_1, line_2],
    )
    
    line_0 = LineRenderIntermediate(8, 'In [0]: ')
    for part in color_code_parts:
        line_0.add_command(part)
    line_0.add_part('hey')
    for part in format_reset_parts:
        line_0.add_command(part)
    line_1 = LineRenderIntermediate(8, '   ...: ')
    for part in color_code_parts:
        line_1.add_command(part)
    line_1.add_part('mister')
    for part in format_reset_parts:
        line_1.add_command(part)
    line_2 = LineRenderIntermediate(8, '   ...: ')
    for part in color_code_parts:
        line_2.add_command(part)
    line_2.add_part('sister')
    for part in format_reset_parts:
        line_2.add_command(part)
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        [line_0, line_1, line_2],
    )
    
    line_0 = LineRenderIntermediate(8, 'In [0]: ')
    
    yield (
        [''],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        80,
        8,
        'In [0]: ',
        '   ...: ',
        [line_0],
    )

    line_0 = LineRenderIntermediate(8, 'In [0]: ')
    for part in color_code_parts:
        line_0.add_command(part)
    line_0.add_part('a' * (80 - 8 - len(EMPTY_LINE_PREFIX_CHARACTER)))
    line_0.add_part(CONTINUOUS_LINE_POSTFIX)
    line_1 = LineRenderIntermediate(8, EMPTY_LINE_PREFIX_CHARACTER * 8)
    # The last used command is collected and joined, so add it as one.
    line_1.add_command(''.join(color_code_parts))
    line_1.add_part('a' * (1 + 8 + len(EMPTY_LINE_PREFIX_CHARACTER)))
    for part in format_reset_parts:
        line_1.add_command(part)
    
    yield (
        ['a' * 81],
        {
            'cursor_index': 4,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        80 - 8 - len(EMPTY_LINE_PREFIX_CHARACTER),
        8,
        'In [0]: ',
        '   ...: ',
        [line_0, line_1],
    )


@vampytest._(vampytest.call_from(_iter_options__get_line_render_intermediates()).returning_last())
def test__DisplayState__get_line_render_intermediates(
    buffer, attributes, new_content_width, prefix_length, prefix_initial, prefix_continuous
):
    """
    Tests whether ``DisplayState.get_line_render_intermediates`` works as intended.
    
    Parameters
    ----------
    buffer : `list<str>`
        Buffer to create display state with.
    attributes : `dict<str, object>`
        Additional attributes to set.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    prefix_initial : `str`
        Prefix to use for the first line.
    prefix_continuous : `str`
        Prefix to use for additional lines.
    
    Returns
    -------
    output : `list<LineRenderIntermediate>`
    """
    display_state = DisplayState(buffer)
    for item in attributes.items():
        setattr(display_state, *item)
    
    return display_state.get_line_render_intermediates(
        prefix_length, prefix_initial, prefix_continuous, new_content_width
    )


def _iter_options__write_difference():
    color_code = '\x1b[38;2;220;255;255m'
    
    yield (
        ['aa aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        ['aa aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([]),
    )
    
    yield (
        ['aa aa'],
        {
            'cursor_index': 1,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        ['aa aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([create_command_right(1)]),
    )
    
    yield (
        [''],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 2,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            # On first line prefix is shared, so we it
            COMMAND_START_LINE, create_command_right(8), COMMAND_FORMAT_RESET, color_code, 'hey', COMMAND_FORMAT_RESET,
            COMMAND_DOWN, COMMAND_START_LINE, '   ...: ', color_code, 'mister', COMMAND_FORMAT_RESET,
            COMMAND_DOWN, COMMAND_START_LINE, '   ...: ', color_code, 'sister', COMMAND_FORMAT_RESET,
            create_command_up(1),
            create_command_left(4),
        ]),
    )
    
    yield (
        ['hey', 'mister', 'sister'],
        {
            'cursor_index': 2,
            'cursor_line_index': 1,
            'content_width': 80,
        },
        [''],
        {
            'cursor_index': 0,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([
            create_command_up(1),
            COMMAND_START_LINE, create_command_right(8), COMMAND_CLEAR_LINE_FROM_CURSOR,
            COMMAND_DOWN, COMMAND_CLEAR_LINE_WHOLE,
            COMMAND_DOWN, COMMAND_CLEAR_LINE_WHOLE,
            create_command_up(2),
        ]),
    )
    
    yield (
        ['aa'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        ['aaa'],
        {
            'cursor_index': 3,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([COMMAND_START_LINE, create_command_right(10), color_code, 'a', COMMAND_FORMAT_RESET]),
    )
    
    yield (
        ['de'],
        {
            'cursor_index': 2,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        ['def'],
        {
            'cursor_index': 3,
            'cursor_line_index': 0,
            'content_width': 80,
        },
        8,
        'In [0]: ',
        '   ...: ',
        ''.join([COMMAND_START_LINE, create_command_right(8), '\x1b[38;2;255;109;109m', 'def', COMMAND_FORMAT_RESET]),
    )


@vampytest._(vampytest.call_from(_iter_options__write_difference()).returning_last())
def test__DisplayState__write_difference(
    buffer_old, attributes_old, buffer_new, attributes_new, prefix_length, prefix_initial, prefix_continuous
):
    """
    Tests whether ``DisplayState.write_difference`` works as intended.
    
    Parameters
    ----------
    buffer_old : `list<str>`
        Buffer to create display state with.
    attributes_old : `dict<str, object>`
        Additional attributes to set.
    buffer_new : `list<str>`
        Buffer to create display state with.
    attributes_new : `dict<str, object>`
        Additional attributes to set.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    prefix_initial : `str`
        Prefix to use for the first line.
    prefix_continuous : `str`
        Prefix to use for additional lines.
    
    Returns
    -------
    output : `str`
    """
    display_state_old = DisplayState(buffer_old)
    for item in attributes_old.items():
        setattr(display_state_old, *item)
    
    display_state_new = DisplayState(buffer_new)
    for item in attributes_new.items():
        setattr(display_state_new, *item)
    
    write_buffer = []
    display_state_new.write_difference(
        display_state_old, write_buffer, prefix_length, prefix_initial, prefix_continuous
    )
    return ''.join(write_buffer)
