__all__ = ('CallableAnalyzer', 'RichAnalyzer')

from itertools import zip_longest
from types import FunctionType

from .async_utils import is_coroutine_function, is_coroutine_generator_function
from .code import CODE_FLAG_VARARGS, CODE_FLAG_VARKEYWORDS
from .method_like import MethodLike


IS_PYTHON_STULTUS = False


INSTANCE_TO_ASYNC_FALSE = 1
INSTANCE_TO_ASYNC_TRUE = 2
INSTANCE_TO_ASYNC_CANNOT = 3
INSTANCE_TO_ASYNC_GENERATOR_FALSE = 4
INSTANCE_TO_ASYNC_GENERATOR_TRUE = 5

PARAMETER_TYPE_POSITIONAL_ONLY = 1
PARAMETER_TYPE_POSITIONAL_AND_KEYWORD = 2
PARAMETER_TYPE_KEYWORD_ONLY = 3
PARAMETER_TYPE_ARGS = 4
PARAMETER_TYPE_KWARGS = 5

PARAMETER_TYPE_NAMES = {
    PARAMETER_TYPE_POSITIONAL_ONLY: 'positional only',
    PARAMETER_TYPE_POSITIONAL_AND_KEYWORD: 'positional',
    PARAMETER_TYPE_KEYWORD_ONLY: 'keyword only',
    PARAMETER_TYPE_ARGS: 'args',
    PARAMETER_TYPE_KWARGS: 'kwargs',
}

