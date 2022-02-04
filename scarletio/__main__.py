import sys, warnings
from functools import partial as partial_func
from types import FunctionType

from . import __package__ as PACKAGE_NAME, Future, create_event_loop, get_event_loop, is_awaitable

from code import InteractiveConsole


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

LOGO = (
    f'                     _      _   _       \n'
    f'                    | |    | | (_)      \n'
    f'  ___  ___ __ _ _ __| | ___| |_ _  ___  \n'
    f' / __|/ __/ _` | \'__| |/ _ \ __| |/ _ \ \n'
    f' \__ \ (_| (_| | |  | |  __/ |_| | (_) |\n'
    f' |___/\___\__,_|_|  |_|\___|\__|_|\___/ \n'
    f'                                        \n'
    f'{PACKAGE.__version__:>40}\n'
)


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


def __main__(local_variables=None):
    """
    Runs an asynchronous interactive console.
    
    > You need python3.8 or higher!
    
    Parameters
    ----------
    local_variables : `None`, `dict` of (`str`, `Any`) items = `None`
        Parameters to start th console with. If not defined will start with `scarletio.__all__`'s.
    """
    if local_variables is None:
        interactive_console_locals = {PACKAGE_NAME: PACKAGE}
        for variable_name in {
            '__name__',
            '__package__',
            '__loader__',
            '__spec__',
            '__builtins__',
            '__file__'
        }:
            interactive_console_locals[variable_name] = getattr(PACKAGE, variable_name)
        
        for variable_name in PACKAGE.__all__:
            interactive_console_locals[variable_name] = getattr(PACKAGE, variable_name)
    else:
        interactive_console_locals = dict(local_variables)
    
    banner = (
        f'{LOGO}\n\n'
        f'{PACKAGE_NAME} interactive_console {sys.version} on {sys.platform}.\n'
        f'{AWAIT_NOTE}\n'
        f'Type \'help\', \'copyright\', \'credits\' or \'license\' for more information.'
    )
    
    exit_message = f'exiting {PACKAGE_NAME} interactive_console...'
    
    event_loop = get_or_create_event_loop()
    
    console = AsynchronousInteractiveConsole(interactive_console_locals, event_loop)
    
    try:
        console.interact(
            banner = banner,
            exitmsg = exit_message,
        )
    finally:
        warnings.filterwarnings(
            'ignore',
            message = r'^coroutine .* was never awaited$',
            category = RuntimeWarning,
        )
        
        event_loop.stop()


if __name__ == '__main__':
    __main__()
