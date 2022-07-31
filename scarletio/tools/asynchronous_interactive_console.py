__all__ = (
    'collect_package_local_variables', 'create_banner', 'create_exit_message', 'run_asynchronous_interactive_console'
)

import sys, warnings
from code import InteractiveConsole
from functools import partial as partial_func
from types import FunctionType

from .. import __package__ as PACKAGE_NAME
from ..core import Future, create_event_loop, get_default_trace_writer_highlighter, get_event_loop
from ..utils import HIGHLIGHT_TOKEN_TYPES, is_awaitable, render_exception_into
from ..utils.trace import (
    CONSOLE_LINE_CACHE, _render_syntax_error_representation_into, _iter_highlight_producer, is_syntax_error
)

try:
    import readline
except ImportError:
    pass

PACKAGE = __import__(PACKAGE_NAME)

# On python3.6 not present?
try:
    from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
except ImportError:
    PyCF_ALLOW_TOP_LEVEL_AWAIT = 1 << 13
    AWAIT_AVAILABLE = False
else:
    AWAIT_AVAILABLE = True


if AWAIT_AVAILABLE:
    AWAIT_NOTE = 'Use "await" directly.'
else:
    AWAIT_NOTE = '!!! Direct "await" is not available on your python version. Please use python 3.8 or newer !!!'


def get_or_create_event_loop():
    """
    Tries to get the current event loop. If not found creates a new one.
    
    Returns
    -------
    event_loop : ``EventThread``
    """
    try:
        event_loop = get_event_loop()
    except RuntimeError:
        event_loop = create_event_loop(daemon=False)
    
    return event_loop


LOGO_SEPARATOR = '\n\n'


def _produce_banner(package, logo):
    """
    Produces banner parts with their tokens.
    
    This method is an iterable generator.
    
    Yields
    ------
    part : `str`
        Banner part.
    token_type : `int`
        The part's type.
    """
    if package is None:
        package = PACKAGE
    
    if (logo is None) and (package is PACKAGE):
        logo = (
            f'                     _      _   _\n'
            f'                    | |    | | (_)\n'
            f'  ___  ___ __ _ _ __| | ___| |_ _  ___\n'
            f' / __|/ __/ _` | \'__| |/ _ \ __| |/ _ \\\n'
            f' \__ \ (_| (_| | |  | |  __/ |_| | (_) |\n'
            f' |___/\___\__,_|_|  |_|\___|\__|_|\___/\n'
        )
    
    
    if (logo is not None):
        yield logo, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_LOGO
        
        if (package is not None):
            yield '\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
            
            
            logo_length = max((len(line) for line in logo.splitlines()), default=0)
            package_version = package.__version__
            package_version_length = len(package_version)
            
            adjust = logo_length - package_version_length
            if adjust > 0:
                yield ' ' * adjust, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
            
            yield package_version, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_LOGO_VERSION
            yield '\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
            
        yield '\n\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
    
    # At cpython it has a ` \n` in it, but in pypy we have just a `\n`.
    system_version = ' '.join(sys.version.split())
    
    # get package name and upper case it's first character
    package_name = package.__package__
    if package_name and not package_name[0].isupper():
        package_name = package_name[0].upper() + package_name[1:]
    
    console_description = f'{package_name} interactive console {system_version} on {sys.platform}.\n'
    yield console_description, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION
    
    if AWAIT_AVAILABLE:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT
    else:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE
    
    yield AWAIT_NOTE, await_token_type
    
    console_help ='\nType "help", "copyright", "credits" or "license" for more information.'
    yield console_help, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION


def create_banner(package=None, logo=None, *, highlighter=None):
    """
    helper creating console banner.
    
    Parameters
    ----------
    package : `None`, `ModuleType` = `None`, Optional
        The package, which runs the interactive console.
    
    logo : `None`, `str` = `None`, Optional
        The logo of the package if any.
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Formatter storing highlighting details.
    
    Returns
    -------
    banner : `str`
        Console banner.
    """
    return ''.join([*_iter_highlight_producer(_produce_banner(package, logo), highlighter)])


def create_exit_message(package=None):
    """
    helper creating console exit message.
    
    Parameters
    ----------
    package : `None`, `ModuleType` = `None`, Optional
        The package, which runs the interactive console.
    
    Returns
    -------
    exit_message : `str`
        Console exit message.
    """
    if package is None:
        package = PACKAGE
    
    return f'exiting {package.__package__} interactive_console...'


