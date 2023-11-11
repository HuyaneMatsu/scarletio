__all__ = ('cached_property', 'class_property', 'docs_property', 'module_property', 'name_property',)

from .docs import has_docs


NoneType = type(None)


@has_docs
class docs_property:
    """
    Property to return the class's docs if called from class, else the given object.
    """
    __slots__ = ()
    
    @has_docs
    def __init__(self):
        """
        Creates a new docs property.
        """
    
    def __get__(self, obj, type_):
        if obj is None:
            return type_.__class_doc__
        else:
            return obj.__instance_doc__
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')


@has_docs
class name_property:
    """
    Property to return the class's name if called from the respective class.
    
    Attributes
    ----------
    class_name : `str`
        The class's name.
    fget : `callable`
        Callable what's return will be returned, when called from an instance.
    """
    __slots__ = ('class_name', 'fget')
    
    @has_docs
    def __init__(self, name, fget):
        """
        Creates a new docs property.
        """
        self.class_name = name
        self.fget = fget
    
    def __get__(self, obj, type_):
        if obj is None:
            return type_.class_name
        else:
            return self.fget(obj)
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')


@has_docs
class module_property:
    """
    Instead of defining a  `.__module__` attribute as `property`, define it as `module_property` to avoid getter issues,
    when calling from class.
    
    Attributes
    ----------
    fget : `func`
        Getter used when calling the module from instance.
    module : `str`
        The module where the `module_property` was created.
    """
    __slots__ = ('fget', 'module', )
    
    def __new__(cls, fget):
        module = getattr(fget, '__module__', None)
        if module is None:
            module = cls.__module__
        elif type(module) is str:
            module = module
        elif isinstance(module, str):
            module = str(module)
        else:
            module = cls.__module__
        
        self = object.__new__(cls)
        self.fget = fget
        self.module = module
        return self
    
    def __get__(self, obj, type_):
        if obj is None:
            return self.module
        
        return self.fget()
    
    def __set__(self, obj, module):
        if module is None:
            module = self.__module__
        elif type(module) is str:
            module = module
        elif isinstance(module, str):
            module = str(module)
        else:
            module = self.__module__
        
        self.module = module
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')


class class_property:
    __doc__ = docs_property()
    
    __class_doc__ = ("""
    Class level property.
    
    Attributes
    ----------
    fget : `callable`
        getter method.
    fset : `callable`
        Setter method.
    fdel : `callable`
        Deleter method.
    __instance_doc__ : `object`
        Documentation for the property.
    """)
    
    def __new__(cls, fget = None, fset = None, fdel = None, doc = None):
        """
        Creates a new ``class_property`` from the given parameters.
        
        If `doc` is not given or given as `None`, it will default to `fget`'s if applicable.
        
        Parameters
        ----------
        fget : `None`, `callable` = `None`, Optional
            getter method.
        fset : `None`, `callable` = `None`, Optional
            Setter method.
        fdel : `None`, `callable` = `None`, Optional
            Deleter method.
        doc : `None`, `object` = `None`, Optional
            Documentation for the property.
        """
        if (doc is None) and (fget is not None):
            doc = fget.__doc__
        
        self = object.__new__(cls)
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__instance_doc__ = doc
        return self
    
    def __get__(self, obj, type_):
        getter = self.fget
        
        if getter is None:
            raise AttributeError('unreadable attribute')
        
        return getter(type_)
    
    def __set__(self, obj, value):
        setter = self.fset
        if setter is None:
            raise AttributeError('can\'t set attribute')
        
        return setter(type(obj), value)
    
    def __delete__(self, obj):
        deleter = self.fdel
        if deleter is None:
            raise AttributeError('can\'t delete attribute')
        
        return deleter(type(obj))
    
    def getter(self, fget):
        """
        Returns a new property with getter set.
        
        Parameters
        ----------
        fget : `callable`
            Getter method.
        
        Returns
        -------
        new : ``class_property``
        """
        return type(self)(fget, self.fset, self.fdel, self.__instance_doc__)
    
    def setter(self, fset):
        """
        Returns a new property with setter set.
        
        Parameters
        ----------
        fset : `callable`
            Setter method.
        
        Returns
        -------
        new : ``class_property``
        """
        return type(self)(self.fget, fset, self.fdel, self.__instance_doc__)
    
    def deleter(self, fdel):
        """
        Returns a new property with deleter set.
        
        Parameters
        ----------
        fdel : `callable`
            Deleter method.
        
        Returns
        -------
        new : ``class_property``
        """
        return type(self)(self.fget, self.fset, fdel, self.__instance_doc__)


@has_docs
class cached_property:
    """
    Cached property, what can be used as a method decorator. It operates almost like python's `@property`, but it puts
    the result of the method to the respective instance's `_cache`, preferably type `dict` attribute.
    
    Attributes
    ----------
    fget : `function`
        Getter method of the cached property.
    name : `str`
        The name of the cached property.
    """
    __slots__ = ('fget', 'name',)
    
    @has_docs
    def __new__(cls, fget):
        """
        Creates a new cached property instance with the given getter.
        
        Parameters
        ----------
        fget : `function`
            Getter method of the cached property.

        Raises
        ------
        TypeError
            If `fget` has no name or it's name is not `str`.
        """
        name = getattr(fget, '__name__', None)
        
        name_type = name.__class__
        if name_type is NoneType:
            name_type_correct = False
        elif name_type is str:
            name_type_correct = True
        elif issubclass(name_type, str):
            name = str(name)
            name_type_correct = True
        else:
            name_type_correct = False
        
        if not name_type_correct:
            raise TypeError(
                f'`fget.__name__` can be `str`, got {name_type.__name__}; {name!r}.'
            )
        
        self = object.__new__(cls)
        self.fget = fget
        self.name = name
        return self
    
    def __get__(self, obj, type_):
        if obj is None:
            return self
        
        value = obj._cache.get(self.name, ...)
        if value is ...:
            value = self.fget(obj)
            obj._cache[self.name] = value
        
        return value
    
    def __set__(self, obj, value):
        raise AttributeError('can\'t set attribute')
    
    def __delete__(self, obj):
        raise AttributeError('can\'t delete attribute')