class Parameter:
    """
    Represents a callable's parameter.
    
    Attributes
    ----------
    annotation : `object`
        The parameter's annotation if applicable. Defaults to `None`.
    default : `object`
        The default value of the parameter if applicable. Defaults to `None`.
    has_annotation : `bool`
        Whether the parameter has annotation.
    has_default : `bool`
        Whether the parameter has default value.
    name : `str`
        The parameter's name.
    positionality : `int`
        Whether the parameter is positional, keyword or such.
        
        Can be set one of the following:
        +----------------------------------------+-----------+
        | Respective Name                        | Value     |
        +========================================+===========+
        | PARAMETER_TYPE_POSITIONAL_ONLY         | 1         |
        +----------------------------------------+-----------+
        | PARAMETER_TYPE_POSITIONAL_AND_KEYWORD  | 2         |
        +----------------------------------------+-----------+
        | PARAMETER_TYPE_KEYWORD_ONLY            | 3         |
        +----------------------------------------+-----------+
        | PARAMETER_TYPE_ARGS                    | 4         |
        +----------------------------------------+-----------+
        | PARAMETER_TYPE_KWARGS                  | 5         |
        +----------------------------------------+-----------+
    reserved : `bool`
        Whether the parameter is reserved.
        
        For example at the case of methods, the first parameter is reserved for the `self` parameter.
    """
    __slots__ = ('annotation', 'default', 'has_annotation', 'has_default', 'name', 'positionality', 'reserved', )
    
    def __repr__(self):
        """Returns the parameter's representation."""
        repr_parts = []
        repr_parts.append('<')
        repr_parts.append(type(self).__name__)
        repr_parts.append(' ')
        
        if self.reserved:
            repr_parts.append('reserved, ')
        
        repr_parts.append(PARAMETER_TYPE_NAMES[self.positionality])
        
        repr_parts.append(', name = ')
        repr_parts.append(repr(self.name))
        
        if self.has_default:
            repr_parts.append(', default = ')
            repr_parts.append(repr(self.default))
        
        if self.has_annotation:
            repr_parts.append(', annotation = ')
            repr_parts.append(repr(self.annotation))
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two parameters are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # has_annotation
        has_annotation = self.has_annotation
        if (has_annotation != other.has_annotation):
            return False
        
        if has_annotation:
            # annotation
            if self.annotation != other.annotation:
                return False
        
        # has_default
        has_default = self.has_default
        if (has_default != other.has_default):
            return False
        
        if has_default:
            # default
            if (self.default is not other.default) or (self.default != other.default):
                return False
        
        # name
        if self.name != other.name:
            return False
        
        # positionality
        if self.positionality != other.positionality:
            return False
        
        # reserved
        if self.reserved != other.reserved:
            return False
        
        return True
    
    
    def is_positional_only(self):
        """
        Returns whether the parameter is positional only.
        
        Returns
        -------
        is_positional_only : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_POSITIONAL_ONLY:
            return True
        
        return False
    
    
    def is_positional(self):
        """
        Returns whether the parameter is positional.
        
        Returns
        -------
        is_positional : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_POSITIONAL_ONLY:
            return True
        
        if positionality == PARAMETER_TYPE_POSITIONAL_AND_KEYWORD:
            return True
        
        return False
    
    
    def is_keyword(self):
        """
        Returns whether the parameter can be used as a keyword parameter.
        
        Returns
        -------
        is_keyword : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_POSITIONAL_AND_KEYWORD:
            return True
        
        if positionality == PARAMETER_TYPE_KEYWORD_ONLY:
            return True
        
        return False
    
    
    def is_keyword_only(self):
        """
        Returns whether they parameter is keyword only.
        
        Returns
        -------
        is_keyword_only : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_KEYWORD_ONLY:
            return True
        
        return False
    
    
    def is_args(self):
        """
        Returns whether the parameter is an `*args` parameter.
        
        Returns
        -------
        is_args : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_ARGS:
            return True
        
        return False
    
    
    def is_kwargs(self):
        """
        Returns whether the parameter is an `**kwargs` parameter.
        
        Returns
        -------
        is_kwargs : `bool`
        """
        positionality = self.positionality
        if positionality == PARAMETER_TYPE_KWARGS:
            return True
        
        return False


if IS_PYTHON_STULTUS:
    def compile_annotations(real_function, annotations):
        new_annotations = {}
        if not annotations:
            return new_annotations
        
        global_variables = getattr(real_function, '__globals__', None)
        if (global_variables is None):
            # Builtins go brrr
            return new_annotations
        
        for key, value in annotations.items():
            if type(value) is str:
                try:
                    value = eval(value, global_variables, None)
                except:
                    pass
            
            new_annotations[key] = value
        
        return new_annotations


class CallableAnalyzer:
    """
    Analyzer for callable-s.
    
    Can analyze functions, methods, callable objects and types or such.
    
    Attributes
    ----------
    args_parameter : `None`, ``Parameter``
        If the analyzed callable has `*args` parameter, then this attribute is set to it. Defaults to `None`.
    parameters : `list` of ``Parameter``
        The analyzed callable's parameters.
    callable : `callable`
        The analyzed object.
    instance_to_async : `int`
        Whether the analyzed object can be instanced to async.
        
        +---------------------------+-----------+-------------------------------------------+
        | Respective Name           | Value     | Description                               |
        +===========================+===========+===========================================+
        | INSTANCE_TO_ASYNC_FALSE   | 1         | Whether the object is async.              |
        +---------------------------+-----------+-------------------------------------------+
        | INSTANCE_TO_ASYNC_TRUE    | 2         | Whether the object is on async callable,  |
        |                           |           | but after instancing it, returns one.     |
        +---------------------------+-----------+-------------------------------------------+
        | INSTANCE_TO_ASYNC_CANNOT  | 3         | Whether the object is not async.          |
        +---------------------------+-----------+-------------------------------------------+
    kwargs_parameter : `None`, ``Parameter``
        If the analyzed callable has `**kwargs`, then this attribute is set to it. Defaults to `None`.
    method_allocation : `int`
        How much parameter is allocated if the analyzed callable is method if applicable.
    real_function : `callable`
        The function wrapped by the given callable.
    """
    __slots__ = (
        'args_parameter', 'parameters', 'callable', 'instance_to_async', 'kwargs_parameter', 'method_allocation',
        'real_function'
    )
    
    def __repr__(self):
        """Returns the callable analyzer's representation."""
        repr_parts = []
        repr_parts.append('<')
        repr_parts.append(self.__class__.__name__)
        
        if self.is_async():
            repr_parts.append(' async')
        elif self.is_async_generator():
            repr_parts.append(' async generator')
        elif self.can_instance_to_async_callable():
            repr_parts.append(' instance async')
        elif self.can_instance_to_async_generator():
            repr_parts.append(' instance async generator')
        
        method_allocation = self.method_allocation
        if method_allocation:
            repr_parts.append(' method')
            if method_allocation != 1:
                repr_parts.append(' (')
                repr_parts.append(repr(method_allocation))
                repr_parts.append(')')
        
        repr_parts.append(' ')
        callable_ = self.callable
        repr_parts.append(repr(callable_))
        real_function = self.real_function
        if (callable_ is not real_function):
            repr_parts.append(' (')
            repr_parts.append(repr(real_function))
            repr_parts.append(')')
        
        repr_parts.append(', parameters = ')
        repr_parts.append(repr(self.parameters))
        
        args_parameter = self.args_parameter
        if (args_parameter is not None):
            repr_parts.append(', args = ')
            repr_parts.append(repr(args_parameter))
        
        kwargs_parameter = self.kwargs_parameter
        if (kwargs_parameter is not None):
            repr_parts.append(', kwargs = ')
            repr_parts.append(repr(kwargs_parameter))
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    
    def __new__(cls, callable_, as_method = False):
        """
        Analyzes the given callable.
        
        Parameters
        ----------
        callable_ : `callable`
            The callable to analyze.
        as_method : `bool` = `False`, Optional
            Whether the given `callable` is given as a `function`, but it should be analyzed as a `method`.
        
        Raises
        ------
        TypeError
            If the given object is not callable, or could not be used as probably intended.
        """
        while True:
            if isinstance(callable_, FunctionType):
                
                real_function = callable_
                if is_coroutine_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_FALSE
                elif is_coroutine_generator_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_FALSE
                else:
                    instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                
                method_allocation = 0
                break
            
            if isinstance(callable_, MethodLike):
                real_function = callable_
                
                if is_coroutine_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_FALSE
                elif is_coroutine_generator_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_FALSE
                else:
                    instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                
                method_allocation = MethodLike.get_reserved_parameter_count(callable_)
                break
            
            if not isinstance(callable_, type) and hasattr(type(callable_), '__call__'):
                real_function = type(callable_).__call__
                
                if is_coroutine_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_FALSE
                elif is_coroutine_generator_function(real_function):
                    instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_FALSE
                else:
                    instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                    
                if type(real_function) is FunctionType:
                    method_allocation = 1
                else:
                    method_allocation = MethodLike.get_reserved_parameter_count(real_function)
                
                break
            
            if not issubclass(callable_, type) and isinstance(callable_, type):
                
                while True:
                    real_function = callable_.__new__
                    if not callable(real_function):
                        raise TypeError(
                            f'`{callable_!r}.__new__` should be callable, got {real_function.__class__.__name__}; '
                            f'{real_function!r}.'
                        )
                    
                    if real_function is not object.__new__:
                        if is_coroutine_function(real_function):
                            instance_to_async = INSTANCE_TO_ASYNC_FALSE
                        elif is_coroutine_generator_function(real_function):
                            instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_FALSE
                        else:
                            if hasattr(callable_, '__call__'):
                                call = callable_.__call__
                                if is_coroutine_function(call):
                                    instance_to_async = INSTANCE_TO_ASYNC_TRUE
                                elif is_coroutine_generator_function(call):
                                    instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_TRUE
                                else:
                                    instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                            else:
                                instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                        
                        if type(real_function) is FunctionType:
                            method_allocation = 1
                        else:
                            method_allocation = MethodLike.get_reserved_parameter_count(real_function)
                        
                        break
                    
                    real_function = callable_.__init__
                    if not callable(real_function):
                        raise TypeError(
                            f'`{callable_!r}.__init__` should be callable, got {type(real_function).__name__}; '
                            f'{real_function!r}.'
                        )
                    
                    if real_function is not object.__init__:
                        if hasattr(callable_, '__call__'):
                            call = callable_.__call__
                            if is_coroutine_function(call):
                                instance_to_async = INSTANCE_TO_ASYNC_TRUE
                            elif is_coroutine_generator_function(call):
                                instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_TRUE
                            else:
                                instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                        else:
                            instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                        
                        if type(real_function) is FunctionType:
                            method_allocation = 1
                        else:
                            method_allocation = MethodLike.get_reserved_parameter_count(real_function)
                        
                        break
                    
                    real_function = None
                    method_allocation = 0
                    
                    if hasattr(callable_, '__call__'):
                        call = callable_.__call__
                        if is_coroutine_function(call):
                            instance_to_async = INSTANCE_TO_ASYNC_TRUE
                        elif is_coroutine_generator_function(call):
                            instance_to_async = INSTANCE_TO_ASYNC_GENERATOR_TRUE
                        else:
                            instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                    else:
                        instance_to_async = INSTANCE_TO_ASYNC_CANNOT
                    break
                
                break
            
            raise TypeError(
                f'Expected `FunctionType`, `MethodType`, `callable`, got {callable_.__class__.__name__}; {callable_!r}.'
            )
        
        if as_method and type(callable_) is FunctionType:
            method_allocation += 1
        
        if (real_function is not None) and not hasattr(real_function, '__code__'):
            raise TypeError(
                f'Expected `function-like`, got {real_function.__class__.__name__}; {real_function!r}.'
            )
        
        parameters = []
        if (real_function is not None):
            parameter_count = real_function.__code__.co_argcount
            accepts_args = real_function.__code__.co_flags & CODE_FLAG_VARARGS
            keyword_only_parameter_count = real_function.__code__.co_kwonlyargcount
            accepts_kwargs = real_function.__code__.co_flags & CODE_FLAG_VARKEYWORDS
            positional_only_parameter_count = getattr(real_function.__code__, 'co_posonlyargcount', 0)
            default_parameter_values = real_function.__defaults__
            default_keyword_only_parameter_values = real_function.__kwdefaults__
            annotations = getattr(real_function, '__annotations__', None)
            if (annotations is None):
                annotations = {}
            elif IS_PYTHON_STULTUS:
                annotations = compile_annotations(real_function, annotations)
            
            start = 0
            end = parameter_count
            parameter_names = real_function.__code__.co_varnames[start:end]
            
            start = end
            end = start + keyword_only_parameter_count
            keyword_only_parameter_names = real_function.__code__.co_varnames[start:end]
            
            if accepts_args:
                args_name = real_function.__code__.co_varnames[end]
                end += 1
            else:
                args_name = None
            
            if accepts_kwargs:
                kwargs_name = real_function.__code__.co_varnames[end]
            else:
                kwargs_name = None
            
            names_to_defaults = {}
            if (default_parameter_values is not None) and default_parameter_values:
                parameter_index = parameter_count - len(default_parameter_values)
                default_index = 0
                while parameter_index < parameter_count:
                    name = parameter_names[parameter_index]
                    default = default_parameter_values[default_index]
                    
                    names_to_defaults[name] = default
                    
                    parameter_index += 1
                    default_index += 1
            
            if (default_keyword_only_parameter_values is not None) and default_keyword_only_parameter_values:
                parameter_index = keyword_only_parameter_count - len(default_keyword_only_parameter_values)
                while parameter_index < keyword_only_parameter_count:
                    name = keyword_only_parameter_names[parameter_index]
                    default = default_keyword_only_parameter_values[name]
                    
                    names_to_defaults[name] = default
                    
                    parameter_index += 1
            
            if (method_allocation > parameter_count) and (args_name is None):
                raise TypeError(
                    f'Received a `method-like`, but has not enough positional parameters, got '
                    f'{real_function.__class__.__name__}; {real_function!r}; '
                    f'allocated parameter count={method_allocation!r}; total parameter count={parameter_count!r}.'
                )
            
            index = 0
            while index < parameter_count:
                parameter = Parameter()
                name = parameter_names[index]
                parameter.name = name
                
                try:
                    annotation = annotations[name]
                except KeyError:
                    parameter.has_annotation = False
                    parameter.annotation = None
                else:
                    parameter.has_annotation = True
                    parameter.annotation = annotation
                
                try:
                    default = names_to_defaults[name]
                except KeyError:
                    parameter.has_default = False
                    parameter.default = None
                else:
                    parameter.has_default = True
                    parameter.default = default
                
                if index < positional_only_parameter_count:
                    parameter.positionality = PARAMETER_TYPE_POSITIONAL_ONLY
                else:
                    parameter.positionality = PARAMETER_TYPE_POSITIONAL_AND_KEYWORD
                
                parameter.reserved = (index<method_allocation)
                parameters.append(parameter)
                index = index + 1
            
            if args_name is None:
                args_parameter = None
            else:
                args_parameter = Parameter()
                args_parameter.name = args_name
                
                try:
                    annotation = annotations[args_name]
                except KeyError:
                    args_parameter.has_annotation = False
                    args_parameter.annotation = None
                else:
                    args_parameter.has_annotation = True
                    args_parameter.annotation = annotation

                args_parameter.has_default = False
                args_parameter.default = None
                args_parameter.positionality = PARAMETER_TYPE_ARGS
                
                if method_allocation > parameter_count:
                    args_parameter.reserved = True
                else:
                    args_parameter.reserved = False
                parameters.append(args_parameter)
            
            index = 0
            while index < keyword_only_parameter_count:
                parameter = Parameter()
                name = keyword_only_parameter_names[index]
                parameter.name = name
                
                try:
                    annotation = annotations[name]
                except KeyError:
                    parameter.has_annotation = False
                    parameter.annotation = None
                else:
                    parameter.has_annotation = True
                    parameter.annotation = annotation
                
                try:
                    default = names_to_defaults[name]
                except KeyError:
                    parameter.has_default = False
                    parameter.default = None
                else:
                    parameter.has_default = True
                    parameter.default = default
                
                parameter.positionality = PARAMETER_TYPE_KEYWORD_ONLY
                parameter.reserved = False
                parameters.append(parameter)
                index = index + 1
            
            if kwargs_name is None:
                kwargs_parameter = None
            else:
                kwargs_parameter = Parameter()
                kwargs_parameter.name = kwargs_name
                try:
                    annotation = annotations[kwargs_name]
                except KeyError:
                    kwargs_parameter.has_annotation = False
                    kwargs_parameter.annotation = None
                else:
                    kwargs_parameter.has_annotation = True
                    kwargs_parameter.annotation = annotation
                
                kwargs_parameter.has_default = False
                kwargs_parameter.default = None
                kwargs_parameter.positionality = PARAMETER_TYPE_KWARGS
                kwargs_parameter.reserved = False
                parameters.append(kwargs_parameter)
        
        else:
            args_parameter = None
            kwargs_parameter = None
        
        self = object.__new__(cls)
        self.parameters = parameters
        self.args_parameter = args_parameter
        self.kwargs_parameter = kwargs_parameter
        self.callable = callable_
        self.method_allocation = method_allocation
        self.real_function = real_function
        self.instance_to_async = instance_to_async
        return self
    
    
    def __eq__(self, other):
        """Returns whether the two analyzers are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.callable != other.callable:
            return False
        
        return True
    
    
    def __mod__(self, other):
        """Returns whether the two analyzers kinda match."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.instance_to_async != other.instance_to_async:
            return False
        
        for self_parameter, other_parameter in zip_longest(
            self.iter_non_reserved_parameters(), other.iter_non_reserved_parameters()
        ):
            if self_parameter != other_parameter:
                return False
        
        return True
    
    
    def is_async(self):
        """
        Returns whether the analyzed callable is async.
        
        Returns
        -------
        is_async : `bool`
        """
        if self.instance_to_async == INSTANCE_TO_ASYNC_FALSE:
            return True
        
        return False
    
    
    def is_async_generator(self):
        """
        Returns whether the analyzed callable is an async generator.
        
        Returns
        is_async_generator : `bool`
        """
        if self.instance_to_async == INSTANCE_TO_ASYNC_GENERATOR_FALSE:
            return True
        
        return False
    
    
    def can_instance_to_async_callable(self):
        """
        Returns whether the analyzed callable can be instanced to async.
        
        Returns
        -------
        can_instance_to_async_callable : `bool`
        """
        if self.instance_to_async != INSTANCE_TO_ASYNC_TRUE:
            return False
        
        for parameter in self.parameters:
            if parameter.reserved:
                continue
            
            if parameter.has_default:
                continue
            
            return False
        
        return True
    
    
    def can_instance_to_async_generator(self):
        """
        Returns whether the analyzed callable can be instanced to async.
        
        Returns
        -------
        can_instance_to_async_callable : `bool`
        """
        if self.instance_to_async != INSTANCE_TO_ASYNC_GENERATOR_TRUE:
            return False
        
        for parameter in self.parameters:
            if parameter.reserved:
                continue
            
            if parameter.has_default:
                continue
            
            return False
        
        return True
    
    
    # call `.can_instance_async_callable`, `.can_instance_to_async_generator` before
    def instance(self):
        """
        Instances the analyzed callable.
        
        Should be called only after a ``.can_instance_async_callable`` call, if it returned `True`.
        
        Returns
        -------
        instance_to_async_callable : `object`
        """
        return self.callable()
    
    
    def get_non_default_keyword_only_parameter_count(self):
        """
        Returns the amount of non default keyword only parameters of the analyzed callable.
        
        Returns
        -------
        non_default_keyword_only_parameter_count : `int`
        """
        count = 0
        for value in self.parameters:
            if not value.is_keyword_only():
                continue
            
            if value.has_default:
                break
            
            count += 1
            continue
        
        return count
    
    
    def get_non_reserved_keyword_only_parameters(self):
        """
        Returns the non reserved keyword only parameters of the analyzed callable.
        
        Returns
        -------
        non_default_keyword_only_parameters : `int`
        """
        result = []
        for parameter in self.parameters:
            if not parameter.is_keyword_only():
                continue
            
            if parameter.reserved:
                continue
            
            result.append(parameter)
            continue
        
        return result
    
    
    def get_non_reserved_positional_parameters(self):
        """
        Returns the non reserved positional parameters of the analyzed callable.
        
        Returns
        -------
        non_reserved_positional_parameters : `list` of ``Parameter``
        """
        result = []
        for parameter in self.parameters:
            if not parameter.is_positional():
                break
            
            if parameter.reserved:
                continue
            
            result.append(parameter)
            continue
        
        return result
    
    
    def get_non_reserved_positional_parameter_count(self):
        """
        Returns the amount of the non reserved positional parameters of the analyzed callable.
        
        Returns
        -------
        non_reserved_positional_parameters : `int`
        """
        count = 0
        for parameter in self.parameters:
            if not parameter.is_positional():
                break
            
            if parameter.reserved:
                continue
            
            count += 1
            continue
        
        return count
    
    
    def get_non_reserved_non_default_parameter_count(self):
        """
        Returns the amount of the non reserved non default parameters of the analyzed callable.
        
        Returns
        -------
        non_reserved_non_default_parameter_count : `int`
        """
        count = 0
        for parameter in self.parameters:
            if not parameter.is_positional():
                break
            
            if parameter.reserved:
                continue
            
            if parameter.has_default:
                continue
            
            count += 1
            continue
        
        return count
    
    
    def get_non_reserved_positional_parameter_range(self):
        """
        Returns the minimal and the maximal amount how much non reserved positional parameters the analyzed callable
        expects / accepts.
        
        Returns
        -------
        start : `int`
            The minimal amount of non reserved parameters, what the analyzed callable expects.
        end : `int`
            The maximal amount of non reserved parameters, what the analyzed callable accepts.
        
        Notes
        -----
        `*args` parameter is ignored from the calculation.
        """
        parameters = self.parameters
        length = len(parameters)
        index = 0
        start = 0
        
        while index < length:
            parameter = parameters[index]
            if not parameter.is_positional():
                return start, start
            
            if parameter.reserved:
                index += 1
                continue
            
            if parameter.has_default:
                start = index
                break
            
            index += 1
            start += 1
            continue
        
        else:
            return start, start
        
        end = start
        while index < length:
            if not parameter.is_positional():
                return start, end
            
            index += 1
            
            if parameter.reserved:
                continue
            
            end += 1
            continue
        
        return start, end
    
    
    def accepts_args(self):
        """
        Returns whether the analyzed callable accepts `*args` parameter.
        
        Returns
        -------
        accepts_args : `bool`
        """
        return (self.args_parameter is not None)
    
    
    def accepts_kwargs(self):
        """
        Returns whether the analyzed callable accepts `**kwargs` parameter.
        
        Returns
        -------
        accepts_kwargs : `bool`
        """
        return (self.kwargs_parameter is not None)
    
    
    def get_parameter(self, parameter_name):
        """
        Returns the parameter for the given name.
        
        Parameters
        ----------
        parameter_name : `str`
            The parameter's name.
        
        Returns
        -------
        parameter : `None, ``Parameter``
        """
        for parameter in self.parameters:
            if parameter.name == parameter_name:
                return parameter
    
    
    def has_parameter(self, parameter_name):
        """
        Returns whether the analyzed callable has the given parameter by name.
        
        Parameters
        ----------
        parameter_name : `str`
            The parameter's name.
        
        Returns
        -------
        has_parameter : `bool`
        """
        for parameter in self.parameters:
            if parameter.name == parameter_name:
                return True
        
        return False
    
    
    def iter_non_reserved_parameters(self):
        """
        Iterates over the non-reserved parameters of the analyzer.
        
        This method is an iterable generator.
        
        Yields
        ------
        parameter : ``Parameter``
        """
        for parameter in self.parameters:
            if not parameter.reserved:
                yield parameter


