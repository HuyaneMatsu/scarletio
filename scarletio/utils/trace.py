__all__ = ('ignore_frame', 'render_exception_into', 'render_frames_into', 'should_ignore_frame',)

import reprlib, sys, warnings
from collections import OrderedDict
from linecache import checkcache as check_file_cache, getline as _get_file_line
from os.path import sep as PATH_SEPARATOR
from types import (
    AsyncGeneratorType as CoroutineGeneratorType, CoroutineType, FrameType, FunctionType, GeneratorType, MethodType,
    TracebackType
)

from .cause_group import CauseGroup
from .docs import copy_docs
from .highlight import HIGHLIGHT_TOKEN_TYPES, iter_highlight_code_lines
from .highlight.token import Token


SlotWrapperType = object.__lt__.__class__

IGNORED_FRAME_LINES = {}


class ConsoleLineInput:
    """
    A cached value of ``ConsoleLineCache``. An console line instance represents an input value.
    
    Attributes
    ----------
    _content : `str`
        The inputted content.
    _lines : `None`, `list` of `str`
        Cached splitted content.
    file_name : `str`
        The respective input's file name.
    length : `str`
        The content's length.
    """
    __slots__ = ('_content', '_lines', 'file_name','length')
    
    def __new__(cls, file_name, content):
        """
        Creates a new console line input.
        
        Parameters
        ----------
        file_name : `str`
            The file name to reference content with.
        content : `str`
            The line's content.
        """
        self = object.__new__(cls)
        self._content = content
        self._lines = None
        self.file_name = file_name
        self.length = len(content)
        return self
    
    
    def __repr__(self):
        """Returns the console line input's representation."""
        return f'<{self.__class__.__name__} file_name={self.file_name!r}, length={self.length!r}>'
    
    
    def get_lines(self):
        """
        Gets the lines of the input.
        
        Returns
        -------
        lines : `list` of `str`
        """
        lines = self._lines
        if (lines is None):
            content = self._content
            # should not happen
            if (content is None):
                lines = []
            else:
                lines = content.splitlines()
                self._content = None
        
            self._lines = lines
        
        return lines
    
    
    def get_line(self, line_number):
        """
        Tries to get the line of the input.
        
        Parameters
        ----------
        line_number : `int`
            The line's number (1 based). 
        
        Returns
        -------
        line : `str`
        """
        if line_number < 1:
            return ''
        
        lines = self.get_lines()
        
        if line_number > len(lines):
            return ''
        
        return lines[line_number - 1] + '\n'


class ConsoleLineCache:
    """
    Line cash, which can be for console, so line lookup wont fail for their lines.
    
    Attributes
    ----------
    max_size : `int`
        The maximal size to cache.
    actual_size : `int`
        The actual stored size.
    cache : `OrderedDict` of (`str`, ``ConsoleLineInput``) items
        cache used to store inputs.
    """
    def __new__(cls, max_size = 1000000):
        """
        Creates a new console line cache instance.
        
        parameters
        ----------
        max_size : `int` = `1000_000`, Optional
            The maximal amount of input to remember.
        """
        self = object.__new__(cls)
        
        self.max_size = max_size
        self.actual_size = 0
        self.cache = OrderedDict()
        
        return self
    
    def __repr__(self):
        """Returns the console line cache's representation."""
        return f'<{self.__class__.__name__} size: {self.actual_size!r} / {self.max_size!r}>'
    
    
    def feed(self, file_name, content):
        """
        Feeds content with the given file-name.
        
        Feeding a new content with an old file name overwrites the old value, so make sure to always fee with a new
        name.
        
        Parameters
        ----------
        file_name : `str`
            The file name to feed content with.
        content : `str`
            The content to feed.
        """
        line_input = ConsoleLineInput(file_name, content)
        actual_size = self.actual_size + line_input.length
        max_size = self.max_size
        cache = self.cache
        
        if max_size > actual_size:
            to_pop = []
            
            for value in cache.values():
                actual_size -= value.length
                
                if actual_size <= max_size:
                    break
                
                to_pop.append(value)
                continue
            
            for value in to_pop:
                del cache[value.file_name]
        
        cache[file_name] = line_input
        self.actual_size = actual_size
    
    
    def get_line(self, file_name, line_number):
        """
        Gets the line of the given file for the given index.
        
        Parameters
        ----------
        file_name : `str`
            The file to get it's line of.
        line_number : `int`
            The line's number (1 based). 
        
        Returns
        -------
        line : `str`
        """
        cache = self.cache
        
        try:
            line_input = cache[file_name]
        except KeyError:
            return ''
        
        cache.move_to_end(file_name)
        return line_input.get_line(line_number)


CONSOLE_LINE_CACHE = ConsoleLineCache()


def get_file_line(file_name, line_number):
    """
    Tries to get the line of the file.
    
    Parameters
    ----------
    file_name : `str`
        The file to get it's line of.
    line_number : `int`
        The line's number (1 based). 
    
    Returns
    -------
    line : `str`
    """
    # First check file lines
    line = _get_file_line(file_name, line_number, None)
    
    # Second check console lines
    if not line:
        line = CONSOLE_LINE_CACHE.get_line(file_name, line_number)
    
    return line


def try_get_raw_exception_representation(exception):
    """
    Tries to get raw exception representation.
    
    Parameters
    ----------
    exception : ``BaseException``
        The respective exception instance.
    
    Returns
    -------
    raw_exception_representation : `str`
    """
    raw_exception_representation_parts = [
        '> repr(exception) raised, trying to get raw representation.\n'
    ]
    
    exception_name = getattr(type(exception), '__name__')
    if type(exception_name) is str:
        pass
    elif isinstance(exception_name, str):
        try:
            exception_name = str(exception_name)
        except:
            exception_name = '<Exception>'
    else:
        exception_name = '<Exception>'
    
    raw_exception_representation_parts.append(exception_name)
    raw_exception_representation_parts.append('(')
    
    try:
        args = getattr(exception, 'args', None)
    except:
        pass
    else:
        if (args is not None) and (type(args) is tuple):
            length = len(args)
            if length:
                index = 0
                while True:
                    element = args[index]
                    
                    try:
                        element_representation = repr(element)
                    except:
                        element_representation = f'<parameter_{index}>'
                    else:
                        if type(element_representation) is not str:
                            try:
                                element_representation = str(element_representation)
                            except:
                                element_representation = f'<parameter_{index}>'
                    
                    raw_exception_representation_parts.append(element_representation)
                    
                    index += 1
                    if index == length:
                        break
                    
                    raw_exception_representation_parts.append(', ')
                    continue
        
    
    raw_exception_representation_parts.append(')')
    return ''.join(raw_exception_representation_parts)


