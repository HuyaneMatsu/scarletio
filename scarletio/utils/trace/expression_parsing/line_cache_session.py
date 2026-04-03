__all__ = ('LineCacheSession',)

from .cache_constants import LINE_CACHE_SESSIONS


class LineCacheSession:
    """
    Keeps file caches alive till the length of a session.
    
    Attributes
    ----------
    memorized_file_infos : `set<FIleInfo>`
        The memorised file infos.
    """
    __slots__ = ('memorized_file_infos',)
    
    def __new__(cls):
        """
        Creates a new line cache context.
        """
        self = object.__new__(cls)
        self.memorized_file_infos = set()
        return self
    
    
    def __repr__(self):
        """Returns the line cache context's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' memorized_file_infos = ')
        repr_parts.append(repr(self.memorized_file_infos))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __enter__(self):
        """
        Enters the context manager adding self to the active contexts.
        """
        LINE_CACHE_SESSIONS.add(self)
        return self
    
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Exists the context manager removing self from the active contexts.
        """
        LINE_CACHE_SESSIONS.remove(self)
        return False
