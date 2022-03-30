__all__ = ('check_satisfaction', 'export', 'include',)

import sys, warnings
from importlib.util import module_from_spec
from types import ModuleType


INCLUDED = {}
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
        try:
            modules = INCLUDED[obj_name]
        except KeyError:
            modules = INCLUDED[obj_name] = set()
        
        modules.add(module)
    
    return NotImplemented


def export(obj, obj_name=None):
    """
    Exports the given object.
    
    Parameters
    ----------
    obj : `Any`
        The object to export.
    obj_name : `str` = `None`, Optional
        The name of the object. If not given, is detected from `obj` itself.
    
    Returns
    -------
    obj : `Any`
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
        modules = INCLUDED.pop(obj_name)
    except KeyError:
        pass
    else:
        for module in modules:
            setattr(module, obj_name, obj)
    
    return obj


def check_satisfaction():
    """
    Checks whether every ``include`` requirement is satisfied with ``export``.
    
    Raises
    ------
    AssertionError
    """
    assert (not INCLUDED), f'Unsatisfied includes: {", ".join(INCLUDED.keys())}'
