__all__ = ('run_asynchronous_interactive_console',)

import sys, warnings
from functools import partial as partial_func
from math import floor, log
from types import FunctionType

from ...core import (
    Future, get_default_trace_writer_highlighter, get_event_loop, get_or_create_event_loop, write_exception_sync
)
from ...utils import HIGHLIGHT_TOKEN_TYPES, is_awaitable, render_exception_into
from ...utils.trace.exception_representation import ExceptionRepresentationSyntaxError
from ...utils.trace.exception_representation.syntax_error_helpers import (
    fixup_syntax_error_line_from_buffer, is_syntax_error
)
from ...utils.trace.rendering import _render_exception_representation_syntax_error_into

from .auto_completer import AutoCompleter
from .console_helpers import create_banner, create_exit_message
from .editors import EditorAdvanced, EditorBase, EditorSimple, can_use_advanced_editor
from .history import History


def _ignore_console_frames(frame):
    """
    Ignores the frames of the asynchronous console.
    
    Parameters
    ----------
    frame : ``FrameProxyBase``
        The frame to check.
    
    Returns
    -------
    should_show_frame : `bool`
        Whether the frame should be shown.
    """
    should_show_frame = True
    
    file_name = frame.file_name
    name = frame.name
    line = frame.line
    
    if file_name == __file__:
        if name == 'run_code_callback':
            if line == 'coroutine = function()':
                should_show_frame = False
        
        elif name == 'run_code':
            if line == 'result = future.sync_wrap().wait()':
                should_show_frame = False
            
            elif line == 'result = sync_wrapper.wait()':
                should_show_frame = False
    
    return should_show_frame


def run_code_callback(console, future, code):
    """
    Ensures the given `code` object on the event loop if awaitable. If not runs it instantly.
    
    Parameters
    ----------
    console : ``AsynchronousInteractiveConsole``
        The respective interactive console.
    future : ``Future``
        Future to set it's result.
    code : ``CodeType``
        The code to run.
    """
    function = FunctionType(code, console.local_variables)
    try:
        coroutine = function()
    except BaseException as err:
        future.set_result_if_pending((True, err))
        return
    
    if not is_awaitable(coroutine):
        future.set_result_if_pending((False, coroutine))
        return
    
    try:
        task = console.loop.ensure_future(coroutine)
    except BaseException as err:
        future.set_result_if_pending((True, err))
    else:
        console.task = task
        future.set_result_if_pending((False, None))


