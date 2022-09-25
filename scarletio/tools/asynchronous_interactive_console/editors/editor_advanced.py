__all__ = ()

import sys, re, termios, tty
from os import get_blocking, get_terminal_size, set_blocking
from select import poll as Poller, POLLOUT as EVENT_POLL_WRITE
from selectors import DefaultSelector, EVENT_READ
from socket import socketpair as create_socket_pair
from ....utils import DEFAULT_ANSI_HIGHLIGHTER, copy_docs, create_ansi_format_code, iter_highlight_code_lines

from .compilation import maybe_compile
from .editor_base import EditorBase, _validate_buffer
from .prefix_trimming import trim_console_prefix


KEY_KEYBOARD_INTERRUPT = 3
KEY_DESTROY = 4
KEY_TAB = 9
KEY_NEW_LINE_ALL = (10, 13)
KEY_ARROW_ALL_INITIAL = 27
KEY_ARROW_ALL = 91
KEY_ARROW_UP = 65
KEY_ARROW_DOWN = 66
KEY_ARROW_RIGHT = 67
KEY_ARROW_LEFT = 68
KEY_ARROW_BACK_TAB = 90
KEY_DELETE_LEFT = 127
KEY_DELETE_RIGHT = 126

COMMAND_NEXT_LINE = '\n'
COMMAND_PREVIOUS_LINE = '\033[F'
COMMAND_START_LINE = '\u001b[1000D'
COMMAND_CLEAR_LINE = '\u001b[0K'
COMMAND_FORMAT_RESET = create_ansi_format_code()

EMPTY_LINE_PREFIX_CHARACTER = ' '
CONTINUOUS_LINE_POSTFIX = '\\'

DEDENT_WORDS = frozenset((
    'pass',
    'return',
    'continue',
    'break'
))

EMPTY_CHARACTERS = frozenset((' ', '\t', '\n'))

INDEXED_INPUT_RP = re.compile('\s*in\s*\[\s*(\d+)\s*\]\s*', re.I)

CHARACTER_CHAINED_OPERATION = chr(KEY_ARROW_ALL_INITIAL)

STDOUT_WRITE_TIMEOUT = 30.0


def create_command_move_cursor(position):
    """
    Creates a command which moves the cursor on the current line to the given position.
    
    Parameters
    ----------
    position : `str`
        The position to move the cursor to
    
    Returns
    -------
    command : `str`
    """
    if position <= 0:
        return ''
    
    return f'\u001b[{position + 1}C'


def get_starting_space_count(line):
    """
    Returns how much space the line has at it's start.
    
    Parameters
    ----------
    line : `str`
        The line to check out.
    
    Returns
    -------
    space_count : `int`
    """
    space_count = 0
    for character in line:
        if character != ' ':
            break
            
        space_count += 1
        continue
    
    return space_count


def add_linebreaks_between(lines):
    """
    Adds linebreaks between the given lines and returns a new list.
    
    Parameters
    ----------
    lines : `list` of `str`
        Lines to add spaces between.
    
    Returns
    -------
    new_lines : `list` of `str`
    """
    new_lines = []
    
    length = len(lines)
    if length:
        
        index = 0
        
        while True:
            line = lines[index]
            new_lines.append(line)
            
            index += 1
            if index >= length:
                break
            
            new_lines.append('\n')
            continue
    
    return new_lines


def line_ends_with(line, target):
    """
    Returns whether the given line ends with the given character.
    
    Spaces ignored.
    
    Parameters
    ----------
    line : `str`
        The lien to check out.
    target : `str`
        The character to look for.
    
    Returns
    -------
    ends_with : `bool`
    """
    for character in reversed(line):
        if character == target:
            return True
        
        if character == ' ':
            continue
        
        break
    
    return False


def line_starts_with_word_any(line, words):
    """
    Returns whether the given line ends with the any of the given words.
    
    Spaces ignored.
    
    Parameters
    ----------
    line : `str`
        The lien to check out.
    words : `frozenset` of `str`
        The words to look for.
    
    Returns
    -------
    ends_with : `bool`
    """
    line = line.lstrip()
    
    for word in words:
        if line.startswith(word):
            if len(line) == len(word) or line[len(word)] == ' ':
                return True
    
    return False


def iter_highlighted_buffer_parts(buffer, highlighter):
    """
    Iterates over the buffer parts and highlights them.
    
    This method is an iterable generator.
    
    Parameters
    ----------
    buffer : `list` of `str`
        Line buffer.
    highlighter : `None`, ``HighlightFormatterContext``
        The highlighter to use.
    
    Yields
    ------
    part : `str`
    """
    buffer = add_linebreaks_between(buffer)
    
    if highlighter is None:
        yield from buffer
    
    else:
        yield from iter_highlight_code_lines(buffer, highlighter)


def is_command(part):
    """
    Returns whether the given part is an ansi command.
    
    Parameters
    ----------
    part : `str`
        the part to check.
    
    Returns
    -------
    is_ansi_command : `bool`
    """
    return part.startswith('\u001b[')


def get_new_content_width(display_state, editor):
    """
    Gets the new column with and whether it changes.
    
    Parameters
    ----------
    display_state : ``DisplayState``
        The current display state.
    editor : ``EditorAdvanced``
        The respective editor.
    
    Returns
    -------
    new_column_with : `int`
        Returns `-1` if there was no change.
    """
    new_column_with = get_terminal_size().columns - editor.prefix_length - len(CONTINUOUS_LINE_POSTFIX)
    if display_state.content_width == new_column_with:
        new_column_with = - 1
    
    return new_column_with


def get_line_line_count(line_length, content_width, new_content_width, prefix_length):
    """
    Returns how much lines the given line is displayed as.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    line_line_count : `int`
    """
    if (new_content_width == -1) or (new_content_width > content_width):
        return _get_line_line_count_unchanged(line_length, content_width)
    
    return _get_line_line_count_changed(line_length, content_width, new_content_width, prefix_length)


