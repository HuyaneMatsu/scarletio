__all__ = (
    'is_awaitable', 'is_coroutine', 'is_coroutine_function', 'is_coroutine_generator',
    'is_coroutine_generator_function', 'to_coroutine'
)

import sys
from types import AsyncGeneratorType, CoroutineType, FunctionType, GeneratorType, MethodType

from .code import CO_ASYNC_GENERATOR, CO_COROUTINE_ALL, CO_GENERATOR, CO_ITERABLE_COROUTINE
from .docs import has_docs, set_docs


@has_docs
def is_coroutine_function(func):
    """
    Returns whether the given `obj` is a coroutine function, so is created with `async def`.
    
    Parameters
    ----------
    func : `Any`
    
    Returns
    -------
    is_coroutine_function : `bool`
    """
    if isinstance(func, (FunctionType, MethodType)) and func.__code__.co_flags & CO_COROUTINE_ALL:
        return True
    else:
        return False


@has_docs
def is_coroutine_generator_function(func):
    """
    Returns whether the given `obj` is a coroutine generator function, so is created with `async def` and uses `yield`
    statement.
    
    Parameters
    ----------
    func : `Any`
    
    Returns
    -------
    is_coroutine_function_generator : `bool`
    """
    if isinstance(func, (FunctionType, MethodType)) and func.__code__.co_flags & CO_ASYNC_GENERATOR:
        return True
    else:
        return False


@has_docs
def is_coroutine(obj):
    """
    Returns whether the given `obj` is a coroutine created by an `async def` function.
    
    Parameters
    ----------
    obj : `Any`
    
    Returns
    -------
    is_coroutine : `bool`
    """
    return isinstance(obj, (CoroutineType, GeneratorType))


@has_docs
def is_awaitable(obj):
    """
    Returns whether the given `obj` can be used in `await` expression.
    
    Parameters
    ----------
    obj : `Any`
    
    Returns
    -------
    is_awaitable : `bool`
    """
    if isinstance(obj, (CoroutineType, GeneratorType)):
        return True
    
    if hasattr(type(obj), '__await__'):
        return True
    
    return False


@has_docs
def is_coroutine_generator(obj):
    """
    Returns whether the given `obj` is a coroutine generator created by an `async def` function, and can be used inside
    of an `async for` loop.
    
    Returns
    -------
    is_coroutine_generator : `bool`
    """
    if isinstance(obj, AsyncGeneratorType):
        code = obj.ag_code
    elif isinstance(obj, CoroutineType):
        code = obj.cr_code
    elif isinstance(obj, GeneratorType):
        code = obj.gi_code
    else:
        return False
    
    if code.co_flags & CO_ASYNC_GENERATOR:
        return True
    
    return False


if sys.version_info >= (3, 11, 0):
    def to_coroutine(function):
        if not isinstance(function, FunctionType):
            raise TypeError(
                f'`function` can only be `{FunctionType.__name__}`, got {function.__class__.__name__}; '
                f'{function!r}.'
            )
        
        code_object = function.__code__
        code_flags = code_object.co_flags
        if code_flags & CO_COROUTINE_ALL:
            return function
        
        if not code_flags & CO_GENERATOR:
            raise TypeError(
                f'`function` can only be given as generator or as coroutine type, got {function!r}, '
                f'co_flags={code_flags!r}.'
            )
        
        function.__code__ = type(code_object)(
            code_object.co_argcount,
            code_object.co_posonlyargcount,
            code_object.co_kwonlyargcount,
            code_object.co_nlocals,
            code_object.co_stacksize,
            code_flags | CO_ITERABLE_COROUTINE,
            code_object.co_code,
            code_object.co_consts,
            code_object.co_names,
            code_object.co_varnames,
            code_object.co_filename,
            code_object.co_name,
            code_object.co_qualname,
            code_object.co_firstlineno,
            code_object.co_lnotab,
            code_object.co_endlinetable,
            code_object.co_columntable,
            code_object.co_exceptiontable,
            code_object.co_freevars,
            code_object.co_cellvars,
        )
        
        return function

elif sys.version_info >= (3, 8, 0):
    def to_coroutine(function):
        if not isinstance(function, FunctionType):
            raise TypeError(
                f'`function` can only be `{FunctionType.__name__}`, got {function.__class__.__name__}; '
                f'{function!r}.'
            )
        
        code_object = function.__code__
        code_flags = code_object.co_flags
        if code_flags & CO_COROUTINE_ALL:
            return function
        
        if not code_flags & CO_GENERATOR:
            raise TypeError(
                f'`function` can only be given as generator or as coroutine type, got {function!r}, '
                f'co_flags={code_flags!r}.'
            )
        
        function.__code__ = type(code_object)(
            code_object.co_argcount,
            code_object.co_posonlyargcount,
            code_object.co_kwonlyargcount,
            code_object.co_nlocals,
            code_object.co_stacksize,
            code_flags | CO_ITERABLE_COROUTINE,
            code_object.co_code,
            code_object.co_consts,
            code_object.co_names,
            code_object.co_varnames,
            code_object.co_filename,
            code_object.co_name,
            code_object.co_firstlineno,
            code_object.co_lnotab,
            code_object.co_freevars,
            code_object.co_cellvars,
        )
        
        return function
else:
    def to_coroutine(function):
        if not isinstance(function, FunctionType):
            raise TypeError(
                f'`function` can only be `{FunctionType.__name__}`, got {function.__class__.__name__}; '
                f'{function!r}.'
            )
        
        code_object = function.__code__
        code_flags = code_object.co_flags
        if code_flags & CO_COROUTINE_ALL:
            return function
        
        if not code_flags & CO_GENERATOR:
            raise TypeError(
                f'`function` can only be given as generator or as coroutine type, got {function!r}, '
                f'co_flags={code_flags!r}.'
            )
        
        function.__code__ = type(code_object)(
            code_object.co_argcount,
            code_object.co_kwonlyargcount,
            code_object.co_nlocals,
            code_object.co_stacksize,
            code_flags | CO_ITERABLE_COROUTINE,
            code_object.co_code,
            code_object.co_consts,
            code_object.co_names,
            code_object.co_varnames,
            code_object.co_filename,
            code_object.co_name,
            code_object.co_firstlineno,
            code_object.co_lnotab,
            code_object.co_freevars,
            code_object.co_cellvars,
        )
        
        return function

set_docs(to_coroutine,
    """
    Transforms the given generator function to coroutine function.
    
    Parameters
    ----------
    function : ``FunctionType``
        The generator function.
    
    Returns
    -------
    function : ``FunctionType``
    
    Raises
    ------
    TypeError
        - `function`'s type is incorrect.
        - `Function` cannot be turned to coroutine.
    """)