class AsynchronousInteractiveConsole:
    """
    Asynchronous interactive console.
    
    Attributes
    ----------
    _console_id : `int`
        The console's identifier.
    _file_name : `None`, `str`
        cached file name.
    _input_id : `int`
        Incremental value to update the file name of the input for each input chunk.
    banner : `str`
        banner shown when the console is started.
    editor_type : `type<EditorBase>`
        The specific editor type to use when inputting a expression.
    exit_message : `str`
        Message shown when the console is exited.
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    history : ``History``
        History used for caching inputs.
    local_variables : `dict` of (`str`, `object`) items
        Variables to run the compiled code with.
    loop : ``EventThread``
        The event loop on which the console runs it's code.
    stop_on_interruption : `bool`
        Whether the console should be stopped on keyboard interrupt.
    task : `None`, ``Future``
        Asynchronous task running on the event loop on what's result the console is waiting for.
    """
    _console_counter = 0
    
    __slots__ = (
        '_console_id', '_file_name', '_input_id', 'banner', 'editor_type', 'exit_message', 'highlighter', 'history',
        'local_variables', 'loop', 'stop_on_interruption', 'task',
    )
    
    def __new__(
        cls,
        *,
        banner = None,
        editor_type = None,
        event_loop = None,
        exit_message = None,
        highlighter = None,
        local_variables = None,
        stop_on_interruption = False,
    ):
        """
        Creates a new async interactive console.
        
        Parameters
        ----------
        banner : `None`, `str` = `None`, Optional (Keyword only)
            Interactive console banner.
            
        editor_type : `type<EditorBase>`
            The specific editor type to use when inputting a expression.
            
        event_loop : `None`, ``EventThread`` = `None`, Optional (Keyword only)
                The event loop to run the executed code on.
        
        exit_message : `None`, `str` = `None`, Optional (Keyword only)
            Interactive console exit message.
        
        highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
            Formatter storing highlighting details.
        
        local_variables : `None`, `dict` of (`str`, `object`) items = `None`, Optional (Keyword only)
            Initial local variables for the executed code inside of the console.
        
        stop_on_interruption : `bool` = `False`, Optional (Keyword only)
            Whether the console should be stopped on keyboard interrupt.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        RuntimeError
            - If there are no event loops.
        """
        if event_loop is None:
            event_loop = get_event_loop()
        
        if editor_type is None:
            if can_use_advanced_editor():
                editor_type = EditorAdvanced
            
            else:
                editor_type = EditorSimple
        
        else:
            if (not isinstance(editor_type, type)) or (not issubclass(editor_type, EditorBase)):
                raise TypeError(
                    f'`editor_type` can be `None`, `{EditorBase.__name__}` subclass, got '
                    f'{editor_type.__class__.__name__}; {editor_type!r}.'
                )
        
        if exit_message is None:
            exit_message = create_exit_message()
        
        if highlighter is None:
            highlighter = get_default_trace_writer_highlighter()
        
        if banner is None:
            banner = create_banner(highlighter = highlighter)
        
        if local_variables is None:
            local_variables = {}
        
        local_variables.setdefault('__builtins__', __builtins__)
        
        console_id = cls._console_counter + 1
        cls._console_counter = console_id
        
        history = History()
        
        self = object.__new__(cls)
        
        self._console_id = console_id
        self._file_name = None
        self._input_id = 0
        self.banner = banner
        self.editor_type = editor_type
        self.exit_message = exit_message
        self.highlighter = highlighter
        self.history = history
        self.local_variables = local_variables
        self.loop = event_loop
        self.stop_on_interruption = stop_on_interruption
        self.task = None
        
        return self
    
    
    def run_code(self, compiled_code):
        """
        Runs the given code object on the respective event loop.
        
        Parameters
        ----------
        compiled_code : ``CodeType``
            The code to run.
        
        Returns
        -------
        result : `object`
            The value returned by the ran code.
        
        Raises
        ------
        SystemExit
        """
        future = Future(self.loop)
        
        self.loop.call_soon_thread_safe(partial_func(run_code_callback, self, future, compiled_code))
        
        try:
            is_exception, result = future.sync_wrap().wait()
            future = None
            
            if is_exception:
                write_exception_sync(
                    result, file = sys.stdout, filter = _ignore_console_frames, highlighter = self.highlighter
                )
                return None
            
            task = self.task
            if (task is None):
                return result
            
            sync_wrapper = task.sync_wrap()
            task = None
            
            try:
                result = sync_wrapper.wait()
            except:
                # Cancel the sync wrapper if exception occurs. This will stop warnings.
                sync_wrapper.cancel()
                raise
            
            else:
                return result
        
        except BaseException as err:
            if (future is not None):
                if (not future.is_done()):
                    future.cancel()
            
            task = self.task
            if (task is not None) and (not task.is_done()):
                task.cancel()
                task = None
            
            if isinstance(err, SystemExit):
                raise
            
            write_exception_sync(
                err, file = sys.stdout, filter = _ignore_console_frames, highlighter = self.highlighter
            )
            
            if isinstance(err, KeyboardInterrupt):
                if self.stop_on_interruption:
                    sys.stdout.write('[Interrupt again to exit]\n')
        
        finally:
            self.task = None
            sys.stdout.flush()
    
    
    def raw_input(self, prefix):
        """
        Inputs from console with the given prompt.
        
        Parameters
        ----------
        prefix : `str`
            Prefix to start the line with.
        
        Returns
        -------
        input_value : `str`
        
        Raises
        ------
        BaseException
        """
        try:
            return input(prefix)
        except KeyboardInterrupt:
            if self.stop_on_interruption:
                sys.stdout.write('\n')
                sys.stdout.flush()
                raise SystemExit() from None
            
            raise
    
    
    def get_file_name(self):
        """
        Returns the file name of the current line.
        
        Returns
        -------
        file_name : `str`
        """
        file_name = self._file_name
        if (file_name is None):
            file_name = self._create_file_name()
            self._file_name = file_name
        
        return file_name
    
    
    def _create_file_name(self):
        """
        Creates the current file name of the console.
        
        Returns
        -------
        file_name : `str`
        """
        file_name_parts = ['<console']
        
        console_id = self._console_id
        if self._console_counter > console_id:
            file_name_parts.append('[')
            file_name_parts.append(str(console_id))
            file_name_parts.append(']')
        
        file_name_parts.append(' in[')
        file_name_parts.append(str(self._input_id))
        file_name_parts.append(']>')
        return ''.join(file_name_parts)
    
    
    def increment_input_counter(self):
        """
        Increments the console's input counter.
        """
        self._input_id += 1
        self._file_name = None
    
    
    def get_prefix_initial(self):
        """
        Returns the console's current initial prefix.
        
        Returns
        -------
        prefix_initial : `str`
        """
        marker = f'In [{self._input_id}]'
        prefix = ':'
        
        highlighter = self.highlighter
        if (highlighter is not None):
            marker = highlighter.highlight_as(
                marker, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_MARKER_IN_INITIAL
            )
            
            prefix = highlighter.highlight_as(
                prefix, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_MARKER_PREFIX_INITIAL
            )
        
        return f'{marker}{prefix} '
    
    
    def get_prefix_length(self):
        """
        Returns the console's current prefix's length.
        
        Returns
        -------
        prefix_length : `int`
        """
        input_id = self._input_id
        if input_id == 0:
            input_id_representation_length = 1
        else:
            input_id_representation_length = 1 + floor(log(input_id, 10))
        
        return input_id_representation_length + 7
    
    
    def get_prefix_continuous(self):
        """
        Returns the console's current continuous prefix.
        
        Returns
        -------
        continuous_prefix : `str`
        """
        marker_length = self.get_prefix_length() - 5
        
        indention = ' ' * marker_length
        marker = '...'
        prefix = ':'
        
        highlighter = self.highlighter
        if (highlighter is not None):
            marker = highlighter.highlight_as(
                marker, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_MARKER_IN_CONTINUOUS
            )
            
            prefix = highlighter.highlight_as(
                prefix, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_MARKER_PREFIX_CONTINUOUS
            )
        
        return f'{indention}{marker}{prefix} '
    
    
    def interact(self):
        """
        Emulates python interactive console.
        """
        sys.stdout.write(self.banner)
        sys.stdout.flush()
        editor = None
        
        while True:
            try:
                editor = self.editor_type(
                    None,
                    self.get_file_name(),
                    self.get_prefix_initial(),
                    self.get_prefix_continuous(),
                    self.get_prefix_length(),
                    self.highlighter,
                    self.history,
                    AutoCompleter(self.local_variables),
                )
                
                compiled_code = editor()
                if (compiled_code is not None):
                    self.run_code(compiled_code)
            
            except SyntaxError as err:
                self.history.maybe_add_buffer_of(self._input_id, editor)
                self.increment_input_counter()
                
                self.show_syntax_error(err, editor)
            
            except KeyboardInterrupt as err:
                self.history.maybe_add_buffer_of(self._input_id, editor)
                self.increment_input_counter()
                
                if self.stop_on_interruption:
                    if (editor is None) or editor.is_empty():
                        raise SystemExit() from err
                    
                    sys.stdout.write('\nKeyboardInterrupt [Interrupt again to exit]\n')
                    sys.stdout.flush()
                else:
                    sys.stdout.write('\nKeyboardInterrupt\n')
                    sys.stdout.flush()
            
            else:
                self.history.maybe_add_buffer_of(self._input_id, editor)
                self.increment_input_counter()
            
            finally:
                editor = None
        
        
        exit_message = self.exit_message
        sys.stdout.write(exit_message)
        if not exit_message.endswith('\n'):
            sys.stdout.write('\n')
        sys.stdout.flush()
    
    
    def show_syntax_error(self, syntax_error, editor):
        """
        Shows the given syntax error.
        
        Parameters
        ----------
        syntax_error : `SyntaxError`, `OverflowError`, `ValueError`
            The syntax error, or other derping to show.
        editor : `None`, ``EditorBase``
            The respective editor.
        """
        into = []
        
        if is_syntax_error(syntax_error):
            # message, (old_file_name, *additional_details) = syntax_error.args
            # syntax_error.args = (message, (self.get_file_name(), *additional_details))
            
            if (editor is not None):
                fixup_syntax_error_line_from_buffer(syntax_error, editor.get_buffer())
            
            _render_exception_representation_syntax_error_into(
                ExceptionRepresentationSyntaxError(syntax_error, None), into, self.highlighter
            )
        else:
            render_exception_into(syntax_error, into, filter = _ignore_console_frames, highlighter = self.highlighter)
        
        sys.stdout.write(''.join(into))
        sys.stdout.flush()


