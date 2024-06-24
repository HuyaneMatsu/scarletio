__all__ = ()

from itertools import islice, zip_longest
from os import get_blocking, get_terminal_size, write
from select import poll as Poller, POLLOUT as EVENT_POLL_WRITE
from time import monotonic

from ....utils import DEFAULT_ANSI_HIGHLIGHTER, RichAttributeErrorBaseType, iter_highlight_code_lines

from .editor_base import _validate_buffer
from .line_render_intermediate import LineRenderIntermediate
from .terminal_control_commands import (
    COMMAND_CLEAR_LINE_FROM_CURSOR, COMMAND_CLEAR_LINE_WHOLE, COMMAND_FORMAT_RESET, COMMAND_DOWN, COMMAND_UP, COMMAND_START_LINE,
    create_command_down, create_command_left, create_command_right, create_command_up, is_command
)

EMPTY_LINE_PREFIX_CHARACTER = ' '
CONTINUOUS_LINE_POSTFIX = '\\'


def _get_line_line_count(line_length, content_width, new_content_width, prefix_length):
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
    if (content_width == -1) or (new_content_width >= content_width):
        return _get_line_line_count_same_or_increased(
            line_length,
            (new_content_width if content_width == -1 else content_width),
        )
    
    return _get_line_line_count_reduced(line_length, content_width, new_content_width, prefix_length)


def _get_line_line_count_same_or_increased(line_length, content_width):
    """
    Returns how much lines the given line is displayed as.
    
    This function handles the case when content width is not changed or is increased.
    Increase does not matter because when resizing the old linebreaks are kept, so the lines are not squashed.
    
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


def _get_line_line_count_reduced(line_length, content_width, new_content_width, prefix_length):
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
        
        full_line_count, last_line_length = divmod(line_length, content_width)
        
        # If the last line is full (so last_line_length == 0 and full_line_count > 0)
        # then that line does not have `/` at the end, so we should remove that
        # from `full_line_count` and add to `last_line_length` instead.
        if not last_line_length and full_line_count:
            full_line_count -= 1
            last_line_length = line_length
            
        if full_line_count:
            line_line_count += full_line_count * _get_line_line_count_same_or_increased(
                old_full_line_length, new_full_line_length
            )
        
        if last_line_length:
            line_line_count += 1 + ((last_line_length + prefix_length - 1) // new_full_line_length)
        
    return line_line_count


def _get_line_cursor_index(content_width, cursor_index, prefix_length):
    """
    Gets the cursor's index depending on the parameters.
    
    Parameters
    ----------
    content_width : `int`
        The content field's width.
    cursor_index : `int`
        The cursors index on the current line.
    prefix_length : `int`
        Prefix length used for calculations when column width is changed.
    
    Returns
    -------
    cursor_index : `int`
    """
    line_cursor_index = prefix_length
    if cursor_index:
        line_cursor_index += (cursor_index - 1) % content_width + 1
    
    return line_cursor_index


def _jump_vertical(write_buffer, old_index, new_index):
    """
    Jumps from the old position to the new position.
    
    Parameters
    ----------
    write_buffer : `list<str>`
        Write buffer to extend.
    old_index : `int`
        Old line index to jump to.
    new_index : `int`
        New line index to jump to.
    """
    if old_index > new_index:
        command = create_command_up(old_index - new_index)
    
    elif new_index > old_index:
        command = create_command_down(new_index - old_index)
    
    else:
        return
    
    write_buffer.append(command)


def _jump_horizontal(write_buffer, old_index, new_index):
    """
    Jumps from the old position to the new position.
    
    Parameters
    ----------
    write_buffer : `list<str>`
        Write buffer to extend.
    old_index : `int`
        Old line index to jump to.
    new_index : `int`
        New line index to jump to.
    """
    if old_index > new_index:
        command = create_command_left(old_index - new_index)
    
    elif new_index > old_index:
        command = create_command_right(new_index - old_index)
    
    else:
        return
    
    write_buffer.append(command)


def _cut_same_prefix(string_0, string_1):
    """
    Cuts the prefix of the two strings till they are same.
    
    Parameters
    ----------
    string_0 : `str`
        String to cut.
    string_1 : `str`
        String to cut.
    
    Returns
    -------
    cut_count : `int`
    cut_string_0 : `str`
    cut_string_1 : `str`
    """
    index = 0
    length_string_0 = len(string_0)
    length_string_1 = len(string_1)
    
    while index < length_string_0 and index < length_string_1:
        if string_0[index] != string_1[index]:
            break
        
        index += 1
        continue
    
    return index, string_0[index:], string_1[index:]


def get_new_content_width(prefix_length):
    """
    Gets the new column with and whether it changes.
    
    Parameters
    ----------
    prefix_length : `int`
        Prefix length used for calculations of content width.
    
    Returns
    -------
    new_content_width : `int`
    """
    return get_terminal_size().columns - prefix_length - len(CONTINUOUS_LINE_POSTFIX)


def _add_linebreaks_between(lines):
    """
    Adds linebreaks between the given lines and returns a new list.
    
    Parameters
    ----------
    lines : `list<str>`
        Lines to add spaces between.
    
    Returns
    -------
    new_lines : `list<str>`
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
    buffer = _add_linebreaks_between(buffer)
    
    if highlighter is None:
        yield from buffer
    
    else:
        yield from iter_highlight_code_lines(buffer, highlighter)


