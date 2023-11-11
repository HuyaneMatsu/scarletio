__all__ = ('BaseMethodDescriptor', 'BaseMethodType',)

from .docs import has_docs
from .method_like import MethodLike
from .properties import docs_property


@has_docs
class BaseMethodType(MethodLike):
    """
    A `method-like`, which always passes to it's function the respective type and an instance. The instance might be
    given as `None` if used as a classmethod.
    
    Attributes
    ----------
    __base__ : `object`
        The instance from where the method was called from. Might be `None` if used as a classmethod.
    __func__ : `function`
        The method's function to call.
    __self__ : `type`
        The class from where the method was called from.
    
    Class Attributes
    ----------------
    __reserved_argcount__ : `int` = `2`
        The amount of reserved parameters by BaseMethodTypes.
    """
    __slots__ = ('__base__', '__func__', '__self__', )
    
    __reserved_argcount__ = 2
    
    @has_docs
    def __init__(self, func, cls, base):
        """
        Creates a new BaseMethodType with the given parameters.
        
        Parameters
        ----------
        func : `function`
            The method's function to call.
        cls : `type`
            The class from where the method was called from.
        base : `object`
            The instance from where the method was called from. Can be given as `None` as well.
        """
        self.__base__ = base
        self.__func__ = func
        self.__self__ = cls
    
    @has_docs
    def __call__(self, *args, **kwargs):
        """
        Calls the BaseMethodType with the given parameters.
        
        Parameters
        ----------
        *args : Parameters
            Parameters to call the internal function with.
        **kwargs : Keyword parameters
            Keyword parameters to call the internal function with.
        
        Returns
        -------
        result : `object`
            The object returned by the internal function.
        
        Raises
        ------
        BaseException
            Exception raised by the internal function.
        """
        return self.__func__(self.__self__, self.__base__, *args, **kwargs)
    
    def __getattr__(self,name):
        return getattr(self.__func__, name)
    
    __class_doc__ = None
    
    @property
    @has_docs
    def __instance__doc__(self):
        """
        Returns the ``BaseMethodType``'s internal function's docstring.
        
        Returns
        -------
        docstring : `None`, `str`
        """
        return self.__func__.__doc__
    
    __doc__ = docs_property()

@has_docs
class BaseMethodDescriptor:
    """
    Descriptor, which can be used as a decorator to wrap a function to a BaseMethodType.
    
    Attributes
    ----------
    fget : `function`
        The wrapped function.
    """
    __slots__ = ('fget',)
    
    @has_docs
    def __init__(self, fget):
        """
        Creates a new ``BaseMethodDescriptor`` with the given parameter.
        
        Parameters
        ----------
        fget : `function`
            The function to wrap.
        """
        self.fget = fget
    
    def __get__(self, obj, type_):
        return BaseMethodType(self.fget, type_, obj)
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')
