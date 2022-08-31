__all__ = (
    'ExceptionWriterContextManager', 'get_default_trace_writer_highlighter', 'render_frames_into_async',
    'render_exception_into_async', 'set_default_trace_writer_highlighter', 'set_trace_writer_highlighter',
    'write_exception_async', 'write_exception_maybe_async', 'write_exception_sync'
)

import sys
from os import get_terminal_size
from sys import _getframe as get_frame, platform as PLATFORM
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
        highlighter = get_default_trace_writer_highlighter()
    
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
    file.flush()


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
    Writes the given exception's traceback on a non-async thread. If called from an async thread will use an executor.
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


_DEFAULT_TRACE_WRITER_HIGHLIGHTER = None


def get_default_trace_writer_highlighter():
    """
    Returns the default highlighter for trace writer functions.
    
    Returns
    -------
    highlighter : `None`, ``HighlightFormatterContext``
    """
    return _DEFAULT_TRACE_WRITER_HIGHLIGHTER


@call
def set_default_trace_writer_highlighter():
    """
    Re-sets the default highlighter for trace writer functions.
    """
    global _DEFAULT_TRACE_WRITER_HIGHLIGHTER
    
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
    
    _DEFAULT_TRACE_WRITER_HIGHLIGHTER = highlighter


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
    global _DEFAULT_TRACE_WRITER_HIGHLIGHTER
    
    if (highlighter is not None) and (not isinstance(highlighter, HighlightFormatterContext)):
        raise TypeError(
            f'`highlighter` can be `None`, `{HighlightFormatterContext.__name__}, got '
            f'{highlighter.__class__.__name__}; {highlighter!r}'
        )
    
    _DEFAULT_TRACE_WRITER_HIGHLIGHTER = highlighter


EXCEPTION_MESSAGE_TITLE_STANDALONE = 'Ignoring occurred exception.\n'
EXCEPTION_MESSAGE_TITLE_BASE = 'Ignoring occurred exception at: '


