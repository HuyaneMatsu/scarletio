__all__ = ()

import sys

from functools import partial as partial_func
from os.path import sep as PATH_SEPARATOR
from reprlib import repr as short_repr
from types import AsyncGeneratorType as CoroutineGeneratorType, CoroutineType, GeneratorType

from ..function_tools import alchemy_incendiary


def _cut_file_name(file_name):
    """
    Cuts the given file name.
    
    Parameters
    ----------
    file_name : `None | str`
        The file name to cut.
    
    Returns
    -------
    file_name : `None | str`
    """
    if (file_name is None) or (not file_name):
        return None
    
    file_name_length = len(file_name)
    
    for path in sys.path:
        path_length = len(path)
        
        if not file_name.startswith(path):
            continue
        
        if file_name_length <= path_length:
            continue
        
        if file_name[path_length] != PATH_SEPARATOR:
            continue
        
        return '...' + file_name[path_length:]
    
    return file_name


def _merge_nullable_tuples(tuple_0, tuple_1):
    """
    Merges two nullable tuple.
    
    Parameters
    ----------
    tuple_0 : `None | tuple`
        Tuple to merge.
    tuple_1 : `None | tuple`
        Tuple ot merge.
    
    Returns
    -------
    merged : `None | tuple`
    """
    if tuple_0 is None:
        return tuple_1
    
    if tuple_1 is None:
        return tuple_0
    
    return tuple_0 + tuple_1


def _merge_nullable_dicts(dict_0, dict_1):
    """
    Merges two nullable tuple.
    
    Parameters
    ----------
    dict_0 : `None | dict<str, object>`
        Dictionary to merge.
    dict_1 : `None | dict<str, object>`
        Dictionary ot merge.
    
    Returns
    -------
    merged : `None | dict<str, object>`
    """
    if dict_0 is None:
        return dict_1
    
    if dict_1 is None:
        return dict_0
    
    return {**dict_1, **dict_0}


def format_callback(function, positional_parameters = None, keyword_parameters = None):
    """
    Formats the given callback to a more user friendly representation.
    
    Parameters
    ----------
    function : `callable`
        The callback to format.
    positional_parameters : `None | tuple<object>` = `None`, Optional
        Additional parameters to call the `function` with.
    keyword_parameters : `None | dict<str, object>` = `None`, Optional
        Additional keyword parameters to call the `function` with.
    
    Returns
    -------
    result : `str`
        The formatted callback.
    """
    # Unwrap
    while True:
        if isinstance(function, alchemy_incendiary):
            # `alchemy_incendiary` is not accepting nesting, yeet old parameters.
            positional_parameters = function.positional_parameters
            keyword_parameters = function.keyword_parameters
            function = function.function
            continue
        
        if isinstance(function, partial_func):
            # `partial_func` accepts nesting, extend old parameters.
            positional_parameters = _merge_nullable_tuples(function.args, positional_parameters)
            keyword_parameters = _merge_nullable_dicts(keyword_parameters, function.keywords)
            function = function.func
            continue
        
        break

    function_representation = getattr(function, '__qualname__', None)
    if function_representation is None:
        function_representation = getattr(function, '__name__', None)
        if function_representation is None:
            function_representation = type(function).__name__
    
    
    parts = [function_representation, '(']
    parameters_added = False
    
    # Add positional parameters
    if (positional_parameters is not None) and positional_parameters:
        parameters_added = True
        
        index = 0
        length = len(positional_parameters)
        
        while True:
            value = positional_parameters[index]
            parts.append(short_repr(value))
            
            index += 1
            if index >= length:
                break
            
            parts.append(', ')
            continue
    
    
    # Add keyword parameters
    if (keyword_parameters is not None) and keyword_parameters:
        if parameters_added:
            parts.append(', ')
        
        index = 0
        length = len(keyword_parameters)
        items = sorted(keyword_parameters.items())
        
        while True:
            key, value = items[index]
            parts.append(key)
            parts.append(' = ')
            parts.append(short_repr(value))
            
            index += 1
            if index >= length:
                break
            
            parts.append(', ')
            continue
    
    
    parts.append(')')
    return ''.join(parts)


def format_builtin(function):
    """
    Formats the given built-in's name.
    
    Parameters
    ----------
    function : `callable`
        The builtin to format.
    
    Returns
    -------
    result : `str`
        The formatted builtin.
    """
    # Cython or builtin
    name = getattr(function, '__qualname__', None)
    if name is None:
        name = getattr(function, '__name__', None)
        if name is None: # builtins might reach this part
            name = type(function).__name__
    
    return f'{name!s}()'


def format_coroutine(coroutine):
    """
    Formats the given coroutine to a more user friendly representation.
    
    Parameters
    ----------
    coroutine : `CoroutineType`, `GeneratorType`, `CoroutineGeneratorType`
        The coroutine to get representation of.
    
    Returns
    -------
    result : `str`
        The formatted coroutine.
    """
    coroutine_type = type(coroutine)
    if coroutine_type is GeneratorType:
        code = coroutine.gi_code
        frame = coroutine.gi_frame
        running = coroutine.gi_running
    
    elif coroutine_type is CoroutineType:
        code = coroutine.cr_code
        frame = coroutine.cr_frame
        running = coroutine.cr_running
    
    elif coroutine_type is CoroutineGeneratorType:
        code = coroutine.ag_code
        frame = coroutine.ag_frame
        running = coroutine.ag_running
    
    else:
        code = None
        frame = None
        running = -1
    
    if running == True:
        state = 'running'
    
    elif running == False:
        if frame is None:
            state = 'finished'
        
        else:
            state = 'suspended'
    
    else:
        state = 'unknown state'
    
    if running == -1:
        name = format_builtin(coroutine)
    else:
        name = format_callback(coroutine)
    
    if (code is None):
        location = None
    else:
        file_name = _cut_file_name(code.co_filename)
        if file_name is None:
            location = None
        else:
            if frame is None:
                line_number = code.co_firstlineno
            else:
                line_number = frame.f_lineno
            
            location = f'"{file_name!s}", line {line_number!s}'
    
    if location is None:    
        location = 'unknown location'
    
    return f'<{name!s} from {location!s}; {state!s}>'
