__all__ = ('modulize',)

import sys
from types import FunctionType, GetSetDescriptorType, MappingProxyType, ModuleType

from .docs import has_docs


NoneType = type(None)

try:
    from _weakref import ref as WeakrefType
except ImportError:
    from weakref import ref as WeakrefType

# This 2 type can be function
WrapperDescriptorType = type(object.__ne__)
MethodDescriptorType = type(object.__format__)

DO_NOT_MODULIZE_TYPES = [MappingProxyType, GetSetDescriptorType]

if WrapperDescriptorType is not FunctionType:
    DO_NOT_MODULIZE_TYPES.append(WrapperDescriptorType)

if MethodDescriptorType is not FunctionType:
    DO_NOT_MODULIZE_TYPES.append(MethodDescriptorType)

DO_NOT_MODULIZE_TYPES = tuple(DO_NOT_MODULIZE_TYPES)

@has_docs
def _modulize_function(old, globals_, source_module, module_name, module_path):
    """
    Changes the given function's scopes and qualname if they were defined inside of a modulized class.
    
    Parameters
    ----------
    old : `function`
        A function present inside of a modulized class.
    globals_ : `dict` of (`str`, `object`)
        Global variables of the respective module.
    source_module : `module`
        The module, where the modulized class was defined.
    module_name : `str`
        The newly created module's name.
    module_path : `str`
        The newly created module's path.

    Returns
    -------
    new : `function`
        Newly recreated function if applicable.
    """
    if old.__module__ != source_module:
        return old
    
    new = FunctionType(old.__code__, globals_, old.__name__, old.__defaults__, old.__closure__)
    new.__module__ = module_path
    qualname = old.__qualname__
    if (qualname is not None) and (len(qualname) > len(module_name)) and qualname[len(module_name)] == '.' and \
            qualname.startswith(module_name):
        new.__qualname__ = qualname[len(module_name) + 1:]
    
    return new

@has_docs
def _modulize_type(klass, globals_, source_module, module_name, module_path):
    """
    Changes the given class's scopes and qualname if they were defined inside of a modulized class.
    
    Parameters
    ----------
    klass : `type`
        A class present inside of a modulized class.
    globals_ : `dict` of (`str`, `object`)
        Global variables of the respective module.
    source_module : `module`
        The module, where the modulized class was defined.
    module_name : `str`
        The newly created module's name.
    module_path : `str`
        The newly created module's path.
    """
    if klass.__module__ != source_module:
        return
    
    qualname = klass.__qualname__
    if (qualname is None) or (len(qualname) <= len(module_name)) or qualname[len(module_name)] != '.' \
            or not qualname.startswith(module_name):
        return
    
    klass.__qualname__ = qualname[len(module_name) + 1:]
    klass.__module__ = module_path
    
    for name in dir(klass):
        value = getattr(klass, name)
        
        value_type = value.__class__
        if value_type is FunctionType:
            value = _modulize_function(value, globals_, source_module, module_name, module_path)
            setattr(klass, name, value)
        
        if issubclass(value_type, type):
            _modulize_type(value, globals_, source_module, module_name, module_path)

@has_docs
def modulize(klass):
    """
    Transforms the given class to a module.
    
    Every functions and classes defined inside of given class, which are also present at transformation as well, will
    have their global scope modified.
    
    Parameters
    ----------
    klass : `type`
        The class to transform to module.
    
    Returns
    -------
    result_module : `module`
        The created module object.
    
    Raises
    ------
    TypeError
        If `klass` is not given as `type`.
    """
    if not isinstance(klass, type):
        raise TypeError(
            f'Only types can be modulized, got {klass.__class__.__name__}; {klass!r}.'
    )
    
    source_module = klass.__module__
    module_name = klass.__name__
    module_path = f'{klass.__module__}.{module_name}'
    try:
        result_module = sys.modules['module_path']
    except KeyError:
        result_module = ModuleType(module_path)
        sys.modules[module_path] = result_module
        globals_ = result_module.__dict__
        globals_['__builtins__'] = __builtins__
    else:
        globals_ = result_module.__dict__
        collected_names = []
        for name in globals_.keys():
            if name.startswith('__') and name.endswith('__'):
                continue
            
            collected_names.append(name)
        
        for name in collected_names:
            del globals_[name]
        
        globals_['__doc__'] = None
    
    for name in type.__dir__(klass):
        if name.startswith('__') and name.endswith('__') and name != '__doc__':
            continue
        
        value = type.__getattribute__(klass, name)
        value_type = type(value)
        if value_type in DO_NOT_MODULIZE_TYPES:
            continue
        
        if value_type is FunctionType:
            value = _modulize_function(value, globals_, source_module, module_name, module_path)
        
        if issubclass(value_type, type):
            _modulize_type(value, globals_, source_module, module_name, module_path)
        
        ModuleType.__setattr__(result_module, name, value)
    
    return result_module