class ExceptionWriterContextManager:
    """
    Exception catcher which can be used to catch and write occurred exceptions captured by it!
    
    Examples
    --------
    ```py
    from scarletio import catching
    
    def i_raise():
        raise ValueError
    
    with catching(ValueError, location="right here"):
        i_raise()
    ```
    
    Attributes
    ----------
    exclude : `None`, ``BaseException``, `tuple` of `BaseException`
        The exception types to not catch.
        
        > By default ignores `GeneratorExit` if inside of a task.
        
    filter : `None`, `callable`
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
    
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    
    include : `None`, ``BaseException``, `tuple` of `BaseException`
        The exception types to catch.
        
        > By default catches everything.
    
    location : `None`, `str`
        The place where the exception might be occurring.
    
    """
    __slots__ = ('exclude', 'filter', 'highlighter', 'include', 'location')
    
    def __new__(cls, include=None, exclude=None, *, location=None, filter=None, highlighter=None):
        """
        Creates a new exception catcher.
        
        Parameters
        ----------
        include : `None`, ``BaseException``, `tuple` of `BaseException` = `None`, Optional
            The exception types to catch.
            
            > By default allows all exceptions.
        
        exclude : `None`, ``BaseException``, `tuple` of `BaseException` = `None`, Optional 
            The exception types to not catch.
            
            > By default excludes only `GeneratorExit` if inside of a task.
        
        location : `None`, `str` = `None`, Optional (Keyword only)
            The place where the exception might be occurring.
            
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
        self = object.__new__(cls)
        self.exclude = exclude
        self.filter = filter
        self.highlighter = highlighter
        self.include = include
        self.location = location
        return self
    
    
    def __repr__(self):
        """Returns the exception catcher's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        # location
        location = self.location
        if (location is not None):
            repr_parts.append(' location=')
            repr_parts.append(repr(location))
            
            field_added = True
        else:
            field_added = False
        
        # include
        include = self.include
        if (include is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' include=')
            repr_parts.append(repr(include))
        
        # exclude
        exclude = self.exclude
        if (exclude is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' exclude=')
            repr_parts.append(repr(exclude))
        
        # filter
        filter = self.filter
        if (filter is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' filter=')
            repr_parts.append(repr(filter))
        
        # highlighter
        highlighter = self.highlighter
        if (highlighter is not None):
            if field_added:
                repr_parts.append(',')
            
            repr_parts.append(' highlighter=')
            repr_parts.append(repr(highlighter))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __enter__(self):
        """
        Enters the catching block as an synchronous context manager.
        
        Returns
        -------
        self : ``catch`` 
        """
        return self
    
    
    async def __aenter__(self):
        """
        Enters the catching block as an asynchronous context manager.
        
        This method is a coroutine.
        
        Returns
        -------
        self : ``catch`` 
        """
        return self
    
    
    def __exit__(self, exception_type, exception, exception_traceback):
        """
        Exits the context manager.
        
        Parameters
        ----------
        exception_type : `None`, `type<BaseException>`
            The occurred exception's type if any.
        
        exception : `None`, `BaseException`
            The occurred exception if any.
        
        exception_traceback : `None`, `TracebackType`
            the exception's traceback if any.
        
        Returns
        -------
        captured : `bool`
            Whether the exception was captured.
        """
        if not self._should_capture(exception, False):
            return False
        
        write_exception_maybe_async(
            exception,
            before = self._get_location_message(),
            filter = self.filter,
            highlighter = self.highlighter,
        )
        return True
    
    
    async def __aexit__(self, exception_type, exception, exception_traceback):
        """
        Exits the context manager.
        
        Parameters
        ----------
        exception_type : `None`, `type<BaseException>`
            The occurred exception's type if any.
        
        exception : `None`, `BaseException`
            The occurred exception if any.
        
        exception_traceback : `None`, `TracebackType`
            the exception's traceback if any.
        
        Returns
        -------
        captured : `bool`
            Whether the exception was captured.
        """
        if not self._should_capture(exception, True):
            return False
        
        await write_exception_async(
            exception,
            before = self._get_location_message(),
            filter = self.filter,
            highlighter = self.highlighter,
        )
        return True
    
    
    def _should_capture(self, exception, asynchronous):
        """
        Returns whether the given exception should be captured.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            The exception to check.
        asynchronous : `bool`
            Whether we are at an exit of an asynchronous context manager.
        
        Returns
        -------
        should_capture : `bool`
        """
        # If we have no exception we should not capture.
        if exception is None:
            return False
        
        if not asynchronous:
            thread = current_thread()
            if isinstance(thread, EventThread) and (thread.current_task is not None):
                asynchronous = True
            
            else:
                asynchronous = False
        
        if asynchronous:
            # If we are inside of a task, we ignore `GeneratorExit`
            if isinstance(exception, GeneratorExit):
                return False
        
        # If we exclude the exception we should not capture
        exclude = self.exclude
        if (exclude is not None) and isinstance(exception, exclude):
            return False
        
        # If we not include the exception we should not capture.
        include = self.include
        if (include is not None) and (not isinstance(exception, include)):
            return False
        
        return True
    
    
    def _get_location_message(self):
        """
        Creates the location message of the context.
        
        Returns
        -------
        location_message : `str`
        """
        for location_message in self._iter_location_messages():
            if (location_message is not None):
                return location_message
        
        return EXCEPTION_MESSAGE_TITLE_STANDALONE
    
    
    def _iter_location_messages(self):
        """
        Iterates over the location messages.
        
        This method is an iterable generator.
        
        Yields
        ------
        location_message : `None`, `str`
        """
        yield self._create_location_message_from_location()
        yield self._create_location_message_from_task_name()
        yield self._create_location_message_from_tracing()
    
    
    def _create_location_message_from_location(self):
        """
        Creates location message using ``.location``
        
        Returns
        -------
        location_message : `None`, `str`
        """
        location = self.location
        if (location is not None):
            return f'{EXCEPTION_MESSAGE_TITLE_BASE}{location}\n'
    
    
    def _create_location_message_from_task_name(self):
        """
        Creates location message from the current task's qualname.
        
        Returns
        -------
        location_message : `None`, `str`
        """
        thread = current_thread()
        if isinstance(thread, EventThread):
            current_task = thread.current_task
            if (current_task is not None):
                return f'{EXCEPTION_MESSAGE_TITLE_BASE}{current_task.qualname}\n'
    
    
    def _create_location_message_from_tracing():
        """
        Creates location message by tracing back to the first non-local frame.
        
        Returns
        -------
        location_message : `None`, `str`
        """
        frame = get_frame()
        while True:
            if frame is None:
                return
            
            if frame.f_code.co_filename != __file__:
                break
            
            frame = frame.f_back
            continue
        
        return EXCEPTION_MESSAGE_TITLE_BASE + frame.f_code.co_name
