__all__ = ()

from .docs import has_docs
from .utils import is_iterable

@has_docs
class DictionaryKeyIteratorBase:
    """
    Key iterator of a dictionary..
    
    Attributes
    ----------
    _parent : `dict`
        The parent dictionary.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new dictionary key iterator bound to the given dictionary.
        
        Parameters
        ----------
        parent : `dict`
            The parent dictionary.
        """
        self._parent = parent
    
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the dictionary's keys.
        
        This method is an iterable generator.
        
        Yields
        ------
        key : `object`
        """
        return
        yield
    
    
    @has_docs
    def __contains__(self, contains_key):
        """Returns whether the respective dictionary contains the given key."""
        return False
    
    
    @has_docs
    def __len__(self):
        """Returns the respective dictionary's length."""
        return len(self._parent)
    
    
    @has_docs
    def __repr__(self):
        """Returns the dictionary key iterator's representation."""
        return f'<{self.__class__.__name__} to {self._parent!r}>'


    @has_docs
    def __eq__(self, other):
        """Returns whether the two dictionary key iterators are the same."""
        if isinstance(other, type(self)):
            return self._parent == other._parent
        
        return self._parent.__eq__(other)


@has_docs
class DictionaryValueIteratorBase:
    """
    Value iterator of a dictionary..
    
    Attributes
    ----------
    _parent : `dict`
        The parent dictionary.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new dictionary value iterator bound to the given dictionary.
        
        Parameters
        ----------
        parent : `dict`
            The parent dictionary.
        """
        self._parent = parent
    
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the dictionary's values.
        
        This method is an iterable generator.
        
        Yields
        ------
        value : `object`
        """
        return
        yield
    
    
    @has_docs
    def __contains__(self, contains_value):
        """Returns whether the respective dictionary contains the given value."""
        return False
    
    
    @has_docs
    def __len__(self):
        """Returns the respective dictionary's length."""
        return len(self._parent)
    
    
    @has_docs
    def __repr__(self):
        """Returns the dictionary value iterator's representation."""
        return f'<{self.__class__.__name__} to {self._parent!r}>'
    
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the two dictionary item iterators are the same."""
        if isinstance(other, type(self)):
            return self._parent == other._parent
        
        elif isinstance(other, list):
            if len(self) != len(other):
                return False
            
            other = other.copy()
        
        elif is_iterable(other):
            has_length_method = hasattr(type(other), '__len__')
            
            if has_length_method:
                if len(self) != len(other):
                    return False
            
            other = list(other)
            
            if not has_length_method:
                if len(self) != len(other):
                    return False
        
        else:
            return NotImplemented
        
        for value in self:
            try:
                other.remove(value)
            except ValueError:
                return False
        
        if other:
            return False
        
        return True


@has_docs
class DictionaryItemIteratorBase:
    """
    Item iterator of a dictionary..
    
    Attributes
    ----------
    _parent : `dict`
        The parent dictionary.
    """
    __slots__ = ('_parent',)
    
    @has_docs
    def __init__(self, parent):
        """
        Creates a new dictionary item iterator bound to the given dictionary.
        
        Parameters
        ----------
        parent : `dict`
            The parent dictionary.
        """
        self._parent = parent
    
    
    @has_docs
    def __iter__(self):
        """
        Iterates over the dictionary's items.
        
        This method is an iterable generator.
        
        Yields
        ------
        item : `tuple` (`object`, `str`)
        """
        return
        yield
    
    
    @has_docs
    def __contains__(self, contains_item):
        """Returns whether the respective dictionary contains the given item."""
        return False
    
    
    @has_docs
    def __len__(self):
        """Returns the respective dictionary's length."""
        return len(self._parent)
    
    
    @has_docs
    def __repr__(self):
        """Returns the dictionary item iterator's representation."""
        return f'<{self.__class__.__name__} to {self._parent!r}>'
    
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the two dictionary item iterators are the same."""
        if isinstance(other, type(self)):
            return self._parent == other._parent
        
        elif isinstance(other, list):
            if len(self) != len(other):
                return False
            
            other = other.copy()
        
        elif is_iterable(other):
            has_length_method = hasattr(type(other), '__len__')
            
            if has_length_method:
                if len(self) != len(other):
                    return False
            
            other = list(other)
            
            if not has_length_method:
                if len(self) != len(other):
                    return False
        
        else:
            return NotImplemented
        
        for item in self:
            try:
                other.remove(item)
            except ValueError:
                return False
        
        if other:
            return False
        
        return True
