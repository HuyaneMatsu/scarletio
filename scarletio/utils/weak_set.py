__all__ = ('WeakSet',)

from .docs import has_docs
from .weak_core import WeakReferer, add_to_pending_removals


@has_docs
class _WeakSetCallback:
    """
    Callback used by ``WeakSet``-s.
    
    Attributes
    ----------
    _parent : ``WeakReferer`` to ``WeakSet``
        The parent weak set.
    """
    __slots__ = ('_parent', )
    
    @has_docs
    def __new__(cls, parent):
        """
        Creates a new ``_WeakKeyDictionaryCallback`` bound to the given ``WeakSet``.
        
        Parameters
        ----------
        parent : ``WeakSet``
            The parent weak set.
        """
        parent = WeakReferer(parent)
        self = object.__new__(cls)
        self._parent = parent
        return self
    
    
    @has_docs
    def __call__(self, reference):
        """
        Called when a key of the respective weak set is garbage collected.
        
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
            set.discard(parent, reference)


class WeakSet(set):
    """
    Weak set, which stores it's elements weakly referenced.
    
    Attributes
    ----------
    _pending_removals : `None`, `set` of ``WeakReferer``
        Pending removals of the weak set if applicable.
    _iterating : `int`
        Whether the weak set is iterating and how much times.
    _callback : ``_WeakKeyDictionaryCallback``
        Callback added to the ``WeakSet``'s weak keys.
    
    Class Attributes
    ----------------
    MAX_REPR_ELEMENT_LIMIT : `int` = `50`
        The maximal amount of items to render by ``.__repr__``.
    
    Notes
    -----
    ``WeakSet``-s are weakreferable.
    """
    __slots__ = ('_pending_removals', '_iterating', '_callback')
    
    MAX_REPR_ELEMENT_LIMIT = 50


    @has_docs
    def _commit_removals(self):
        """
        Commits the pending removals of the weak set if applicable.
        """
        if self._iterating:
            return
        
        pending_removals = self._pending_removals
        if pending_removals is None:
            return
        
        self._pending_removals = None
        
        for key_reference in pending_removals:
            try:
                set.discard(self, key_reference)
            except KeyError:
                return
    
    @has_docs
    def __and__(self, other):
        """Returns a new set with the elements common of self and other."""
        if isinstance(other, type(self)):
            new = type(self)()
            
            for weak_element in set.__iter__(other):
                if set.__contains__(self, weak_element):
                    element = weak_element()
                    if (element is not None):
                        new.add(element)
            
            return new
        
        if hasattr(type(other), '__iter__'):
            new = type(self)()
            
            for element in other:
                if element in self:
                    new.add(element)
            
            return new
        
        return NotImplemented
    
    # __class__ -> same
    
    @has_docs
    def __contains__(self, element):
        """Returns whether the weak set contains the given element."""
        try:
            element = WeakReferer(element)
        except TypeError:
            return False
        
        return dict.__contains__(self, element)
    
    # __delattr__ -> same
    # __dir__ -> same
    # __doc__ -> same
    # __eq__ -> same
    # __format__ -> same
    
    @has_docs
    def __ge__(self, other):
        """Returns whether every element in other is in the set."""
        if isinstance(other, type(self)):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = type(self)(other)
        
        else:
            return NotImplemented
        
        return set.__ge__(self, other)
    
    # __getattribute__ -> same
    
    @has_docs
    def __gt__(self, other):
        """Returns whether the set is a proper superset of other."""
        if isinstance(other, type(self)):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = type(self)(other)
        
        else:
            return NotImplemented
        
        return set.__gt__(self, other)
    
    # __hash__ ->same
    
    @has_docs
    def __iand__(self, other):
        """Update the set, keeping only elements found in it and all others."""
        if isinstance(other, type(self)):
            other_set = set(iter(self))
        
        elif isinstance(other, set):
            other_set = other
        
        elif hasattr(type(other), '__iter__'):
            other_set = set(other)
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        for element in self_set ^ other_set:
            self.discard(element)
    
    
    @has_docs
    def __init__(self, iterable=None):
        """
        Creates a new ``WeakSet`` from the given iterable.
        
        Parameters
        ----------
        iterable : `iterable`, Optional
            Iterable to update the created set with.
        """
        self._pending_removals = None
        self._iterating = 0
        self._callback = _WeakSetCallback(self)
        if (iterable is not None):
            self.update(iterable)
    
    # __init_subclass__ -> same
    
    @has_docs
    def __ior__(self, other):
        """Updates the set with the element of others"""
        if isinstance(other, type(self)) or hasattr(type(other), '__iter__'):
            for element in other:
                self.add(element)
            
            return self
        
        return NotImplemented
    
    
    @has_docs
    def __isub__(self, other):
        """Update the set, removing elements found in others."""
        if isinstance(other, type(self)):
            for weak_element in set.__iter__(other):
                set.discard(self, weak_element)
        
        elif hasattr(type(other), '__iter__'):
            for element in other:
                self.discard(element)
        
        else:
            return NotImplemented
        
        return self
    
    @has_docs
    def __iter__(self):
        """
        Iterates over a weak set's elements.
        
        This method is a generator.
        
        Yields
        ------
        element : `Any`
        """
        self._iterating += 1
        
        try:
            for key_reference in set.__iter__(self):
                key = key_reference()
                if (key is None):
                    add_to_pending_removals(self, key_reference)
                    continue
                
                yield key
                continue
        
        finally:
            self._iterating -= 1
            self._commit_removals()
    
    @has_docs
    def __ixor__(self, other):
        """Update the set, keeping only elements found in either set, but not in both."""
        if isinstance(other, type(self)):
            for weak_element in set.__iter__(other):
                element = weak_element()
                if element is None:
                    continue
                
                try:
                    set.remove(self, weak_element)
                except KeyError:
                    self.add(element)
        
        elif isinstance(other, (set, dict)):
            for element in other:
                
                try:
                    self.remove(element)
                except KeyError:
                    self.add(element)
        
        elif hasattr(type(other), '__iter__'):
            # Make sure, we have unique elements, so convert other to set
            for element in set(other):
                
                try:
                    self.remove(element)
                except KeyError:
                    self.add(element)
        
        else:
            return NotImplemented
        
        return self
    
    @has_docs
    def __le__(self, other):
        """Test whether every element in the set is in other."""
        if isinstance(other, type(self)):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = type(self)(other)
        
        else:
            return NotImplemented
        
        return set.__le__(self, other)
    
    
    @has_docs
    def __len__(self):
        """Returns the length of the set."""
        length = set.__len__(self)
        pending_removals = self._pending_removals
        if (pending_removals is not None):
            length -= len(pending_removals)
        
        return length
    
    @has_docs
    def __lt__(self, other):
        """Test whether the set is a proper superset of other"""
        if isinstance(other, type(self)):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = type(self)(other)
        
        else:
            return NotImplemented
        
        return set.__lt__(self, other)
    
    # __ne__ -> same
    # __new__-> same
    
    @has_docs
    def __or__(self, other):
        """Returns the union of two sets."""
        if isinstance(other, type(self)) or hasattr(type(other), '__iter__'):
            new = self.copy()
            
            for element in other:
                new.add(element)
            
            return new
        
        return NotImplemented
    
    @has_docs
    def __rand__(self, other):
        """Returns a new set with the elements common of self and other."""
        return self.__and__(other)
    
    @has_docs
    def __reduce__(self):
        """Reduces the set to a picklable object."""
        return (type(self), list(self))
    
    @has_docs
    def __reduce_ex__(self, version):
        """Reduces the set to a picklable object."""
        return type(self).__reduce__(self)
    
    @has_docs
    def __repr__(self):
        """Returns the set's representation."""
        result = [self.__class__.__name__, '({']
        if len(self):
            limit = self.MAX_REPR_ELEMENT_LIMIT
            collected = 0
            
            for element_reference in set.__iter__(self):
                element = element_reference()
                if (element is None):
                    add_to_pending_removals(self, element_reference)
                    continue
                
                result.append(repr(element))
                result.append(', ')
                
                collected +=1
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
    
    __ror__ = __or__
    
    @has_docs
    def __rsub__(self, other):
        """Returns a new the set, without elements found in self."""
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            return NotImplemented
        
        new = type(self)()
        
        for element in other:
            if element not in self:
                new.add(element)
        
        return new
    
    @has_docs
    def __rxor__(self, other):
        """Return a new set with elements in either the set or other but not both."""
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        return type(self)(self_set ^ other)
    
    # __setattr__ -> same
    # __sizeof__ -> same
    
    __str__ = __repr__
    
    @has_docs
    def __sub__(self, other):
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            return NotImplemented
        
        new = type(self)()
        
        for element in self:
            if element not in other:
                new.add(element)
        
        return new
    
    # __subclasshook__ -> same
    
    __xor__ = __rxor__
    
    @has_docs
    def add(self, element):
        """
        Adds the `element` to the set.
        
        Parameters
        ----------
        element : `Any`
            The element to add.
        
        Raises
        ------
        TypeError
            If `element` is not weakreferable.
        """
        element_reference = WeakReferer(element, self._callback)
        set.add(self, element_reference)
    
    @has_docs
    def clear(self):
        """Remove all elements from the set."""
        self._pending_removals = None
        set.clear(self)
    
    @has_docs
    def copy(self):
        """Return a shallow copy of the set."""
        new = type(self)()
        new_callback = new._callback
        
        for element_reference in set.__iter__(self):
            element = element_reference()
            if (element is not None):
                element_reference =  WeakReferer(element, new_callback)
                set.add(new, element_reference)
    
    
    difference = __sub__
    
    difference_update = __isub__
    
    @has_docs
    def discard(self, element):
        """
        Removes `element` from the set if it is present.
        
        Parameters
        ----------
        element : `Any`
            The element to remove.
        """
        try:
            element_reference = WeakReferer(element)
        except TypeError:
            pass
        else:
            set.discard(self, element_reference)
    
    intersection = __and__
    
    intersection_update = __iand__
    
    @has_docs
    def isdisjoint(self, other):
        """
        Return whether if the set has no elements in common with other. Sets are disjoint if and only if
        their intersection is the empty set.
        
        Returns
        -------
        is_disjoint : `bool`
        """
        if isinstance(other, type(self)):
            return set.isdisjoint(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            raise TypeError(
                f'`Cannot discount with other, got {other.__class__.__name__}; {other!r}.'
            )
        
        self_set = set(iter(self))
        return self_set.isdisjoint(other)
    
    
    issubset = __le__
    
    issuperset = __ge__
    
    @has_docs
    def pop(self):
        """
        Remove and return an arbitrary element from the set.
        
        Returns
        -------
        element
        
        Raises
        ------
        KeyError
            If the set is empty.
        """
        while True:
            element_reference = set.pop(self)
            
            element = element_reference()
            if (element is not None):
                return element
    
    @has_docs
    def remove(self, element):
        """
        Removes `element` from the set.
        
        Parameters
        ----------
        element : `Any`
            The element ot remove.
        
        Raises
        ------
        KeyError
            If `element` is not in the set.
        """
        try:
            element_reference = WeakReferer(element)
        except TypeError:
            raise KeyError(element) from None
        
        set.remove(self, element_reference)
    
    
    symmetric_difference = __xor__
    
    symmetric_difference_update = __xor__
    
    union = __or__
    
    update = __ior__