def is_syntax_error(exception):
    """
    Returns whether the given exception is a syntax error with the expected structure.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to check.
    
    Returns
    -------
    is_syntax_error : `bool`
    """
    if not isinstance(exception, SyntaxError):
        return False
    
    exception_parameters = exception.args
    if (not isinstance(exception_parameters, tuple)) or (len(exception_parameters) != 2):
        return False
    
    message, details = exception_parameters
    if (message is not None) and (not isinstance(message, str)):
        return False
    
    if (not isinstance(details, tuple)) or (len(details) not in (4, 6)):
        return False
    
    # Pulled from C 3.11
    #
    #     args = Py_BuildValue("(O(OiiNii))", errmsg, tok->filename, tok->lineno,
    #                          col_offset, errtext, tok->lineno, end_col_offset);
    #
    # file_name is annotated as `O`, so it probably can be `None` as well.
    # also: line_number == end_line_number, so we can ignore it.
    #
    # On older Python versions `line` can also be `None`. How stupid!
    
    file_name = details[0]
    line_number = details[1]
    offset = details[2]
    line = details[3]
    
    if (file_name is not None) and (not isinstance(file_name, str)):
        return False
    
    if not isinstance(line_number, int):
        return False
    
    if not isinstance(offset, int):
        return False
    
    if (line is not None) and (not isinstance(line, str)):
        return False
    
    if len(details) == 4:
        return True
    
    end_line_number = details[4]
    end_offset = details[5]
    
    if not isinstance(end_line_number, int):
        return False
    
    if not isinstance(end_offset, int):
        return False
    
    return True


def fixup_syntax_error_line_from_buffer(syntax_error, buffer):
    """
    Tries to fix up the syntax error's missing line.
    
    Should be only called if ``is_syntax_error`` returned `True` on the given exception.
    
    Parameters
    ----------
    syntax_error : ``SyntaxError``
        Respective SyntaxError
    buffer : `list` of `str`
        Buffer containing the respective lines.
    """
    message, (file_name, line_number, offset, line, *end) = syntax_error.args
    if line is not None:
        return
    
    buffer_length = len(buffer)
    # `line_number` means `line_index + 1`
    if (line_number > buffer_length) or (line_number < 1):
        return
    
    line = buffer[line_number - 1]
    syntax_error.args = (message, (file_name, line_number, offset, line, *end))


def right_strip_syntax_error_line(syntax_error):
    """
    Right strips the syntax error's line. This can be useful when comparing two syntax errors, but one has new line
    character at the end.
    
    Should be only called if ``is_syntax_error`` returned `True` on the given exception.
    
    Parameters
    ----------
    syntax_error : `SyntaxError`
        The syntax error to strip.
    """
    message, (file_name, line_number, offset, line, *end) = syntax_error.args
    if line is None:
        return
    
    line = line.rstrip()
    
    syntax_error.args = (message, (file_name, line_number, offset, line, *end))


def _render_syntax_error_representation_into(syntax_error, into, highlighter):
    """
    Renders a syntax exception's representation.
    
    Parameters
    ----------
    syntax_error : ``SyntaxError``
        The respective exception instance.
    
    into : `list` of `str`
        The list of strings to extend.
    
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    
    Returns
    -------
    into  : `list` of `str`
    """
    message, details = syntax_error.args
    
    file_name = details[0]
    line_number = details[1]
    offset = details[2]
    line = details[3]
    
    if len(details) == 6:
        end_offset = details[5]
    else:
        end_offset = -1
    
    if (file_name is None):
        file_name = ''
    
    into.extend(_iter_highlight_producer(_produce_file_location(file_name, line_number, ''), highlighter))
    into.append('\n')
    
    if (line is not None):
        line = line.strip()
        
        left_stripped_count = 0
        for character in line:
            if character in {' ', '\n', '\t', '\f'}:
                left_stripped_count += 1
                continue
            
            break
        
        line = line[left_stripped_count:]
        
        into.append('    ')
        if highlighter is None:
            into.append(line)
        else:
            into.extend(iter_highlight_code_lines([line], highlighter))
        
        into.append('\n')
        
        if offset - 1 >= left_stripped_count:
            into.append(' ' * (3 + offset - left_stripped_count))
            
            if end_offset == -1:
                pointer_length = 1
            else:
                pointer_length = end_offset - offset
                
                if pointer_length < 1:
                    pointer_length = 1
            
            pointer = '^'
            if pointer_length != 1:
                pointer = '^' * pointer_length
            
            
            into = _add_typed_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR, pointer, into, highlighter
            )
            
            into.append('\n')
    
    
    exception_representation = type(syntax_error).__name__
    
    if (message is not None) and message:
        exception_representation = f'{exception_representation}: {message}'
    
    into = _add_typed_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR, exception_representation, into, highlighter
    )
    
    return into


def _get_simple_exception_representation(exception):
    """
    Tries to get simple exception representation.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to get it's representation of.
    
    Returns
    -------
    exception_representation : `None`, `str`
        Returns `None` if simple representation is not available.
    """
    exception_type = type(exception)
    if FunctionType is SlotWrapperType:
        if (exception_type.__init__ is not BaseException.__init__):
            return None
    
    else:
        if exception_type.__init__.__class__ is not SlotWrapperType:
            return None
    
    exception_parameters = getattr(exception, 'args', None)
    if (exception_parameters is None) or (not isinstance(exception_parameters, tuple)) :
        return None
    
    exception_parameters_length = len(exception_parameters)
    if exception_parameters_length > 1:
        return None
    
    exception_representation = exception_type.__name__
    if (exception_parameters_length == 1):
        exception_representation = f'{exception_representation}: {exception_parameters[0]}'

    return exception_representation


def get_exception_representation(exception):
    """
    Gets the exception's representation.
    
    Parameters
    ----------
    exception : ``BaseException``
        The respective exception instance.
    
    Returns
    -------
    exception_representation : `str`
    """
    try:
        exception_representation = _get_simple_exception_representation(exception)
        if (exception_representation is None):
            exception_representation = repr(exception)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        exception_representation = try_get_raw_exception_representation(exception)
    
    return exception_representation