def run_asynchronous_interactive_console(
    local_variables = None,
    *,
    banner = None,
    callback = None,
    exit_message = None,
    highlighter = None,
    stop_event_loop_when_done = True,
    stop_on_interruption = False,
):
    """
    Runs asynchronous interactive console.
    
    Parameters
    ----------
    local_variables : `None`, `dict` of (`str`, `object`) items = `None`, Optional
        Local variables to start the console with.
    
    banner : `None`, `str` = `None`, Optional (Keyword only)
        Interactive console banner.
    
    callback : `None`, `FunctionType` = `None`, Optional (Keyword only)
        Callback to run when execution the console is closed.
        
        > This runs before the event loop is shut down!
    
    exit_message : `None`, `str` = `None`, Optional (Keyword only)
        Interactive console exit message.
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    stop_event_loop_when_done : `bool` = `True`, Optional (Keyword only)
        Whether the event loop should be closed when the console is closed.
    
    stop_on_interruption : `bool` = `False`, Optional (Keyword only)
        Whether the console should be stopped on keyboard interrupt.
    """
    event_loop = get_or_create_event_loop(daemon = False)
    
    console = AsynchronousInteractiveConsole(
        banner = banner,
        event_loop = event_loop,
        exit_message = exit_message,
        highlighter = highlighter,
        local_variables = local_variables,
        stop_on_interruption = stop_on_interruption,
    )
    
    try:
        console.interact()
    finally:
        try:
            if (callback is not None):
                callback()
            
        finally:
            if stop_event_loop_when_done:
                warnings.filterwarnings(
                    'ignore',
                    message = '^coroutine .* was never awaited$',
                    category = RuntimeWarning,
                )
                
                event_loop.stop()
