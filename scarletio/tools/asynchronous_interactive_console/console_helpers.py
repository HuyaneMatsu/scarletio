__all__ = ('collect_package_local_variables', 'create_banner', 'create_exit_message')


import sys

from ... import __package__ as PACKAGE_NAME
from ...core import create_event_loop, get_event_loop
from ...utils import HIGHLIGHT_TOKEN_TYPES
from ...utils.trace import _iter_highlight_producer

from .editors.compilation import PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT


PACKAGE = __import__(PACKAGE_NAME)


if PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT:
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
    
    console_description = f'{package_name} interactive console {system_version} on {sys.platform}.'
    yield console_description, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION
    yield '\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
    
    if PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT
    else:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE
    
    yield AWAIT_NOTE, await_token_type
    
    yield '\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE
    console_help ='Type "help", "copyright", "credits" or "license" for more information.'
    yield console_help, HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION
    yield '\n', HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE


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