def _get_line_line_count_unchanged(line_length, content_width):
    """
    Returns how much lines the given line is displayed as.
    
    This function handles the case when content width is not changed or is increased.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    
    Returns
    -------
    line_line_count : `int`
    """
    if line_length == 0:
        line_line_count = 1
    else:
        line_line_count = 1 + (line_length - 1) // content_width
    
    return line_line_count


def _get_line_line_count_changed(line_length, content_width, new_content_width, prefix_length):
    """
    Returns how much lines the given line is displayed as.
    
    This function handles the case when the content width is reduced and further calculations are required.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    new_content_width : `int`
        The new column width to use.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    line_line_count : `int`
    """
    line_line_count = 0
    
    if line_length == 0:
        line_line_count += 1
    
    else:
        additional_length = prefix_length + len(CONTINUOUS_LINE_POSTFIX)
        old_full_line_length = content_width + additional_length
        new_full_line_length = new_content_width + additional_length
        
        full_line_count = line_length // content_width
        if full_line_count > 0:
            last_line_length = line_length - (full_line_count * content_width)
            
            line_line_count = full_line_count * _get_line_line_count_unchanged(
                old_full_line_length, new_full_line_length
            )
            
        else:
            last_line_length = line_length
        
        if last_line_length > 0:
            line_line_count += 1 + ((last_line_length + prefix_length - 1) // new_full_line_length)
        
    return line_line_count


def _check_is_line_empty(line):
    """
    Returns whether the given line is empty.
    
    Parameters
    ----------
    line : `str`
        The line to check out.
    
    Returns
    -------
    is_empty : `bool`
    """
    for character in line:
        if character not in EMPTY_CHARACTERS:
            return False
    
    return True


def _check_is_line_empty_at(line, index):
    """
    Returns whether the line is empty at the given position.
    
    Parameters
    ----------
    line : `str`
        The line to check out.
    index : `int`
        The exact position.
    
    Returns
    -------
    is_line_empty_at : `bool`
    """
    line_length = len(line)
    if (index < line_length) and (index >= 0):
        if line[index] not in EMPTY_CHARACTERS:
            return False
    
    return True


def _check_is_buffer_line_empty_at(buffer, line_index, index):
    """
    Returns whether the buffer's specified line is empty at the given index.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    line_index : `int`
        The line's index to check out.
    index : `int`
        The exact position.
    
    Returns
    -------
    is_buffer_line_empty_at : `bool`
    """
    buffer_length = len(buffer)
    if (line_index < buffer_length) and (line_index >= 0):
        return _check_is_line_empty_at(buffer[line_index], index)
    
    return True


def _check_is_line_empty_after(line, index):
    """
    Returns whether the line is empty after the given index. Excluding the character at `index` position.
    
    Parameters
    ----------
    line : `str`
        The line to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_line_empty_after : `bool`
    """
    index += 1
    
    line_length = len(line)
    while index < line_length:
        if line[index] not in EMPTY_CHARACTERS:
            return False
        
        index += 1
    
    return True


def _check_is_buffer_line_empty_after(buffer, line_index, index):
    """
    Returns whether the buffer's specified line is empty after the given index.
    Excluding the character at `index` position.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    line_index : `int`
        The line's index to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_buffer_line_empty_after : `bool`
    """
    buffer_length = len(buffer)
    if (line_index < buffer_length) and (line_index >= 0):
        return _check_is_line_empty_after(buffer[line_index], index)
    
    return True


def _check_is_line_empty_before(line, index):
    """
    Returns whether the line is empty before the given index. Excluding the character at `index` position.
    
    Parameters
    ----------
    line : `str`
        The line to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_line_empty_before : `bool`
    """
    index -= 1
    
    line_length = len(line)
    if index >= line_length:
        index = line_length - 1
    
    while index >= 0:
        if line[index] not in EMPTY_CHARACTERS:
            return False
        
        index -= 1
        continue

    return True


def _check_is_buffer_line_empty_before(buffer, line_index, index):
    """
    Returns whether the buffer's specified line is empty before the given index.
    Excluding the character at `index` position.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    line_index : `int`
        The line's index to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_buffer_line_empty_before : `bool`
    """
    buffer_length = len(buffer)
    if (line_index < buffer_length) and (line_index >= 0):
        return _check_is_line_empty_before(buffer[line_index], index)
    
    return True


def _check_is_buffer_empty_at(buffer, index):
    """
    Returns whether the exact line of the buffer is empty.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    index : `int`
        The line's index to check out.
    
    Returns
    -------
    is buffer_empty_at : `bool`
    """
    buffer_length = len(buffer)
    if (index < buffer_length) and (index >= 0):
        return _check_is_line_empty(buffer[index])
    
    return True


def _check_is_buffer_empty_before(buffer, index):
    """
    Returns whether the buffer is empty before the given index. Excluding the `index`'s exact position.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_buffer_empty_before : `bool`
    """
    index -= 1
    
    buffer_length = len(buffer)
    if index >= buffer_length:
        index = buffer_length - 1
    
    
    while index >= 0:
        if not _check_is_line_empty(buffer[index]):
            return False
        
        index -= 1
        continue
    
    return True


def _check_is_buffer_empty_after(buffer, index):
    """
    Returns whether the buffer is empty after the given index. Excluding the `index`'s exact position.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The buffer to check out.
    index : `int`
        The starting position.
    
    Returns
    -------
    is_buffer_empty_after : `bool`
    """
    buffer_length = len(buffer)
    
    index += 1
    
    while index < buffer_length:
        if not _check_is_line_empty(buffer[index]):
            return False
        
        index += 1
        continue
    
    return True


def _check_should_try_compile_one_line(display_state):
    """
    Checks whether the current input should be tried to be compiled.
    
    This function is called when the buffer's length is `exactly 1`.
    
    Parameters
    ----------
    display_state : ``DisplayState``
        The respective input.
    
    Returns
    -------
    should_try_compile : `bool`
    """
    line = display_state.buffer[display_state.cursor_line_index]
    cursor_index = display_state.cursor_index
    
    if not _check_is_line_empty_after(line, cursor_index):
        return False
    
    if not _check_is_line_empty_at(line, cursor_index):
        return False
    
    if _check_is_line_empty_before(line, cursor_index):
        return False
    
    return True


def _check_should_try_compile_multi_line(display_state):
    """
    Checks whether the current input should be tried to be compiled.
    
    This function is called when the buffer's length is `over 1`.
    
    Parameters
    ----------
    display_state : ``DisplayState``
        The respective input.
    
    Returns
    -------
    should_try_compile : `bool`
    """
    buffer = display_state.buffer
    
    # If we are checking multi-line
    
    if len(buffer) < 3:
        return False
    
    cursor_index = display_state.cursor_index
    cursor_line_index = display_state.cursor_line_index
    
    # If there is anything after our current position return false.
    
    if (
        not _check_is_buffer_line_empty_at(buffer, cursor_line_index, cursor_index) or
        not _check_is_buffer_line_empty_after(buffer, cursor_line_index, cursor_index) or
        not _check_is_buffer_empty_after(buffer, cursor_line_index)
    ):
        return False
    
    # If there is no code before the current position return false.
    
    if (
        _check_is_buffer_line_empty_before(buffer, cursor_line_index, cursor_index) and
        _check_is_buffer_empty_before(buffer, cursor_line_index)
    ):
        return False
    
    # We should only compile when we have 1 free line above us and our current line is empty too.
    if (
        _check_is_buffer_empty_after(buffer, cursor_line_index) and
        _check_is_buffer_empty_at(buffer, cursor_line_index) and
        _check_is_buffer_empty_at(buffer, cursor_line_index - 1)
    ):
        return True
    
    return False


def _check_should_try_compile(display_state):
    """
    Tries whether based on the current input, we should try to compile the input.
    
    Parameters
    ----------
    display_state : ``DisplayState``
        The respective input.
    
    Returns
    -------
    should_try_compile : `bool`
    """
    buffer_length = len(display_state.buffer)
    
    if buffer_length == 0:
        # Should not happen
        return False
    
    if buffer_length == 1:
        return _check_should_try_compile_one_line(display_state)
    
    return _check_should_try_compile_multi_line(display_state)


class DisplayState:
    """
    A current display state of ``EditorAdvanced``.
    
    Attributes
    ----------
    buffer : `list` of `str`
        Line buffer.
    content_width : `int`
        The screen's with.
    cursor_index : `int`
        The cursors index on the current line.
    cursor_line_index : `int`
        The cursor's line's index in the buffer.
    """
    __slots__ = ('buffer', 'content_width', 'cursor_index', 'cursor_line_index')
    
    def __new__(cls, buffer):
        """
        Creates a new display state.
        
        Parameters
        ----------
        buffer : `None`, `list` of `str`
            Line buffer.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        """
        buffer = _validate_buffer(buffer)
        if not buffer:
            buffer.append('')
        
        self = object.__new__(cls)
        self.buffer = buffer
        self.cursor_index = len(buffer[-1])
        self.cursor_line_index = len(buffer) - 1
        self.content_width = -1
        return self
    
    
    def __repr__(self):
        """
        Returns the representation of the display state.
        """
        repr_parts = ['<', self.__class__.__name__]
        
        repr_parts.append(' cursor_index=')
        repr_parts.append(repr(self.cursor_index))
        
        repr_parts.append(', cursor_line_index=')
        repr_parts.append(repr(self.cursor_line_index))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def copy(self):
        """
        Copies the display state.
        
        Returns
        -------
        new : ``DisplayState``
        """
        new = object.__new__(type(self))
        new.buffer = self.buffer.copy()
        new.cursor_index = self.cursor_index
        new.cursor_line_index = self.cursor_line_index
        new.content_width = -1
        return new
    
    
    def get_cursor_till_end_display_line_count(self, new_content_width, prefix_length):
        """
        Counts how much lines are from the display position till the end of the display.
        
        Parameters
        ----------
        new_content_width : `int`
            The new column width to use.
        prefix_length : `int`
            Prefix length used for calculations when column width is changed.
        
        Returns
        -------
        count : `int`
        """
        buffer = self.buffer
        cursor_index = self.cursor_index
        cursor_line_index = self.cursor_line_index
        content_width = self.content_width
        
        line = buffer[cursor_line_index]
        line_length = len(line)
        
        line_line_count = get_line_line_count(line_length, content_width, new_content_width, prefix_length)
        line_cursor_index = get_line_line_count(cursor_index, content_width, new_content_width, prefix_length)
        count = line_line_count - line_cursor_index
        
        index = cursor_line_index + 1
        limit = len(buffer)
        if index < limit:
            while True:
                count += get_line_line_count(len(buffer[index]), content_width, new_content_width, prefix_length)
                
                index += 1
                if index == limit:
                    break
                
                continue
        
        return count
    
    
    def get_start_till_end_display_line_count(self, new_content_width, prefix_length):
        """
        Counts how much lines are displayed.
        
        Parameters
        ----------
        new_content_width : `int`
            The new column width to use.
        prefix_length : `int`
            Prefix length used for calculations when column width is changed.
        
        Returns
        -------
        count : `int`
        """
        buffer = self.buffer
        count = 0
        content_width = self.content_width
        
        for line in buffer:
            count += get_line_line_count(len(line), content_width, new_content_width, prefix_length)
        
        return count
    
    
    def jump_to_end(self, editor):
        """
        Jumps to end of the displayed content.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor to use.
        """
        if (self.content_width == -1):
            # self was never rendered
            return
        
        self._jump_to_end(editor, get_new_content_width(self, editor))
    
    
    def _jump_to_end(self, editor, new_content_width):
        """
        Jumps to end of the displayed content.
        
        Called by ``.jump_to_end`` after checking pre-requirements.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor
        new_content_width : `int`
            The new column width to use.
        """
        output_stream = editor.output_stream
        
        for _ in range(self.get_cursor_till_end_display_line_count(new_content_width, editor.prefix_length)):
            write_to_io(output_stream, COMMAND_NEXT_LINE)
    
    
    def clear(self, editor):
        """
        Clears self from the editor.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor to use.
        """
        if (self.content_width == -1):
            # self was never rendered
            return
        
        new_content_width = get_new_content_width(self, editor)
        
        self._jump_to_end(editor, new_content_width)
        self._clear_from_end(editor, new_content_width)
    
    
    def _clear_from_end(self, editor, new_content_width):
        """
        Clears self from the editor. Should be called after ``._jump_to_end``.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor to use.
        new_content_width : `int`
            The new column width to use.
        """
        output_stream = editor.output_stream
        
        write_to_io(output_stream, COMMAND_START_LINE)
        write_to_io(output_stream, COMMAND_CLEAR_LINE)
        
        for _ in range(self.get_start_till_end_display_line_count(new_content_width, editor.prefix_length) - 1):
            write_to_io(output_stream, COMMAND_PREVIOUS_LINE)
            write_to_io(output_stream, COMMAND_START_LINE)
            write_to_io(output_stream, COMMAND_CLEAR_LINE)
    
    
    def write_cursor(self, editor):
        """
        Jumps the cursor to it's location.
        
        The output must be written out before.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor to use.
        """
        # Jump back to cursor line
        output_stream = editor.output_stream
        
        for _ in range(self.get_cursor_till_end_display_line_count(-1, editor.prefix_length)):
            write_to_io(output_stream, COMMAND_PREVIOUS_LINE)
        
        write_to_io(output_stream, COMMAND_START_LINE)
        
        cursor_index = self.cursor_index
        if cursor_index == 0:
            line_cursor_index = -1
        else:
            line_cursor_index = ((cursor_index - 1) % self.content_width)
        
        line_cursor_index += editor.prefix_length
        
        write_to_io(output_stream, create_command_move_cursor(line_cursor_index))
    
    
    def write(self, editor):
        """
        Writes out the buffer.
        
        Parameters
        ----------
        editor : ``EditorAdvanced``
            The editor to use.
        """
        buffer = self.buffer
        output_stream = editor.output_stream
        
        prefix_initial = editor.prefix_initial
        prefix_continuous = editor.prefix_continuous
        prefix_length = editor.prefix_length
        
        content_width = get_terminal_size().columns - prefix_length - len(CONTINUOUS_LINE_POSTFIX)
        
        if content_width < 1:
            return
        
        self.content_width = content_width
        
        if len(buffer) == 1 and not buffer[0]:
            write_to_io(output_stream, COMMAND_START_LINE)
            write_to_io(output_stream, COMMAND_CLEAR_LINE)
            write_to_io(output_stream, COMMAND_FORMAT_RESET)
            write_to_io(output_stream, prefix_initial)
            return
        
        line_index = 0
        line_count = len(buffer)
        is_new_line = True
        leftover_line_length = content_width
        
        for part in iter_highlighted_buffer_parts(buffer, DEFAULT_ANSI_HIGHLIGHTER):
            
            if part.endswith('\n'):
                is_line_break = True
                part = part[:-2]
            else:
                is_line_break = False
            
            if is_new_line:
                leftover_line_length = content_width
                
                write_to_io(output_stream, COMMAND_START_LINE)
                write_to_io(output_stream, COMMAND_CLEAR_LINE)
                write_to_io(output_stream, COMMAND_FORMAT_RESET)
                
                is_new_line = False
                
                if line_index == 0:
                    prefix = prefix_initial
                else:
                    prefix = prefix_continuous
                
                write_to_io(output_stream, prefix)
            
            if part:
                if is_command(part):
                    write_to_io(output_stream, part)
                
                else:
                    while True:
                        part_length = len(part)
                        leftover_line_length -= part_length
                        if leftover_line_length >= 0:
                            write_to_io(output_stream, part)
                            break
                        
                        write_to_io(output_stream, part[:leftover_line_length])
                        part = part[leftover_line_length:]
                        
                        write_to_io(output_stream, CONTINUOUS_LINE_POSTFIX)
                        write_to_io(output_stream, COMMAND_NEXT_LINE)
                        write_to_io(output_stream, COMMAND_START_LINE)
                        write_to_io(output_stream, EMPTY_LINE_PREFIX_CHARACTER * prefix_length)
                        leftover_line_length = content_width
                        continue
            
            if is_line_break:
                # At last line skip line break
                line_index += 1
                if line_index == line_count:
                    break
                
                is_new_line = True
                write_to_io(output_stream, COMMAND_NEXT_LINE)
                write_to_io(output_stream, COMMAND_START_LINE)
                write_to_io(output_stream, prefix_continuous)
                continue
            
            continue


def _get_input_content_length(content):
    """
    Gets the input content's length.
    
    Parameter
    ---------
    content : `str`
        Input content.
    
    Returns
    -------
    length : `int`
    """
    length = len(content)
    if length:
        length -= (content.count(CHARACTER_CHAINED_OPERATION) << 1)
        
        if length < 1:
            length = 1
    
    return length


class InputIterator:
    """
    Helper class for processing a bigger chunk of input data at once.
    
    Attributes
    ----------
    iterator : `None, `str_iterator`
        Content iterator.
    length : `int`
        The estimated length of the input.
    """
    __slots__ = ('iterator', 'length')
    
    def __new__(cls, content):
        """
        Creates a new input iterator.
        
        Parameters
        ----------
        content : `str`
            The content to iterate over.
        """
        length = _get_input_content_length(content)
        if length:
            trimmed_content = trim_console_prefix(content)
            if (trimmed_content is not None):
                content = trimmed_content
                length = _get_input_content_length(content)
        
        if length:
            iterator = iter(content)
        else:
            iterator = None
        
        self = object.__new__(cls)
        self.iterator = iterator
        self.length = length
        return self
    
    
    def __iter__(self):
        """Returns self."""
        return self
    
    
    def __next__(self):
        """Gets the next element of the input iterator."""
        iterator = self.iterator
        if iterator is not None:
            next_ = next(iterator, None)
            if next_ is not None:
                return next_
            
            self.iterator = None
        
        raise StopIteration()
    
    
    def get_next(self):
        """Manually reads the next element."""
        iterator = self.iterator
        if iterator is not None:
            next_ = next(iterator, None)
            if next_ is not None:
                return next_
            
            self.iterator = None
        
        return None


def write_to_io(io, content):
    """
    Writes to the given `io`
    
    Parameters
    ----------
    io : `file-like`
        The io to write to.
    content : `str`
        The content to write.
    
    Raises
    ------
    RuntimeError
        - If the `io` did not became writable within timeout.
    """
    file_descriptor = io.fileno()
    if not get_blocking(file_descriptor):
        poller = Poller()
        poller.register(file_descriptor, EVENT_POLL_WRITE)
        events = poller.poll(STDOUT_WRITE_TIMEOUT)
        if not events:
            raise RuntimeError(
                f'The io did not became writable within timeout ({STDOUT_WRITE_TIMEOUT}).'
            )
        
    io.write(content)



def try_decode(data):
    """
    Tries to decode the given bytes data. On decode error changes decode error handling for that specific part.
    
    Parameters
    ----------
    data : `bytes`
        The data to decode.
    
    Returns
    -------
    content : `str`
        The decoded content.
    data_continuous : `None`, `bytes`
        Undecodable data at the end.
    """
    content_chunk_parts = None
    data_continuous = None
    content = ''
    
    while True:
        try:
            content = data.decode()
        except UnicodeDecodeError as err:
            
            end = err.end
            start = err.start
            length = len(data)
            
            if end == length:
                if start > 0:
                    content = data[:start].decode()
                    
                    if (content_chunk_parts is not None):
                        content_chunk_parts.append(content)
                
                data_continuous = data[start:]
                break
            
            if content_chunk_parts is None:
                content_chunk_parts = []
            
            if start > 0:
                content_chunk_parts.append(data[:start].decode())
            
            content_chunk_parts.append(data[start:end].decode(errors = 'backslashreplace'))
            data = data[end:]
            continue
        
        else:
            if (content_chunk_parts is not None):
                content_chunk_parts.append(content)
            break
    
    
    if content_chunk_parts is None:
        content = content
    
    else:
        content = ''.join(content_chunk_parts)
    
    return content, data_continuous


class EditorAdvanced(EditorBase):
    """
    A simple repl command editor.
    
    Attributes
    ----------
    alive : `str`
        Whether the input loop is alive.
    async_output_content_continuous : `None`, `str`
        Async content to write. Set if the last async content chunk did not end with linebreak.
    async_output_data_continuous : `None`, `bytes`
        Async content to write. Set if the end of content is not decodable.
    async_output_written : `bool`
        Whether async output was already written.
    compiled_code : `None`, ``CodeType``
        The compiled inputted code.
    display_state : ``DisplayState``
        The currently displayed state.
    file_name : `str`
        File name of the code produced by the editor.
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    history : ``History``
        History used for caching inputs.
    input_stream : `file-like`
        Input stream to read.
    input_stream_blocking_original : `bool`
        The original value of input stream's blockedness.
    input_stream_settings_original : `list` (`int`, `int`, `int`, `int`, `int`, `int`, `list` of `bytes`)
        The original settings og the input stream.
    modified : `bool`
        Whether the input is modified.
    output_proxy_read_socket : `Socket`
        Read pair socket of ``.output_proxy_write_socket``.
    output_proxy_write_socket : `Socket`
        Socket proxying stdout and stderr.
    output_stream : `file-like`
        Output stream to write.
    prefix_continuous : `str`
        Non-first line's prefix.
    prefix_initial : `str`
        First line's prefix.
    prefix_length : `int`
        As how long should the prefix's length be interpreted
    selector : ``DefaultSelector``
        Selector used to poll from `stdin`, `stdout` and `stderr`.
    """
    __slots__ = (
        'alive', 'async_output_content_continuous', 'async_output_data_continuous', 'async_output_written',
        'display_state', 'file_name', 'highlighter', 'history', 'input_stream', 'input_stream_blocking_original',
        'input_stream_settings_original', 'modified', 'output_proxy_read_socket', 'output_proxy_write_socket',
        'output_stream', 'selector'
    )
    
    @copy_docs(EditorBase.__new__)
    def __new__(cls, buffer, file_name, prefix_initial, prefix_continuous, prefix_length, highlighter, history):
        
        display_state = DisplayState(buffer)
        
        input_stream = sys.stdin
        input_stream_file_descriptor = input_stream.fileno()
        input_stream_blocking_original = get_blocking(input_stream_file_descriptor)
        set_blocking(input_stream_file_descriptor, False)
        input_stream_settings_original = termios.tcgetattr(input_stream)
        
        output_proxy_read_socket, output_proxy_write_socket = create_socket_pair()
        set_blocking(output_proxy_read_socket.fileno(), False)
        
        
        self = EditorBase.__new__(
            cls, buffer, file_name, prefix_initial, prefix_continuous, prefix_length, highlighter, history
        )
        
        self.alive = False
        self.async_output_content_continuous = None
        self.async_output_data_continuous = None
        self.async_output_written = False
        self.display_state = display_state
        self.history = history
        self.input_stream = input_stream
        self.input_stream_blocking_original = input_stream_blocking_original
        self.input_stream_settings_original = input_stream_settings_original
        self.modified = False
        self.output_proxy_read_socket = output_proxy_read_socket
        self.output_proxy_write_socket = output_proxy_write_socket
        self.output_stream = sys.stdout
        self.selector = DefaultSelector()
        
        return self
    
    
    @copy_docs(EditorBase.__call__)
    def __call__(self):
        new_stdout = open(self.output_proxy_write_socket.fileno(), 'w')
        old_stderr = sys.stderr
        sys.stdout = new_stdout
        sys.stderr = new_stdout
        
        tty.setraw(self.input_stream)
        self.selector.register(self.input_stream.fileno(), EVENT_READ)
        self.selector.register(self.output_proxy_read_socket.fileno(), EVENT_READ)
        self.output_stream.flush()
        
        try:
            self.alive = True
            self.initialise_display()
            
            while True:
                if not self.alive:
                    break
                
                new_display_state = self.poll_and_process_input()
                if (new_display_state is not None):
                    self.update_display(new_display_state)
        
        finally:
            self.alive = False
            self._maybe_display_continuous_content()
            self.display_state.jump_to_end(self)
            write_to_io(self.output_stream, '\n')
            write_to_io(self.output_stream, COMMAND_START_LINE)
            write_to_io(self.output_stream, COMMAND_FORMAT_RESET)
            self.output_stream.flush()
            
            termios.tcsetattr(self.input_stream, termios.TCSADRAIN, self.input_stream_settings_original)
            set_blocking(self.input_stream.fileno(), self.input_stream_blocking_original)
            
            sys.stdout = self.output_stream
            sys.stderr = old_stderr
            
            try:
                self.output_proxy_read_socket.close()
            except OSError as err:
                if err.errno != 9:
                    raise
            finally:
                self.output_proxy_read_socket = None
            
            try:
                self.output_proxy_write_socket.close()
            except OSError as err:
                if err.errno != 9:
                    raise
            finally:
                self.output_proxy_write_socket = None
            
            self.selector.close()
        
        return self.compiled_code
    
    
    @copy_docs(EditorBase.get_buffer)
    def get_buffer(self):
        return self.display_state.buffer
    
    
    @classmethod
    @copy_docs(EditorBase.has_history_support)
    def has_history_support(cls):
        return True
    
    
    def execute_enter(self, old_display_state, should_auto_format):
        """
        Executes an enter key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        should_auto_format : `bool`
            Whether auto formatting should be applied.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        
        Raises
        ------
        SyntaxError
        """
        if should_auto_format:
            new_display_state = self.checkout_indexed_input(old_display_state)
            if (new_display_state is not None):
                return new_display_state
            
            if self.check_exit_conditions(old_display_state):
                return None
        
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        line = buffer[cursor_line_index]
        current_line_new = line[:cursor_index]
        next_line = line[cursor_index:]
        
        if should_auto_format:
            new_line_starter_space_count = get_starting_space_count(line)
            # In which order should we check this?
            if line_ends_with(current_line_new, ':'):
                new_line_starter_space_count += 4
            elif line_starts_with_word_any(current_line_new, DEDENT_WORDS):
                new_line_starter_space_count -= 4
            
            if new_line_starter_space_count < 0:
                new_line_starter_space_count = 0
            
            next_line = ' ' * new_line_starter_space_count + next_line
        
        else:
            new_line_starter_space_count = 0
        
        buffer[cursor_line_index] = current_line_new
        cursor_line_index += 1
        buffer.insert(cursor_line_index, next_line)
        
        new_display_state.cursor_index = new_line_starter_space_count
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def execute_arrow_left(self, old_display_state):
        """
        Executes an arrow-left key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        if (cursor_index == 0):
            if (cursor_line_index == 0):
                return None
            
            cursor_line_index -= 1
            cursor_index = len(buffer[cursor_line_index])
        
        else:
            cursor_index -= 1
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        return new_display_state
    
    
    def execute_arrow_right(self, old_display_state):
        """
        Executes an arrow-right key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        line_length = len(buffer[cursor_line_index])
        if cursor_index == line_length:
            if cursor_line_index == len(buffer) - 1:
                return None
            
            cursor_line_index += 1
            cursor_index = 0
        else:
            cursor_index += 1
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        return new_display_state
    
    
    def execute_arrow_up(self, old_display_state, should_auto_format):
        """
        Executes an arrow-up key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        should_auto_format : `bool`
            Whether the content should be auto formatted.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        if should_auto_format:
            new_display_state = self.try_rewind_in_history()
            if (new_display_state is not None):
                return new_display_state
        
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        if cursor_line_index == 0:
            if (cursor_index == 0):
                return None
            
            cursor_index = 0
        
        else:
            cursor_line_index -= 1
            
            line_length = len(buffer[cursor_line_index])
            if line_length < cursor_index:
                cursor_index = line_length
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        return new_display_state
    
    
    def execute_arrow_down(self, old_display_state, should_auto_format):
        """
        Executes an arrow-down key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        should_auto_format : `bool`
            Whether the content should be auto formatted.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        if should_auto_format:
            new_display_state = self.try_forward_in_history()
            if (new_display_state is not None):
                return new_display_state
        
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        if cursor_line_index == len(buffer) - 1:
            line_length = len(buffer[cursor_line_index])
            if cursor_index == line_length:
                return None
            
            cursor_index = line_length
        
        else:
            cursor_line_index += 1
            
            line_length = len(buffer[cursor_line_index])
            if line_length < cursor_index:
                cursor_index = line_length
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        return new_display_state
    
    
    def execute_back_tab(self, old_display_state):
        """
        Executes a back-tab key press (shift + tab).
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        line = buffer[cursor_line_index]
        
        back_space_count = get_starting_space_count(line)
        if back_space_count == 0:
            return None
        
        remove_space_count = 4 - (-back_space_count & 3)
        cursor_index -= remove_space_count
        if (cursor_index < 0):
            cursor_index = 0
        line = line[remove_space_count:]
        buffer[cursor_line_index] = line
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def execute_tab(self, old_display_state, should_auto_format):
        """
        Executes a tab key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        should_auto_format : `bool`
            Whether auto formatting should be applied.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        line = buffer[cursor_line_index]
        
        if should_auto_format:
            add_spaces_count =  4 - (cursor_index & 3)
            line_length = len(line)
            while add_spaces_count:
                if cursor_index >= line_length:
                    break
                
                if line[cursor_index] != ' ':
                    break
                
                cursor_index += 1
                add_spaces_count -= 1
        else:
            add_spaces_count = 4
        
        if add_spaces_count:
            buffer[cursor_line_index] = f'{line[:cursor_index]}{" " * add_spaces_count}{line[cursor_index:]}'
            cursor_index += add_spaces_count
        
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def execute_delete_left(self, old_display_state):
        """
        Executes a delete-left key press (backspace).
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        if cursor_index == 0:
            if cursor_line_index == 0:
                return None
                
            line = buffer.pop(cursor_line_index)
            cursor_line_index -= 1
            previous_line = buffer[cursor_line_index]
            buffer[cursor_line_index] = previous_line + line
            cursor_index = len(previous_line)
        
        else:
            line = buffer[cursor_line_index]
            buffer[cursor_line_index] = f'{line[:cursor_index - 1]}{line[cursor_index:]}'
            cursor_index -= 1
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def execute_delete_right(self, old_display_state):
        """
        Executes a delete-right key press (delete).
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        line = buffer[cursor_line_index]
        line_length = len(line)
        if cursor_index == line_length:
            if cursor_line_index == len(buffer) - 1:
                return None
                
            next_line = buffer.pop(cursor_line_index + 1)
            line = line + next_line
            buffer[cursor_line_index] = line
                
        else:
            line = f'{line[:cursor_index]}{line[cursor_index + 1:]}'
            buffer[cursor_line_index] = line
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def execute_print(self, old_display_state, character_string):
        """
        Executes a printable character key press.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        character_string : `str`
            The character to print out.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        new_display_state = old_display_state.copy()
        buffer = new_display_state.buffer
        cursor_index = new_display_state.cursor_index
        cursor_line_index = new_display_state.cursor_line_index
        
        line = buffer[cursor_line_index]
        buffer[cursor_line_index] = f'{line[:cursor_index]}{character_string}{line[cursor_index:]}'
        cursor_index += 1
        
        new_display_state.cursor_index = cursor_index
        new_display_state.cursor_line_index = cursor_line_index
        
        self.modified = True
        
        return new_display_state
    
    
    def poll(self):
        """
        Polls a character from any input stream.
        
        Returns
        -------
        content : `str`
            The inputted string into `sys.stdin`.
        """
        content = None
        
        while True:
            # We force flush every second.
            sys.stdout.flush()
            
            event_list = self.selector.select(1)
            if not event_list:
                continue
                
            for key, mask in event_list:
                file_descriptor = key.fileobj
                
                if (file_descriptor == self.output_proxy_read_socket.fileno()) and (mask & EVENT_READ):
                    try:
                        data = self.output_proxy_read_socket.recv(1024)
                    except (BlockingIOError, InterruptedError):
                        pass
                    else:
                        if data:
                            self._process_async_content(data)
                        
                        data = None
                    
                    continue
                
                if (file_descriptor == self.input_stream.fileno()) and (mask & EVENT_READ):
                    try:
                        content = self.input_stream.read()
                    except (BlockingIOError, InterruptedError):
                        pass
                    
                    continue
            
            
            if (content is not None):
                if content:
                    return content
                
                content = None
    
    
    def poll_and_process_input(self):
        """
        Inputs one action and returns whether any actions took place.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        
        Raises
        ------
        KeyboardInterrupt
        SystemExit
        SyntaxError
        """
        content = self.poll()
        input_iterator = InputIterator(content)
        should_auto_format = input_iterator.length <= 1
        
        old_display_state = self.display_state
        new_display_state = old_display_state
        
        for character_string in input_iterator:
            received_display_state = self.process_input(
                new_display_state, input_iterator, character_string, should_auto_format
            )
            if (received_display_state is not None):
                new_display_state = received_display_state
        
        if (new_display_state is old_display_state):
            new_display_state = None
        
        return new_display_state
    
    
    def process_input(self, old_display_state, input_iterator, character_string, should_auto_format):
        """
        Processes one input.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        input_iterator : ``InputIterator``
            The input iterator to pull additional characters if required.
        character_string : `str`
            The input string.
        should_auto_format : `bool`
            Whether the content should be auto formatted.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        character_int = ord(character_string)
        
        if character_int == KEY_KEYBOARD_INTERRUPT:
            raise KeyboardInterrupt()
        
        if character_int == KEY_DESTROY:
            raise SystemExit()
        
        if character_int in KEY_NEW_LINE_ALL:
            return self.execute_enter(old_display_state, should_auto_format)
        
        if character_int == KEY_ARROW_ALL_INITIAL:
            next_1_string = input_iterator.get_next()
            next_2_string = input_iterator.get_next()
            
            if (next_1_string is None) or (next_2_string is None):
                # Escape was pressed.
                return None
            
            next_1_int = ord(next_1_string)
            next_2_int = ord(next_2_string)
            
            if next_1_int != KEY_ARROW_ALL:
                return None
            
            if next_2_int == KEY_ARROW_LEFT:
                return self.execute_arrow_left(old_display_state)
            
            if next_2_int == KEY_ARROW_RIGHT:
                return self.execute_arrow_right(old_display_state)
            
            if next_2_int == KEY_ARROW_UP:
                return self.execute_arrow_up(old_display_state, should_auto_format)
            
            if next_2_int == KEY_ARROW_DOWN:
                return self.execute_arrow_down(old_display_state, should_auto_format)
            
            if next_2_int == KEY_ARROW_BACK_TAB:
                return self.execute_back_tab(old_display_state)
            
            return None
        
        if character_int == KEY_TAB:
            return self.execute_tab(old_display_state, should_auto_format)
        
        if character_int == KEY_DELETE_LEFT:
            return self.execute_delete_left(old_display_state)
        
        if character_int == KEY_DELETE_RIGHT:
            return self.execute_delete_right(old_display_state)
        
        if character_string.isprintable():
            return self.execute_print(old_display_state, character_string)
        
        return None
    
    
    def initialise_display(self):
        """
        Initialises the display.
        
        Called after the editor was started.
        """
        self.display_state.write(self)
        
        self.output_stream.flush()
    
    
    def update_display(self, new_display_state):
        """
        Updates the display.
        
        This method is called after an action took place.
        
        Parameters
        ----------
        new_display_state : ``DisplayState``
            The new display state to render.
        """
        old_display_state = self.display_state
        self.display_state = new_display_state
        
        old_display_state.clear(self)
        new_display_state.write(self)
        new_display_state.write_cursor(self)
        
        self.output_stream.flush()
    
    
    def _process_async_content(self, data):
        """
        Processes the given async content and decides whether it should be flushed before the editor's input.
        
        Parameters
        ----------
        content : `bytes`
            Raw content to write.
        """
        async_output_data_continuous = self.async_output_data_continuous
        if (async_output_data_continuous is not None):
            data = async_output_data_continuous + data
            self.async_output_data_continuous = None
        
        content, self.async_output_data_continuous = try_decode(data)
        
        async_output_content_continuous = self.async_output_content_continuous
        if (async_output_content_continuous is not None):
            content = async_output_content_continuous + content
            self.async_output_content_continuous = None
        
        if not content.endswith('\n'):
            line_break_index = content.rfind('\n')
            if line_break_index == -1:
                self.async_output_content_continuous = content
                return
            
            line_break_index += 1
            self.async_output_content_continuous = content[line_break_index:]
            content = content[:line_break_index]
        
        if content:
            self._display_async_content(content)
    
    
    def _maybe_display_continuous_content(self):
        """
        If there is async content to display, displays it.
        """
        content = None
        
        async_output_data_continuous = self.async_output_data_continuous
        if (async_output_data_continuous is not None):
            content = async_output_data_continuous.decode(errors = 'backslashreplace')
            self.async_output_data_continuous = None
        
        async_output_content_continuous = self.async_output_content_continuous
        if (async_output_content_continuous is not None):
            if content is None:
                content = async_output_content_continuous
            else:
                content = async_output_content_continuous + content
        
        if (content is not None):
            self._display_async_content(content)
    
    
    def _display_async_content(self, content):
        """
        Writes the given content before the editor's input.
        
        Parameters
        ----------
        content : `str`
            The content to write.
        """
        self.display_state.clear(self)
        
        async_output_written = self.async_output_written
        
        if async_output_written:
            write_to_io(self.output_stream, COMMAND_PREVIOUS_LINE)
        
        termios.tcsetattr(self.input_stream, termios.TCSADRAIN, self.input_stream_settings_original)
        write_to_io(self.output_stream, content)
        tty.setraw(self.input_stream)
        
        write_to_io(self.output_stream, COMMAND_NEXT_LINE)
        write_to_io(self.output_stream, COMMAND_START_LINE)
        
        if not async_output_written:
            self.async_output_written = True
        
        self.display_state.write(self)
        self.display_state.write_cursor(self)
        
        self.output_stream.flush()
    
    
    def check_exit_conditions(self, old_display_state):
        """
        Checks whether any exit conditions are met.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Raises
        ------
        SyntaxError
        """
        if _check_should_try_compile(old_display_state):
            compiled_code = maybe_compile(old_display_state.buffer, self.file_name)
            if (compiled_code is not None):
                self.compiled_code = compiled_code
                self.alive = False
                return True
        
        return False
    
    
    def should_move_in_history(self):
        """
        Returns whether history moving can be executed.
        """
        display_state = self.display_state
        if display_state.cursor_line_index != 0:
            return False
        
        display_state = self.display_state
        if display_state.cursor_index != 0:
            return False
        
        return self.can_move_in_history()
        
    
    def can_move_in_history(self):
        """
        Returns whether history moving can be executed.
        
        Returns
        -------
        can_move_in_history : `bool`
        """
        if not self.modified:
            return True
        
        if self.is_empty():
            self.modified = False
            return True
        
        return False
    
    
    def try_rewind_in_history(self):
        """
        Tries to go back in history if applicable.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        if not self.should_move_in_history():
            return None
        
        buffer = self.history.get_previous()
        if buffer is None:
            buffer = ['']
        
        display_state = self.display_state.copy()
        display_state.buffer = buffer.copy()
        return display_state
    
    
    def try_forward_in_history(self):
        """
        Tries to go forward in history if applicable.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        if not self.should_move_in_history():
            return None
        
        buffer = self.history.get_next()
        if buffer is None:
            buffer = ['']
        
        display_state = self.display_state.copy()
        display_state.buffer = buffer.copy()
        return display_state
    
    
    def checkout_indexed_input(self, old_display_state):
        """
        Checks out whether an index of the history. If it is returns a new display state.
        
        Parameters
        ----------
        old_display_state : ``DisplayState``
            The old display state to work from.
        
        Returns
        -------
        new_display_state : `None`, ``DisplayState``
            The new display state.
        """
        index = -1
        
        for line in old_display_state.buffer:
            if _check_is_line_empty(line):
                continue
            
            if index != -1:
                return None
            
            matched = INDEXED_INPUT_RP.fullmatch(line)
            if matched is None:
                return None
            
            index = int(matched.group(1))
            continue
        
        if index == -1:
            return None
        
        buffer = self.history.get_at(index)
        return DisplayState(buffer)