def ignore_frame(file, name, line):
    """
    When rendering an exception traceback, specified frames can be added to being stopped from rendering.
    
    Parameters
    ----------
    file : `str`
        The name of the respective file.
    name : `str`
        The name of the respective function.
    line : `str`
        The respective line's stripped content.
    """
    try:
        files = IGNORED_FRAME_LINES[file]
    except KeyError:
        files = {}
        IGNORED_FRAME_LINES[file] = files

    try:
        names = files[name]
    except KeyError:
        names = set()
        files[name] = names

    names.add(line)


def _should_ignore_frame(file_name, name, line):
    """
    Returns whether the given frame should be ignored from rending.
    
    Called by ``should_ignore_frame`` before calling it's `filter`.
    
    Parameters
    ----------
    file_name : `str`
        The frame's respective file's name.
    name : `str`
        The frame's respective function's name.
    line : `str`
        The frame's respective stripped line.
    
    Returns
    -------
    should_ignore_frame : `bool`
        Whether the frame should be ignored.
    """
    try:
        files = IGNORED_FRAME_LINES[file_name]
    except KeyError:
        return False

    try:
        names = files[name]
    except KeyError:
        return False
    
    return (line in names)


def should_ignore_frame(file_name, name, line_number, line=..., filter=None):
    """
    Returns whether the given frame should be ignored from rending.
    
    Parameters
    ----------
    file_name : `str`
        The frame's respective file's name.
    name : `str`
        The frame's respective function's name.
    line_number : `int`
        The line's index where the exception occurred.
    line : `str`
        The frame's respective stripped line.
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
        
        Called with 4 parameters:
        
        +---------------+-----------+---------------------------------------------------------------+
        | Name          | Type      | Description                                                   |
        +===============+===========+===============================================================+
        | file_name     | `str`     | The frame's file's name.                                      |
        +---------------+-----------+---------------------------------------------------------------+
        | name          | `str`     | The name of the function.                                     |
        +---------------+-----------+---------------------------------------------------------------+
        | line_number   | `int`     | The line's index of the file where the exception occurred.    |
        +---------------+-----------+---------------------------------------------------------------+
        | line          | `str`     | The line of the file.                                         |
        +---------------+-----------+---------------------------------------------------------------+
    
    Returns
    -------
    should_ignore : `bool`
    """
    if line is ...:
        line = line_number
        line_number = 0
        
        warnings.warn(
            (
                'Please call `should_ignore_frame` with `4` parameters: `file, name, line_number, line`\n'
                'The `3` parameter version is deprecated and will be removed in 2022 Jun.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
    
    if _should_ignore_frame(file_name, name, line):
        return True
    
    
    if (filter is not None) and (not filter(file_name, name, line_number, line)):
        return True
    
    return False


def format_callback(func, args=None, kwargs=None):
    """
    Formats the given callback to a more user friendly representation.
    
    Parameters
    ----------
    func : `callable`
        The callback to format.
    args : `None`, `iterable` of `Any` = `None`, Optional
        Additional parameters to call the `func` with.
    kwargs : `None`, `dict` of (`str`, `Any`) items = `None`, Optional
        Additional keyword parameters to call the `func` with.
    
    Returns
    -------
    result : `str`
        The formatted callback.
    """
    result = []
    # un-warp the wrappers
    while True:
        if not (None is args is kwargs):
            sub_result = ['(']
            if (args is not None) and args:
                for arg in args:
                    sub_result.append(reprlib.repr(arg))
                    sub_result.append(', ')
            
            if (kwargs is not None) and kwargs:
                for key, arg in kwargs.items():
                    sub_result.append(str(key)) # never trust
                    sub_result.append('=')
                    sub_result.append(reprlib.repr(arg))
                    sub_result.append(', ')
            
            if len(sub_result) > 1:
                del sub_result[-1]
            
            sub_result.append(')')
            result.append(''.join(sub_result))
        
        if hasattr(func, 'func'):
            wrapped = func.func
        
        else:
            if (type(func) is MethodType) and hasattr(type(func.__self__), 'get_coroutine'):
                coroutine = func.__self__.get_coroutine()
                coroutine_repr = getattr(coroutine, '__qualname__', None)
                if coroutine_repr is None:
                    coroutine_repr = getattr(coroutine, '__name__', None)
                    if coroutine_repr is None:
                        coroutine_repr = repr(coroutine)
                func_repr = f'<Bound method {func.__func__.__name__} of Task {coroutine_repr}>'
            else:
                func_repr = getattr(func, '__qualname__', None)
                if func_repr is None:
                    func_repr = getattr(func, '__name__', None)
                    if func_repr is None:
                        func_repr = repr(func)
            
            result.insert(0, func_repr)
            break
        
        args = getattr(func, 'args', None)
        kwargs = getattr(func, 'kwargs', None)
        func = wrapped
    
    return ''.join(result)


def _cut_file_name(file_name):
    """
    Cuts the given file name.
    
    Parameters
    ----------
    file_name : `str`
        The file name to cut.
    
    Returns
    -------
    file_name : `str`
    """
    for path in sys.path:
        if file_name.startswith(path + PATH_SEPARATOR):
            return '...' + file_name[len(path):]
    
    return file_name


def format_builtin(func):
    """
    Formats the given built-in's name.
    
    Parameters
    ----------
    func : `callable`
        The builtin to format.
    
    Returns
    -------
    result : `str`
        The formatted builtin.
    """
    # Cython or builtin
    name = getattr(func, '__qualname__', None)
    if name is None:
        name = getattr(func, '__name__', None)
        if name is None: # builtins might reach this part
            name = type(func).__name__
    
    return f'{name}()'


def format_coroutine(coroutine):
    """
    Formats the given coroutine to a more user friendly representation.
    
    Parameters
    ----------
    coroutine : `CoroutineType`, `GeneratorType`, `CoroutineGeneratorType`
        The coroutine to get representation of.
    
    Returns
    -------
    result : `str`
        The formatted coroutine.
    """
    coroutine_type = type(coroutine)
    if coroutine_type is GeneratorType:
        code = coroutine.gi_code
        frame = coroutine.gi_frame
        running = coroutine.gi_running
    
    elif coroutine_type is CoroutineType:
        code = coroutine.cr_code
        frame = coroutine.cr_frame
        running = coroutine.cr_running
    
    elif coroutine_type is CoroutineGeneratorType:
        code = coroutine.ag_code
        frame = coroutine.ag_frame
        running = coroutine.ag_running
    
    else:
        code = None
        frame = None
        running = -1
    
    if running == True:
        state = 'running'
    
    elif running == False:
        if frame is None:
            state = 'finished'
        
        else:
            state = 'suspended'
    
    else:
        state = 'unknown state'
    
    if running == -1:
        name = format_builtin(coroutine)
    else:
        name = format_callback(coroutine)
    
    if (code is None):
        location = 'unknown location'
    
    else:
        file_name = _cut_file_name(code.co_filename)
        
        if frame is None:
            line_number = code.co_firstlineno
        else:
            line_number = frame.f_lineno
        
        location = f'"{file_name}", line {line_number}'
    
    return f'<{name} from {location}; {state}>'


STRING_TYPE_NONE = 0
STRING_TYPE_SINGLE_QUOTE = 1
STRING_TYPE_DOUBLE_QUOTE = 2
STRING_TYPE_TRIPLE_SINGLE_QUOTE = 3
STRING_TYPE_TRIPLE_DOUBLE_QUOTE = 4

PARENTHESES_RELATION = {
    ')': '(',
    ']': '[',
    '}': '{',
}

def get_expression_lines(file_name, line_number):
    """
    Gets all the lines of the expression starting at the given position.
    
    Parameters
    ----------
    file_name : `file_name`
        The respective file's name.
    line_number : `int`
        The expression's first line's index.
    
    Returns
    -------
    expression_lines : `str`
        The lines of the expression.
    """
    parentheses_stack = []
    string_type = STRING_TYPE_NONE
    lines = []
    
    while True:
        line = get_file_line(file_name, line_number)
        if not line:
            break
        
        lines.append(line)
        
        parsing_failed = False
        line_escaped = False
        
        character_index = -1
        character_limit = len(line)
        
        while True:
            character_index += 1
            if character_index >= character_limit:
                break
            
            character = line[character_index]
            
            if string_type == STRING_TYPE_NONE:
                if character in {'(', '[', '{'}:
                    parentheses_stack.append(character)
                    continue
                
                if character in {')', ']', '}'}:
                    if not parentheses_stack:
                        parsing_failed = True
                        break
                    
                    
                    if parentheses_stack[-1] != PARENTHESES_RELATION[character]:
                        parsing_failed = True
                        break
                    
                    del parentheses_stack[-1]
                    continue
                
                if character == '\'':
                    if (
                        (character_index + 2 < character_limit) and
                        (line[character_index + 1] == '\'') and
                        (line[character_index + 2] == '\'')
                    ):
                        character_index += 2
                        string_type = STRING_TYPE_TRIPLE_SINGLE_QUOTE
                    else:
                        string_type = STRING_TYPE_SINGLE_QUOTE
                    
                    continue
                
                if character == '"':
                    if (
                        (character_index + 2 < character_limit) and
                        (line[character_index + 1] == '\"') and
                        (line[character_index + 2] == '\"')
                    ):
                        character_index += 2
                        string_type = STRING_TYPE_TRIPLE_DOUBLE_QUOTE
                    else:
                        string_type = STRING_TYPE_DOUBLE_QUOTE
                    
                    continue
                
                if character == '#':
                    break
                
                if character == '\\':
                    line_escaped = True
                    break
            
            else:
                if character == '\n':
                    if string_type in (STRING_TYPE_SINGLE_QUOTE, STRING_TYPE_DOUBLE_QUOTE):
                        parsing_failed = True
                        break
                    
                    continue
                
                if character == '\\':
                    character_index += 1
                    
                    if string_type in (STRING_TYPE_SINGLE_QUOTE, STRING_TYPE_DOUBLE_QUOTE):
                        if (character_index >= character_limit):
                            parsing_failed = True
                            break
                    
                    continue
                
                
                if character == '\'':
                    if string_type == STRING_TYPE_SINGLE_QUOTE:
                        string_type = STRING_TYPE_NONE
                        continue
                    
                    if string_type == STRING_TYPE_TRIPLE_SINGLE_QUOTE:
                        if (
                            (character_index + 2 < character_limit) and
                            (line[character_index + 1] == '\'') and
                            (line[character_index + 2] == '\'')
                        ):
                            character_index += 2
                            string_type = STRING_TYPE_NONE
                            continue
                    
                    continue
                
                if character == '"':
                    if string_type == STRING_TYPE_DOUBLE_QUOTE:
                        string_type = STRING_TYPE_NONE
                        continue
                    
                    if string_type == STRING_TYPE_TRIPLE_DOUBLE_QUOTE:
                        if (
                            (character_index + 2 < character_limit) and
                            (line[character_index + 1] == '"') and
                            (line[character_index + 2] == '"')
                        ):
                            character_index += 2
                            
                            string_type = STRING_TYPE_NONE
                            continue
                    
                    continue
        
        
        if parsing_failed:
            break
        
        
        if not line.endswith('\n'):
            # no more lines. Simple.
            should_continue_parsing = False
        elif string_type in (STRING_TYPE_TRIPLE_SINGLE_QUOTE, STRING_TYPE_TRIPLE_DOUBLE_QUOTE):
            should_continue_parsing = True
        elif line_escaped:
            should_continue_parsing = True
        elif parentheses_stack:
            should_continue_parsing = True
        else:
            should_continue_parsing = False
        
        
        if not should_continue_parsing:
            break
        
        line_number += 1
        continue
    
    if not lines:
        return lines
    
    for index in range(len(lines)):
        lines[index] = lines[index].rstrip()
    
    indentation_to_remove = 0
    
    while True:
        for line in lines:
            if len(line) <= indentation_to_remove:
                continue
            
            if line[indentation_to_remove] in (' ', '\t'):
                continue
            
            break
        
        else:
            indentation_to_remove += 1
            continue
        
        break
    
    
    for index in range(len(lines)):
        lines[index] = lines[index][indentation_to_remove:]
    
    return lines


class FrameDetail:
    """
    Represents information about a frame.
    
    Used when rendering frames.
    
    Attributes
    ----------
    file_name : `str`
        Path to the represented file.
    line_number : `int`
        The respective line's index.
    lines : `None`, `list` of `str`
        The python source code lines of the respective instruction.
    mention_count : `int`
        How much times this exact frame was mentioned.
    name : `str`
        The represented function's name.
    produced_content : `None`, `list` of `str`
        The produced content.
    """
    __slots__ = ('file_name', 'line_number', 'lines', 'mention_count', 'name', 'produced_content')
    
    def __new__(cls, file_name, line_number, name):
        self = object.__new__(cls)
        self.file_name = file_name
        self.name = name
        self.line_number = line_number
        self.lines = None
        self.produced_content = None
        self.mention_count = 0
        return self
    
    def __repr__(self):
        """Returns the frame info's representation."""
        return f'{self.__class__.__name__}({self.file_name!r}, {self.line_number!r}, {self.name!r})'
    
    
    def __eq__(self, other):
        """Returns whether self equals to other."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.file_name != other.file_name:
            return False
        
        if self.line_number != other.line_number:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the frame info's hash value."""
        return hash(self.file_name) ^ self.line_number ^ hash(self.name)
    
    
    def do_mention(self):
        """
        Increments how much times the frame is mentioned.
        """
        self.mention_count += 1
    
    
    def get_lines(self):
        """
        Returns the lines of the instruction of the trace.
        
        Returns
        -------
        lines : `list` of `str`
            Can be empty.
        """
        lines = self.lines
        if (lines is None):
            lines = get_expression_lines(self.file_name, self.line_number)
            self.lines = lines
        
        return lines
    
    
    def get_line(self):
        """
        Returns the line where the exception occurred.
        
        Returns
        -------
        line : `str`
        """
        return '\n'.join(self.get_lines())
    
    
    def _render(self, highlighter):
        """
        Produces each part of the frame to render.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        highlighter : `None`, ``HighlightFormatterContext``
            Formatter storing highlighting details.
        
        Yields
        ------
        part : `str`
        """
        
        yield from _iter_highlight_producer(
            _produce_file_location(self.file_name, self.line_number, self.name),
            highlighter,
        )
        
        yield '\n'
        
        lines = self.get_lines()
        
        if lines:
            if (highlighter is None):
                for line in lines:
                    yield '    '
                    yield line
                    yield '\n'
            
            else:
                yield from iter_highlight_code_lines([f'    {line}\n' for line in lines], highlighter)
    
    
    def render_into(self, into, highlighter):
        """
        Renders frame.
        
        Parameters
        ----------
        into : `list` of `str`
            The list of strings to render the representation into.
        highlighter : `None`, ``HighlightFormatterContext``
            Formatter storing highlighting details.
        
        Returns
        -------
        into : `list` of `str`
        """
        if self.mention_count > 1:
            produced_content = self.produced_content
            if (produced_content is None):
                produced_content = [*self._render(highlighter)]
                self.produced_content = produced_content
            
            into.extend(produced_content)
        else:
            into.extend(self._render(highlighter))
        
        return into


FRAME_DETAIL_GROUP_TYPE_NONE = 0
FRAME_DETAIL_GROUP_TYPE_SINGLES = 1
FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT = 2
FRAME_DETAIL_GROUP_TYPE_REPEAT = 3


class FrameDetailGroup:
    """
    Represents a group of frame details.
    
    Attributes
    ----------
    details : `list` of ``FrameDetail``
        The stored details by the group.
    group_type : `int`
        The group's type.
    repeat_count : `int`
        How much times is the group repeated.
    """
    __slots__ = ('details', 'group_type', 'repeat_count')
    
    def __new__(cls):
        """
        Creates a new frame detail group.
        """
        self = object.__new__(cls)
        self.details = []
        self.group_type = FRAME_DETAIL_GROUP_TYPE_NONE
        self.repeat_count = 1
        return self
    
    
    @classmethod
    def _create_repeated(cls, repeat_count, details):
        """
        Creates a repeated frame detail group.
        
        Parameters
        ----------
        repeat_count : `int`
            How much times is the group repeated.
        details : `list` of ``FrameDetail``
            The stored details by the group.
        
        Returns
        -------
        self : ``FrameDetailGroup``
        """
        self = object.__new__(cls)
        self.details = details
        self.group_type = FRAME_DETAIL_GROUP_TYPE_REPEAT
        self.repeat_count = repeat_count
        return self
    
    
    def __eq__(self, other):
        """Returns whether the two frame detail groups are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        if len(self) != len(other):
            return False
        
        for self_detail, other_detail in zip(self.iter_details(), other.iter_details()):
            if self_detail != other_detail:
                return False
        
        return True
    
    
    def __len__(self):
        """Returns how much details are in the group."""
        return len(self.details) * self.repeat_count
    
    
    def __repr__(self):
        """Returns the frame detail group's representation."""
        return f'<{self.__class__.__name__} details={self.details!r}>'
    
    
    def __bool__(self):
        """Returns whether the detail group has any elements."""
        return self.group_type != FRAME_DETAIL_GROUP_TYPE_NONE
    
    
    def add_initial_frame_detail(self, frame_detail):
        """
        Adds the given frame detail to self. Should be only used to add the first element to self.
        
        Parameters
        ----------
        frame_detail : ``FrameDetail``
            The frame detail to add.
        """
        self.details.append(frame_detail)
        
        if frame_detail.mention_count > 1:
            group_type = FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT
        else:
            group_type = FRAME_DETAIL_GROUP_TYPE_SINGLES
        self.group_type = group_type
    
    
    def try_add_frame_detail(self, frame_detail):
        """
        Tries to add the given frame detail to self. On success returns `True`.
        
        Parameters
        ----------
        frame_detail : ``FrameDetail``
            The frame detail to add.
        
        Returns
        -------
        success : `bool`
        """
        group_type = self.group_type
        
        if group_type == FRAME_DETAIL_GROUP_TYPE_NONE:
            self.add_initial_frame_detail(frame_detail)
            return True
        
        
        if group_type == FRAME_DETAIL_GROUP_TYPE_SINGLES:
            if frame_detail.mention_count > 1:
                return False
            
            self.details.append(frame_detail)
            return True
        
        
        if group_type == FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT:
            self.details.append(frame_detail)
            
            if frame_detail.mention_count > 1:
                group_type = FRAME_DETAIL_GROUP_TYPE_REPEAT
            else:
                group_type = FRAME_DETAIL_GROUP_TYPE_SINGLES
            self.group_type = group_type
            return True
        
        
        if group_type == FRAME_DETAIL_GROUP_TYPE_REPEAT:
            if frame_detail.mention_count <= 1:
                return False
            
            self.details.append(frame_detail)
            return True
        
        # No more cases
        return False
    
    
    def try_merge_single_group(self, other):
        """
        Tries to merge self with an other frame detail group. But only merges them if both is possibly a single-mention
        group.
        
        Parameters
        ----------
        other : ``FrameDetailGroup``
            The detail group to merge self with.
        
        Returns
        -------
        merged : `bool`
        """
        if (self.repeat_count != 1) or (other.repeat_count != 1):
            return False
        
        self_group_type = self.group_type
        other_group_type = other.group_type
        
        if self_group_type == FRAME_DETAIL_GROUP_TYPE_SINGLES:
            should_merge = other_group_type in (FRAME_DETAIL_GROUP_TYPE_SINGLES, FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT)
        
        elif self_group_type == FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT:
            should_merge = other_group_type == FRAME_DETAIL_GROUP_TYPE_SINGLES
        
        else:
            should_merge = False
        
        if should_merge:
            self.details.extend(other.iter_exhaust_details())
        
        return should_merge
    
    
    def try_merge_repeat_group(self, other):
        """
        Tries to merge self with an other frame detail group. But only merges them if both is possibly a repeat-mention
        group.
        
        Parameters
        ----------
        other : ``FrameDetailGroup``
            The detail group to merge self with.
        
        Returns
        -------
        merged : `bool`
        """
        if (self.repeat_count != 1) or (other.repeat_count != 1):
            return False
        
        self_group_type = self.group_type
        other_group_type = other.group_type
        
        if self_group_type in (FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT, FRAME_DETAIL_GROUP_TYPE_REPEAT):
            should_merge = other_group_type in (FRAME_DETAIL_GROUP_TYPE_MAYBE_REPEAT, FRAME_DETAIL_GROUP_TYPE_REPEAT)
        
        else:
            should_merge = False
        
        if should_merge:
            self.details.extend(other.iter_exhaust_details())
        
        return should_merge
    
    
    def iter_details(self):
        """
        Iterates over the details of the detail group.
        
        This method is an iterable generator.
        
        Yields
        ------
        detail : ``FrameDetail``
        """
        details = self.details
        for index in range(self.repeat_count):
            yield from details
    
    
    def iter_exhaust_details(self):
        """
        Iterates over the details of the detail group, exhausting its own.
        
        This method is an iterable generator.
        
        Yields
        ------
        detail : ``FrameDetail``
        """
        try:
            yield from self.iter_details()
        finally:
            self.details.clear()
            self.group_type = FRAME_DETAIL_GROUP_TYPE_NONE
    
    
    def iter_break_repeated_patterns(self):
        """
        Breaks down self to repeated patterns if possible.
        
        This method is an iterable generator.
        
        Yields
        ------
        detail_groups : ``FrameDetailGroup``
        """
        # Can we break it down?
        if (self.group_type != FRAME_DETAIL_GROUP_TYPE_REPEAT):
            yield self
            return
        
        # If it has repeat set, it is already a broken group
        if self.repeat_count > 1:
            yield self
            return
        
        details = self.details
        details_length = len(details)
        start = details_length - 1
        detail_groups = []
        
        
        while True:
            for reverse_shift in range(start, 1, -1):
                for chunk_length in range(1, (reverse_shift >> 1) + 2):
                    repeat = 1
                    for chunk_end_index in range(reverse_shift - chunk_length, -1, -chunk_length):
                        for index in range(chunk_length):
                            if details[reverse_shift - index] != details[chunk_end_index - index]:
                                break
                        else:
                            repeat += 1
                            continue
                        
                        break
                    
                    if repeat * chunk_length <= 2:
                        continue
                    
                    if repeat > 1:
                        if start != reverse_shift:
                            detail_groups.append(type(self)._create_repeated(1, details[reverse_shift + 1 : start + 1]))
                        
                        detail_groups.append(type(self)._create_repeated(
                            repeat, details[reverse_shift - chunk_length + 1: reverse_shift + 1]
                        ))
                        start = reverse_shift - repeat * chunk_length
                        break
                    
                else:
                    continue
                break
            else:
                break
        
        # Did we match anything even?
        if start == details_length - 1:
            yield self
            return
        
        if start != details_length:
            detail_groups.append(type(self)._create_repeated(1 , details[0 : start + 1]))
        
        yield from reversed(detail_groups)
    
    
    def render_into(self, into, highlighter):
        """
        Renders frame group.
        
        Parameters
        ----------
        into : `list` of `str`
            The list of strings to render the representation into.
        highlighter : `None`, ``HighlightFormatterContext``
            Formatter storing highlighting details.
        
        Returns
        -------
        into : `list` of `str`
        """
        repeat_count = self.repeat_count
        details = self.details
        
        if (repeat_count > 1):
            into = _add_typed_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_DETAIL_FRAME_REPEAT,
                (
                    f'[Following {len(details)} frame{"s were" if len(details) > 1 else " was"} '
                    f'repeated {repeat_count} times]'
                ),
                into,
                highlighter
            )
            into.append('\n')
        
        for detail in details:
            detail.render_into(into, highlighter)
        
        if (repeat_count > 1):
            into = _add_typed_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_DETAIL_FRAME_REPEAT,
                f'[End of repeated frames]',
                into,
                highlighter
            )
            into.append('\n')
        
        return into


