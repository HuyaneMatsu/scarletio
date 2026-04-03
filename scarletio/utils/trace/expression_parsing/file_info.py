__all__ = ('FileInfo',)

from os import stat as get_stats

from ...highlight import (
    ParseResult, get_highlight_parse_result, search_line_end_index_in_tokens, search_line_start_index_in_tokens
)

from .cache_constants import CONSOLE_INPUT_CACHE, FILE_INFO_CACHE, LINE_CACHE_SESSIONS


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
    
    content : `str`
        The file's content.
    
    file_size : `int`
        The file's size. Used to identify file modifications.
    
    parse_result : ``ParseResult``
        The result of parsing the file.
    """
    __slots__ = (
        '__weakref__', 'alive', 'console', 'content', 'file_modification_time', 'file_name', 'file_size', 'parse_result'
    )
    
    def __new__(cls, file_name, file_size, file_modification_time, content, parse_result, alive, console):
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
        
        content : `str`
            The file's content.
        
        parse_result : ``ParseResult``
            The result of parsing the file.
        
        alive : `bool`
            Whether the file's source is alive.
        
        console : `bool`
            Whether the file's source is from console.
        """
        self = object.__new__(cls)
        self.alive = alive
        self.console = console
        self.content = content
        self.file_modification_time = file_modification_time
        self.file_name = file_name
        self.file_size = file_size
        self.parse_result = parse_result
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(', alive = ')
        repr_parts.append(repr(self.alive))
        
        repr_parts.append(', console = ')
        repr_parts.append(repr(self.console))
        
        repr_parts.append(' file_modification_time = ')
        repr_parts.append(repr(self.file_modification_time))
        
        repr_parts.append(', file_name = ')
        repr_parts.append(repr(self.file_name))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def is_up_to_date(self):
        """
        Returns whether the file info is up to date.
        
        Returns
        -------
        is_up_to_date : `bool`
        """
        if self.console:
            try:
                CONSOLE_INPUT_CACHE.move_to_end(self.file_name)
            except KeyError:
                CONSOLE_INPUT_CACHE[self.file_name] = self
            return True
        
        if not self.alive:
            return True
        
        try:
            stats = get_stats(self.file_name)
        except OSError:
            pass
        else:
            if self.file_size != stats.st_size:
                return False
            
            if self.file_modification_time != stats.st_mtime:
                return False
            
            return True
        
        return False
    
    
    def get_line(self, line_index):
        """
        Gets the line of the file.
        
        Parameters
        ----------
        line_index : `int`
            The line's index.
        
        Returns
        -------
        hit : `bool`
        line : `str`
        """
        tokens = self.parse_result.tokens
        if not tokens:
            return False, ''
        
        line_start_index = search_line_start_index_in_tokens(tokens, line_index)
        line_end_index = search_line_end_index_in_tokens(tokens, line_index)
        if line_start_index == line_end_index:
            return False, ''
        
        start_index = tokens[line_start_index].content_character_index
        content = self.content
        
        if line_end_index == len(tokens):
            end_index = len(content)
        else:
            end_index = tokens[line_end_index].content_character_index
        
        return True, content[start_index : end_index]
    
    
    def get_token_index_range_for_line_index(self, line_index):
        """
        Gets the token index range for the given line index.
        
        Returns
        -------
        line_range : `(int, int)`
        """
        tokens = self.parse_result.tokens
        if not tokens:
            return 0, 0
        
        return (
            search_line_start_index_in_tokens(tokens, line_index),
            search_line_end_index_in_tokens(tokens, line_index),
        )


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
    while True:
        # Pull from cache
        try:
            file_info = FILE_INFO_CACHE[file_name]
        except KeyError:
            pass
        else:
            break
        
        # Try create
        try:
            stats = get_stats(file_name)
        except OSError:
            pass
        else:
            try:
                with open(file_name, 'r', encoding = 'utf-8', errors = 'replace') as file:
                    content = file.read()
            except OSError:
                pass
            else:
                parse_result = get_highlight_parse_result(content)
                
                file_info = FileInfo(file_name, stats.st_size, stats.st_mtime, content, parse_result, True, False)
                break
            
        # Could not create full instance, create dummy.
        file_info = FileInfo(file_name, 0, 0.0, '', ParseResult([], []), False, False)
        break
    
    # Put file to temporary cache
    FILE_INFO_CACHE[file_name] = file_info
    for line_cache_context in LINE_CACHE_SESSIONS:
        line_cache_context.memorized_file_infos.add(file_info)
    
    return file_info