def collect_package_local_variables(package):
    """
    Collects importable variables of scarletio.
    
    Parameters
    ----------
    package : `ModuleType`
        The package to collect variables from.
    
    Returns
    -------
    interactive_console_locals : `dict` of (`str`, `Any`) items
    """
    interactive_console_locals = {package.__package__: package}
    for variable_name in {
        '__name__',
        '__package__',
        '__loader__',
        '__spec__',
        '__builtins__',
        '__file__'
    }:
        interactive_console_locals[variable_name] = getattr(package, variable_name)
    
    for variable_name in getattr(package, '__all__', ()):
        interactive_console_locals[variable_name] = getattr(package, variable_name)
    
    return interactive_console_locals


def run_code_callback(console, code):
    """
    Ensures the given `code` object on the event loop if awaitable. If not runs it instantly.
    
    Parameters
    ----------
    console : ``AsynchronousInteractiveConsole``
        The respective interactive console.
    code : ``CodeType``
        The code to run.
    """
    function = FunctionType(code, console.locals)
    try:
        coroutine = function()
    except BaseException as err:
        console.future.set_exception(err)
        return
    
    if not is_awaitable(coroutine):
        console.future.set_result(coroutine)
        return
    
    try:
        task = console.loop.ensure_future(coroutine)
    except BaseException as err:
        console.future.set_exception(err)
    else:
        console.future.set_result(None)
        console.task = task


def _ignore_console_frames(file_name, name, line_number, line):
    """
    Ignores the frames of the asynchronous console.
    
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
    should_show_frame : `bool`
        Whether the frame should be shown.
    """
    should_show_frame = True
    
    if file_name == __file__:
        if name == 'run_code_callback':
            if line == 'coroutine = function()':
                should_show_frame = False
        
        elif name == 'run_code':
            if line == 'result = self.future.sync_wrap().wait()':
                should_show_frame = False
    
    return should_show_frame


