__all__ = ('KeepType',)

from .docs import has_docs


@has_docs
class KeepType:
    """
    A decorator, what can be used to add features to an already existing class, by defining a new one, what will extend
    the old one's functionality.
    
    Note, that already existing attributes will not be overwritten and neither of the followingly named attributes
    either:
        - `__name__`
        - `__qualname__`
        - `__weakref__`
        - `__dict__`
        - `__slots__`
    
    Attributes
    ----------
    old_class : `type`
        The old class to extend.
    
    Class Attributes
    ----------------
    _ignored_attr_names : `set` of `str`
        Attribute names to ignore when extending.
    """
    __slots__ = ('old_class',)
    
    _ignored_attr_names = frozenset(('__name__', '__qualname__', '__weakref__', '__dict__', '__slots__', '__module__'))
    
    @has_docs
    def __new__(cls, old_class, *, new_class = None):
        """
        Creates a new ``KeepType`` with given `old_class` to extend. Can be used as a decorator if `new_class`
        parameter is not given.
        
        Parameters
        ----------
        old_class : `type`
            The old class to extend.
        new_class : `None`, `type` = `None`, Optional (Keyword only)
            The new class to extend the old class's functionality with.
        
        Returns
        -------
        obj : ``KeepType``, `type`
            If only `old_class` attribute is given, then returns itself enabling using it as a decorator, but if
            `new_class` is given as well, then returns the extended `old_class`.
        """
        self = object.__new__(cls)
        self.old_class = old_class
        
        if new_class is None:
            return self
        
        return self(new_class)
    
    @has_docs
    def __call__(self, new_class):
        """
        Calls the ``KeepType`` extending it's old ``.old_class`` with the new given `new_class`.
        
        Parameters
        ----------
        new_class : `type`
            The new class to extend the old class's functionality with.
        
        Returns
        -------
        old_class : `type`
            The extended old class.
        """
        old_class = self.old_class
        ignored_attr_names = self._ignored_attr_names
        for attribute_name in dir(new_class):
            if attribute_name in ignored_attr_names:
                continue
            
            attribute_value = getattr(new_class, attribute_name)
            if (attribute_name == '__doc__') and (attribute_value is None):
                continue
            
            if hasattr(object, attribute_name) and (attribute_value is getattr(object, attribute_name)):
                continue
            
            setattr(old_class, attribute_name, attribute_value)
        
        return old_class
