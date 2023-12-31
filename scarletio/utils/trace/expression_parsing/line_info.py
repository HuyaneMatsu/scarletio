__all__ = ('LineInfo',)

from os import stat as get_stats

from .cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE, LINE_INFO_CACHE, LINE_CACHE_MAX_SIZE
from .file_info import get_file_info


class LineInfo:
    """
    Represents a cached line.
    
    Attributes
    ----------
    file_modification_time : `float`
        When the file was last modified. Using system time. Used to identify file modifications.
    file_name : `str`
        The line's owner file's name.
    file_size : `int`
        The file's size. Used to identify file modifications.
    hit : `bool`
        Whether the line is a hit.
    index : `int`
        The line's index.
    line : `str`
        The stored line. Can be an empty string.
    """
    __slots__ = ('file_modification_time', 'file_name', 'file_size', 'hit', 'index', 'line')
    
    def __new__(cls, file_name, file_size, file_modification_time, line, index, hit):
        """
        Creates a new line info.
        
        Parameters
        ----------
        file_name : `str`
            The line's owner file's name.
        file_size : `int`
            The file's size.
        file_modification_time : `float`
            When the file was last modified.
        line : `str`
            The stored line.
        index : `int`
            The line's index.
        hit : `bool`
            Whether the line is a hit.
        """
        self = object.__new__(cls)
        self.file_modification_time = file_modification_time
        self.file_name = file_name
        self.file_size = file_size
        self.hit = hit
        self.index = index
        self.line = line
        return self
    
    
    def __repr__(self):
        """Returns the line info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' file_modification_time = ')
        repr_parts.append(repr(self.file_modification_time))
        
        repr_parts.append(', file_name = ')
        repr_parts.append(repr(self.file_name))
        
        repr_parts.append(', file_size = ')
        repr_parts.append(repr(self.file_size))
        
        repr_parts.append(', hit = ')
        repr_parts.append(repr(self.hit))
        
        repr_parts.append(', index = ')
        repr_parts.append(repr(self.index))
        
        repr_parts.append(', line = ')
        repr_parts.append(repr(self.line))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def is_up_to_date(self):
        """
        Returns whether the line info is up to date.
        
        Returns
        -------
        is_up_to_date : `bool`
        """
        file_name = self.file_name
        try:
            file_info = FILE_INFO_CACHE[file_name]
        except KeyError:
            pass
        else:
            if file_info.console:
                try:
                    CONSOLE_INPUT_CACHE.move_to_end(file_name)
                except KeyError:
                    CONSOLE_INPUT_CACHE[file_name] = file_info
                return True
            
            if not file_info.alive:
                return True
            
            if self.file_size != file_info.file_size:
                return False
            
            if self.file_modification_time != file_info.file_modification_time:
                return False
            
            return True
        
        try:
            stats = get_stats(file_name)
        except OSError:
            pass
        else:
            if self.file_size != stats.st_size:
                return False
            
            if self.file_modification_time != stats.st_mtime:
                return False
            
            return True
        
        return False
    
    
    def update(self):
        """
        Updates the line info.
        """
        file_info = get_file_info(self.file_name)
        if file_info.alive:
            self.hit, self.line = file_info.get_line(self.index)
        
    
    def get(self):
        """
        Gets the line of the line info. Updates it if required.
        
        Returns
        -------
        hit : `bool`
            whether the line is a hit.
        line : `str`
            The line of the line info.
        """
        if not self.is_up_to_date():
            self.update()
        
        return self.hit, self.line


def get_file_line(file_name, line_index):
    """
    Gets the file's line.
    
    Parameters
    ----------
    file_name : `str`
        The file's name.
    line_index : `int`
        The line's index to get.
    
    Returns
    -------
    hit : `bool`
    line : `str`
    """
    key = (file_name, line_index)
    
    # Try get from cache
    try:
        line_info = LINE_INFO_CACHE[key]
    except KeyError:
        pass
    else:
        LINE_INFO_CACHE.move_to_end(key)
        return line_info.get()
    
    # Get file -> get line -> cache it
    file_info = get_file_info(file_name)
    hit, line = file_info.get_line(line_index)
    line_info = LineInfo(file_name, file_info.file_size, file_info.file_modification_time, line, line_index, hit)
    LINE_INFO_CACHE[key] = line_info
    
    if len(LINE_INFO_CACHE) >= LINE_CACHE_MAX_SIZE:
        del LINE_INFO_CACHE[next(iter(LINE_INFO_CACHE))]
    
    return hit, line
