__all__ = ('ZipStreamFile',)

from datetime import datetime as DateTime, timezone as TimeZone

from ...utils import RichAttributeErrorBaseType

from .compression import check_compression_method_supported
from .constants import COMPRESSION_METHOD_NONE


class ZipStreamFile(RichAttributeErrorBaseType):
    """
    Represents a file to be added to a zip stream.
    
    Attributes
    ----------
    async_generator : `async-iterable`
        Asynchronous iterable to stream from.
    
    compression_method : `int`
        Compression method to use.
    
    modified_at : `DateTime`
        Whe the file was last modified.
    
    name : `str`
        The name of the file.
    """
    __slots__ = ('async_generator', 'compression_method', 'modified_at', 'name')
    
    def __new__(cls, name, async_generator, *, compression_method = COMPRESSION_METHOD_NONE, modified_at = None):
        """
        Creates a new file for zipping.
        
        The `async_generator` will be async-iterated over and its produced data will be streamed through.
        If you want the file to be reusable then passing a type implementing `__aiter__` is recommended.
        (The function is re-executed when streaming begins, allowing you to re-use it.)
        
        Parameters
        ----------
        name : `str`
            The name of the file.
        
        async_generator : `async-iterable`
            Asynchronous iterable to stream from.
        
        compression_method : `int` = `COMPRESSION_METHOD_NONE`, Optional (Keyword only)
            Compression method to use. Defaults to no compression.
        
        modified_at : `None | DateTime` = `None`, Optional (Keyword only)
            Whe the file was last modified.
        
        Raises
        ------
        RuntimeError
            - If the given compression method is not supported.
        """
        check_compression_method_supported(compression_method)
        
        if modified_at is None:
            modified_at = DateTime.now(tz = TimeZone.utc)
        
        self = object.__new__(cls)
        self.async_generator = async_generator
        self.compression_method = compression_method
        self.modified_at = modified_at
        self.name = name
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return f'<{type(self).__name__} name = {self.name!r}>'
