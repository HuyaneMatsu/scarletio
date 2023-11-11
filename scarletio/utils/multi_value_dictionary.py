__all__ = ('MultiValueDictionary', )

from .dict_iterator_bases import DictionaryItemIteratorBase, DictionaryValueIteratorBase
from .docs import copy_docs, has_docs
from .removed_descriptor import RemovedDescriptor
from .utils import is_iterable

@has_docs
class _MultiValueDictionaryItemIterator(DictionaryItemIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryItemIteratorBase.__len__)
    def __len__(self):
        length = 0
        
        for values in dict.values(self._parent):
            length += len(values)
        
        return length
    
    
    @copy_docs(DictionaryItemIteratorBase.__iter__)
    def __iter__(self):
        for key, values in dict.items(self._parent):
            for value in values:
                yield key, value
    
    
    @copy_docs(DictionaryItemIteratorBase.__contains__)
    def __contains__(self, item):
        if not isinstance(item, tuple):
            return False
        
        if len(item) != 2:
            return False
        
        key, value = item
        
        try:
            values = dict.__getitem__(self._parent, key)
        except KeyError:
            return False
        
        return value in values


@has_docs
class _MultiValueDictionaryValueIterator(DictionaryValueIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryValueIteratorBase.__len__)
    def __len__(self):
        length = 0
        
        for values in dict.values(self._parent):
            length += len(values)
        
        return length
    
    
    @copy_docs(DictionaryValueIteratorBase.__iter__)
    def __iter__(self):
        for values in dict.values(self._parent):
            yield from values
    
    
    @copy_docs(DictionaryValueIteratorBase.__contains__)
    def __contains__(self, value):
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
    def __init__(self, iterable = None):
        """
        Creates a new ``MultiValueDictionary``.
        
        Parameters
        ----------
        iterable : `None`, `iterable` = `None`, Optional
            Iterable to update the created dictionary initially.
            
            Can be given as one of the following:
                - ``MultiValueDictionary``.
                - `dict`.
                - `iterable` of `key` - `value` pairs.
        """
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
                    if value not in values:
                        values.append(value)
    
    
    @has_docs
    def __getitem__(self, key):
        """
        Returns the dictionary's `value` for the given `key`. If the `key` has more values, then returns the 0th of
        them.
        """
        return dict.__getitem__(self, key)[0]
    
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the dictionary."""
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
        Removes the `value` for the given `key` from the dictionary. If the `key` has more values, then removes only
        the 0th of them.
        """
        my_list = dict.__getitem__(self, key)
        if len(my_list) == 1:
            dict.__delitem__(self, key)
        else:
            del my_list[0]
    
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the dictionary equals to other."""
        if isinstance(other, type(self)):
            return dict.__eq__(self, other)
        
        if is_iterable(other):
            try:
                other = type(self)(other)
            except TypeError:
                return NotImplemented
            
            return dict.__eq__(self, other)
        
        return NotImplemented
    
    
    @has_docs
    def __ne__(self, other):
        """Returns whether the dictionary equals to other."""
        if isinstance(other, type(self)):
            return dict.__ne__(self, other)
        
        if is_iterable(other):
            try:
                other = type(self)(other)
            except TypeError:
                return NotImplemented
            
            return dict.__ne__(self, other)
        
        return NotImplemented
    
    
    @has_docs
    def __reduce__(self):
        """Reduces the dictionary to a picklable object."""
        return (type(self), list(self.items()))
    
    
    @has_docs
    def __reduce_ex__(self, version):
        """Reduces the dictionary to a picklable object."""
        return type(self).__reduce__(self)
    
    
    @has_docs
    def extend(self, mapping):
        """
        Extends the dictionary with the given `mapping`'s items.
        
        Parameters
        ----------
        mapping : `object`
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
    def get_all(self, key, default = None):
        """
        Returns all the values matching the given `key`.
        
        Parameters
        ----------
        key : `object`
            The `key` to match.
        default : `object` = `None`, Optional
            Default value to return if `key` is not present in the dictionary.
        
        Returns
        -------
        values : `default or `list` of `object`
            The values for the given `key` if present.
        """
        try:
            return dict.__getitem__(self, key).copy()
        except KeyError:
            return default
    
    
    @has_docs
    def get_one(self, key, default = None):
        """
        Returns the 0th value matching the given `key`.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object` = `None`, Optional
            Default value to return if `key` is not present in the dictionary.
        
        Returns
        -------
        value : `default`, `object`
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
    def setdefault(self, key, default = None):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the dictionary, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object` = `None`, Optional
            Default value to set and return if `key` is not present in the dictionary.
        
        Returns
        -------
        value : `default`, `object`
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
    def pop_all(self, key, default = ...):
        """
        Removes all the values from the dictionary which the given `key` matched.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object`, Optional
            Default value to return if `key` is not present in the dictionary.
        
        Returns
        -------
        values : `default`, `list` of `object`
            The matched values. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the dictionary and `default` value is not given either.
        """
        try:
            return dict.pop(self, key)
        except KeyError:
            if default is not ...:
                return default
            raise
    
    
    @has_docs
    def pop_one(self, key, default = ...):
        """
        Removes the first value from the dictionary, which matches the given `key`.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object`, Optional
            Default value to return if `key` is not present in the dictionary.
        
        Returns
        -------
        value : `default`, `list` of `object`
            The 0th matched value. If `key` is not present, but `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            if `key` is not present in the dictionary and `default` value is not given either.
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
    
    
    @has_docs
    def popitem(self):
        """
        Pops an item of the dictionary.
        
        Returns
        -------
        item : `tuple` (`object`, `object`)
        
        Raises
        ------
        KeyError
            If the dictionary is empty.
        """
        key, values = dict.popitem(self)
        value = values.pop(0)
        
        if values:
            dict.__setitem__(self, key, values)
        
        return key, value
        
        raise KeyError('popitem(): dictionary is empty.')
    
    
    @has_docs
    def copy(self):
        """
        Copies the dictionary.
        
        Returns
        -------
        new : ``MultiValueDictionary``
        """
        new = dict.__new__(type(self))
        setitem = dict.__setitem__
        for key, values in dict.items(self):
            setitem(new, key, values.copy())
        
        return new
    
    
    @has_docs
    def items(self):
        """
        Returns an item iterator for the dictionary.
        
        Returns
        -------
        items : ``_MultiValueDictionaryItemIterator``
        """
        return _MultiValueDictionaryItemIterator(self)
    
    
    @has_docs
    def values(self):
        """
        Returns a value iterator for the dictionary.
        
        Returns
        -------
        items : ``_MultiValueDictionaryValueIterator``
        """
        return _MultiValueDictionaryValueIterator(self)
    
    
    @has_docs
    def __repr__(self):
        """Returns the dictionary's representation."""
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
        Converts the dictionary to `**kwargs`-able dictionary. If a `key` has more values, then always returns the last
        value for it.
        
        Returns
        -------
        result : `dict` of (`object`, `object`) items
        """
        result = {}
        for key, values in dict.items(self):
            result[key] = values[-1]
        
        return result
    
    update = RemovedDescriptor()
