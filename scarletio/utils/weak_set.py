__all__ = ('WeakSet',)

from .docs import has_docs
from .utils import is_hashable
from .weak_core import WeakReferer, add_to_pending_removals, is_weakreferable


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
                    try:
                        new.add(element)
                    except TypeError:
                        return NotImplemented
            
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
        
        return set.__contains__(self, element)
    
    
    # __delattr__ -> same
    # __dir__ -> same
    # __doc__ -> same
    
    
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return set.__eq__(self, other)
        
        if isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        return self_set == other
    
    
    # __format__ -> same
    
    
    @has_docs
    def __ge__(self, other):
        """Returns whether every element in other is in the set."""
        if isinstance(other, type(self)):
            return set.__ge__(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        return set(iter(self)) >= other
    
    
    # __getattribute__ -> same
    
    
    @has_docs
    def __gt__(self, other):
        """Returns whether the set is a proper superset of other."""
        if isinstance(other, type(self)):
            return set.__gt__(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        return set(iter(self)) > other
    
    
    # __hash__ ->same
    
    
    @has_docs
    def __iand__(self, other):
        """Update the set, keeping only elements found in it and all others."""
        if isinstance(other, type(self)):
            other_set = set(iter(other))
        
        elif isinstance(other, set):
            other_set = other
        
        elif hasattr(type(other), '__iter__'):
            try:
                other_set = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        elements_to_remove = []
        
        for element in self:
            if element not in other_set:
                elements_to_remove.append(element)
        
        for element in elements_to_remove:
            self.discard(element)
        
        return self
    
    
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
        if isinstance(other, type(self)):
            pass
        
        elif isinstance(other, (set, dict)):
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
            
        elif isinstance(other, (tuple, list)):
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
                
                if not is_hashable(element):
                    return NotImplemented
                    
        elif hasattr(type(other), '__iter__'):
            # Make sure, we have unique elements, so convert other to set
            other = list(other)
            
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
                
                if not is_hashable(element):
                    return NotImplemented
        
        else:
            return NotImplemented
        
        for element in other:
            self.add(element)
        
        return self
    
    
    @has_docs
    def __isub__(self, other):
        """Update the set, removing elements found in others."""
        if isinstance(other, type(self)):
            for weak_element in set.__iter__(other):
                set.discard(self, weak_element)
            
            return self
        
        elif hasattr(type(other), '__iter__'):
            pass
        
        else:
            return NotImplemented
        
        for element in other:
            self.discard(element)
        
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
            
            return self
        
        if isinstance(other, (set, dict)):
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
            
        elif isinstance(other, (tuple, list)):
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
                
                if not is_hashable(element):
                    return NotImplemented
                    
        elif hasattr(type(other), '__iter__'):
            # Make sure, we have unique elements, so convert other to set
            other = list(other)
            
            for element in other:
                if not is_weakreferable(element):
                    return NotImplemented
                
                if not is_hashable(element):
                    return NotImplemented
        
        else:
            return NotImplemented
        
        for element in other:
            try:
                self.remove(element)
            except KeyError:
                self.add(element)
        
        return self
    
    
    @has_docs
    def __le__(self, other):
        """Test whether every element in the set is in other."""
        if isinstance(other, type(self)):
            return set.__le__(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        return set(iter(self)) <= other
    
    
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
            return set.__lt__(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        return set(iter(self)) < other
    
    
    def  __ne__(self, other):
        if isinstance(other, type(self)):
            return set.__ne__(self, other)
        
        if isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented
        
        self_elements = set(iter(self))
        
        return self_elements != other
    
    
    # __new__-> same
    
    
    @has_docs
    def __or__(self, other):
        """Returns the union of two sets."""
        if isinstance(other, type(self)):
            new = self.copy()
            
            for element in other:
                new.add(element)
        
        elif hasattr(type(other), '__iter__'):
            new = self.copy()
            
            for element in other:
                try:
                    new.add(element)
                except TypeError:
                    return NotImplemented
            
        else:
            return NotImplemented
        
        return new
    
    __rand__ = __and__
    
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
        """Returns a new set, without elements found in self."""
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        
        else:
            return NotImplemented
        
        new = type(self)()
        
        for element in other:
            if element not in self:
                try:
                    new.add(element)
                except TypeError:
                    return NotImplemented
        
        return new
    
    
    @has_docs
    def __rxor__(self, other):
        """Return a new set with elements in either the set or other but not both."""
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        
        else:
            return NotImplemented
        
        self_set = set(iter(self))
        
        new = type(self)()
        
        for element in (self_set ^ other):
            try:
                new.add(element)
            except TypeError:
                return NotImplemented
        
        return new
    
    
    # __setattr__ -> same
    # __sizeof__ -> same
    
    
    __str__ = __repr__
    
    
    @has_docs
    def __sub__(self, other):
        """Returns a new set, without elements found in other."""
        if isinstance(other, type(self)):
            other = set(iter(other))
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            try:
                other = set(other)
            except TypeError:
                return NotImplemented
        
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
        
        return new
    
    
    def difference(self, iterable):
        """
        Returns a new set, without elements found in `iterable`.
        
        Parameters
        ----------
        iterable : `iterable`
            The values to get difference with.
        
        Returns
        -------
        new : ``WeakSet``
        
        Raises
        ------
        TypeError
            - If `iterable` is not `iterable`.
            - If an element of `iterable` is not hashable.
            - If an element of `iterable` is now weakreferable.
        """
        if isinstance(iterable, type(self)):
            iterable = set(iter(iterable))
        
        elif isinstance(iterable, set):
            pass
        
        elif hasattr(type(iterable), '__iter__'):
            iterable = set(iterable)
        
        else:
            raise TypeError(
                f'`iterable` can be `iterable`, got {iterable.__class__.__name__}; {iterable!r}.'
            )
        
        new = type(self)()
        
        for element in self:
            if element not in iterable:
                new.add(element)
        
        return new
    
    
    def difference_update(self, iterable):
        """
        Update the set, removing elements found in others.
        
        Parameters
        ----------
        iterable : `iterable`
            The values to make difference with.
        
        Raises
        ------
        TypeError
            - If `iterable` is not `iterable`.
            - If an element of `iterable` is not hashable.
            - If an element of `iterable` is now weakreferable.
        """
        if isinstance(iterable, type(self)):
            for weak_element in set.__iter__(iterable):
                set.discard(self, weak_element)
        
        elif hasattr(type(iterable), '__iter__'):
            for element in iterable:
                self.discard(element)
        
        else:
            raise TypeError(
                f'`iterable` can be `iterable`, got {iterable.__class__.__name__}; {iterable!r}.'
            )
    
    
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
    
    
    @has_docs
    def intersection(self, iterable):
        """
        Returns a new set with the elements common of self and other.
        
        Parameters
        ----------
        iterable : `iterable`
            The values to make difference with.
        
        Raises
        ------
        TypeError
            - If `iterable` is not `iterable`.
            - If an element of `iterable` is not hashable.
            - If an element of `iterable` is now weakreferable.
        """
        if isinstance(iterable, type(self)):
            new = type(self)()
            
            for weak_element in set.__iter__(iterable):
                if set.__contains__(self, weak_element):
                    element = weak_element()
                    if (element is not None):
                        new.add(element)
            
            return new
        
        if hasattr(type(iterable), '__iter__'):
            new = type(self)()
            
            for element in iterable:
                if element in self:
                    new.add(element)
            
            return new
        
        raise TypeError(
            f'`iterable` can be `iterable`, got {iterable.__class__.__name__}; {iterable!r}.'
        )
    
    
    @has_docs
    def intersection_update(self, iterable):
        """
        Update the set, keeping only elements found in it and all others.
        
        Parameters
        ----------
        iterable : `iterable`
            The values to make difference with.
        
        Raises
        ------
        TypeError
            - If `iterable` is not `iterable`.
            - If an element of `iterable` is not hashable.
        """
        if isinstance(iterable, type(self)):
            iterable_set = set(iter(iterable))
        
        elif isinstance(iterable, set):
            iterable_set = iterable
        
        elif hasattr(type(iterable), '__iter__'):
            iterable_set = set(iterable)
        
        else:
            raise TypeError(
                f'`iterable` can be `iterable`, got {iterable.__class__.__name__}; {iterable!r}.'
            )
        
        elements_to_remove = []
        
        for element in self:
            if element not in iterable_set:
                elements_to_remove.append(element)
        
        for element in elements_to_remove:
            self.discard(element)
    
    
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
            other = set(iter(other))
            
            # Something breaks the normal solution:
            # return set.isdisjoint(self, other)
        
        elif isinstance(other, set):
            pass
        
        elif hasattr(type(other), '__iter__'):
            other = set(other)
        
        else:
            raise TypeError(
                f'`Cannot disjoint with other, got {other.__class__.__name__}; {other!r}.'
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
    
    symmetric_difference_update = __ixor__
    
    union = __or__
    
    def update(self, iterable):
        """
        Updates the set in-place.
        
        Parameters
        ----------
        iterable : `iterable`
            Iterable to extend the set's elements with.
        
        Raises
        ------
        TypeError
            - If `iterable` is not iterable.
            - If an element of `iterable` is not hashable.
            - If an element of `iterable` is not weakreferable.
        """
        if isinstance(iterable, type(self)) or hasattr(iterable, '__iter__'):
            for element in iterable:
                self.add(element)
        
        else:
            raise TypeError(
                f'`iterable` can be `iterable`, got {iterable.__class__.__name__}; {iterable!r}.'
            )