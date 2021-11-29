__all__ = ('multidict', )

from .docs import has_docs
from .removed_descriptor import RemovedDescriptor

@has_docs
class _multidict_items:
    """
    ``multidict`` item iterator.
    
    Attributes
    ----------
    _parent : ``multidict``
        The parent multidict.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new ``multidict`` item iterator.
        
        Parameters
        ----------
        parent : ``multidict``
            The parent multidict.
        """
        self._parent = parent
    
    
    @has_docs
    def __len__(self):
        """Returns the respective ``multidict``'s length."""
        return len(self._parent)
    
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the respective ``multidict``'s items.
        
        This method is a generator.
        
        Yields
        -------
        item : `tuple` (`Any`, `Any`)
            Items of the respective multidict as `key` - `value` pairs.
        """
        for key, values in dict.items(self._parent):
            for value in values:
                yield key, value
    
    
    @has_docs
    def __contains__(self, item):
        """Returns whether the respective multidict contains the given item."""
        key, value = item
        parent = self._parent
        try:
            values = parent[key]
        except KeyError:
            return False
        return value in values


@has_docs
class _multidict_values:
    """
    ``multidict`` value iterator.
    
    Attributes
    ----------
    _parent : ``multidict``
        The parent multidict.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new ``multidict`` value iterator.
        
        Parameters
        ----------
        parent : ``multidict``
            The parent multidict.
        """
        self._parent = parent
    
    @has_docs
    def __len__(self):
        """Returns the respective ``multidict``'s length."""
        return len(self._parent)
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the respective ``multidict``'s values.
        
        This method is a generator.
        
        Yields
        -------
        value : `Any`
            Values of the respective multidict.
        """
        for values in dict.values(self._parent):
            yield from values
    
    @has_docs
    def __contains__(self, value):
        """Returns whether the respective multidict contains the given value."""
        for values in dict.values(self._parent):
            if value in values:
                return True
        return False

@has_docs
class multidict(dict):
    """
    Dictionary subclass, which can hold multiple values bound to a single key.
    """
    __slots__ = ()
    
    @has_docs
    def __init__(self, iterable=None):
        """
        Creates a new ``multidict`` instance.
        
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
        
        if isinstance(iterable, multidict):
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
        Returns the multidict's `value` for the given `key`. If the `key` has more values, then returns the 0th of
        them.
        """
        return dict.__getitem__(self, key)[0]
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the multidict."""
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
        Removes the `value` for the given `key` from the multidict. If the `key` has more values, then removes only
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
        Extends the multidict with the given `mapping`'s items.
        
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
            Default value to return if `key` is not present in the multidict. Defaults to `None`.
        
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
            Default value to return if `key` is not present in the multidict. Defaults to `None`.
        
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
        try:
            return dict.pop(self, key)
        except KeyError:
            if default is not ...:
                return default
            raise
    
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
        Copies the multidict.
        
        Returns
        -------
        new : ``multidict`` instance
            The new multidict.
        """
        new = dict.__new__(type(self))
        setitem = dict.__setitem__
        for key, values in dict.items(self):
            setitem(new, key, values.copy())
        
        return new
    
    @has_docs
    def items(self):
        """
        Returns an item iterator for the multidict.
        
        Returns
        -------
        items : ``_multidict_items``
        """
        return _multidict_items(self)
    
    @has_docs
    def values(self):
        """
        Returns a value iterator for the multidict.
        
        Returns
        -------
        items : ``_multidict_values``
        """
        return _multidict_values(self)
    
    @has_docs
    def __repr__(self):
        """Returns the multidict's representation."""
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
        Converts the multidict to `**kwargs`-able dictionary. If a `key` has more values, then always returns the last
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
