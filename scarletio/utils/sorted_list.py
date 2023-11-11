__all__ = ('SortedList', )

from .docs import has_docs
from .removed_descriptor import RemovedDescriptor


@has_docs
class SortedList(list):
    """
    An auto sorted list.
    
    Attributes
    ----------
    _reversed : `bool`
        Whether the list is reversed.
    """
    __slots__ = ('_reversed', )
    
    __setitem__ = RemovedDescriptor()
    insert = RemovedDescriptor()
    sort = RemovedDescriptor()
    __add__ = RemovedDescriptor()
    __radd__ = RemovedDescriptor()
    __iadd__ = RemovedDescriptor()
    __mul__ = RemovedDescriptor()
    __rmul__ = RemovedDescriptor()
    __imul__ = RemovedDescriptor()
    append = RemovedDescriptor()
    
    @has_docs
    def __init__(self, iterable = None, reverse = False):
        """
        Creates a new ``SortedList`` with the given parameters.
        
        Parameters
        ----------
        it : `None`, `iterable`, Optional
            An iterable to extend the created list with.
        reverse : `bool`, Optional
            Whether the created list should be reversed sorted.
        """
        self._reversed = reverse
        if (iterable is not None):
            self.extend(iterable)
            list.sort(self, reverse = reverse)
    
    
    @has_docs
    def __repr__(self):
        """Returns the sorted list's representation."""
        result = [self.__class__.__name__, '([']
        
        limit = len(self)
        if limit:
            index = 0
            while True:
                element = self[index]
                index += 1
                result.append(repr(element))
                
                if index == limit:
                    break
                
                result.append(', ')
                continue
        
        result.append('], reversed = ')
        result.append(repr(self._reversed))
        result.append(')')
        
        return ''.join(result)
    
    def __getstate__(self):
        return self._reversed
    
    def __setstate__(self, state):
        self._reversed = state
    
    @property
    @has_docs
    def reverse(self):
        """
        A get-set descriptor to check or set how the sorted list sorted.
        """
        return self._reversed
    
    @reverse.setter
    def reverse(self, value):
        if self._reversed == value:
            return
        
        self._reversed = value
        list.reverse(self)
    
    @has_docs
    def add(self, value):
        """
        Adds a new value to the sorted list.
        
        Parameters
        ----------
        value : `object`
            The value to insert to the SortedList.
        """
        index = self.relative_index(value)
        if index == len(self):
            # If the the index is at the end, then we just list append it.
            list.append(self, value)
            return
        
        element = self[index]
        if element == value:
            # If the element is same as the current, we overwrite it.
            list.__setitem__(self, index, value)
            return
        
        # No more special cases, simply list insert it
        list.insert(self, index, value)
        return
    
    
    @has_docs
    def remove(self, value):
        """
        Removes the given value from the SortedList.
        
        If the value is not in the list will not raise.
        
        Parameters
        ----------
        value : `object`
            The value to remove.
        """
        index = self.relative_index(value)
        if index == len(self):
            # The element is not at self, leave
            return
        
        element = self[index]
        if element != value:
            # The element is different as the already added one att the correct position, leave.
            return
        
        # No more special case, remove it.
        list.__delitem__(self, index)
    
    
    @has_docs
    def extend(self, iterable):
        """
        Extends the SortedList with the given iterable object.
        
        Parameters
        ----------
        iterable : `iterable`
            Iterable object to extend the SortedList with.
        """
        ln = len(self)
        insert = list.insert
        bot = 0
        if self._reversed:
            if type(self) is not type(iterable):
                other = sorted(iterable, reverse = True)
            elif not iterable._reversed:
                other = reversed(iterable)
            else:
                other = iterable
            
            for value in other:
                top = ln
                while True:
                    if bot < top:
                        half = (bot + top) >> 1
                        if self[half] > value:
                            bot = half + 1
                        else:
                            top = half
                        continue
                    break
                insert(self, bot, value)
                ln += 1
        else:
            if type(self) is not type(iterable):
                other = sorted(iterable)
            elif iterable._reversed:
                other = reversed(iterable)
            else:
                other = iterable
            
            for value in other:
                top = ln
                while True:
                    if bot < top:
                        half = (bot + top) >> 1
                        if self[half] < value:
                            bot = half + 1
                        else:
                            top = half
                        continue
                    break
                insert(self, bot, value)
                ln += 1
    
    
    @has_docs
    def __contains__(self, value):
        """Returns whether the SortedList contains the given value."""
        index = self.relative_index(value)
        if index == len(self):
            return False
        
        if self[index] == value:
            return True
        
        return False
    
    
    @has_docs
    def index(self, value):
        """Returns the index of the given value inside of the SortedList."""
        index = self.relative_index(value)
        if index == len(self) or self[index] != value:
            raise ValueError(f'{value!r} is not in the {self.__class__.__name__}.')
        
        return index
    
    
    @has_docs
    def relative_index(self, value):
        """
        Returns the relative index of the given value if it would be inside of the SortedList.
        
        Parameters
        ----------
        value : `object`
            The object's what's relative index is returned.
        
        Returns
        -------
        relative_index : `bool`
            The index where the given value would be inserted or should be inside of the SortedList.
        """
        bot = 0
        top = len(self)
        if self._reversed:
            while True:
                if bot < top:
                    half = (bot + top) >> 1
                    if self[half] > value:
                        bot = half + 1
                    else:
                        top = half
                    continue
                break
        else:
            while True:
                if bot < top:
                    half = (bot + top) >> 1
                    if self[half] < value:
                        bot = half + 1
                    else:
                        top = half
                    continue
                break
        
        return bot
    
    
    @has_docs
    def keyed_relative_index(self, value, key):
        """
        Returns the relative index of the given value if it would be inside of the SortedList.
        
        Parameters
        ----------
        value : `object`
            The object's what's relative index is returned.
        key : `callable`
            A function that serves as a key for the sort comparison.
        
        Returns
        -------
        relative_index : `bool`
            The index where the given value would be inserted or should be inside of the SortedList.
        """
        bot = 0
        top = len(self)
        if self._reversed:
            while True:
                if bot < top:
                    half = (bot + top) >> 1
                    if key(self[half]) > value:
                        bot = half + 1
                    else:
                        top = half
                    continue
                break
        else:
            while True:
                if bot < top:
                    half = (bot + top) >> 1
                    if key(self[half]) < value:
                        bot = half + 1
                    else:
                        top = half
                    continue
                break
        return bot
    
    
    @has_docs
    def copy(self):
        """
        Copies the SortedList.
        
        Returns
        -------
        new : ``SortedList``
        """
        new = list.__new__(type(self))
        new._reversed = self._reversed
        list.extend(new, self)
        return new
    
    
    @has_docs
    def resort(self):
        """
        Resorts the SortedList.
        """
        list.sort(self, reverse = self._reversed)
    
    
    @has_docs
    def get(self, value, key, default = None):
        """
        Gets an element from the SortedList, what passed trough `key` equals to the given value.
        
        Parameters
        ----------
        value : `object`
            The value to search in the SortedList.
        key : `callable`
            A function that serves as a key for the sort comparison.
        default : `object` = `None`, Optional
            Default value to returns if no matching element was present.
        
        Returns
        -------
        element : `object`, `default`
            The matched element or the `default` value if not found.
        """
        index = self.keyed_relative_index(value, key)
        if index == len(self):
            return default
        
        element = self[index]
        if key(element) == value:
            return element
        
        return default
    
    
    @has_docs
    def pop(self, value, key, default = None):
        """
        Gets and removes element from the SortedList, what's is passed trough `key` equals to the given value.
        
        Parameters
        ----------
        value : `object`
            The value to search in the SortedList.
        key : `callable`
            A function that serves as a key for the sort comparison.
        default : `object` = `None`, Optional
            Default value to returns if no matching element was present.
        
        Returns
        -------
        element : `object`, `default`
            The matched element or the `default` value if not found.
        """
        index = self.keyed_relative_index(value, key)
        if index == len(self):
            return default
        
        element = self[index]
        if key(element) == value:
            del self[index]
            return element
        
        return default
