__all__ = ('WeakValueDictionary', )

from .dict_iterator_bases import DictionaryItemIteratorBase, DictionaryKeyIteratorBase, DictionaryValueIteratorBase
from .dict_update_iterable_iterator import _dict_update_iterable_iterator
from .docs import copy_docs, has_docs
from .weak_core import KeyedReferer, WeakReferer, add_to_pending_removals


@has_docs
class _WeakValueDictionaryCallback:
    """
    Callback used by ``WeakValueDictionary``-s and by ``HybridValueDictionary``-s.
    
    Attributes
    ----------
    _parent : ``WeakReferer`` to (``WeakValueDictionary``, ``HybridValueDictionary``)
        The parent weak or hybrid value dictionary.
    """
    __slots__ = ('_parent', )
    
    @has_docs
    def __new__(cls, parent):
        """
        Creates a new ``_WeakValueDictionaryCallback`` bound to the given ``WeakValueDictionary`` or
        ``HybridValueDictionary``.
        
        Parameters
        ----------
        parent : ``WeakValueDictionary``, ``HybridValueDictionary``
            The parent weak or hybrid value dictionary.
        """
        parent = WeakReferer(parent)
        self = object.__new__(cls)
        self._parent = parent
        return self
    
    @has_docs
    def __call__(self, reference):
        """
        Called when a value of the respective weak or hybrid value dictionary is garbage collected.
        
        Parameters
        ----------
        reference : ``KeyedReferer``
            Weakreference to the respective object.
        """
        parent = self._parent()
        if parent is None:
            return
        
        if parent._iterating:
            add_to_pending_removals(parent, reference)
        else:
            try:
                dict.__delitem__(parent, reference.key)
            except KeyError:
                pass


