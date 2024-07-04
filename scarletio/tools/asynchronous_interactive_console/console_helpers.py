__all__ = ('collect_module_variables', 'create_banner', 'create_exit_message')


import sys

from ... import __package__ as PACKAGE_NAME
from ...utils import HIGHLIGHT_TOKEN_TYPES
from ...utils.trace.rendering import _add_typed_parts_into

from .editors.compilation import PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT


PACKAGE = __import__(PACKAGE_NAME)


if PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT:
    AWAIT_NOTE = 'Use "await" directly.'
else:
    AWAIT_NOTE = '!!! Direct "await" is not available on your python version. Please use python 3.8 or newer !!!'


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
            f' / __|/ __/ _` | \'__| |/ _ \\ __| |/ _ \\\n'
            f' \\__ \\ (_| (_| | |  | |  __/ |_| | (_) |\n'
            f' |___/\\___\\__,_|_|  |_|\\___|\\__|_|\\___/\n'
        )
    
    
    if (logo is not None):
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_LOGO, logo
        
        if (package is not None):
            yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n'
            
            
            logo_length = max((len(line) for line in logo.splitlines()), default = 0)
            package_version = package.__version__
            package_version_length = len(package_version)
            
            adjust = logo_length - package_version_length
            if adjust > 0:
                yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, ' ' * adjust
            
            yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_LOGO_VERSION, package_version
            yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n'
            
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n\n'
    
    # At cpython it has a ` \n` in it, but in pypy we have just a `\n`.
    system_version = ' '.join(sys.version.split())
    
    # get package name and upper case it's first character
    package_name = package.__package__
    if package_name and not package_name[0].isupper():
        package_name = package_name[0].upper() + package_name[1:]
    
    console_description = f'{package_name} interactive console {system_version} on {sys.platform}.'
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION, console_description
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n'
    
    if PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT
    else:
        await_token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE
    
    yield await_token_type, AWAIT_NOTE
    
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n'
    console_help = 'Type "help", "copyright", "credits" or "license" for more information.'
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION, console_help
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_CONSOLE, '\n'


def create_banner(package = None, logo = None, *, highlighter = None):
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
    return ''.join(_add_typed_parts_into(_produce_banner(package, logo), [], highlighter))


def create_exit_message(package = None):
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


def collect_module_variables(module):
    """
    Collects importable variables of scarletio.
    
    Parameters
    ----------
    module : `ModuleType`
        The module to collect variables from.
    
    Returns
    -------
    interactive_console_locals : `dict` of (`str`, `object`) items
    """
    interactive_console_locals = {}
    
    package_name = module.__package__
    if (package_name is not None):
        interactive_console_locals[package_name] = module
    
    for variable_name in (
        '__name__',
        '__package__',
        '__loader__',
        '__spec__',
        '__builtins__',
        '__file__',
    ):
        try:
            variable_value = getattr(module, variable_name)
        except AttributeError:
            pass
        else:
            interactive_console_locals[variable_name] = variable_value
    
    if package_name is None:
        interactive_console_locals.update(module.__dict__)
    else:
        for variable_name in getattr(module, '__all__', ()):
            interactive_console_locals[variable_name] = getattr(module, variable_name)
        
    return interactive_console_locals
