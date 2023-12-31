__all__ = ()

from types import FunctionType

SlotWrapperType = type(object.__lt__)
BuiltinFunctionOrMethodType = type(object.__new__)


def _get_type_name(type_):
    """
    Gets the type's name.
    
    Parameters
    ----------
    type_ : `type`
        The type to get its name of.
    
    Returns
    -------
    type_name : `str`
    """
    # This ignores ignores user level modifications.
    type_name = type.__dict__['__name__'].__get__(type_, type(type_))
    
    # Note that you can only set `str` as `.__name__`, but subclasses are also allowed.
    if type(type_name) is not str:
        type_name = str(type_name)
    
    return type_name


def _get_value_representation(value):
    """
    Gets the representation of the given value.
    
    Parameters
    ----------
    value : `object`
        The value to get its representation of.
    
    Returns
    -------
    representation : `str`
    """
    try:
        representation = repr(value)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        representation = f'<{_get_type_name(type(value))!s}>'
    
    else:
        # `repr()` can only return `str` instance including sub-types, so no need for `instance` check.
        if type(representation) is not str:
            representation = str(representation)
    
    return representation


def _get_exception_parameters(exception):
    """
    Returns the parameters the exception was created with.
    
    Parameters
    ----------
    exception : ``BaseException``
        Exception to get its parameters of.
    
    Returns
    -------
    exception_parameters : `None | tuple<object>`
    """
    # Exceptions always have `args` set.
    # Directly attach the field descriptor instead of the attribute to avoid user level modifications.
    exception_parameters = BaseException.args.__get__(exception, type(exception))
    if type(exception_parameters) is tuple:
        return exception_parameters
    
    # Do not use `instance` check if `__class__` is overwritten. Later may add mor conditions here depending how hard
    # people mess it up.
    exception_parameters_type = type(exception_parameters)
    if (
        '__class__' not in
        type.__dict__['__dict__'].__get__(exception_parameters_type, type(exception_parameters_type)).keys()
    ):
        if isinstance(exception_parameters, tuple):
            return tuple(exception_parameters)
    
    return None


def _are_exception_constructors_default(exception):
    """
    Gets whether the exception's constructor(s) are the default ones.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception instance to check.
    
    Returns
    -------
    are_default : `bool`
    """
    exception_type = type(exception)
    
    exception_type_new = type.__getattribute__(exception_type, '__new__')
    exception_type_init = type.__getattribute__(exception_type, '__init__')
    
    # is it pypy?
    if FunctionType is SlotWrapperType:
        if (exception_type_new is not BaseException.__new__) and (exception_type_new is not object.__new__):
            return False
        
        if (exception_type_init is not BaseException.__init__) and (exception_type_init is not object.__init__):
            return False
        
        return True
    
    # Not pypy
    if type(exception_type_new) is not BuiltinFunctionOrMethodType:
        return False
    
    if type(exception_type_init) is not SlotWrapperType:
        return False
    
    return True


def _get_exception_representation_fallback(exception):
    """
    Gets exception representation by building it.
    
    Parameters
    ----------
    exception : ``BaseException``
        The respective exception instance.
    
    Returns
    -------
    raw_exception_representation : `str`
    """
    parts = ['> repr(exception) raised, using fallback representation.\n']
    
    parts.append(_get_type_name(type(exception)))
    parts.append('(')
    
    exception_parameters = _get_exception_parameters(exception)
    if (exception_parameters is not None):
        length = len(exception_parameters)
        if length:
            index = 0
            while True:
                element = exception_parameters[index]
                parts.append(_get_value_representation(element))
                
                index += 1
                if index == length:
                    break
                
                parts.append(', ')
                continue
    
    parts.append(')')
    return ''.join(parts)


def _get_exception_representation_simple(exception):
    """
    Tries to get simple exception representation.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to get it's representation of.
    
    Returns
    -------
    exception_representation : `None`, `str`
        Returns `None` if simple representation is not available.
    """
    if not _are_exception_constructors_default(exception):
        return None
    
    exception_parameters = _get_exception_parameters(exception)
    if (exception_parameters is None) or len(exception_parameters) > 1:
        return None
    
    exception_representation = _get_type_name(type(exception))
    if len(exception_parameters) == 1:
        # Get value representation only if value is not `str`.
        value = exception_parameters[0]
        if issubclass(type(value), str):
            value = str(value)
        else:
            value = _get_value_representation(value)
        
        exception_representation = f'{exception_representation!s}: {value!s}'
    
    return exception_representation


def get_exception_representation_generic(exception):
    """
    Gets the exception's representation.
    
    Parameters
    ----------
    exception : ``BaseException``
        The respective exception instance.
    
    Returns
    -------
    exception_representation : `str`
    """
    exception_representation = _get_exception_representation_simple(exception)
    if exception_representation is not None:
        return exception_representation
    
    try:
        exception_representation = repr(exception)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass
    else:
        if type(exception_representation) is not str:
            exception_representation = str(exception_representation)
        return exception_representation
    
    return _get_exception_representation_fallback(exception)
