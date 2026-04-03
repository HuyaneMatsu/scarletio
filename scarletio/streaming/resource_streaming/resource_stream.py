__all__ = ('ResourceStream',)

from ...utils import RichAttributeErrorBaseType


class ResourceStream(RichAttributeErrorBaseType):
    """
    Encapsulates a function with its call parameters as a reusable stream.
    
    Attributes
    ----------
    function : `FunctionType`
        The function to call.
    
    keyword_parameters : `dict<str, object>`
        Keyword parameters to call the function with.
    
    positional_parameters : `tuple<object>`
        Positional parameters to call the function with.
    """
    __slots__ = ('function', 'keyword_parameters', 'positional_parameters')
    
    def __new__(cls, function, *positional_parameters, **keyword_parameters):
        """
        Creates a new resource stream instance.
        
        Parameters
        ----------
        function : `FunctionType`
            The function to call.
        
        *positional_parameters : Positional parameters
            Positional parameters to call the function with.
        
        *keyword_parameters : Keyword parameters
            Keyword parameters to call the function with.
        """
        self = object.__new__(cls)
        self.function = function
        self.positional_parameters = positional_parameters
        self.keyword_parameters = keyword_parameters
        return self
    
    
    @classmethod
    def from_fields(cls, function, positional_parameters, keyword_parameters):
        """
        Creates a new resource stream instance from the given fields.
        
        Parameters
        ----------
        function : `FunctionType`
            The function to call.
        
        positional_parameters : `tuple<object>`
            Positional parameters to call the function with.
        
        keyword_parameters : `dict<str, object>`
            Keyword parameters to call the function with.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.function = function
        self.positional_parameters = positional_parameters
        self.keyword_parameters = keyword_parameters
        return self
    
    
    def __aiter__(self):
        """
        Calls the wrapped function returning the coroutine generator to async iterate over.
        
        Returns
        -------
        coroutine_generator : ``CoroutineGeneratorType``
        """
        return self.function(*self.positional_parameters, **self.keyword_parameters)
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__, ' streaming ']
        
        function = self.function
        try:
            function_name = function.__name__
        except AttributeError:
            function_name = type(function).__name__
        
        repr_parts.append(function_name)
        repr_parts.append('(')
        
        field_added = False
        
        for positional_parameter in self.positional_parameters:
            if field_added:
                repr_parts.append(', ')
            else:
                field_added = True
            
            repr_parts.append(repr(positional_parameter))
        
        for keyword_parameter_name, keyword_parameter_value in self.keyword_parameters.items():
            if field_added:
                repr_parts.append(', ')
            else:
                field_added = True
            
            repr_parts.append(keyword_parameter_name)
            repr_parts.append(' = ')
            repr_parts.append(repr(keyword_parameter_value))
        
        repr_parts.append(')>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # function
        if self.function != other.function:
            return False
        
        # positional_parameters
        if self.positional_parameters != other.positional_parameters:
            return False
        
        # keyword_parameters
        if self.keyword_parameters != other.keyword_parameters:
            return False
        
        return True
