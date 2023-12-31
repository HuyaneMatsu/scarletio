__all__ = ('FileInfo',)

from os import stat as get_stats

from .cache_constants import FILE_INFO_CACHE, LINE_CACHE_SESSIONS


class FileInfo:
    """
    Represents a file.
    
    Attributes
    ----------
    alive : `bool`
        Whether the file's source is alive.
    console : `bool`
        Whether the file's source is from console.
    file_modification_time : `float`
        When the file was last modified. Using system time. Used to identify file modifications.
    file_name : `str`
        The line's owner file's name.
    file_size : `int`
        The file's size. Used to identify file modifications.
    lines : `list<str>`
        The file's lines.
    """
    __slots__ = ('__weakref__', 'alive', 'console', 'file_modification_time', 'file_name', 'file_size', 'lines')
    
    def __new__(cls, file_name, file_size, file_modification_time, lines, alive, console):
        """
        Creates a new file info.
        
        Parameters
        ----------
        file_name : `str`
            The line's owner file's name.
        file_size : `int`
            The file's size.
        file_modification_time : `float`
            When the file was last modified.
        lines : `list<str>`
            The file's lines.
        alive : `bool`
            Whether the file's source is alive.
        console : `bool`
            Whether the file's source is from console.
        """
        self = object.__new__(cls)
        self.alive = alive
        self.console = console
        self.file_modification_time = file_modification_time
        self.file_name = file_name
        self.file_size = file_size
        self.lines = lines
        return self
    
    
    def __repr__(self):
        """Returns the file info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(', alive = ')
        repr_parts.append(repr(self.alive))
        
        repr_parts.append(', console = ')
        repr_parts.append(repr(self.console))
        
        repr_parts.append(' file_modification_time = ')
        repr_parts.append(repr(self.file_modification_time))
        
        repr_parts.append(', file_name = ')
        repr_parts.append(repr(self.file_name))
        
        repr_parts.append(', file_size = ')
        repr_parts.append(repr(self.file_size))
        
        repr_parts.append(', lines = ')
        repr_parts.append(repr(self.lines))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def get_line(self, index):
        """
        Gets the line of the file.
        
        Parameters
        ----------
        index : `int`
            The line's index.
        
        Returns
        -------
        hit : `bool`
        line : `str`
        """
        if index < 0:
            return False, ''
        
        lines = self.lines
        if index >= len(lines):
            return False, ''
        
        return True, lines[index]


def get_file_info(file_name):
    """
    Gets file info for the given file name.
    
    Parameters
    ----------
    file_name : `str`
        The file's name.
    
    Returns
    -------
    file_info : ``FileInfo``
    """
    # Pull from cache
    file_info = FILE_INFO_CACHE.get(file_name, None)
    
    if (file_info is None):
        # Try create
        try:
            stats = get_stats(file_name)
        except OSError:
            file_info = None
        else:
            try:
                with open(file_name, 'r') as file:
                    lines = file.read().splitlines()
            except OSError:
                file_info = None
            else:
                file_info = FileInfo(file_name, stats.st_size, stats.st_mtime, lines, True, False)
    
    # Could not create full instance, create dummy.
    if file_info is None:
        file_info = FileInfo(file_name, 0, 0.0, [], False, False)
    
    # Put file to temporary cache
    FILE_INFO_CACHE[file_name] = file_info
    for line_cache_context in LINE_CACHE_SESSIONS:
        line_cache_context.memorized_file_infos.add(file_info)
    
    return file_info

