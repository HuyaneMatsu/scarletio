__all__ = (
    'render_frames_into_async', 'render_exception_into_async', 'set_default_trace_writer_highlighter',
    'set_trace_writer_highlighter', 'write_exception_async', 'write_exception_maybe_async'
)

import sys
from os import get_terminal_size
from sys import platform as PLATFORM
from threading import current_thread

from ...utils import (
    DEFAULT_ANSI_HIGHLIGHTER, HighlightFormatterContext, alchemy_incendiary, call, export, include,
    render_exception_into, render_frames_into
)
from .event_loop import get_event_loop


EventThread = include('EventThread')


async def render_frames_into_async(frames, extend=None, *, filter=None, highlighter=None, loop=None):
    """
    Renders the given frames into a list of strings.
    
    This function provides asynchronous way of executing of ``render_frames_into``.
    
    ``render_frames_into`` contains blocking io operations, like file-reads.
    
    This method is a coroutine.
    
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
    
    loop : `None`, ``EventThread`` = `None`, Optional (Keyword only)
        The event loop to execute the operation on. If not given, is auto-detected.
    
    Returns
    -------
    extend : `list` of `str`
        The rendered frames as a `list` of it's string parts.
    
    Raises
    ------
    RuntimeError
        There are are no detectable event loops.
    """
    if loop is None:
        loop = get_event_loop()
    
    return await loop.run_in_executor(
        alchemy_incendiary(
            render_frames_into,
            (frames, extend),
            {'filter': filter, 'highlighter': highlighter}
        )
    )


async def render_exception_into_async(exception, extend=None, *, filter=None, highlighter=None, loop=None):
    """
    Renders the given exception's frames into a list of strings.
    
    This function provides asynchronous way of executing of ``render_exception_into``.
    
    ``render_exception_into`` calls ``render_frames_into`` which contains blocking io operations, like file-reads.
    
    This method is a coroutine.
    
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
    future : ``Future`` -> `list` of `str`
        The rendered frames as a `list` of it's string parts.
    """
    if loop is None:
        loop = get_event_loop()
    
    return await loop.run_in_executor(
        alchemy_incendiary(
            render_exception_into,
            (exception, extend),
            {'filter': filter, 'highlighter': highlighter}
        )
    )


def write_exception_sync(exception, before=None, after=None, file=None, *, filter=None, highlighter=None):
    """
    Writes the given exception's traceback.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to render.
    
    before : `str`, `list` of `str` = `None`, Optional
        Any content, what should go before the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.
    
    after : `str`, `list` of `str` = `None`, Optional
        Any content, what should go after the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.
    
    file : `None`, `I/O stream` = `None`, Optional
        The file to print the stack to. Defaults to `sys.stderr`.
    
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
    """
    extracted = []
    
    if before is None:
        pass
    elif isinstance(before, str):
        extracted.append(before)
    elif isinstance(before, list):
        for element in before:
            if isinstance(element, str):
                extracted.append(element)
            else:
                extracted.append(repr(element))
                extracted.append('\n')
    else:
        # ignore exception cases
        extracted.append(repr(before))
        extracted.append('\n')
    
    if (file is None) and (highlighter is None):
        highlighter = DEFAULT_TRACE_WRITER_HIGHLIGHTER
    
    render_exception_into(exception, extracted, filter=filter, highlighter=highlighter)
    
    if after is None:
        pass
    elif isinstance(after, str):
        extracted.append(after)
    elif isinstance(after, list):
        for element in after:
            if isinstance(element, str):
                extracted.append(element)
            else:
                extracted.append(repr(element))
                extracted.append('\n')
    else:
        extracted.append(repr(after))
        extracted.append('\n')
    
    if file is None:
        # ignore exception cases
        file = sys.stderr
    
    file.write(''.join(extracted))


@export
def write_exception_async(exception, before=None, after=None, file=None, *, filter=None, highlighter=None, loop=None):
    """
    Writes the given exception's traceback asynchronously.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to render.
    
    before : `None`, `str`, `list` of `str` = `None`, Optional
        Any content, what should go before the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.
    
    after : `None`, `str`, `list` of `str` = `None`, Optional
        Any content, what should go after the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.

    file : `None`, `I/O stream` = `None`, Optional
        The file to print the stack to. Defaults to `sys.stderr`.
    
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
    
    loop : `None`, ``EventThread`` = `None`, Optional (Keyword only)
        The event loop to use.
    
    Returns
    -------
    future : ``Future``
        Returns a future, what can be awaited to wait for the rendering to be done.
    """
    if loop is None:
        loop = get_event_loop()
    
    future = loop.run_in_executor(
        alchemy_incendiary(
            write_exception_sync,
            (exception, before, after, file),
            {'filter': filter, 'highlighter': highlighter},
        )
    )
    assert future.__silence__() is None
    return future


@export
def write_exception_maybe_async(exception, before=None, after=None, file=None, *, filter=None, highlighter=None):
    """
    Writes the given exception's traceback on a blocking thread. If called from an async thread will use an executor.
    If called from a sync thread, will block instead.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to render.
    
    before : `None`, `str`, `list` of `str` = `None`, Optional
        Any content, what should go before the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.
    
    after : `None`, `str`, `list` of `str` = `None`, Optional
        Any content, what should go after the exception's traceback.
        
        If given as `str`, or if `list`, then the last element of it should end with linebreak.

    file : `None`, `I/O stream` = `None`, Optional
        The file to print the stack to. Defaults to `sys.stderr`.
    
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
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        write_exception_async(exception, before, after, file, filter=filter, highlighter=highlighter, loop=local_thread)
    else:
        write_exception_sync(exception, before, after, file, filter=filter, highlighter=highlighter)


DEFAULT_TRACE_WRITER_HIGHLIGHTER = None

@call
def set_default_trace_writer_highlighter():
    """
    Re-sets the default highlighter for trace writer functions.
    """
    global DEFAULT_TRACE_WRITER_HIGHLIGHTER
    
    if PLATFORM != 'linux':
        highlighter = None
    else:
        try:
            get_terminal_size()
        except OSError:
            # If the os not supports this operation, we wont highlight
            highlighter = None
        else:
            highlighter = DEFAULT_ANSI_HIGHLIGHTER
    
    DEFAULT_TRACE_WRITER_HIGHLIGHTER = highlighter


def set_trace_writer_highlighter(highlighter):
    """
    Sets highlighter for trace writer functions.
    
    Parameters
    ----------
    highlighter : `None`, ``HighlightFormatterContext``
        The highlighter to set.
    
    Raises
    ------
    TypeError
        - If `highlighter`'s type is incorrect.
    """
    global DEFAULT_TRACE_WRITER_HIGHLIGHTER
    
    if (highlighter is not None) and (not isinstance(highlighter, HighlightFormatterContext)):
        raise TypeError(
            f'`highlighter` can be `None`, `{HighlightFormatterContext.__name__}, got '
            f'{highlighter.__class__.__name__}; {highlighter!r}'
        )
    
    DEFAULT_TRACE_WRITER_HIGHLIGHTER = highlighter
