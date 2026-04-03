__all__ = ('WeakKeyDictionary',)

from .dict_iterator_bases import DictionaryItemIteratorBase, DictionaryKeyIteratorBase, DictionaryValueIteratorBase
from .dict_update_iterable_iterator import _dict_update_iterable_iterator
from .docs import copy_docs, has_docs
from .weak_core import WeakReferer, add_to_pending_removals


@has_docs
class _WeakKeyDictionaryCallback:
    """
    Callback used by ``WeakKeyDictionary``-s.
    
    Attributes
    ----------
    _parent : ``WeakReferer`` to ``WeakKeyDictionary``
        The parent weak key dictionary.
    """
    __slots__ = ('_parent', )
    
    @has_docs
    def __new__(cls, parent):
        """
        Creates a new ``_WeakKeyDictionaryCallback`` bound to the given ``WeakKeyDictionary``.
        
        Parameters
        ----------
        parent : ``WeakKeyDictionary``
            The parent weak key dictionary.
        """
        parent = WeakReferer(parent)
        self = object.__new__(cls)
        self._parent = parent
        return self
    
    
    @has_docs
    def __call__(self, reference):
        """
        Called when a key of the respective weak key dictionary is garbage collected.
        
        Parameters
        ----------
        reference : ``WeakReferer``
            Weakreference to the respective object.
        """
        parent = self._parent()
        if parent is None:
            return
        
        if parent._iterating:
            add_to_pending_removals(parent, reference)
        else:
            try:
                dict.__delitem__(parent, reference)
            except KeyError:
                pass


