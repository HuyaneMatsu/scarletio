__all__ = ('WeakMap',)

from .docs import has_docs
from .removed_descriptor import RemovedDescriptor
from .weak_core import WeakReferer, add_to_pending_removals


@has_docs
class _WeakMapCallback:
    """
    Callback used by ``WeakMap``-s.
    
    Attributes
    ----------
    _parent : ``WeakReferer`` to ``WeakMap``
        The parent weak map.
    """
    __slots__ = ('_parent', )
    
    @has_docs
    def __new__(cls, parent):
        """
        Creates a new ``_WeakMapCallback`` bound to the given ``WeakMap``.
        
        Parameters
        ----------
        parent : ``WeakMap``
            The parent weak map.
        """
        parent = WeakReferer(parent)
        self = object.__new__(cls)
        self._parent = parent
        return self
    
    @has_docs
    def __call__(self, reference):
        """
        Called when an element of the respective weak map is garbage collected.
        
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


@has_docs
class WeakMap(dict):
    """
    Weak map is a mix of weak dictionaries and weak sets. Can be used to retrieve an already existing weakreferenced
    value from itself.
    
    Attributes
    ----------
    _pending_removals : `None`, `set` of ``WeakReferer``
        Pending removals of the weak map if applicable.
    _iterating : `int`
        Whether the weak map is iterating and how much times.
    _callback : ``_WeakMapCallback``
        Callback added to the ``WeakMap``'s weak keys.
    
    Class Attributes
    ----------------
    MAX_REPR_ELEMENT_LIMIT : `int` = `50`
        The maximal amount of items to render by ``.__repr__``.
    
    Notes
    -----
    ``WeakMap``-s are weakreferable.
    """
    __slots__ = ('__weakref__', '_pending_removals', '_iterating', '_callback')
    
    MAX_REPR_ELEMENT_LIMIT = 50
    
    @has_docs
    def _commit_removals(self):
        """
        Commits the pending removals of the weak map if applicable.
        """
        if self._iterating:
            return
        
        pending_removals = self._pending_removals
        if pending_removals is None:
            return
        
        for reference in pending_removals:
            try:
                dict.__delitem__(self, reference)
            except KeyError:
                pass
        
        self._pending_removals = None
    
    # __class__ -> same
    
    @has_docs
    def __contains__(self, key):
        """Returns whether the weak map contains the given key."""
        try:
            reference = WeakReferer(key)
        except TypeError:
            return False
        
        return dict.__contains__(self, reference)
    
    # __delattr__ -> same
    
    @has_docs
    def __delitem__(self, key):
        """Deletes the given key from the weak map"""
        try:
            reference = WeakReferer(key)
        except TypeError:
            raise KeyError(key) from None
        
        try:
            dict.__delitem__(self, reference)
        except KeyError as err:
            raise KeyError(key) from None
    
    # __dir__ -> same
    # __doc__ -> same
    
    def __eq__(self, other):
        """returns whether the two weak maps are equal."""
        if isinstance(other, type(self)):
            return dict.__eq__(self, other)
        
        if isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        return self_set == other
    
    # __format__ -> same
    # __ge__ -> same
    # __getattribute__ -> same
    
    @has_docs
    def __getitem__(self, key):
        """Gets the already existing key from the weak map, which matches the given one."""
        try:
            reference = WeakReferer(key)
        except TypeError:
            raise KeyError(key) from None
        
        reference = dict.__getitem__(self, reference)
        key = reference()
        if (key is None):
            if self._iterating:
                add_to_pending_removals(self, reference)
            else:
                dict.__delitem__(self, reference)
            
            raise KeyError(key)
        
        return key
    
    
    # __gt__ -> same
    # __hash__ -> same
    
    @has_docs
    def __init__(self, iterable = None):
        """
        Creates a new ``WeakMap`` from the given iterable.
        
        Parameters
        ----------
        iterable : `None`, `iterable` = `None`, Optional
            Iterable to update the created map with.
        """
        self._pending_removals = None
        self._iterating = 0
        self._callback = _WeakMapCallback(self)
        if (iterable is not None):
            self.update(iterable)
    
    # __init_subclass__ -> same
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the weak map's elements.
        
        This method is an iterable generator,
        """
        self._iterating += 1
        
        try:
            for reference in dict.__iter__(self):
                key = reference()
                if (key is None):
                    add_to_pending_removals(self, reference)
                    continue
                
                yield key
                continue
        
        finally:
            self._iterating -= 1
            self._commit_removals()
    
    # __le__ -> same
    
    @has_docs
    def __len__(self):
        """Returns the length of the weak map."""
        length = dict.__len__(self)
        pending_removals = self._pending_removals
        if (pending_removals is not None):
            length -= len(pending_removals)
        
        return length
    
    # __lt__ -> same
    
    def __ne__(self, other):
        """returns whether the two weak maps are equal."""
        if isinstance(other, type(self)):
            return dict.__ne__(self, other)
        
        if isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        return self_set != other
    
    # __new__ -> same
    
    @has_docs
    def __reduce__(self):
        """Reduces the map to a picklable object."""
        return (type(self), list(self))
    
    
    @has_docs
    def __reduce_ex__(self, version):
        """Reduces the map to a picklable object."""
        return type(self).__reduce__(self)
    
    
    @has_docs
    def __repr__(self):
        """Returns the weak map's representation."""
        result = [self.__class__.__name__, '({']
        if len(self):
            limit = self.MAX_REPR_ELEMENT_LIMIT
            collected = 0
            
            for reference in dict.__iter__(self):
                key = reference()
                if (key is None):
                    add_to_pending_removals(self, reference)
                    continue
                
                result.append(repr(key))
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
    
    # __setattr__ -> same
    __setitem__ = RemovedDescriptor()
    # __sizeof__ -> same
    
    __str__ = __repr__
    
    # __subclasshook__ -> same
    
    @has_docs
    def clear(self):
        """
        Clear's the weak map.
        """
        dict.clear(self)
        self._pending_removals = None
    
    
    @has_docs
    def copy(self):
        """
        Copies the weak map.
        
        Returns
        -------
        new : ``WeakMap``
        """
        new = dict.__new__(type(self))
        new._iterating = 0
        new._pending_removals = None
        new._callback = callback = _WeakMapCallback(new)
        
        for reference in dict.__iter__(self):
            key = reference()
            if (key is None):
                add_to_pending_removals(self, reference)
                continue
            
            reference = WeakReferer(key, callback)
            dict.__setitem__(new, reference, reference)
            continue
        
        self._commit_removals()
        
        return new
    
    
    @has_docs
    def get(self, key, default = None):
        """
        Gets the key of the weak map, which matches the given one.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        default : `object` = `None`, Optional
            Default value to return if the given `key` could not be matched.
        
        Returns
        -------
        real_key : `object`, `default`
            The matched key. If no key was matched returns the `default` value.
        """
        try:
            reference = WeakReferer(key)
        except TypeError:
            return default
        
        real_reference = dict.get(self, reference, reference)
        if real_reference is reference:
            return default
        
        real_key = real_reference()
        if (real_key is not None):
            return real_key
        
        if self._iterating:
            add_to_pending_removals(self, real_reference)
        else:
            dict.__delitem__(self, real_reference)
        
        return default
    
    
    items = RemovedDescriptor()
    keys = RemovedDescriptor()
    
    
    @has_docs
    def pop(self, key, default = ...):
        """
        Pops a key from the weak map which matches the given one.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        default : `object`, Optional
            Default value to return if the given `key` could not be matched.
        
        Returns
        -------
        real_key : `object`, `default`
            The matched key. If no key was matched and `default` value is given, then returns that.
        
        Raises
        ------
        KeyError
            If `key` could not be matched and `default` value is was not given either.
        """
        try:
            reference = WeakReferer(key)
        except TypeError:
            pass
        else:
            real_reference = dict.pop(self, reference, ...)
            if (real_reference is not ...):
                real_key = real_reference()
                if (real_key is not None):
                    return real_key
                
                if self._iterating:
                    add_to_pending_removals(self, real_reference)
                else:
                    dict.__delitem__(self, real_reference)
        
        if default is ...:
            raise KeyError(key)
        
        return default
    
    
    popitem = RemovedDescriptor()
    setdefault = RemovedDescriptor()
    
    
    @has_docs
    def update(self, iterable):
        """
        Updates the map with the given iterable.
        
        Parameters
        ----------
        iterable : `iterable`
            The iterable to update the map with.
        
        Raises
        ------
        TypeError
            If the given value is not `iterable`, or any of it's elements is not weakreferable.
        """
        if hasattr(type(iterable), '__iter__'):
            # Make sure, we have unique elements, so convert other to set
            for element in iterable:
                self.set(element)
        
        else:
            raise TypeError(
                f'Parameter `iterable` must be an iterable, got {iterable.__class__.__name__}; {iterable!r}.'
            )
    
    
    values = RemovedDescriptor()
    
    
    @has_docs
    def set(self, key):
        """
        Sets a key to the ``WeakMap`` and then returns it. If they given key is already present in the ``WeakMap``,
        returns that instead.
        
        Parameters
        ----------
        key : `object`
            A key to match.
        
        Returns
        -------
        real_key : `object`
            The matched key, or the given one.
        
        Raises
        ------
        TypeError
            If `key` not supports weakreferencing.
        """
        reference = WeakReferer(key, self._callback)
        real_reference = dict.get(self, reference, None)
        if (real_reference is not None):
            real_key = real_reference()
            if (real_key is not None):
                return real_key
        
        dict.__setitem__(self, reference, reference)
        return key
