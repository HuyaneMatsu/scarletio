__all__ = ('WeakItemDictionary',)

from .dict_iterator_bases import DictionaryItemIteratorBase, DictionaryValueIteratorBase
from .dict_update_iterable_iterator import _dict_update_iterable_iterator
from .docs import copy_docs, has_docs
from .weak_core import KeyedReferer, WeakReferer, add_to_pending_removals
from .weak_key_dictionary import _WeakKeyDictionaryCallback, _WeakKeyDictionaryKeyIterator


@has_docs
class _WeakItemDictionaryValueCallback:
    """
    Callback used by ``WeakItemDictionary``-s.
    
    Attributes
    ----------
    _parent : ``WeakReferer`` to ``WeakItemDictionary``
        The parent weak or hybrid value dictionary.
    """
    __slots__ = ('_parent', )
    
    @has_docs
    def __new__(cls, parent):
        """
        Creates a new ``_WeakItemDictionaryValueCallback``.
        
        Parameters
        ----------
        parent : ``WeakItemDictionary``
            The parent weak or hybrid value dictionary.
        """
        parent = WeakReferer(parent)
        self = object.__new__(cls)
        self._parent = parent
        return self
    
    
    @has_docs
    def __call__(self, reference):
        """
        Called when a value of the respective weak value is garbage collected.
        
        Parameters
        ----------
        reference : ``KeyedReferer``
            Weakreference to the respective object.
        """
        parent = self._parent()
        if parent is None:
            return
        
        key_reference = reference.key
        
        if parent._iterating:
            add_to_pending_removals(parent, key_reference)
        else:
            try:
                dict.__delitem__(parent, key_reference)
            except KeyError:
                pass


