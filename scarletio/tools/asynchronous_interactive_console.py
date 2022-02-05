__all__ = (
    'collect_package_local_variables', 'create_banner', 'create_exit_message', 'run_asynchronous_interactive_console'
)

import sys, warnings
from code import InteractiveConsole
from functools import partial as partial_func
from types import FunctionType

from .. import __package__ as PACKAGE_NAME
from ..core import Future, create_event_loop, get_event_loop
from ..utils import is_awaitable


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
    AWAIT_NOTE = 'Use \'await\' directly.'
else:
    AWAIT_NOTE = '!!! Direct \'await\' is not available on your python version. Please use python 3.8 or newer !!!'


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

def create_banner(package=None, logo=None):
    """
    helper creating console banner.
    
    Parameters
    ----------
    package : `None`, `ModuleType` = `None`, Optional
        The package, which runs the interactive console.
    logo : `None`, `str` = `None`, Optional
        The logo of the package if any.
    
    Returns
    -------
    banner : `str`
        Console banner.
    """
    if package is None:
        package = PACKAGE
    
    if (logo is None) and (package is PACKAGE):
        logo = (
            f'                     _      _   _       \n'
            f'                    | |    | | (_)      \n'
            f'  ___  ___ __ _ _ __| | ___| |_ _  ___  \n'
            f' / __|/ __/ _` | \'__| |/ _ \ __| |/ _ \ \n'
            f' \__ \ (_| (_| | |  | |  __/ |_| | (_) |\n'
            f' |___/\___\__,_|_|  |_|\___|\__|_|\___/ \n'
            f'                                        \n'
            f'{package.__version__:>40}\n'
        )
    
    return (
        f'{"" if (logo is None) else logo}{"" if (logo is None) else LOGO_SEPARATOR}'
        f'{package.__package__} interactive console {sys.version} on {sys.platform}.\n'
        f'{AWAIT_NOTE}\n'
        f'Type \'help\', \'copyright\', \'credits\' or \'license\' for more information.'
    )


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
        if isinstance(err, KeyboardInterrupt):
            console.interrupted = True
        
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


class AsynchronousInteractiveConsole(InteractiveConsole):
    """
    Asynchronous interactive console.
    
    Attributes
    ----------
    future : `None`, ``Future``
        Used to forward the result of an executed code from the event loop to the console.
    interrupted : `bool`
        Whether the console is interrupted.
    loop : ``EventThread``
        The event loop on which the console runs it's code.
    task : `None`, ``Future``
        Asynchronous task running on the event loop on what's result the console is waiting for.
    """
    def __init__(self, local_variables, event_loop):
        """
        Creates a new async interactive console.
        
        Parameters
        ----------
        local_variables : `dict` of (`str`, `Any`) items
            Initial local variables for the executed code inside of the console.
        event_loop : ``EventThread``
            The event loop to run the executed code on.
        """
        InteractiveConsole.__init__(self, local_variables)
        self.compile.compiler.flags |= PyCF_ALLOW_TOP_LEVEL_AWAIT
        
        self.future = None
        self.interrupted = False
        self.task = None
        self.loop = event_loop
    
    
    def runcode(self, code):
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
        self.task = None
        
        self.loop.call_soon_thread_safe(partial_func(run_code_callback, self, code))
        
        try:
            result = self.future.sync_wrap().wait()
            
            task = self.task
            if (task is not None):
                result = task.sync_wrap().wait()
        
        except BaseException as err:
            future = self.future
            if (not future.is_done()):
                future.cancel()
            
            task = self.task
            if (task is not None) and (not task.is_done()):
                task.cancel()
            
            if isinstance(err, SystemExit):
                raise
            
            if self.interrupted:
                self.write('\nKeyboardInterrupt\n')
            else:
                self.showtraceback()
        else:
            return result


def run_asynchronous_interactive_console(
    interactive_console_locals = None,
    *,
    banner = None,
    exit_message = None,
    callback = None,
    stop_event_loop_when_done = True,
):
    """
    Runs asynchronous interactive console.
    
    Parameters
    ----------
    interactive_console_locals : `None`, `dict` of (`str`, `Any`) items = `None`, Optional
        Parameters to start the console with.
    banner : `None`, `str` = `None`, Optional (Keyword only)
        Interactive console banner.
    exit_message : `None`, `str` = `None`, Optional (Keyword only)
        Interactive console exit message.
    callback : `None`, `FunctionType` = `None`, Optional (Keyword only)
        Callback to run when execution the console is closed.
        
        > This runs before the event loop is shut down!
    stop_event_loop_when_done : `bool` = `True`, Optional (Keyword only)
        Whether the event loop should be closed when the console is closed.
    """
    if interactive_console_locals is None:
        interactive_console_locals = {}
    
    if banner is None:
        banner = create_banner()
    
    if exit_message is None:
        exit_message = create_exit_message()
    
    event_loop = get_or_create_event_loop()
    
    console = AsynchronousInteractiveConsole(interactive_console_locals, event_loop)
    
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
