__all__ = ('ignore_frame', 'render_exception_into', 'render_frames_into', 'should_ignore_frame',)

import linecache, reprlib
from types import CoroutineType, GeneratorType, MethodType


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


def should_ignore_frame(file, name, line):
    """
    Returns whether the given frame should be ignored from rending.
    
    Parameters
    ----------
    file : `str`
        The frame's respective file's name.
    name : `str`
        The frame's respective function's name.
    line : `str`
        The frame's respective stripped line.
    
    Returns
    -------
    should_ignore : `bool`
    """
    try:
        files = IGNORED_FRAME_LINES[file]
    except KeyError:
        return False

    try:
        names = files[name]
    except KeyError:
        return False
    
    return (line in names)


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
        
        try:
            wrapped = func.func
        except AttributeError:
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
    coroutine : `CoroutineType`, `GeneratorType` (or any compatible cyi or builtin)
        The coroutine to get representation of.
    
    Returns
    -------
    result : `str`
        The formatted coroutine.
    """
    if not (hasattr(coroutine, 'cr_code') or hasattr(coroutine, 'gi_code')):
        # Cython or builtin
        name = getattr(coroutine, '__qualname__', None)
        if name is None:
            name = getattr(coroutine, '__name__', None)
            if name is None: # builtins might reach this part
                name = coroutine.__class__.__name__
        
        if type(coroutine) is GeneratorType:
            running = coroutine.gi_running
        elif type(coroutine) is CoroutineType:
            running = coroutine.cr_running
        else:
            running = False
        
        if running:
            state = 'running'
        else:
            state = 'done'
        
        return f'{name}() {state}'
    
    name = format_callback(coroutine)
    
    if type(coroutine) is GeneratorType:
        code = coroutine.gi_code
        frame = coroutine.gi_frame
    else:
        code = coroutine.cr_code
        frame = coroutine.cr_frame
    
    file_name = code.co_filename
    
    if frame is None:
        line_number = code.co_firstlineno
        state = 'done'
    else:
        line_number = frame.f_lineno
        state = 'running'
    
    return f'{name} {state} defined at {file_name}:{line_number}'


def render_frames_into(frames, extend=None):
    """
    Renders the given frames into a list of strings.
    
    Parameters
    ----------
    frames : `list` of (`frame`, ``ExceptionFrameProxy``)
        The frames to render.
    extend : `None`, `list` of `str`
        Whether the frames should be rendered into an already existing list.
    
    Returns
    -------
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    checked = set()
    
    last_file_name = ''
    last_line_number = ''
    last_name = ''
    count = 0
    
    for frame in frames:
        line_number = frame.f_lineno
        code = frame.f_code
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
            linecache.checkcache(file_name)
        
        line = linecache.getline(file_name, line_number, None)
        line = line.strip()
        
        if should_ignore_frame(file_name, name, line):
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
        if (line is not None) and line:
            extend.append('\n    ')
            extend.append(line)
        extend.append('\n')
        
    if count > 3:
        count -= 3
        extend.append('  [Previous line repeated ')
        extend.append(str(count))
        extend.append(' more times]\n')
    
    return extend


class ExceptionFrameProxy:
    """
    Wraps a `traceback` object to be `frame` compatible.
    
    Attributes
    ----------
    tb : `traceback`
        The wrapped traceback frame.
    """
    __slots__ = ('tb',)
    
    def __init__(self, tb):
        """
        Creates a new ``ExceptionFrameProxy`` with the given traceback.
        
        tb : `traceback`
            The traceback to wrap.
        """
        self.tb = tb
    
    @property
    def f_builtins(self):
        """
        Returns the traceback's frame's builtins.
        
        Returns
        -------
        f_builtins : `dict` of (`str`, `Any`) items
        """
        return self.tb.tb_frame.f_builtins
    
    @property
    def f_code(self):
        """
        Returns the traceback's frame's code.
        
        Returns
        -------
        f_code : `code`
        """
        return self.tb.tb_frame.f_code
    
    @property
    def f_globals(self):
        """
        Returns the traceback's frame's globals.
        
        Returns
        -------
        f_globals : `dict` of (`str`, `Any`)
        """
        return self.tb.tb_frame.f_globals
    
    @property
    def f_lasti(self):
        """
        Returns the traceback's frame's last attempted instruction index in the bytecode.
        
        Returns
        -------
        f_lasti : `int`
        """
        return self.tb.tb_frame.f_lasti
    
    @property
    def f_lineno(self):
        """
        Returns the traceback's frame's current line number in Python source code.
        
        Returns
        -------
        f_lineno : `int`
        """
        return self.tb.tb_lineno
    
    @property
    def f_locals(self):
        """
        Returns the local variables, what the traceback's frame can see.
        
        Returns
        -------
        f_locals : `dict` of (`str`, `Any`)
        """
        return self.tb.tb_frame.f_locals
    
    @property
    def f_trace(self):
        """
        Tracing function for the traceback's frame.
        
        Returns
        -------
        f_trace : `Any`
            Defaults to `None`.
        """
        return self.tb.tb_frame.f_trace

def _get_exception_frames(exception):
    """
    Gets the frames of the given exception.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to trace back.
    
    Returns
    -------
    frames : `list` of ``ExceptionFrameProxy``
        A list of `frame` compatible exception frames.
    """
    frames = []
    tb = exception.__traceback__
    
    while True:
        if tb is None:
            break
        frame = ExceptionFrameProxy(tb)
        frames.append(frame)
        tb = tb.tb_next
    
    return frames

def render_exception_into(exception, extend=None):
    """
    Renders the given exception's frames into a list of strings.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to render.
    extend : `None`, `list` of `str`
        Whether the frames should be rendered into an already existing list.
    
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
        extend = render_frames_into(frames, extend=extend)
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