class _WeakKeyDictionaryKeyIterator(DictionaryKeyIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryKeyIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for key_reference in dict.keys(parent):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(parent, key_reference)
                    continue
                
                yield key
                continue
        
        finally:
            parent._iterating -= 1
            parent._commit_removals()
    
    
    @copy_docs(DictionaryKeyIteratorBase.__contains__)
    def __contains__(self, contains_key):
        return (contains_key in self._parent)


class _WeakKeyDictionaryValueIterator(DictionaryValueIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryValueIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for key_reference, value in dict.items(parent):
                if (key_reference() is None):
                    add_to_pending_removals(parent, key_reference)
                    continue
                
                yield value
                continue
        
        finally:
            parent._iterating -= 1
            parent._commit_removals()
    
    
    @copy_docs(DictionaryValueIteratorBase.__contains__)
    def __contains__(self, contains_value):
        parent = self._parent
        
        for key_reference, value in dict.items(parent):
            if (key_reference() is None):
                add_to_pending_removals(parent, key_reference)
                continue
            
            if value == contains_value:
                result = True
                break
        
        else:
            result = False
        
        parent._commit_removals()
        
        return result
    

class _WeakKeyDictionaryItemIterator(DictionaryItemIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryItemIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for key_reference, value in dict.items(parent):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(parent, key_reference)
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
        
        contains_key, contains_value = contains_item
        
        try:
            contains_key_reference = WeakReferer(contains_key)
        except TypeError:
            return False
        
        value = dict.get(self._parent, contains_key_reference)
        if value is None:
            return False
        
        return (value == contains_value)


@has_docs
class WeakKeyDictionary(dict):
    """
    Weak key dictionary, which stores it's keys weakly referenced.
    
    Attributes
    ----------
    _pending_removals : `None`, `set` of ``WeakReferer``
        Pending removals of the weak key dictionary if applicable.
    _iterating : `int`
        Whether the weak key dictionary is iterating and how much times.
    _callback : ``_WeakKeyDictionaryCallback``
        Callback added to the ``WeakKeyDictionary``'s weak keys.
    
    Class Attributes
    ----------------
    MAX_REPR_ELEMENT_LIMIT : `int` = `50`
        The maximal amount of items to render by ``.__repr__``.
    
    Notes
    -----
    ``WeakKeyDictionary``-s are weakreferable.
    """
    __slots__ = ('__weakref__', '_pending_removals', '_iterating', '_callback')
    
    MAX_REPR_ELEMENT_LIMIT = 50
    
    @has_docs
    def _commit_removals(self):
        """
        Commits the pending removals of the weak key dictionary if applicable.
        """
        if self._iterating:
            return
        
        pending_removals = self._pending_removals
        if pending_removals is None:
            return
        
        self._pending_removals = None
        
        for key_reference in pending_removals:
            try:
                dict.__delitem__(self, key_reference)
            except KeyError:
                return
    
    # __class__ -> same
    
    @has_docs
    def __contains__(self, key):
        """Returns whether the weak key dictionary contains the given key."""
        try:
            key = WeakReferer(key)
        except TypeError:
            return False
        
        return dict.__contains__(self, key)
    
    # __delattr__ -> same
    
    @has_docs
    def __delitem__(self, key):
        """Deletes the value of the weak key dictionary which matches the given key."""
        dict.__delitem__(self, WeakReferer(key))
    
    # __dir__ -> same
    # __doc__ -> same
    
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the two dictionaries are the same."""
        if isinstance(other, type(self)):
            return dict.__eq__(self, other)
        
        if isinstance(other, dict):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = dict(other)
            except (TypeError, ValueError):
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
        """Gets the value of the weak key dictionary which matches the given key."""
        return dict.__getitem__(self, WeakReferer(key))
    
    # __gt__ -> same
    # __hash__ -> same
    
    @has_docs
    def __init__(self, iterable = None):
        """
        Creates a new ``WeakKeyDictionary`` from the given iterable.
        
        Parameters
        ----------
        iterable : `None`, `iterable` = `None`, Optional
            Iterable to update the created dictionary with.
        """
        self._pending_removals = None
        self._iterating = 0
        self._callback = _WeakKeyDictionaryCallback(self)
        if (iterable is not None):
            self.update(iterable)
    
    # __init_subclass__ -> same
    
    @has_docs
    def __iter__(self):
        """Returns a ``_WeakKeyDictionaryKeyIterator`` iterating over the weak key dictionary's keys."""
        return iter(_WeakKeyDictionaryKeyIterator(self))
    
    # __le__ -> same
    
    @has_docs
    def __len__(self):
        """Returns the length of the weak key dictionary."""
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
            except (TypeError, ValueError):
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
        """Returns the representation of the weak key dictionary."""
        result = [self.__class__.__name__, '({']
        
        if len(self):
            limit = self.MAX_REPR_ELEMENT_LIMIT
            collected = 0
            for key_reference, value in dict.items(self):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(self, key_reference)
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
        """Adds the given `key` - `value` pair to the weak key dictionary."""
        dict.__setitem__(self, WeakReferer(key, self._callback), value)
    
    # __sizeof__ -> same
    
    __str__ = __repr__
    
    # __subclasshook__ -> same
    
    @has_docs
    def clear(self):
        """
        Clears the weak key dictionary.
        """
        dict.clear(self)
        self._pending_removals = None
    
    
    @has_docs
    def copy(self):
        """
        Copies the weak key dictionary.
        
        Returns
        -------
        new : ``WeakKeyDictionary``
        """
        new = dict.__new__(type(self))
        new._pending_removals = None
        callback = _WeakKeyDictionaryCallback(new)
        new._callback = callback
        new._iterating = 0
        
        for key_reference, value in dict.items(self):
            key = key_reference()
            if key is None:
                add_to_pending_removals(self, key_reference)
                continue
            
            dict.__setitem__(new, WeakReferer(key, callback), value)
            continue
        
        self._commit_removals()
        
        return new
    
    @has_docs
    def get(self, key, default = None):
        """
        Gets the value of the weak key dictionary which matches the given key.
        
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
        return dict.get(self, WeakReferer(key), default)
    
    
    @has_docs
    def items(self):
        """
        Returns item iterator for the weak key dictionary.
        
        Returns
        -------
        item_iterator : ``_WeakKeyDictionaryItemIterator``
        """
        return _WeakKeyDictionaryItemIterator(self)
    
    
    @has_docs
    def keys(self):
        """
        Returns key iterator for the weak key dictionary.
        
        Returns
        -------
        key_iterator : ``_WeakKeyDictionaryKeyIterator``
        """
        return _WeakKeyDictionaryKeyIterator(self)
    
    
    @has_docs
    def pop(self, key, default = ...):
        """
        Pops the value of the weak key dictionary which matches the given key.
        
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
        try:
            key_reference = WeakReferer(key)
        except TypeError:
            raise KeyError(key) from None
        
        value = dict.pop(self, key_reference, ...)
        if (value is not ...):
            return value
        
        if default is ...:
            raise KeyError(key)
        
        return default
    
    
    @has_docs
    def popitem(self):
        """
        Pops an item of the key value dictionary.
        
        Returns
        -------
        item : `tuple` (`object`, `object`)
        
        Raises
        ------
        KeyError
            If the weak key dictionary is empty.
        """
        while dict.__len__(self):
            key_reference, value = dict.popitem(self)
            key = key_reference()
            
            if (key is not None):
                return key, value
            
            continue
        
        raise KeyError('popitem(): dictionary is empty.')
    
    
    @has_docs
    def setdefault(self, key, default = None):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the weak key dictionary, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object` = `None`, Optional
            Default value to set and return if `key` is not present in the weak key dictionary.
        
        Returns
        -------
        value : `default`, `object`
            The matched value, or `default` if none.
        """
        value = dict.get(self, WeakReferer(key), ...)
        if (value is not ...):
            return value
        
        self[key] = default
        return default
    
    
    @has_docs
    def update(self, iterable):
        """
        Updates the weak key dictionary with the given iterable's elements.
        
        Parameters
        ----------
        iterable : `iterable`
            Iterable to extend the weak key dictionary with.
            
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
        Returns value iterator for the weak key dictionary.
        
        Returns
        -------
        value_iterator : ``_WeakKeyDictionaryValueIterator``
        """
        return _WeakKeyDictionaryValueIterator(self)
