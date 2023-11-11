__all__ = ('check_satisfaction', 'export', 'include', 'include_with_callback')

import sys, warnings
from functools import partial as partial_func
from importlib.util import module_from_spec
from types import ModuleType


CALLBACKS = {}
SATISFIED = {}


def include(obj_name):
    """
    Includes the object with the given name. The requirement is satisfied when the respective object is exported.
    
    Parameters
    ----------
    obj_name : `str`
        The object name to include when exported.
    
    Returns
    -------
    placeholder : `value` / `NotImplementedType`
        Placeholder to trick the editors.
    """
    frame = sys._getframe().f_back
    spec = frame.f_globals.get('__spec__', None)
    if spec is None:
        module = None
    else:
        module = sys.modules.get(spec.name, None)
        if module is None:
            module = module_from_spec(spec)
    
    try:
        value = SATISFIED[obj_name]
    except KeyError:
        pass
    else:
        return value
    
    if (module is None):
        warnings.warn(
            (
                f'Cannot include `{obj_name!r}` into {frame.f_globals.get("__file__", None)}.\n'
                f'The object is not yet resolved & The file is not a module.'
            ),
            ResourceWarning,
            stacklevel = 2,
        )
    
    else:
        _add_callback(obj_name, partial_func(_include_callback, module, obj_name))
    
    return NotImplemented


def include_with_callback(obj_name, callback = None):
    """
    Includes the object with the given name. If the respective object is exported the given `callback` is called.
    
    Parameters
    ----------
    obj_name : `str`
        The object name to pass a parameter when exported.
    
    callback : `None`, `callable` = `None`, Optional
        The callback to run when the requirement is satisfied.
    
    Returns
    -------
    none / decorator : `None` / `functools.partial`
        Allows using it as a decorator if only `obj_name` was passed.
    """
    if callback is None:
        return partial_func(include_with_callback, obj_name)
    
    try:
        value = SATISFIED[obj_name]
    except KeyError:
        _add_callback(obj_name, callback)
    else:
        callback(value)


def export(obj, obj_name = None):
    """
    Exports the given object.
    
    Parameters
    ----------
    obj : `object`
        The object to export.
    obj_name : `str` = `None`, Optional
        The name of the object. If not given, is detected from `obj` itself.
    
    Returns
    -------
    obj : `obj`
        The exported object.
    """
    if obj_name is None:
        try:
            obj_name = obj.__name__
        except AttributeError:
            obj_name = obj.__class__.__name__
    
    if isinstance(obj, ModuleType):
        obj_name = obj_name[obj_name.rfind('.') + 1:]
    
    SATISFIED[obj_name] = obj
    
    try:
        callbacks = CALLBACKS.pop(obj_name)
    except KeyError:
        pass
    else:
        for callback in callbacks:
            callback(obj)
    
    return obj


def _include_callback(module, obj_name, obj):
    """
    Callback ran by ``.include`` if the object cannot be resolved initially.
    
    Parameters
    ----------
    module : `ModuleType`
        Module to set `obj`.
    obj_name : `str`
        The object's name to set as.
    obj : `object`
        the object to set.
    """
    setattr(module, obj_name, obj)


def _add_callback(obj_name, callback):
    """
    Adds callback to run when an object is exported.
    
    Parameters
    ----------
    obj_name : `str`
        the object's name to add the resolve callback for.
    
    callback : `callable`
        The function to call when the export is resolved.
    """
    try:
        callbacks = CALLBACKS[obj_name]
    except KeyError:
        callbacks = []
        CALLBACKS[obj_name] = callbacks
    
    callbacks.append(callback)


def check_satisfaction():
    """
    Checks whether every ``include`` requirement is satisfied with ``export``.
    
    Raises
    ------
    AssertionError
    """
    assert (not CALLBACKS), f'Unsatisfied includes: {", ".join(CALLBACKS.keys())}'