class _WeakValueDictionaryKeyIterator(DictionaryKeyIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryKeyIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for key, value_reference in dict.items(parent):
                if (value_reference() is None):
                    add_to_pending_removals(parent, value_reference)
                    continue
                
                yield key
                continue
        
        finally:
            parent._iterating -= 1
            parent._commit_removals()
    
    
    @copy_docs(DictionaryKeyIteratorBase.__contains__)
    def __contains__(self, key):
        return (key in self._parent)


class _WeakValueDictionaryValueIterator(DictionaryValueIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryValueIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for value_reference in dict.values(parent):
                value = value_reference()
                if (value is None):
                    add_to_pending_removals(parent, value_reference)
                    continue
                
                yield value
                continue
        
        finally:
            parent._iterating -= 1
            parent._commit_removals()
    
    
    @copy_docs(DictionaryValueIteratorBase.__contains__)
    def __contains__(self, contains_value):
        parent = self._parent
        for value_reference in dict.values(parent):
            value = value_reference()
            if (value is None):
                add_to_pending_removals(parent, value_reference)
                continue
            
            if value == contains_value:
                result = True
                break
        
        else:
            result = False
        
        parent._commit_removals()
        
        return result


@has_docs
class _WeakValueDictionaryItemIterator(DictionaryItemIteratorBase):
    __slots__ = ()

    @copy_docs(DictionaryItemIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for key, value_reference in dict.items(parent):
                value = value_reference()
                if (value is None):
                    add_to_pending_removals(parent, value_reference)
                    continue
                
                yield key, value
                continue
        
        finally:
            parent._iterating -= 1
            parent._commit_removals()
    
    
    @copy_docs(DictionaryItemIteratorBase.__contains__)
    def __contains__(self, contains_item):
        if not isinstance(contains_item, tuple):
            return False
        
        if len(contains_item) != 2:
            return False
        
        parent = self._parent
        
        contains_key, contains_value = contains_item
        
        value_reference = dict.get(parent, contains_key)
        if value_reference is None:
            return False
        
        value = value_reference()
        if value is None:
            if parent._iterating:
                add_to_pending_removals(parent, value_reference)
            else:
                dict.__delitem__(parent, contains_key)
            
            return False
        
        return (value == contains_value)


@has_docs
class WeakValueDictionary(dict):
    """
    Weak value dictionary, which stores it's values weakly referenced.
    
    Attributes
    ----------
    _pending_removals : `None`, `set` of (``KeyedReferer``, ``WeakHasher``)
        Pending removals of the weak value dictionary if applicable.
    _iterating : `int`
        Whether the weak value dictionary is iterating and how much times.
    _callback : ``_WeakValueDictionaryCallback``
        Callback added to the ``WeakValueDictionary``'s weak values.
    
    Class Attributes
    ----------------
    MAX_REPR_ELEMENT_LIMIT : `int` = `50`
        The maximal amount of items to render by ``.__repr__``.
    
    Notes
    -----
    ``WeakValueDictionary``-s are weakreferable.
    """
    __slots__ = ('__weakref__', '_pending_removals', '_iterating', '_callback')
    
    MAX_REPR_ELEMENT_LIMIT = 50
    
    @has_docs
    def _commit_removals(self):
        """
        Commits the pending removals of the weak value dictionary if applicable.
        """
        if self._iterating:
            return
        
        pending_removals = self._pending_removals
        if pending_removals is None:
            return
        
        self._pending_removals = None
        
        for value_reference in pending_removals:
            key = value_reference.key
            try:
                actual_value_reference = dict.__getitem__(self, key)
            except KeyError:
                continue
            
            if (actual_value_reference is not value_reference):
                continue
            
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass
    
    # __class__ -> same
    
    @has_docs
    def __contains__(self, key):
        """Returns whether the weak value dictionary contains the given key."""
        value_reference = dict.get(self, key, None)
        if value_reference is None:
            return False
        
        value = value_reference()
        if (value is not None):
            return True
        
        if self._iterating:
            add_to_pending_removals(self, value_reference)
        else:
            dict.__delitem__(self, key)
        
        return False
    
    # __delattr__ -> same
    # __delitem__ -> same
    # __dir__ -> same
    # __doc__ -> same
    
    def __eq__(self, other):
        """Returns whether the two dictionaries are the same."""
        if isinstance(other, type(self)):
            return dict.__eq__(self, other)
        
        if isinstance(other, dict):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = dict(other)
            except TypeError:
                return NotImplemented
        
        else:
            return NotImplemented
        
        self_dict = dict(self.items())
        
        return self_dict == other
    
    # __format__ -> same
    # __ge__ -> same
    # __getattribute__ -> same
    
    @has_docs
    def __getitem__(self, key):
        """Gets the value of the weak value dictionary which matches the given key."""
        value_reference = dict.__getitem__(self, key)
        value = value_reference()
        if (value is not None):
            return value
        
        if self._iterating:
            add_to_pending_removals(self, value_reference)
        else:
            dict.__delitem__(self, key)
        
        raise KeyError(key)
    
    # __gt__ -> same
    # __hash__ -> same
    
    @has_docs
    def __init__(self, iterable = None):
        """
        Creates a new ``WeakValueDictionary`` from the given iterable.
        
        Parameters
        ----------
        iterable : `None`, `iterable` = `None`, Optional
            Iterable to update the created dictionary with.
        """
        self._pending_removals = None
        self._iterating = 0
        self._callback = _WeakValueDictionaryCallback(self)
        if (iterable is not None):
            self.update(iterable)
    
    # __init_subclass__ -> same
    
    @has_docs
    def __iter__(self):
        """Returns a ``_WeakValueDictionaryKeyIterator`` iterating over the weak value dictionary's keys."""
        return iter(_WeakValueDictionaryKeyIterator(self))
    
    # __le__ -> same
    
    @has_docs
    def __len__(self):
        """Returns the length of the weak value dictionary."""
        length = dict.__len__(self)
        pending_removals = self._pending_removals
        if (pending_removals is not None):
            length -= len(pending_removals)
        
        return length
    
    # __lt__ -> same
    
    def __ne__(self, other):
        """Returns whether the two dictionaries are different."""
        if isinstance(other, type(self)):
            return dict.__ne__(self, other)
        
        if isinstance(other, dict):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = dict(other)
            except TypeError:
                return NotImplemented
        
        else:
            return NotImplemented
        
        self_dict = dict(self.items())
        
        return self_dict != other
    
    # __new__ -> same
    
    @has_docs
    def __reduce__(self):
        """Reduces the dictionary to a picklable object."""
        return (type(self), list(self.items()))
    
    
    @has_docs
    def __reduce_ex__(self, version):
        """Reduces the dictionary to a picklable object."""
        return type(self).__reduce__(self)
    
    
    @has_docs
    def __repr__(self):
        """Returns the representation of the weak value dictionary."""
        result = [self.__class__.__name__, '({']
        
        if len(self):
            limit = self.MAX_REPR_ELEMENT_LIMIT
            collected = 0
            for key, value_reference in dict.items(self):
                value = value_reference()
                if (value is None):
                    add_to_pending_removals(self, value_reference)
                    continue
                
                result.append(repr(key))
                result.append(': ')
                result.append(repr(value))
                result.append(', ')
                
                collected += 1
                if collected != limit:
                    continue
                
                leftover = len(self) - collected
                if leftover:
                    result.append('...}, ')
                    result.append(str(leftover))
                    result.append(' truncated)')
                else:
                    result[-1] = '})'
                break
            else:
                result[-1] = '})'
            
            self._commit_removals()
        else:
            result.append('})')
        
        return ''.join(result)
    
    #__setattr__ -> same
    
    @has_docs
    def __setitem__(self, key, value):
        """Adds the given `key` - `value` pair to the weak value dictionary."""
        dict.__setitem__(self, key, KeyedReferer(value, self._callback, key))
    
    # __sizeof__ -> same
    
    __str__ = __repr__
    
    # __subclasshook__ -> same
    
    @has_docs
    def clear(self):
        """
        Clears the weak value dictionary.
        """
        dict.clear(self)
        self._pending_removals = None
    
    
    @has_docs
    def copy(self):
        """
        Copies the weak value dictionary.
        
        Returns
        -------
        new : ``WeakValueDictionary``
        """
        new = dict.__new__(type(self))
        new._pending_removals = None
        callback = _WeakValueDictionaryCallback(new)
        new._callback = callback
        new._iterating = 0
        
        for key, value_reference in dict.items(self):
            value = value_reference()
            if value is None:
                add_to_pending_removals(self, value_reference)
                continue
            
            dict.__setitem__(new, key, KeyedReferer(value, callback, key))
            continue
        
        self._commit_removals()
        
        return new
    
    
    @has_docs
    def get(self, key, default = None):
        """
        Gets the value of the weak value dictionary which matches the given key.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        default : `object` = `None`, Optional
            Default value to return if the given `key` could not be matched.
        
        Returns
        -------
        value : `object`, `default`
            The key's matched value. If no value was matched returns the `default` value.
        """
        value_reference = dict.get(self, key, default)
        if value_reference is default:
            return default
        
        value = value_reference()
        if (value is not None):
            return value
        
        if self._iterating:
            add_to_pending_removals(self, value_reference)
        else:
            dict.__delitem__(self, key)
        
        return default
    
    
    @has_docs
    def items(self):
        """
        Returns item iterator for the weak value dictionary.
        
        Returns
        -------
        item_iterator : ``_WeakValueDictionaryItemIterator``
        """
        return _WeakValueDictionaryItemIterator(self)
    
    
    @has_docs
    def keys(self):
        """
        Returns key iterator for the weak value dictionary.
        
        Returns
        -------
        key_iterator : ``_WeakValueDictionaryKeyIterator``
        """
        return _WeakValueDictionaryKeyIterator(self)
    
    
    @has_docs
    def pop(self, key, default = ...):
        """
        Pops the value of the weak value dictionary which matches the given key.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        default : `object`, Optional
            Default value to return if the given `key` could not be matched.
        
        Returns
        -------
        value : `object`, `default`
            The key's matched value. If no value was matched and `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            If `key` could not be matched and `default` value is was not given either.
        """
        value_reference = dict.pop(self, key, ...)
        if (value_reference is not ...):
            value = value_reference()
            if (value is not None):
                return value
        
        if default is ...:
            raise KeyError(key)
        
        return default
    
    
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
        while dict.__len__(self):
            key, value_reference = dict.popitem(self)
            value = value_reference()
            if (value is not None):
                return key, value
            
            continue
        
        raise KeyError('popitem(): dictionary is empty.')
    
    
    @has_docs
    def setdefault(self, key, default):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the weak value dictionary, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object`
            Default value to set and return if `key` is not present in the weak value dictionary.
        
        Returns
        -------
        value : `default`, `object`
            The matched value, or `default` if none.
        """
        value_reference = dict.get(self, key, ...)
        if (value_reference is not ...):
            value = value_reference()
            if (value is not None):
                return value
        
        self[key] = default
        return default
    
    
    @has_docs
    def update(self, iterable):
        """
        Updates the weak value dictionary with the given iterable's elements.
        
        Parameters
        ----------
        iterable : `iterable`
            Iterable to extend the weak value dictionary with.
            
            Can be given as an object, which:
            - supports `.items` iterator.
            - supports `.keys` and `.__getitem__`.
            - is `iterable` and each iteration returns a sequence with 2 elements.
        
        Raises
        ------
        TypeError
            The given `iterable` is not `iterable`.
        ValueError
            The the given `iterable` sot supports neither `.items` or (`.keys` and `.__getitem__`) and one of it's
            element's length is not `2`.
        """
        iterable_type = iterable.__class__
        if hasattr(iterable_type, 'items'):
            for key, value in iterable.items():
                self[key] = value
            return
        
        if hasattr(iterable_type, 'keys') and hasattr(iterable_type, '__getitem__'):
            for key in iterable.keys():
                value = iterable[key]
                self[key] = value
            return
        
        if hasattr(iterable_type, '__iter__'):
            for key, value in _dict_update_iterable_iterator(iterable):
                self[key] = value
            
            return
        
        raise TypeError(
            f'`iterable` can be `iterable`, got {iterable_type.__name__}; {iterable_type!r}'
        )
    
    
    @has_docs
    def values(self):
        """
        Returns value iterator for the weak value dictionary.
        
        Returns
        -------
        value_iterator : ``_WeakValueDictionaryValueIterator``
        """
        return _WeakValueDictionaryValueIterator(self)
