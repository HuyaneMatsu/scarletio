__all__ = ('MethodLike',)

from types import MethodType

from .docs import has_docs


@has_docs
class SubCheckType(type):
    """
    Metaclass, which can be used for subclass checks. It's type instances should implement a `.__subclasses__`
    class attribute, which contains all of it's "subclasses".
    """
    @has_docs
    def __instancecheck__(cls, instance):
        """Returns whether the given instance's type is a subclass of the respective type."""
        return (type(instance) in cls.__subclasses__)
    
    @has_docs
    def __subclasscheck__(cls, klass):
        """Returns whether the given type is a subclass of the respective type."""
        return (klass in cls.__subclasses__)


@has_docs
class MethodLike(metaclass = SubCheckType):
    """
    Base class for methods.
    
    Class Attributes
    ----------------
    __subclasses__ : `set` of `type`
        Registered method types.
    __reserved_parameter_count__ : `int` = `1`
        The amount of reserved parameters by a method subclass.
    """
    __subclasses__ = {MethodType}
    __slots__ = ()
    def __init_subclass__(cls):
        cls.__subclasses__.add(cls)
    
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
        instance_type = instance.__class__
        reserved_parameter = getattr(instance_type, '__reserved_parameter_count__', -1)
        if reserved_parameter != -1:
            return reserved_parameter
        
        if instance_type in cls.__subclasses__:
            return cls.__reserved_parameter_count__
        
        raise TypeError(
            f'Expected a method like, got {instance_type.__name__}; {instance!r}.'
        )
