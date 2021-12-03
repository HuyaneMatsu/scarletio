__all__ = ('IgnoreCaseMultiValueDictionary', )

from .docs import has_docs
from .multi_value_dictionary import MultiValueDictionary
from .ignore_case_string import IgnoreCaseString

@has_docs
class IgnoreCaseMultiValueDictionary(MultiValueDictionary):
    """
    ``MultiValueDictionary`` subclass, what can be used to hold http headers.
    
    It's keys ignore casing.
    """
    __slots__ = ()
    
    @has_docs
    def __init__(self, iterable=None):
        """
        Creates a new ``IgnoreCaseMultiValueDictionary`` instance.
        
        Parameters
        ----------
        iterable : `None` or `iterable`, Optional
            Iterable to update the created MultiValueDictionary initially.
            
            Can be given as one of the following:
                - ``MultiValueDictionary`` instance.
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
        
        elif isinstance(iterable, MultiValueDictionary):
            for key, values in dict.items(iterable):
                setitem(self, IgnoreCaseString(key), values.copy())
        
        elif isinstance(iterable, dict):
            for key, value in iterable.items():
                key = IgnoreCaseString(key)
                setitem(self, key, [value])
        
        else:
            for key, value in iterable:
                key = IgnoreCaseString(key)
                try:
                    values = getitem(self, key)
                except KeyError:
                    setitem(self, key, [value])
                else:
                    values.append(value)
    
    @has_docs
    def __getitem__(self, key):
        """
        Returns the MultiValueDictionary's `value` for the given `key`. If the `key` has more values, then returns the 0th of
        them.
        """
        key = IgnoreCaseString(key)
        return dict.__getitem__(self, key)[0]
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the MultiValueDictionary."""
        key = IgnoreCaseString(key)
        MultiValueDictionary.__setitem__(self, key, value)
    
    @has_docs
    def __delitem__(self, key):
        """
        Removes the `value` for the given `key` from the MultiValueDictionary. If the `key` has more values, then removes only
        the 0th of them.
        """
        key = IgnoreCaseString(key)
        MultiValueDictionary.__delitem__(self, key)
    
    @has_docs
    def extend(self, mapping):
        """
        Extends the MultiValueDictionary titled with the given `mapping`'s items.
        
        Parameters
        ----------
        mapping : `Any`
            Any mapping type, what has `.items` attribute.
        """
        getitem = dict.__getitem__
        setitem = dict.__setitem__
        for key, value in mapping.items():
            key = IgnoreCaseString(key)
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
            Default value to return if `key` is not present in the MultiValueDictionary. Defaults to `None`.
        
        Returns
        -------
        values : `default or `list` of `Any`
            The values for the given `key` if present.
        """
        key = IgnoreCaseString(key)
        return MultiValueDictionary.get_all(self, key, default)
    
    @has_docs
    def get_one(self, key, default=None):
        """
        Returns the 0th value matching the given `key`.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the MultiValueDictionary. Defaults to `None`.
        
        Returns
        -------
        value : `default` or `Any`
            The value for the given key if present.
        """
        key = IgnoreCaseString(key)
        return MultiValueDictionary.get_one(self, key, default)
    
    get = get_one
    
    @has_docs
    def setdefault(self, key, default=None):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the MultiValueDictionary, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to set and return if `key` is not present in the MultiValueDictionary.
        
        Returns
        -------
        value : `default` or `Any`
            The first value for which `key` matched, or `default` if none.
        """
        key = IgnoreCaseString(key)
        return MultiValueDictionary.setdefault(self, key, default)
    
    @has_docs
    def pop_all(self, key, default=...):
        """
        Removes all the values from the MultiValueDictionary which the given `key` matched.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the MultiValueDictionary.
        
        Returns
        -------
        values : `default` or `list` of `Any`
            The matched values. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the MultiValueDictionary and `default` value is not given either.
        """
        key = IgnoreCaseString(key)
        return MultiValueDictionary.pop_all(self, key, default)
    
    @has_docs
    def pop_one(self, key, default=...):
        """
        Removes the first value from the MultiValueDictionary, which matches the given `key`.
        
        Parameters
        ----------
        key : `Any`
            The key to match.
        default : `Any`, Optional
            Default value to return if `key` is not present in the MultiValueDictionary.
        
        Returns
        -------
        value : `default` or `list` of `Any`
            The 0th matched value. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the MultiValueDictionary and `default` value is not given either.
        """
        key = IgnoreCaseString(key)
        return MultiValueDictionary.pop_one(self, key, default)
    
    pop = pop_one
