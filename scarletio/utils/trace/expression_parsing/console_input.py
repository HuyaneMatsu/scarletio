__all__ = ('add_console_input',)

from .cache_constants import (
    CONSOLE_INPUT_CACHE, CONSOLE_INPUT_MAX_SIZE, CONSOLE_INPUT_CACHE_OUTFLOW_CHECK, FILE_INFO_CACHE
)
from .file_info import FileInfo


def add_console_input(file_name, content):
    """
    Adds a console input. Ignores empty input.
    
    Parameters
    ----------
    file_name : `None | str`
        File name to add the input as.
    content : `None | str`
        Input content to add.
    """
    if (file_name is None) or (not file_name) or (content is None) or (not content):
        return
    
    size = len(content)
    lines = content.splitlines()
    
    file_info = FileInfo(file_name, size, 0.0, lines, False, True)
    
    # Put file to permanent cache
    CONSOLE_INPUT_CACHE[file_name] = file_info
    FILE_INFO_CACHE[file_name] = file_info
    
    if len(CONSOLE_INPUT_CACHE) % CONSOLE_INPUT_CACHE_OUTFLOW_CHECK == 0:
        check_console_cache_overflow()


def check_console_cache_overflow():
    """
    Checks whether the console cache is overflown. If yes clears the overflow.
    """
    total = 0
    to_delete = None
    
    for file_info in reversed(CONSOLE_INPUT_CACHE.values()):
        total += file_info.file_size
        if total < CONSOLE_INPUT_MAX_SIZE:
            continue
        
        if to_delete is None:
            to_delete = []
        
        to_delete.append(file_info.file_name)
    
    
    if (to_delete is not None):
        for file_name in to_delete:
            del CONSOLE_INPUT_CACHE[file_name]