class DisplayState(RichAttributeErrorBaseType):
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
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' cursor_index = ')
        repr_parts.append(repr(self.cursor_index))
        
        repr_parts.append(', cursor_line_index = ')
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
    
    
    def get_cursor_from_start_display_line_count(self, prefix_length):
        """
        Counts how much lines are from display position till the start of the display.
        
        Parameters
        ----------
        prefix_length : `int`
            Prefix length used for calculations when column width is changed.
        
        Returns
        -------
        count : `int`
        """
        content_width = self.content_width
        if (content_width == -1):
            # was never rendered
            return 0
        
        buffer = self.buffer
        cursor_index = self.cursor_index
        cursor_line_index = self.cursor_line_index
        
        count = _get_line_line_count(cursor_index, -1, content_width, prefix_length) - 1
        
        index = cursor_line_index - 1
        while index >= 0:
            count += _get_line_line_count(len(buffer[index]), -1, content_width, prefix_length)
            index -= 1
        
        return count
    
    
    def get_cursor_till_end_display_line_count(self, prefix_length, new_content_width):
        """
        Counts how much lines are from the display position till the end of the display.
        
        Parameters
        ----------
        prefix_length : `int`
            Prefix length used for calculations when column width is changed.
        new_content_width : `int`
            The new column width to use.
        
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
        
        line_line_count = _get_line_line_count(line_length, content_width, new_content_width, prefix_length)
        line_cursor_index = _get_line_line_count(cursor_index, content_width, new_content_width, prefix_length)
        count = line_line_count - line_cursor_index
        
        index = cursor_line_index + 1
        limit = len(buffer)
        while index < limit:
            count += _get_line_line_count(len(buffer[index]), content_width, new_content_width, prefix_length)
            index += 1
        
        return count
    
    
    def get_start_till_end_display_line_count(self, prefix_length, new_content_width):
        """
        Counts how much lines are displayed.
        
        Parameters
        ----------
        prefix_length : `int`
            Prefix length used for calculations when column width is changed.
        new_content_width : `int`
            The new column width to use.
        
        Returns
        -------
        count : `int`
        """
        buffer = self.buffer
        count = 0
        content_width = self.content_width
        
        for line in buffer:
            count += _get_line_line_count(len(line), content_width, new_content_width, prefix_length)
        
        return count
    
    
    def jump_to_end(self, write_buffer, prefix_length, new_content_width):
        """
        Jumps to end of the displayed content.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        new_content_width : `int`
            The new column width to use.
        """
        if (self.content_width == -1):
            # self was never rendered
            return
        
        self._jump_to_end(write_buffer, prefix_length, new_content_width)
    
    
    def _jump_to_end(self, write_buffer, prefix_length, new_content_width):
        """
        Jumps to end of the displayed content.
        
        Called by ``.jump_to_end`` after checking pre-requirements.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        new_content_width : `int`
            The new column width to use.
        """
        _jump_vertical(write_buffer, 0, self.get_cursor_till_end_display_line_count(prefix_length, new_content_width))
    
    
    def clear(self, write_buffer, prefix_length, new_content_width):
        """
        Clears self from the editor.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        new_content_width : `int`
            The new column width to use.
        """
        if (self.content_width == -1):
            # self was never rendered
            return
        
        self._jump_to_end(write_buffer, prefix_length, new_content_width)
        self._clear_from_end(write_buffer, prefix_length, new_content_width)
    
    
    def _clear_from_end(self, write_buffer, prefix_length, new_content_width):
        """
        Clears self from the editor. Should be called after ``._jump_to_end``.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        new_content_width : `int`
            The new column width to use.
        """
        count = self.get_start_till_end_display_line_count(prefix_length, new_content_width)
        
        write_buffer.append(COMMAND_START_LINE)
        
        while True:
            write_buffer.append(COMMAND_CLEAR_LINE_WHOLE)
            
            count -= 1
            if count <= 0:
                break
            
            write_buffer.append(COMMAND_UP)
            continue
    
    
    def write_cursor(self, write_buffer, prefix_length):
        """
        Jumps the cursor to it's location.
        
        The output must be written out before.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        """
        # Jump back to cursor line
        write_buffer.append(
            create_command_up(self.get_cursor_till_end_display_line_count(prefix_length, self.content_width)),
        )
        write_buffer.append(COMMAND_START_LINE)
        write_buffer.append(
            create_command_right(_get_line_cursor_index(self.content_width, self.cursor_index, prefix_length)),
        )
    
    
    def write(self, write_buffer, prefix_length, prefix_initial, prefix_continuous, content_width):
        """
        Writes out the buffer.
        
        Parameters
        ----------
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        prefix_initial : `str`
            Prefix to use for the first line.
        prefix_continuous : `str`
            Prefix to use for additional lines.
        content_width : `int`
            Content width to use.
        """
        lines = self.get_line_render_intermediates(prefix_length, prefix_initial, prefix_continuous, content_width)
        
        line_count = len(lines)
        if not line_count:
            return
        
        write_buffer.append(COMMAND_FORMAT_RESET)
        index = 0
        
        while True:
            line = lines[index]
            index += 1
            
            write_buffer.append(COMMAND_START_LINE)
            
            for part in line.iter_parts():
                write_buffer.append(part)        
            
            if index == line_count:
                break
            
            write_buffer.append(COMMAND_DOWN)
            continue
    
    
    def write_difference(self, other, write_buffer, prefix_length, prefix_initial, prefix_continuous):
        """
        Writes out the difference between the two buffers..
        
        Parameters
        ----------
        other : `instance<type<self>>`
            Other instance to overwrite its buffer of.
        write_buffer : `list<str>`
            Write buffer to extend.
        prefix_length : `int`
            Prefix length used to calculate line count.
        prefix_initial : `str`
            Prefix to use for the first line.
        prefix_continuous : `str`
            Prefix to use for additional lines.
        """
        other_lines = other.get_line_render_intermediates(prefix_length, prefix_initial, prefix_continuous, -1)
        if not other_lines:
            return
        
        self_lines = self.get_line_render_intermediates(
            prefix_length, prefix_initial, prefix_continuous, other.content_width
        )
        
        current_line_index = other.get_cursor_from_start_display_line_count(prefix_length)
        last_written_line = None
        
        for line_index, self_line, other_line in zip_longest(
            range(max(len(other_lines), len(self_lines))),
            self_lines,
            other_lines,
        ):
            if other_line is None:
                _jump_vertical(write_buffer, current_line_index, line_index)
                current_line_index = line_index
                
                write_buffer.append(COMMAND_START_LINE)
                
                if (last_written_line is None):
                    write_buffer.append(COMMAND_FORMAT_RESET)
                
                for part in self_line.iter_parts():
                    write_buffer.append(part)
                
                last_written_line = self_line
                continue
            
            if self_line is None:
                _jump_vertical(write_buffer, current_line_index, line_index)
                current_line_index = line_index
                
                write_buffer.append(COMMAND_CLEAR_LINE_WHOLE)
                
                continue
            
            if self_line == other_line:
                continue
            
            # if we are different only write the difference.
            _jump_vertical(write_buffer, current_line_index, line_index)
            current_line_index = line_index
            
            write_buffer.append(COMMAND_START_LINE)
            
            last_command = None
            to_clear = 0
            jump_to = 0
            write_difference = False
            command_written = False
            
            item_index = 0
            self_items = self_line.parts
            other_items = other_line.parts
            
            # Skip same parts
            for item_index in range(item_index, min(len(self_items), len(other_items))):
                self_item = self_items[item_index]
                other_item = other_items[item_index]
                
                if self_item != other_item:
                    write_difference = True
                    break
                
                length = self_item[0]
                jump_to += length
                if not length:
                    last_command = self_item[1]
                
                continue
            
            # calculate additional shift in case we stopped on something.
            if not write_difference:
                self_length = 0
                self_part = ''
            
            else:
                self_length, self_part = self_item
                other_length, other_part = other_item
                
                # If we are not writing commands, cut the same part out
                if self_length and other_length:
                    cut_count, self_part, other_part = _cut_same_prefix(self_part, other_part)
                    jump_to += cut_count
                
                # Adjust clear count.
                to_clear += other_length - self_length
            
            # if we wanna jump, jump!!!
            if jump_to > 0:
                write_buffer.append(create_command_right(jump_to))
            
            # if wanna write, write!!
            if self_part:
                if self_length:
                    if (last_command is not None):
                        write_buffer.append(last_command)
                    elif (last_written_line is None):
                        write_buffer.append(COMMAND_FORMAT_RESET)
                        
                
                write_buffer.append(self_part)
                command_written = True
            
            # Increment index by 1 to skip the current element next time.
            item_index += 1
            
            # write self parts
            if len(self_items) > item_index:
                if not command_written:
                    write_buffer.append(COMMAND_FORMAT_RESET)
                
                for self_length, self_part in islice(self_items, item_index, None):
                    to_clear -= self_length
                    write_buffer.append(self_part)
            
            # calculate how much to clear
            for other_length, other_part in islice(other_items, item_index, None):
                to_clear += other_length
            
            # fill up space if required.
            if to_clear > 0:
                write_buffer.append(COMMAND_CLEAR_LINE_FROM_CURSOR)
            
            last_written_line = self_line
            continue
        
        # write cursor
        _jump_vertical(
            write_buffer,
            current_line_index,
            self.get_cursor_from_start_display_line_count(prefix_length),
        )
        
        if last_written_line is None:
            cursor_index = _get_line_cursor_index(other.content_width, other.cursor_index, prefix_length)
        else:
            cursor_index = last_written_line.get_length()
        
        _jump_horizontal(
            write_buffer,
            cursor_index,
            _get_line_cursor_index(other.content_width, self.cursor_index, prefix_length),
        )
    
    
    def get_line_render_intermediates(self, prefix_length, prefix_initial, prefix_continuous, content_width):
        """
        Gets line rendering intermediates that contain the content to write but are not written yet.
        
        Parameters
        ----------
        prefix_length : `int`
            Prefix length used to calculate line count.
        prefix_initial : `str`
            Prefix to use for the first line.
        prefix_continuous : `str`
            Prefix to use for additional lines.
        content_width : `int`
            Content width to use.
        
        Returns
        -------
        lines : `list<LineRenderIntermediate>`
        """
        if content_width == -1:
            content_width = self.content_width
        else:
            if content_width < 1:
                return []
        
            self.content_width = content_width
        
        lines = []
        
        line_index = 0
        buffer = self.buffer
        line_count = len(buffer)
        leftover_line_length = content_width
        last_command = COMMAND_FORMAT_RESET
        
        line = LineRenderIntermediate(prefix_length, prefix_initial)
        lines.append(line)
        
        for part in iter_highlighted_buffer_parts(buffer, DEFAULT_ANSI_HIGHLIGHTER):
            # if the part ends with `\n`, remove it and remember it for later
            if part.endswith('\n'):
                is_line_break = True
                part = part[:-2]
            else:
                is_line_break = False
            
            # write line if any. If the part is a command, it will have 0 visible length, so ignore it
            # else only write as much as we can, then break line and continue. 
            if part:
                if is_command(part):
                    line.add_command(part)
                    last_command = part
                
                else:
                    while True:
                        leftover_line_length -= len(part)
                        if leftover_line_length >= 0:
                            line.add_part(part)
                            break
                        
                        line.add_part(part[:leftover_line_length])
                        line.add_part(CONTINUOUS_LINE_POSTFIX)
                        part = part[leftover_line_length:]
                        
                        # Create new line
                        line = LineRenderIntermediate(prefix_length, EMPTY_LINE_PREFIX_CHARACTER * prefix_length)
                        lines.append(line)
                        leftover_line_length = content_width
                        line.add_command(last_command)
                        continue
            
            # If we wrote a line break:
            # - quit if last
            # - jump to next line and write prefix if we have more
            if is_line_break:
                # At last line skip line break
                line_index += 1
                if line_index == line_count:
                    break
                
                
                line = LineRenderIntermediate(prefix_length, prefix_continuous)
                lines.append(line)
                leftover_line_length = content_width
                continue
            
            continue
    
        return lines
