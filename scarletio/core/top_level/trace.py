__all__ = (
    'ExceptionWriterContextManager', 'get_default_trace_writer_highlighter', 'render_frames_into_async',
    'render_exception_into_async', 'set_default_trace_writer_highlighter', 'set_trace_writer_highlighter',
    'write_exception_async', 'write_exception_maybe_async', 'write_exception_sync'
)

import sys, threading
from os import get_terminal_size
from sys import _getframe as get_frame, platform as PLATFORM
from threading import current_thread, get_ident

from ...utils import (
    DEFAULT_ANSI_HIGHLIGHTER, HIGHLIGHT_TOKEN_TYPES, HighlightFormatterContext, alchemy_incendiary, call, export,
    include, render_exception_into, render_frames_into
)
from ...utils.trace.rendering import _add_typed_part_into

from .event_loop import get_event_loop


EventThread = include('EventThread')


async def render_frames_into_async(frames, extend = None, *, filter = None, highlighter = None, loop = None):
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


async def render_exception_into_async(exception, extend = None, *, filter = None, highlighter = None, loop = None):
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


def _build_additional_title(title):
    """
    Builds additional title represented by `before` and `after` parameters of ``write_exception_sync``.
    
    Parameters
    ----------
    title : `str`, `list` of `str`
        The title to put before or after an exception traceback.
    
    Returns
    -------
    built_title : `None`, `str`
    """
    if title is None:
        return None
    
    if isinstance(title, str):
        return _build_additional_title_str(title)
    
    if isinstance(title, list):
        return _build_additional_title_list(title)
    
    return _build_additional_title_object(title)


def _build_additional_title_str(title):
    """
    Builds additional title represented by `before` and `after` parameters of ``write_exception_sync``.
    
    > This function is a type specific version called by ``_build_additional_title``.
    
    Parameters
    ----------
    title : `str`
        The title to put before or after an exception traceback.
    
    Returns
    -------
    built_title : `None`, `str`
    """
    if not title:
        return None
    
    if title.endswith('\n'):
        return title
        
    return title + '\n'


def _build_additional_title_list(title_parts):
    """
    Builds additional title represented by `before` and `after` parameters of ``write_exception_sync``.
    
    > This function is a type specific version called by ``_build_additional_title``.
    
    Parameters
    ----------
    title_parts : `list` of `str`
        The title to put before or after an exception traceback.
    
    Returns
    -------
    built_title : `None`, `str`
    """
    title_elements = []
    
    for element in title_parts:
        if not isinstance(element, str):
            element = repr(element)
        
        if element:
            title_elements.append(element)
    
    if not title_elements:
        return None
    
    if not title_elements[-1].endswith('\n'):
        title_elements.append('\n')
    
    return ''.join(title_elements)


def _build_additional_title_object(title_object):
    """
    Builds additional title represented by `before` and `after` parameters of ``write_exception_sync``.
    
    > This function is a type specific version called by ``_build_additional_title``.
    
    Parameters
    ----------
    title_object : `object`
        The title to put before or after an exception traceback.
    
    Returns
    -------
    built_title : `None`, `str`
    """
    return _build_additional_title_str(repr(title_object))


def write_exception_sync(exception, before = None, after = None, file = None, *, filter = None, highlighter = None):
    """
    Writes the given exception's traceback.
    
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
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    """
    before = _build_additional_title(before)
    after = _build_additional_title(after)
    
    if (file is None) and (highlighter is None):
        highlighter = get_default_trace_writer_highlighter()
    
    extend = []
    
    if (before is not None):
        _add_typed_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_BEFORE,
            before,
            extend,
            highlighter,
        )
    
    render_exception_into(exception, extend, filter = filter, highlighter = highlighter)
    
    if (after is not None):
        _add_typed_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_AFTER,
            after,
            extend,
            highlighter,
        )
    
    if file is None:
        # ignore exception cases
        file = sys.stderr
        
        # On shutdown `sys.stderr` can be set to `None`
        if (file is None):
            return
    
    file.write(''.join(extend))
    file.flush()


@export
def write_exception_async(
    exception, before = None, after = None, file = None, *, filter = None, highlighter = None, loop = None
):
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
    future.silence()
    return future


@export
def write_exception_maybe_async(
    exception, before = None, after = None, file = None, *, filter = None, highlighter = None
):
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
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    """
    local_thread = current_thread()
    if isinstance(local_thread, EventThread):
        write_exception_async(
            exception, before, after, file, filter = filter, highlighter = highlighter, loop = local_thread
        )
    else:
        write_exception_sync(exception, before, after, file, filter = filter, highlighter = highlighter)


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
    
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    
    include : `None`, ``BaseException``, `tuple` of `BaseException`
        The exception types to catch.
        
        > By default catches everything.
    
    location : `None`, `str`
        The place where the exception might be occurring.
    
    """
    __slots__ = ('exclude', 'filter', 'highlighter', 'include', 'location')
    
    def __new__(cls, include = None, exclude = None, *, location = None, filter = None, highlighter = None):
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
            repr_parts.append(' location = ')
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
            
            repr_parts.append(' include = ')
            repr_parts.append(repr(include))
        
        # exclude
        exclude = self.exclude
        if (exclude is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' exclude = ')
            repr_parts.append(repr(exclude))
        
        # filter
        filter = self.filter
        if (filter is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' filter = ')
            repr_parts.append(repr(filter))
        
        # highlighter
        highlighter = self.highlighter
        if (highlighter is not None):
            if field_added:
                repr_parts.append(',')
            
            repr_parts.append(' highlighter = ')
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
    
    
    def _create_location_message_from_tracing(self):
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


# Blackmagic

def __system_exception_hook__(exception_type, exception, exception_traceback):
    """
    Displays the given exception. Used to replace the system default.

    Parameters
    ----------
    exception_type : `None`, `type<BaseException>`
        The occurred exception's type if any.
    
    exception : `None`, `BaseException`
        The occurred exception if any.
    
    exception_traceback : `None`, `TracebackType`
        the exception's traceback if any.
    """
    if (exception is not None):
        write_exception_sync(exception)


def __threading_exception_hook__(threading_exception_hook_parameters):
    """
    Displays the given exception. Used to replace threading default.
    
    Parameters
    ----------
    threading_exception_hook_parameters : `tuple`
        Threading exception hook parameters, which are:
        - exception_type
        - exception
        - exception_traceback
        - thread
    """
    exception_type, exception, exception_traceback, thread = threading_exception_hook_parameters
    if (exception is not None):
        if thread is None:
            thread_name = str(get_ident())
        else:
            thread_name = thread.name
        
        write_exception_sync(exception, before = f'Exception in thread: {thread_name}\n')


@call
def set_exception_hooks():
    """
    Replaces python's exception hooks.
    """
    attribute_name = f'{"except"}{"hook"}' # We do this, so we do not get typo error
    
    setattr(sys, attribute_name, __system_exception_hook__)
    setattr(threading, attribute_name, __threading_exception_hook__)