class AsynchronousInteractiveConsole(InteractiveConsole):
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
    future : `None`, ``Future``
        Used to forward the result of an executed code from the event loop to the console.
    highlighter : `None`, ``HighlightFormatterContext``
        Formatter storing highlighting details.
    loop : ``EventThread``
        The event loop on which the console runs it's code.
    stop_on_interruption : `bool`
        Whether the console should be stopped on keyboard interrupt.
    task : `None`, ``Future``
        Asynchronous task running on the event loop on what's result the console is waiting for.
    """
    _console_counter = 0
    
    def __init__(self, local_variables, event_loop, *, highlighter=None, stop_on_interruption=False):
        """
        Creates a new async interactive console.
        
        Parameters
        ----------
        local_variables : `dict` of (`str`, `Any`) items
            Initial local variables for the executed code inside of the console.
        
        event_loop : ``EventThread``
            The event loop to run the executed code on.
        
        highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
            Formatter storing highlighting details.
        
        stop_on_interruption : `bool` = `False`, Optional (Keyword only)
            Whether the console should be stopped on keyboard interrupt.
        """
        InteractiveConsole.__init__(self, local_variables)
        self.compile.compiler.flags |= PyCF_ALLOW_TOP_LEVEL_AWAIT
        
        self.future = None
        self.highlighter = highlighter
        self.task = None
        self.loop = event_loop
        self.stop_on_interruption = stop_on_interruption
        
        self._input_id = 0
        self._file_name = None
        
        console_id = type(self)._console_counter + 1
        type(self)._console_counter = console_id
        self._console_id = console_id
    
    
    # Disable badly named functions. No-one loves them.
    runcode = NotImplemented
    showsyntaxerror = NotImplemented
    runsource = NotImplemented
    
    
    def run_code(self, code):
        """
        Runs the given code object on the respective event loop.
        
        Parameters
        ----------
        code : ``CodeType``
            The code to run.
        
        Returns
        -------
        result : `Any`
            The value returned by the ran code.
        
        Raises
        ------
        SystemExit
        """
        self.future = Future(self.loop)
        self.interrupted = False
        
        self.loop.call_soon_thread_safe(partial_func(run_code_callback, self, code))
        
        try:
            result = self.future.sync_wrap().wait()
            
            task = self.task
            if (task is not None):
                
                sync_wrapper = task.sync_wrap()
                task = None
                
                try:
                    result = sync_wrapper.wait()
                except:
                    # Cancel the sync wrapper if exception occurs. This will stop warnings.
                    sync_wrapper.cancel()
                    raise
        
        except BaseException as err:
            future = self.future
            if (not future.is_done()):
                future.cancel()
            
            task = self.task
            if (task is not None) and (not task.is_done()):
                task.cancel()
                task = None
            
            if isinstance(err, SystemExit):
                raise
            
            sys.stdout.write(
                ''.join(
                    render_exception_into(err, [], filter=_ignore_console_frames, highlighter=self.highlighter)
                )
            )
            
            if isinstance(err, KeyboardInterrupt):
                if self.stop_on_interruption:
                    raise SystemExit() from None
        
        else:
            return result
        
        finally:
            self.task = None
    
    
    def raw_input(self, prompt=""):
        """
        Inputs from console with the given prompt.
        
        Parameters
        ----------
        prompt : `str`
            Prefix to start the line with.
        
        Returns
        -------
        input_value : `str`
        
        Raises
        ------
        BaseException
        """
        try:
            return input(prompt)
        except KeyboardInterrupt:
            if self.stop_on_interruption:
                self.write('\n')
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
            file_name_parts.append(':')
            file_name_parts.append(str(console_id))
        
        file_name_parts.append(' in:')
        file_name_parts.append(str(self._input_id))
        file_name_parts.append('>')
        return ''.join(file_name_parts)
    
    
    def increment_input_counter(self):
        """
        Increments the console's input counter.
        """
        self._input_id += 1
        self._file_name = None
    
    
    def run_source(self, source):
        """
        Compiles and runs the given source in the console.
        
        Parameters
        ----------
        source : `str`
            The source code to run.
        
        Returns
        -------
        ran : `bool`
            Whether code was ran. 
        """
        file_name = self.get_file_name()
        
        try:
            code = self.compile(source, file_name)
        except (OverflowError, SyntaxError, ValueError) as syntax_error:
            self.show_syntax_error(syntax_error, file_name)
            ran = True
        
        else:
            if code is None:
                ran = False
            
            else:
                CONSOLE_LINE_CACHE.feed(file_name, source)
                self.run_code(code)
                ran = True
        
        if ran:
            self.increment_input_counter()
        
        return ran
    
    
    def push(self, line):
        """
        Pushes a line to the interpreter.
        
        Parameters
        ----------
        line : `bool`
            the line to push.
        
        Returns
        -------
        not_ran : `bool`
            Whether any code was not ran.
            
            If no code was ran, should continue inputting.
        """
        self.buffer.append(line)
        source = '\n'.join(self.buffer)
        
        ran = self.run_source(source)
        if ran:
            self.resetbuffer()
        
        return not ran
    
    
    def show_syntax_error(self, syntax_error, file_name):
        """
        Shows the given syntax error.
        
        Parameters
        ----------
        syntax_error : `SyntaxError`, `OverflowError`, `ValueError`
            The syntax error, or other derping to show.
        
        file_name : `str`
            The file name to use when displaying the output.
        """
        into = []
        
        if is_syntax_error(syntax_error):
            message, (old_file_name, *additional_details) = syntax_error.args
            syntax_error.args = (message, (file_name, *additional_details))
            
            _render_syntax_error_representation_into(syntax_error, into, self.highlighter)
            into.append('\n')
        else:
            render_exception_into(syntax_error, into, filter=_ignore_console_frames, highlighter=self.highlighter)
        
        sys.stdout.write(''.join(into))


def run_asynchronous_interactive_console(
    interactive_console_locals = None,
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
    interactive_console_locals : `None`, `dict` of (`str`, `Any`) items = `None`, Optional
        Parameters to start the console with.
    
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
    if interactive_console_locals is None:
        interactive_console_locals = {}
    
    if highlighter is None:
        highlighter = get_default_trace_writer_highlighter()
    
    if banner is None:
        banner = create_banner(highlighter=highlighter)
    
    if exit_message is None:
        exit_message = create_exit_message()
    
    event_loop = get_or_create_event_loop()
    
    console = AsynchronousInteractiveConsole(
        interactive_console_locals,
        event_loop,
        highlighter = highlighter,
        stop_on_interruption = stop_on_interruption,
    )
    
    try:
        console.interact(
            banner = banner,
            exitmsg = exit_message,
        )
    finally:
        try:
            if (callback is not None):
                callback()
            
        finally:
            if stop_event_loop_when_done:
                warnings.filterwarnings(
                    'ignore',
                    message = r'^coroutine .* was never awaited$',
                    category = RuntimeWarning,
                )
                
                event_loop.stop()
