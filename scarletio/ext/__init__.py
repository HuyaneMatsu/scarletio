__all__ = ()

import warnings

from ..core import write_exception_maybe_async


HOOKS = []
LOADED_EXTENSIONS = set()

def register_library_extension(extension_name):
    """
    Registers a library extension, calling respective hooks if applicable.
    
    Parameters
    ----------
    extension_name : `str`
        The library extension's name.
    """
    if extension_name in LOADED_EXTENSIONS:
        warnings.warn(
            f'A library extension with name {extension_name!r} is already loaded.',
            RuntimeWarning,
            stacklevel = 2,
        )
        return
    
    LOADED_EXTENSIONS.add(extension_name)
    
    for index in reversed(range(len(HOOKS))):
        requirements, hook = HOOKS[index]
        try:
            requirements.discard(extension_name)
        except KeyError:
            continue
        
        if requirements:
            continue
        
        del HOOKS[index]
        
        try:
            hook()
        except BaseException as err:
            write_exception_maybe_async(
                err,
                [
                    'register_library_extension(',
                    repr(extension_name),
                    ') ignores occurred exception meanwhile calling ',
                    repr(hook),
                    ' satisfied library extension hook.\n.'
                ]
            )


def add_library_extension_hook(hook, requirements):
    """
    Adds a library extension hook, what is called, when the given `requirements` are satisfied.
    
    Parameters
    ----------
    hook : `callable`
        Library extension hook called when all the required extensions are loaded as well.
    requirements : `iterable` of `str`
        An iterable of library extension names, which need to be resolved before calling the respective hook.
    """
    requirements_set = set(requirements)
    requirements_set.difference_update(LOADED_EXTENSIONS)
    
    if requirements_set:
        HOOKS.append((requirements_set, hook))
        return
    
    try:
        hook()
    except BaseException as err:
        write_exception_maybe_async(
            err,
            [
                'add_library_extension_hook(',
                repr(hook),
                ', ',
                repr(requirements),
                ') ignores occurred exception '
                'meanwhile calling ',
                repr(hook),
                ' satisfied library extension hook.\n.'
            ]
        )
