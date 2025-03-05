__all__ = ('MethodLike',)

from types import MethodType

from .docs import has_docs


@has_docs
class SubCheckType(type):
    """
    A meta-type that can be used for sub-type checks. It's type instances should implement a `.__sub_types__`
    type attribute that contains all of it's "sub-types".
    """
    @has_docs
    def __instancecheck__(cls, instance):
        """Returns whether the given instance's type is a sub-type of the respective type."""
        return (type(instance) in cls.__sub_types__)
    
    @has_docs
    def __subclasscheck__(cls, klass):
        """Returns whether the given type is a sub-type of the respective type."""
        return (klass in cls.__sub_types__)


@has_docs
class MethodLike(metaclass = SubCheckType):
    """
    Base class for methods.
    
    Type Attributes
    ---------------
    __sub_types__ : `set<type>`
        Registered method types.
    
    __reserved_parameter_count__ : `int` = `1`
        The amount of reserved parameters by a method subclass.
    """
    __sub_types__ = {MethodType}
    __slots__ = ()
    
    def __init_subclass__(cls):
        cls.__sub_types__.add(cls)
    
    __reserved_parameter_count__ = 1
    
    @classmethod
    @has_docs
    def get_reserved_parameter_count(cls, instance):
        """
        Returns the given `instance`'s reserved argcount.
        
        Parameters
        ----------
        instance : `method-like`
            A method like object.
        
        Returns
        -------
        reserved_parameter : `int`
            Reserved argcount of the given method like.
        
        Raises
        ------
        TypeError
            If `instance` is not given as a `method-like`.
        """
        instance_type = type(instance)
        reserved_parameter = getattr(instance_type, '__reserved_parameter_count__', -1)
        if reserved_parameter != -1:
            return reserved_parameter
        
        if instance_type in cls.__sub_types__:
            return cls.__reserved_parameter_count__
        
        raise TypeError(
            f'Expected a method like, got {instance_type.__name__}; {instance!r}.'
        )