def render_frames_into(frames, extend=None, *, filter=None, highlighter=None):
    """
    Renders the given frames into a list of strings.
    
    Parameters
    ----------
    frames : `list` of (`FrameType`, `TraceBack`, ``FrameProxyType``)
        The frames to render.
    
    extend : `None`, `list` of `str` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
        
        Called with 4 parameters:
        
        +---------------+-----------+---------------------------------------------------------------+
        | Name          | Type      | Description                                                   |
        +===============+===========+===============================================================+
        | file_name     | `str`     | The frame's file's name.                                      |
        +---------------+-----------+---------------------------------------------------------------+
        | name          | `str`     | The name of the function.                                     |
        +---------------+-----------+---------------------------------------------------------------+
        | line_number   | `int`     | The line's index of the file where the exception occurred.    |
        +---------------+-----------+---------------------------------------------------------------+
        | line          | `str`     | The line of the file.                                         |
        +---------------+-----------+---------------------------------------------------------------+
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    Returns
    -------
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    frames = _convert_frames(frames)
    
    if extend is None:
        extend = []
    
    checked_file_caches = set()
    
    frame_details_ignored = set()
    frame_details_stack = []
    frame_details_unique = {}
    
    
    for frame in frames:
        frame_detail = FrameDetail(frame.file_name, frame.line_number, frame.name)
        if frame_detail in frame_details_ignored:
            continue
        
        try:
            frame_detail_to_add = frame_details_unique[frame_detail]
        except KeyError:
            
            if frame_detail.file_name not in checked_file_caches:
                checked_file_caches.add(frame_detail.file_name)
                check_file_cache(frame_detail.file_name)
                
            if should_ignore_frame(
                frame_detail.file_name,
                frame_detail.name,
                frame_detail.line_number,
                frame_detail.get_line(),
                filter = filter
            ):
                frame_details_ignored.add(frame_detail)
                continue
            
            frame_detail_to_add = frame_detail
            frame_details_unique[frame_detail_to_add] = frame_detail_to_add
        else:
            frame_detail_to_add.do_mention()
        
        frame_detail_to_add.do_mention()
        frame_details_stack.append(frame_detail_to_add)
    
    
    if len(frame_details_unique) == len(frame_details_stack):
        for frame_detail in frame_details_stack:
            extend = frame_detail.render_into(extend, highlighter)
    
    else:
        frame_detail_group = FrameDetailGroup()
        frame_detail_groups = [frame_detail_group]
        
        for frame_detail in frame_details_stack:
            if not frame_detail_group.try_add_frame_detail(frame_detail):
                frame_detail_group = FrameDetailGroup()
                frame_detail_group.add_initial_frame_detail(frame_detail)
                frame_detail_groups.append(frame_detail_group)
        
        
        for index in reversed(range(1, len(frame_detail_groups))):
            frame_detail_group_1 = frame_detail_groups[index - 1]
            frame_detail_group_2 = frame_detail_groups[index]
            
            if (
                frame_detail_group_1.try_merge_repeat_group(frame_detail_group_2) or
                frame_detail_group_1.try_merge_single_group(frame_detail_group_2)
            ):
                del frame_detail_groups[index]
                continue
        
        for frame_detail_group in frame_detail_groups:
            for frame_detail_group in frame_detail_group.iter_break_repeated_patterns():
                extend = frame_detail_group.render_into(extend, highlighter)
    
    return extend


def _produce_file_location(file_name, line_number, name):
    """
    Produces file location part and their tokens.
    
    Parameters
    ----------
    file_name : `str`
        Path of the respective file.
    line_number : int`
        The respective line's number.
    name : `str`
        The respective functions name.
    
    Yields
    ------
    part : `str`
        Part to render
    token_type : `int`
        The part's type.
    """
    yield '  File ', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION
    
    if file_name:
        yield f'"{file_name}"', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_PATH
    else:
        yield 'unknown location', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION
    
    yield ', line ', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION
    yield  str(line_number), HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER
    
    if name:
        yield ', in ', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION
        yield name, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_NAME


class FrameProxyType:
    """
    Base class for frame proxies.
    
    Frame proxies are used to provide the same api for different types of frame representations.
    """
    __slots__ = ()
    
    def __new__(cls):
        """
        Creates a new frame proxy.
        """
        return object.__new__(cls)
    
    
    def __repr__(self):
        """Returns the frame proxy's representation."""
        return f'<{self.__class__.__name__}>'
    
    
    @property
    def builtins(self):
        """
        Returns the frame's builtins.
        
        Returns
        -------
        builtins : `dict` of (`str`, `Any`) items
        """
        raise NotImplementedError
    
    
    @property
    def globals(self):
        """
        Returns the frame's globals.
        
        Returns
        -------
        globals : `dict` of (`str`, `Any`)
        """
        raise NotImplementedError
    
    
    @property
    def locals(self):
        """
        Returns the local variables of the frame.
        
        Returns
        -------
        locals : `dict` of (`str`, `Any`) items
        """
        raise NotImplementedError
    
    
    @property
    def code(self):
        """
        Returns the frame's code.
        
        Returns
        -------
        code : `CodeType`
        """
        raise NotImplementedError
    
    
    @property
    def last_instruction_index(self):
        """
        Returns the traceback's frame's last attempted instruction index in the bytecode.
        
        Returns
        -------
        last_instruction_index : `int`
        """
        raise NotImplementedError
    
    
    @property
    def line_number(self):
        """
        Returns the traceback's frame's current line number in Python source code.
        
        Returns
        -------
        line_number : `int`
        """
        raise NotImplementedError
    
    
    @property
    def tracing_function(self):
        """
        Tracing function for the traceback's frame.
        
        Returns
        -------
        tracing_function : `FunctionType`, `None`
            Defaults to `None`.
        """
        raise NotImplementedError
    
    
    @property
    def file_name(self):
        """
        Returns the frame's file name-
        
        Returns
        -------
        file_name : `str`
        """
        file_name = self.code.co_filename
        if (file_name is None):
            file_name = ''
        
        return file_name
    
    
    @property
    def name(self):
        """
        Returns the frame's function's name.
        
        Returns
        -------
        name : `str`
        """
        return self.code.co_name


class TracebackFrameProxy(FrameProxyType):
    """
    Wraps a traceback's frame.
    
    Attributes
    ----------
    _traceback : ``TracebackType``
        The wrapped traceback frame.
    """
    __slots__ = ('_traceback',)
    
    def __new__(cls, traceback):
        """
        Creates a new traceback frame proxy.
        
        Parameters
        ----------
        traceback : ``TracebackType``
            The traceback frame to wrap.
        """
        self = object.__new__(cls)
        self._traceback = traceback
        return self
    
    
    @property
    @copy_docs(FrameProxyType.builtins)
    def builtins(self):
        return self._traceback.tb_frame.f_builtins
    
    
    @property
    @copy_docs(FrameProxyType.globals)
    def globals(self):
        return self._traceback.tb_frame.f_globals
    
    
    @property
    @copy_docs(FrameProxyType.locals)
    def locals(self):
        return self._traceback.tb_frame.f_locals
    
    
    @property
    @copy_docs(FrameProxyType.code)
    def code(self):
        return self._traceback.tb_frame.f_code
    
    
    @property
    @copy_docs(FrameProxyType.last_instruction_index)
    def last_instruction_index(self):
        return self._traceback.tb_frame.f_lasti
    
    
    @property
    @copy_docs(FrameProxyType.line_number)
    def line_number(self):
        return self._traceback.tb_lineno
    
    
    @property
    @copy_docs(FrameProxyType.tracing_function)
    def tracing_function(self):
        return self._traceback.tb_frame.f_trace



class FrameProxy(FrameProxyType):
    """
    Wraps a frame.
    
    Attributes
    ----------
    _frame : ``FrameType``
        The wrapped frame.
    """
    __slots__ = ('_frame',)
    
    def __new__(cls, frame):
        """
        Creates a new frame proxy.
        
        Parameters
        ----------
        frame : ``FrameType``
            The frame to wrap.
        """
        self = object.__new__(cls)
        self._frame = frame
        return self
    
    
    @property
    @copy_docs(FrameProxyType.builtins)
    def builtins(self):
        return self._frame.f_builtins
    
    
    @property
    @copy_docs(FrameProxyType.globals)
    def globals(self):
        return self._frame.f_globals
    
    
    @property
    @copy_docs(FrameProxyType.locals)
    def locals(self):
        return self._frame.f_locals
    
    
    @property
    @copy_docs(FrameProxyType.code)
    def code(self):
        return self._frame.f_code
    
    
    @property
    @copy_docs(FrameProxyType.last_instruction_index)
    def last_instruction_index(self):
        return self._frame.f_lasti
    
    
    @property
    @copy_docs(FrameProxyType.line_number)
    def line_number(self):
        return self._frame.f_lineno
    
    
    @property
    @copy_docs(FrameProxyType.tracing_function)
    def tracing_function(self):
        return self._frame.f_trace


def _convert_frames(frames):
    """
    Converts the given frames into frame proxies.
    
    Parameters
    ----------
    frames : `list` of `Any`
        The frames to convert.
    
    Returns
    -------
    frame_proxies : ``FrameProxy``
    
    Raises
    ------
    TypeError
        Unknown frame type.
    """
    frame_proxies = []
    
    for frame in frames:
        if isinstance(frame, FrameProxyType):
            frame_proxy = frame
        
        elif isinstance(frame, FrameType):
            frame_proxy = FrameProxy(frame)
        
        elif isinstance(frame, TracebackType):
            frame_proxy = TracebackFrameProxy(frame)
        
        else:
            raise TypeError(
                f'Unknown frame type, got {type(frame).__name__}; {frame!r}; frames={frames!r}.'
            )
        
        frame_proxies.append(frame_proxy)
    
    return frame_proxies


def _get_exception_frames(exception):
    """
    Gets the frames of the given exception.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to trace back.
    
    Returns
    -------
    frames : `list` of ``FrameProxyType``
        A list of `frame` compatible exception frames.
    """
    frames = []
    traceback = exception.__traceback__
    
    while True:
        if traceback is None:
            break
        
        frame = TracebackFrameProxy(traceback)
        frames.append(frame)
        traceback = traceback.tb_next
    
    return frames


REASON_TYPE_NONE = 0
REASON_TYPE_CAUSE = 1
REASON_TYPE_CONTEXT = 2
REASON_TYPE_CAUSE_GROUP = 3


def render_exception_into(exception, extend=None, *, filter=None, highlighter=None):
    """
    Renders the given exception's frames into a list of strings.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to render.
    
    extend : `None`, `list` of `str` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
        
        Called with 4 parameters:
        
        +---------------+-----------+---------------------------------------------------------------+
        | Name          | Type      | Description                                                   |
        +===============+===========+===============================================================+
        | file_name     | `str`     | The frame's file's name.                                      |
        +---------------+-----------+---------------------------------------------------------------+
        | name          | `str`     | The name of the function.                                     |
        +---------------+-----------+---------------------------------------------------------------+
        | line_number   | `int`     | The line's index of the file where the exception occurred.    |
        +---------------+-----------+---------------------------------------------------------------+
        | line          | `str`     | The line of the file.                                         |
        +---------------+-----------+---------------------------------------------------------------+
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    Returns
    -------
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    exceptions = []
    reason_type = REASON_TYPE_NONE
    while True:
        exceptions.append((exception, reason_type))
        
        cause_exception = exception.__cause__
        if (cause_exception is not None):
            exception = cause_exception
            if isinstance(exception, CauseGroup):
                reason_type = REASON_TYPE_CAUSE_GROUP
            else:
                reason_type = REASON_TYPE_CAUSE
            continue
        
        context_exception = exception.__context__
        if (context_exception is not None):
            exception = context_exception
            reason_type = REASON_TYPE_CONTEXT
            continue
        
        # no other cases
        break
    
    
    for exception, reason_type in reversed(exceptions):
        if reason_type == REASON_TYPE_CAUSE_GROUP:
            extend = _add_trace_title_into(
                f'The following {len(exceptions)} exceptions where the reason of the exception following them:',
                extend,
                highlighter,
            )
            extend.append('\n\n')
            
            for index, cause in enumerate(exception, 1):
                extend = _add_trace_title_into(f'[Exception {index}] ', extend, highlighter)
                extend = render_exception_into(cause, extend = extend, filter = filter, highlighter = highlighter)
                
                if index != len(exception):
                    extend.append('\n')
        
        else:
            extend = _add_trace_title_into('Traceback (most recent call last):', extend, highlighter)
            extend.append('\n')
            
            extend = render_frames_into(
                _get_exception_frames(exception),
                extend,
                filter = filter,
                highlighter = highlighter,
            )
            
            if is_syntax_error(exception):
                extend = _render_syntax_error_representation_into(exception, extend, highlighter)
            else:
                extend = _add_typed_part_into(
                    HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
                    get_exception_representation(exception),
                    extend,
                    highlighter,
                )
            
            extend.append('\n')
            
            if reason_type == REASON_TYPE_NONE:
                break
        
        if reason_type == REASON_TYPE_CAUSE:
            title = 'The above exception was the direct cause of the following exception:'
        
        elif reason_type == REASON_TYPE_CONTEXT:
            title = 'During handling of the above exception, another exception occurred:'
        
        elif reason_type == REASON_TYPE_CAUSE_GROUP:
            title = f'The above {len(exception)} exception was the direct cause of the following exception:'
        
        else:
            title = None
        
        extend.append('\n')
        
        if (title is not None):
            extend = _add_trace_title_into(title, extend, highlighter)
            extend.append('\n\n')
        continue
    
    return extend


def _add_trace_title_into(title, into, highlighter):
    """
    Adds trace title into the given list of strings.
    
    Parameters
    ----------
    title : `str`
        The title to add.
    into : `list` of `str`
        The list of strings to add.
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    Returns
    -------
    into : `list` of `str`
    """
    return _add_typed_part_into(HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE, title, into, highlighter)


def _iter_highlight_producer(producer, highlighter):
    """
    iterates over a producer and applies highlight to each part.
    
    This method is an iterable generator
    
    Parameters
    ----------
    producer : `GeneratorType`
        Generator to produce parts.
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    
    Yields
    ------
    part : `str`
    """
    if highlighter is None:
        for part, token_type in producer:
            yield part
    else:
        for part, token_type in producer:
            yield from highlighter.generate_highlighted(Token(token_type, part))


def _add_typed_part_into(type_, part, into, highlighter):
    """
    Adds trace title into the given list of strings.
    
    Parameters
    ----------
    type_ : `int`
        Token type identifier.
    part : `str`
        The part to add.
    into : `list` of `str`
        The list of strings to add.
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    Returns
    -------
    into : `list` of `str`
    """
    if (highlighter is None):
        into.append(part)
    else:
        into.extend(highlighter.generate_highlighted(Token(type_, part)))
    
    return into