class RichAnalyzerParameterAccess:
    """
    Parameter access of a ``RichAnalyzer``.
    
    Attributes
    ----------
    _analyzer : ``CallableAnalyzer``
        Analyzer analyzing the respective function.
    """
    def __new__(cls, analyzer):
        self = object.__new__(cls)
        self._analyzer = analyzer
        return self
    
    
    def __getattr__(self, attribute_name):
        """
        Tries to find the specified attribute of the respective function.
        
        Returns
        -------
        parameter : ``Parameter``
        
        Raises
        ------
        AttributeError
            - If the parameter by the specified name is not found.
        """
        for parameter in self._analyzer.parameters:
            if parameter.name == attribute_name:
                return parameter
        
        raise AttributeError(attribute_name)


class RichAnalyzer:
    """
    Analyzer supporting rich access.
    
    Attributes
    ----------
    _analyzer : ``CallableAnalyzer``
        Analyzer analyzing the respective function.
    """
    def __new__(cls, callable_, as_method = False):
        """
        Analyzes the given callable.
        
        Parameters
        ----------
        callable_ : `callable`
            The callable to analyze.
        as_method : `bool` = `False`, Optional
            Whether the given `callable` is given as a `function`, but it should be analyzed as a `method`. Defaults
            to `False`.
        
        Raises
        ------
        TypeError
            If the given object is not callable, or could not be used as probably intended.
        """
        analyzer = CallableAnalyzer(callable_, as_method = as_method)
        
        self = object.__new__(cls)
        self._analyzer = analyzer
        return self
    
    
    @property
    def name(self):
        """
        Returns the name of the analyzed callable.
        
        Returns
        -------
        name : `str`
        """
        return self._analyzer.__name__
    
    
    @property
    def parameters(self):
        """
        Returns parameter access to the
        Returns
        -------
        parameter_access : RichAnalyzerParameterAccess
        """
        return RichAnalyzerParameterAccess(self._analyzer)
