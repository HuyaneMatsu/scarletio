__all__ = ('methodize',)

from types import MethodType

from .docs import has_docs


@has_docs
class methodize:
    """
    Wraps a type to as a method, allowing instancing it with it's parent instance object passed by default.
    
    Attributes
    ----------
    klass : `type`
        The type to instance as a method.
    """
    __slots__ = ('klass',)
    
    @has_docs
    def __init__(self, klass):
        """
        Creates a new ``methodize`` with the given class.
        
        Parameters
        ----------
        klass : `type`
             The type to instance as a method.
        """
        self.klass = klass
    
    def __get__(self, obj, type_):
        klass = self.klass
        if obj is None:
            return klass
        
        return MethodType(klass, obj)
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')