class _WeakItemDictionaryValueIterator(DictionaryValueIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryValueIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        parent._iterating += 1
        
        try:
            for value_reference in dict.values(parent):
                value = value_reference()
                if (value is None):
                    add_to_pending_removals(parent, value_reference.key)
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
                add_to_pending_removals(parent, value_reference.key)
                continue
            
            if value == contains_value:
                result = True
                break
        
        else:
            result = False
        
        parent._commit_removals()
        
        return result
    
    

class _WeakItemDictionaryItemIterator(DictionaryItemIteratorBase):
    __slots__ = ()
    
    @copy_docs(DictionaryItemIteratorBase.__iter__)
    def __iter__(self):
        parent = self._parent
        iterating = parent._iterating
        parent._iterating = iterating + 1
        
        try:
            for key_reference, value_reference in dict.items(parent):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(parent, key_reference)
                    continue
                
                value = value_reference()
                if (value is None):
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
        
        parent = self._parent
        
        contains_key, contains_value = contains_item
        
        try:
            contains_key_reference = WeakReferer(contains_key)
        except TypeError:
            return False
        
        value_reference = dict.get(self._parent, contains_key_reference)
        if value_reference is None:
            return False
        
        value = value_reference()
        if value is None:
            if parent._iterating:
                add_to_pending_removals(parent, value_reference.key)
            else:
                dict.__delitem__(parent, value_reference.key)
            
            return False
        
        return (value == contains_value)


@has_docs
class WeakItemDictionary(dict):
    """
    weak item dictionary, which stores it's values weakly referenced.
    
    Attributes
    ----------
    _pending_removals : `None`, `set` of (``KeyedReferer``, ``WeakHasher``)
        Pending removals of the weak item dictionary if applicable.
    _iterating : `int`
        Whether the weak item dictionary is iterating and how much times.
    _key_callback : ``_WeakKeyDictionaryCallback``
        Callback added to the ``WeakItemDictionary``'s weak keys.
    _value_callback : ``_WeakItemDictionaryValueCallback``
        Callback added to the ``WeakItemDictionary``'s weak values.
    
    Class Attributes
    ----------------
    MAX_REPR_ELEMENT_LIMIT : `int` = `50`
        The maximal amount of items to render by ``.__repr__``.
    
    Notes
    -----
    ``WeakItemDictionary``-s are weakreferable.
    """
    __slots__ = ('__weakref__', '_pending_removals', '_iterating', '_key_callback', '_value_callback')
    
    MAX_REPR_ELEMENT_LIMIT = 50
    
    @has_docs
    def _commit_removals(self):
        """
        Commits the pending removals of the weak item dictionary if applicable.
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
                pass
    
    # __class__ -> same
    
    @has_docs
    def __contains__(self, key):
        """Returns whether the weak item dictionary contains the given key."""
        try:
            key = WeakReferer(key)
        except TypeError:
            return False
        
        value_reference = dict.get(self, key, None)
        if value_reference is None:
            return False
        
        value = value_reference()
        if (value is not None):
            return True
        
        if self._iterating:
            add_to_pending_removals(self, value_reference.key)
        else:
            dict.__delitem__(self, key)
        
        return False
    
    # __delattr__ -> same
    
    @has_docs
    def __delitem__(self, key):
        """Deletes the value of the weak item dictionary which matches the given key."""
        try:
            key = WeakReferer(key)
        except TypeError:
            raise KeyError(key) from None
        
        dict.__delitem__(self, key)
    
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
            except (ValueError, TypeError):
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
        """Gets the value of the weak item dictionary which matches the given key."""
        try:
            key_reference = WeakReferer(key)
        except TypeError:
            raise KeyError(key) from None
        
        value_reference = dict.__getitem__(self, key_reference)
        value = value_reference()
        if (value is not None):
            return value
        
        if self._iterating:
            add_to_pending_removals(self, value_reference.key)
        else:
            dict.__delitem__(self, value_reference.key)
        
        raise KeyError(key)
    
    # __gt__ -> same
    # __hash__ -> same
    
    @has_docs
    def __init__(self, iterable = None):
        """
        Creates a new ``WeakItemDictionary`` from the given iterable.
        
        Parameters
        ----------
        iterable : `None`, `iterable` = `None`, Optional
            Iterable to update the created dictionary with.
        """
        self._pending_removals = None
        self._iterating = 0
        self._key_callback = _WeakKeyDictionaryCallback(self)
        self._value_callback = _WeakItemDictionaryValueCallback(self)
        if (iterable is not None):
            self.update(iterable)
    
    # __init_subclass__ -> same
    
    @has_docs
    def __iter__(self):
        """Returns a ``_WeakItemDictionaryKeyIterator`` iterating over the weak item dictionary's keys."""
        return iter(_WeakKeyDictionaryKeyIterator(self))
    
    # __le__ -> same
    
    @has_docs
    def __len__(self):
        """Returns the length of the weak item dictionary."""
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
            except (ValueError, TypeError):
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
        """Returns the representation of the weak item dictionary."""
        result = [self.__class__.__name__, '({']
        
        if len(self):
            limit = self.MAX_REPR_ELEMENT_LIMIT
            collected = 0
            for key_reference, value_reference in dict.items(self):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(self, key_reference)
                    continue
                
                value = value_reference()
                if (value is None):
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
        """Adds the given `key` - `value` pair to the weak item dictionary."""
        key_reference = WeakReferer(key, self._key_callback)
        value_reference = KeyedReferer(value, self._value_callback, key_reference)
        dict.__setitem__(self, key_reference, value_reference)
    
    # __sizeof__ -> same
    
    __str__ = __repr__
    
    # __subclasshook__ -> same
    
    @has_docs
    def clear(self):
        """
        Clears the weak item dictionary.
        """
        dict.clear(self)
        self._pending_removals = None
    
    
    @has_docs
    def copy(self):
        """
        Copies the weak item dictionary.
        
        Returns
        -------
        new : ``WeakItemDictionary``
        """
        new = dict.__new__(type(self))
        new._pending_removals = None
        key_callback = _WeakKeyDictionaryCallback(new)
        new._key_callback = key_callback
        value_callback = _WeakItemDictionaryValueCallback(new)
        new._value_callback = value_callback
        new._iterating = 0
        
        for key_reference, value_reference in dict.items(self):
            key = key_reference()
            if key is None:
                add_to_pending_removals(self, key_reference)
                continue
            
            value = value_reference()
            if value is None:
                add_to_pending_removals(self, key_reference)
                continue
            
            key_reference = WeakReferer(key, self._key_callback)
            value_reference = KeyedReferer(value, self._value_callback, key_reference)
            
            dict.__setitem__(new, key_reference, value_reference)
            continue
        
        self._commit_removals()
        
        return new
    
    
    @has_docs
    def get(self, key, default = None):
        """
        Gets the value of the weak item dictionary which matches the given key.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        default : `None`, `object` = `None`, Optional
            Default value to return if the given `key` could not be matched.
        
        Returns
        -------
        value : `object`, `default`
            The key's matched value. If no value was matched returns the `default` value.
        """
        try:
            key_reference = WeakReferer(key)
        except TypeError:
            pass
        else:
            value_reference = dict.get(self, key_reference, default)
            if value_reference is default:
                return default
            
            value = value_reference()
            if (value is not None):
                return value
            
            if self._iterating:
                add_to_pending_removals(self, value_reference.key)
            else:
                dict.__delitem__(self, key)
        
        return default
    
    
    @has_docs
    def items(self):
        """
        Returns item iterator for the weak item dictionary.
        
        Returns
        -------
        item_iterator : ``_WeakItemDictionaryItemIterator``
        """
        return _WeakItemDictionaryItemIterator(self)
    
    
    @has_docs
    def keys(self):
        """
        Returns key iterator for the weak item dictionary.
        
        Returns
        -------
        key_iterator : ``_WeakKeyDictionaryKeyIterator``
        """
        return _WeakKeyDictionaryKeyIterator(self)
    
    
    @has_docs
    def pop(self, key, default = ...):
        """
        Pops the value of the weak item dictionary which matches the given key.
        
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
        # Use goto
        while True:
            try:
                key_reference = WeakReferer(key)
            except TypeError:
                break
            
            value_reference = dict.pop(self, key_reference, ...)
            if (value_reference is ...):
                break
                
            value = value_reference()
            if (value is None):
                break
            
            return value
        
        
        if default is ...:
            raise KeyError(key)
        
        return default
    
    
    @has_docs
    def popitem(self):
        """
        Pops an item of the weak item dictionary.
        
        Returns
        -------
        item : `tuple` (`object`, `object`)
        
        Raises
        ------
        KeyError
            If the weak item dictionary is empty.
        """
        while dict.__len__(self):
            key_reference, value_reference = dict.popitem(self)
            key = key_reference()
            if key is None:
                continue
            
            value = value_reference()
            if value is None:
                continue
            
            return key, value
        
        raise KeyError('popitem(): dictionary is empty.')
    
    
    @has_docs
    def setdefault(self, key, default):
        """
        Returns the value for the given `key`.
        
        If the `key` is not present in the weak item dictionary, then set's the given `default` value as it.
        
        Parameters
        ----------
        key : `object`
            The key to match.
        default : `object`
            Default value to set and return if `key` is not present in the weak item dictionary.
        
        Returns
        -------
        value : `default`, `object`
            The matched value, or `default` if none.
        """
        value_reference = dict.get(self, WeakReferer(key), ...)
        if (value_reference is not ...):
            value = value_reference()
            if (value is not None):
                return value
        
        self[key] = default
        return default
    
    
    @has_docs
    def update(self, iterable):
        """
        Updates the weak item dictionary with the given iterable's elements.
        
        Parameters
        ----------
        iterable : `iterable`
            Iterable to extend the weak item dictionary with.
            
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
        Returns value iterator for the weak item dictionary.
        
        Returns
        -------
        value_iterator : ``_WeakItemDictionaryValueIterator``
        """
        return _WeakItemDictionaryValueIterator(self)
