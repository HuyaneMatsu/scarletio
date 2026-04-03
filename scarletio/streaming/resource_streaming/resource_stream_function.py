__all__ = ('ResourceStreamFunction',)

from ...utils import MethodLike, RichAttributeErrorBaseType, docs_property

from .resource_stream import ResourceStream


class ResourceStreamFunction(RichAttributeErrorBaseType, MethodLike):
    __doc__ = docs_property()
    
    __type_doc__ = (
    """
    Helper to wrap a function into a reusable resource stream.
    
    Attributes
    ----------
    __func__ : ``FunctionType``
        The wrapped function.
    """)
    
    __slots__ = ('__func__',)
    
    __reserved_parameter_count__ = 0
    
    
    def __new__(cls, function):
        """
        Creates a new resource stream wrapper.
        
        Parameters
        ----------
        function : ``FunctionType``
            The function to wrap.
        """
        self = object.__new__(cls)
        self.__func__ = function
        return self
    
    
    def __call__(self, *positional_parameters, **keyword_parameters):
        """
        Calls the wrapped function with the given parameters.
        
        Parameters
        ----------
        *positional_parameters : Positional parameters
            Positional parameters to call the function with.
        
        *keyword_parameters : Keyword parameters
            Keyword parameters to call the function with.
        
        Returns
        -------
        resource_stream : ``ResourceStream``
        """
        return ResourceStream.from_fields(self.__func__, positional_parameters, keyword_parameters)
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__, ' wrapping ']
        
        function = self.__func__
        try:
            function_name = function.__name__
        except AttributeError:
            function_name = type(function).__name__
        
        repr_parts.append(function_name)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    @property
    def __instance_doc__(self):
        """
        Returns the wrapped function's documentation.
        
        Returns
        -------
        docstring : `None | str`
        """
        return self.__func__.__doc__
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # __func__
        if self.__func__ != other.__func__:
            return False
        
        return True
