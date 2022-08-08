__all__ = ()


class History:
    """
    Represents an editor's history.
    
    Attributes
    ----------
    _cursor_index : `int`
        The position where the cache lookup is at.
    _elements : `dict` of (`int`, `list` of `str`) items
        The added elements to the history.
    _line_cache : `dict` of (`str`, `str`) items
        Line cache caching same lines.
    _size : `int`
        The last registered content's index.
    """
    __slots__ = ('_cursor_index', '_elements', '_line_cache', '_size')
    
    def __new__(cls):
        """
        Creates a editor history.
        """
        self = object.__new__(cls)
        self._line_cache = {}
        self._cursor_index = 0
        self._elements = {}
        self._size = 0
        return self
    
    
    def __repr__(self):
        """Returns representation of the history."""    
        repr_parts = ['<', self.__class__.__name__]
        
        repr_parts.append(' cache: ')
        repr_parts.append(repr(len(self._line_cache)))
        
        repr_parts.append(', elements: ')
        repr_parts.append(repr(len(self._elements)))
        
        repr_parts.append(', size: ')
        repr_parts.append(repr(self._size))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def maybe_add_buffer_of(self, index, editor):
        """
        Adds the given editor's buffer into the history if it supports lookup.
        
        Parameters
        ----------
        editor : ``EditorBase`
            The editor to add it's content.
        buffer : `list` of `str`
            The buffer to add.
        
        Returns
        -------
        added : `bool`
            Whether anything was added.
        """
        self._size = index
        self._cursor_index = index + 1
        
        if (editor is None) or (not editor.has_history_support()):
            return False
        
        return self._add(index, editor.get_stripped_buffer())
    
    
    def _add(self, index, buffer):
        """
        Adds a new element into the history.
        
        Parameters
        ----------
        index : `int`
            The index of the element.
        buffer : `list` of `str`
            The buffer to add.
        
        Returns
        -------
        added : `bool`
            Whether anything was added.
        """
        if buffer:
            line_cache = self._line_cache
            
            element = [line_cache.setdefault(line, line) for line in buffer]
            self._elements[index] = element
            added = True
        
        else:
            added = False
        
        return added
    
    
    def reset_cursor_index(self):
        """
        Resets the cursor's position.
        """
        self._cursor_index = self._size + 1
    
    
    def get_at(self, index):
        """
        Returns the element at the specified position.
        
        Parameters
        ----------
        index : `list` of `int`
            The parameter's index to get.
        
        Returns
        -------
        element : `None`, `list` of `str`
        """
        return self._elements.get(index, None)
    
    
    def get_at_cursor_index_position(self):
        """
        Returns the element at the cursor's current position.
        
        Returns
        -------
        element : `None`, `list` of `str`
        """
        return self._elements.get(self._cursor_index, None)
    
    
    def get_previous(self):
        """
        Gets the previous element of the history moving the cursor.
        
        Returns
        -------
        previous : `None`, `list` of `str`
        """
        cursor_index = self._cursor_index
        elements = self._elements
        current = elements.get(cursor_index, None)
        
        while cursor_index > -1:
            cursor_index -= 1
            element = elements.get(cursor_index, None)
            if (element is not None) and element != current:
                previous = element
                break
        else:
            previous = None
        
        self._cursor_index = cursor_index
        return previous
    
    
    def get_next(self):
        """
        Gets the next element of the history moving the cursor.
        
        Returns
        -------
        next_ : `None`, `list` of `str`
        """
        cursor_index = self._cursor_index
        elements = self._elements
        current = elements.get(cursor_index, None)
        size = self._size
        
        while cursor_index < size:
            cursor_index += 1
            element = elements.get(cursor_index, None)
            if (element is not None) and element != current:
                next_ = element
                break
        else:
            next_ = None
        
        self._cursor_index = cursor_index
        return next_
