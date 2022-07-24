__all__ = ('ignore_frame', 'render_exception_into', 'render_frames_into', 'should_ignore_frame',)

import reprlib, warnings
from linecache import checkcache as check_file_cache, getline as get_file_line
from types import (
    AsyncGeneratorType as CoroutineGeneratorType, CoroutineType, FrameType, GeneratorType, MethodType, TracebackType
)

from .docs import copy_docs


IGNORED_FRAME_LINES = {}

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
        exception_representation = repr(exception)
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
    line_number : `int`
        The line's index where the exception occurred.
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
    filer : `None`, `callable` = `None`, Optional (Keyword only)
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
    
    # Cython or builtin
    name = getattr(coroutine, '__qualname__', None)
    if name is None:
        name = getattr(coroutine, '__name__', None)
        if name is None: # builtins might reach this part
            name = coroutine_type.__name__
    

    if running == True:
        state = 'running'
    
    elif running == False:
        if frame is None:
            state = 'finished'
        
        else:
            state = 'blocked'
    
    else:
        state = 'unknown state'
    
    
    if running == -1:
        name = f'{name}()'
    else:
        name = format_callback(coroutine)
    
    if (code is None):
        location = 'unknown location'
    
    else:
        file_name = code.co_filename
        
        if frame is None:
            line_number = code.co_firstlineno
        else:
            line_number = frame.f_lineno
        
        location = f'{file_name}:{line_number}'
    
    return f'{name} {state} defined at {location}'


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
    
    line_number_position = line_number
    while True:
        line = get_file_line(file_name, line_number_position, None)
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
        
        line_number_position += 1
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


def render_frames_into(frames, extend=None, filter=None):
    """
    Renders the given frames into a list of strings.
    
    Parameters
    ----------
    frames : `list` of (`FrameType`, `TraceBack`, ``FrameProxyType``)
        The frames to render.
    extend : `None`, `list` of `str` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    filer : `None`, `callable` = `None`, Optional (Keyword only)
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
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    frames = _convert_frames(frames)
    
    if extend is None:
        extend = []
    
    checked = set()
    
    last_file_name = ''
    last_line_number = ''
    last_name = ''
    count = 0
    
    for frame in frames:
        line_number = frame.line_number
        code = frame.code
        file_name = code.co_filename
        name = code.co_name
        
        if last_file_name == file_name and last_line_number == line_number and last_name == name:
            count += 1
            if count > 2:
                continue
        else:
            if count > 3:
                count -= 3
                extend.append('  [Previous line repeated ')
                extend.append(str(count))
                extend.append(' more times]\n')
            count = 0
        
        if file_name not in checked:
            checked.add(file_name)
            check_file_cache(file_name)
        
        lines = get_expression_lines(file_name, line_number)
        
        if should_ignore_frame(file_name, name, line_number, '\n'.join(lines), filter=filter):
            continue
        
        last_file_name = file_name
        last_line_number = line_number
        last_name = code.co_name
        
        extend.append('  File \"')
        extend.append(file_name)
        extend.append('\", line ')
        extend.append(str(line_number))
        extend.append(', in ')
        extend.append(name)
        for line in lines:
            extend.append('\n    ')
            extend.append(line)
        
        extend.append('\n')
        
    if count > 3:
        count -= 3
        extend.append('  [Previous line repeated ')
        extend.append(str(count))
        extend.append(' more times]\n')
    
    return extend


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
        self = FrameProxyType.__new__(cls)
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
        traceback : ``FrameType``
            The frame to wrap.
        """
        self = FrameProxyType.__new__(cls)
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


def render_exception_into(exception, extend=None, *, filter=None):
    """
    Renders the given exception's frames into a list of strings.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to render.
    extend : `None`, `list` of `str` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    filer : `None`, `callable` = `None`, Optional (Keyword only)
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
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    exceptions = []
    reason_type = 0
    while True:
        exceptions.append((exception, reason_type))
        cause_exception = exception.__cause__
        if (cause_exception is not None):
            exception = cause_exception
            reason_type = 1
            continue
        
        context_exception = exception.__context__
        if (context_exception is not None):
            exception = context_exception
            reason_type = 2
            continue
        
        # no other cases
        break
    
    for exception, reason_type in reversed(exceptions):
        frames = _get_exception_frames(exception)
        extend.append('Traceback (most recent call last):\n')
        extend = render_frames_into(frames, extend=extend, filter=filter)
        extend.append(get_exception_representation(exception))
        extend.append('\n')
        
        if reason_type == 0:
            break
        
        if reason_type == 1:
            extend.append('\nThe above exception was the direct cause of the following exception:\n\n')
            continue
        
        if reason_type == 2:
            extend.append('\nDuring handling of the above exception, another exception occurred:\n\n')
            continue
        
        # no more cases
        continue
    
    return extend
