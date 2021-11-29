__all__ = ('multidict', )

from .docs import has_docs
from .multidict import multidict
from .istr import istr

@has_docs
class imultidict(multidict):
    """
    ``multidict`` subclass, what can be used to hold http headers.
    
    It's keys ignore casing.
    """
    __slots__ = ()
    
    @has_docs
    def __init__(self, iterable=None):
        """
        Creates a new ``imultidict`` instance.
        
        Parameters
        ----------
        iterable : `None` or `iterable`, Optional
            Iterable to update the created multidict initially.
            
            Can be given as one of the following:
                - ``multidict`` instance.
                - `dict` instance.
                - `iterable` of `key` - `value` pairs.
        """
        dict.__init__(self)
        
        if (iterable is None) or (not iterable):
            return
        
        getitem = dict.__getitem__
        setitem = dict.__setitem__
        
        if type(iterable) is type(self):
            for key, values in dict.items(iterable):
                setitem(self, key, values.copy())
        
        elif isinstance(iterable, multidict):
            for key, values in dict.items(iterable):
                setitem(self, istr(key), values.copy())
        
        elif isinstance(iterable, dict):
            for key, value in iterable.items():
                key = istr(key)
                setitem(self, key, [value])
        
        else:
            for key, value in iterable:
                key = istr(key)
                try:
                    values = getitem(self, key)
                except KeyError:
                    setitem(self, key, [value])
                else:
                    values.append(value)
    
    @has_docs
    def __getitem__(self, key):
        """
        Returns the multidict's `value` for the given `key`. If the `key` has more values, then returns the 0th of
        them.
        """
        key = istr(key)
        return dict.__getitem__(self, key)[0]
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the multidict."""
        key = istr(key)
        multidict.__setitem__(self, key, value)
    
    @has_docs
    def __delitem__(self, key):
        """
        Removes the `value` for the given `key` from the multidict. If the `key` has more values, then removes only
        the 0th of them.
        """
        key = istr(key)
        multidict.__delitem__(self, key)
    
    @has_docs
    def extend(self, mapping):
        """
        Extends the multidict titled with the given `mapping`'s items.
        
        Parameters
        ----------
        mapping : `Any`
            Any mapping type, what has `.items` attribute.
        """
        getitem = dict.__getitem__
        setitem = dict.__setitem__
        for key, value in mapping.items():
            key = istr(key)
            try:
                values = getitem(self, key)
            except KeyError:
                setitem(self, key, [value])
            else:
                if value not in values:
                    values.append(value)
    
    @has_docs
    def get_all(self, key, default=None):
        """
        Returns all the values matching the given `key`.
        
        Parameters
        ----------
        key : `Any`
            The `key` to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the multidict. Defaults to `None`.
        
        Returns
        -------
        values : `default or `list` of `Any`
            The values for the given `key` if present.
        """
        key = istr(key)
        return multidict.get_all(self, key, default)
    
    @has_docs
    def get_one(self, key, default=None):
        """
        Returns the 0th value matching the given `key`.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the multidict. Defaults to `None`.
        
        Returns
        -------
        value : `default` or `Any`
            The value for the given key if present.
        """
        key = istr(key)
        return multidict.get_one(self, key, default)
    
    get = get_one
    
    @has_docs
    def setdefault(self, key, default=None):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the multidict, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to set and return if `key` is not present in the multidict.
        
        Returns
        -------
        value : `default` or `Any`
            The first value for which `key` matched, or `default` if none.
        """
        key = istr(key)
        return multidict.setdefault(self, key, default)
    
    @has_docs
    def pop_all(self, key, default=...):
        """
        Removes all the values from the multidict which the given `key` matched.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the multidict.
        
        Returns
        -------
        values : `default` or `list` of `Any`
            The matched values. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the multidict and `default` value is not given either.
        """
        key = istr(key)
        return multidict.pop_all(self, key, default)
    
    @has_docs
    def pop_one(self, key, default=...):
        """
        Removes the first value from the multidict, which matches the given `key`.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the multidict.
        
        Returns
        -------
        value : `default` or `list` of `Any`
            The 0th matched value. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the multidict and `default` value is not given either.
        """
        key = istr(key)
        return multidict.pop_one(self, key, default)
    
    pop = pop_one
