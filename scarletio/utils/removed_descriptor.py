__all__ = ('RemovedDescriptor', )

from .docs import has_docs


@has_docs
class RemovedDescriptor:
    """
    A descriptor, what can be used to overwrite a class's attribute, what should be inherited anyways.
    
    Attributes
    ----------
    name : `None`, `str`
        The name of the attribute. Set when the class is finalizing.
    """
    __slots__ = ('name',)
    def __init__(self,):
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, type_):
        name = self.name
        if name is None:
            raise RuntimeError(f'`{self.__class__.__name__}` is not initialized correctly yet.')
        
        if obj is None:
            error_message = f'Type object `{type_.__name__!r}` has no attribute {name!r}'
        else:
            error_message = f'`{obj.__class__.__name__}` object has no attribute {name!r}'
        
        raise AttributeError(error_message)
    
    def __set__(self, obj, value):
        name = self.name
        if name is None:
            raise RuntimeError(f'`{self.__class__.__name__}` is not initialized correctly yet.')
        
        raise AttributeError(name)
    
    def __delete__(self, obj):
        name = self.name
        if name is None:
            raise RuntimeError(f'`{self.__class__.__name__}` is not initialized correctly yet.')
        
        raise AttributeError(name)
