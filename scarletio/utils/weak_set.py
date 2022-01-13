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
    __slots__ = ('__weakref__', '_pending_removals', '_iterating', '_callback')
    
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
    
    # TODO
    '''
    @has_docs
    def __or__(self, other):
        """Returns the union of two sets."""
        new = self.copy()
        for element in iter_to_non_weak_set(other):
            if element in self:
                self.discard(element)
            else:
                self.add(element)
        
        return new
    
    __rand__
    __reduce__
    __reduce_ex__
    __repr__
    __ror__
    __rsub__
    __rxor__
    __setattr__
    __sizeof__
    __str__
    __sub__
    __subclasshook__
    __xor__
    add
    clear
    copy
    difference
    difference_update
    discard
    intersection
    intersection_update
    isdisjoint
    issubset
    issuperset
    pop
    remove
    symmetric_difference
    symmetric_difference_update
    union
    update
    '''