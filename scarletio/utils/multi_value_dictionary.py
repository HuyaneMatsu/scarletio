__all__ = ('MultiValueDictionary', )

from .docs import has_docs
from .removed_descriptor import RemovedDescriptor

@has_docs
class _MultiValueDictionaryItemIterator:
    """
    ``MultiValueDictionary`` item iterator.
    
    Attributes
    ----------
    _parent : ``MultiValueDictionary``
        The parent MultiValueDictionary.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new ``MultiValueDictionary`` item iterator.
        
        Parameters
        ----------
        parent : ``MultiValueDictionary``
            The parent multi value dictionary.
        """
        self._parent = parent
    
    
    @has_docs
    def __len__(self):
        """Returns the respective ``MultiValueDictionary``'s length."""
        return len(self._parent)
    
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the respective ``MultiValueDictionary``'s items.
        
        This method is a generator.
        
        Yields
        -------
        item : `tuple` (`Any`, `Any`)
            Items of the respective MultiValueDictionary as `key` - `value` pairs.
        """
        for key, values in dict.items(self._parent):
            for value in values:
                yield key, value
    
    
    @has_docs
    def __contains__(self, item):
        """Returns whether the respective MultiValueDictionary contains the given item."""
        key, value = item
        parent = self._parent
        try:
            values = parent[key]
        except KeyError:
            return False
        return value in values


@has_docs
class _MultiValueDictionaryValueIterator:
    """
    ``MultiValueDictionary`` value iterator.
    
    Attributes
    ----------
    _parent : ``MultiValueDictionary``
        The parent MultiValueDictionary.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new ``MultiValueDictionary`` value iterator.
        
        Parameters
        ----------
        parent : ``MultiValueDictionary``
            The parent MultiValueDictionary.
        """
        self._parent = parent
    
    @has_docs
    def __len__(self):
        """Returns the respective ``MultiValueDictionary``'s length."""
        return len(self._parent)
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the respective ``MultiValueDictionary``'s values.
        
        This method is a generator.
        
        Yields
        -------
        value : `Any`
            Values of the respective MultiValueDictionary.
        """
        for values in dict.values(self._parent):
            yield from values
    
    @has_docs
    def __contains__(self, value):
        """Returns whether the respective MultiValueDictionary contains the given value."""
        for values in dict.values(self._parent):
            if value in values:
                return True
        return False


@has_docs
class MultiValueDictionary(dict):
    """
    Dictionary subclass, which can hold multiple values bound to a single key.
    """
    __slots__ = ()
    
    @has_docs
    def __init__(self, iterable=None):
        """
        Creates a new ``MultiValueDictionary`` instance.
        
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
        
        if isinstance(iterable, MultiValueDictionary):
            for key, values in dict.items(iterable):
                setitem(self, key, values.copy())
        
        elif isinstance(iterable, dict):
            for key, value in iterable.items():
                setitem(self, key, [value])
        
        else:
            for key, value in iterable:
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
        return dict.__getitem__(self, key)[0]
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the MultiValueDictionary."""
        try:
            line = dict.__getitem__(self, key)
        except KeyError:
            dict.__setitem__(self, key, [value])
        else:
            if value not in line:
                line.append(value)
    
    @has_docs
    def __delitem__(self, key):
        """
        Removes the `value` for the given `key` from the MultiValueDictionary. If the `key` has more values, then removes only
        the 0th of them.
        """
        my_list = dict.__getitem__(self, key)
        if len(my_list) == 1:
            dict.__delitem__(self, key)
        else:
            del my_list[0]
    
    @has_docs
    def extend(self, mapping):
        """
        Extends the MultiValueDictionary with the given `mapping`'s items.
        
        Parameters
        ----------
        mapping : `Any`
            Any mapping type, what has `.items` attribute.
        """
        getitem = dict.__getitem__
        setitem = dict.__setitem__
        for key, value in mapping.items():
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
        try:
            return dict.__getitem__(self, key).copy()
        except KeyError:
            return default
    
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
        try:
            values = dict.__getitem__(self, key)
        except KeyError:
            return default
        else:
            return values[0]
    
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
        try:
            values = dict.__getitem__(self, key)
        except KeyError:
            pass
        else:
            return values[0]
        
        dict.__setitem__(self, key, [default])
        return default
    
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
        try:
            return dict.pop(self, key)
        except KeyError:
            if default is not ...:
                return default
            raise
    
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
        try:
            values = dict.__getitem__(self, key)
        except KeyError:
            if default is not ...:
                return default
            raise
        else:
            value = values.pop(0)
            if not values:
                dict.__delitem__(self, key)
            
            return value
    
    pop = pop_one
    
    # inheritable:
    @has_docs
    def copy(self):
        """
        Copies the MultiValueDictionary.
        
        Returns
        -------
        new : ``MultiValueDictionary`` instance
            The new MultiValueDictionary.
        """
        new = dict.__new__(type(self))
        setitem = dict.__setitem__
        for key, values in dict.items(self):
            setitem(new, key, values.copy())
        
        return new
    
    @has_docs
    def items(self):
        """
        Returns an item iterator for the MultiValueDictionary.
        
        Returns
        -------
        items : ``_MultiValueDictionaryItemIterator``
        """
        return _MultiValueDictionaryItemIterator(self)
    
    @has_docs
    def values(self):
        """
        Returns a value iterator for the MultiValueDictionary.
        
        Returns
        -------
        items : ``_MultiValueDictionaryValueIterator``
        """
        return _MultiValueDictionaryValueIterator(self)
    
    @has_docs
    def __repr__(self):
        """Returns the MultiValueDictionary's representation."""
        result = [
            self.__class__.__name__,
            '({',
                ]
        
        if self:
            for key, value in self.items():
                result.append(repr(key))
                result.append(': ')
                result.append(repr(value))
                result.append(', ')
            
            result[-1] = '})'
        else:
            result.append('})')
        
        return ''.join(result)
    
    __str__ = __repr__
    
    @has_docs
    def kwargs(self):
        """
        Converts the MultiValueDictionary to `**kwargs`-able dictionary. If a `key` has more values, then always returns the last
        value for it.
        
        Returns
        -------
        result : `dict` of (`Any`, `Any`) items
        """
        result = {}
        for key, values in dict.items(self):
            result[key] = values[-1]
        
        return result
    
    update = RemovedDescriptor()
