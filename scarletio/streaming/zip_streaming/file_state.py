__all__ = ()

from ...utils import RichAttributeErrorBaseType

from .constants import FLAG_DATA_DESCRIPTOR, FLAG_UTF8


class ZipStreamFileState(RichAttributeErrorBaseType):
    """
    Represents a file's state that stores and tracks additional information about a file while it is streamed.
    
    Attributes
    ----------
    crc : `int`
        Value used for cyclic redundancy check. Each data chunk is calculated into it, so its value is only known
        after all data of the file was iterated through.
    
    flags : `int`
        Bitwise flags describing additional information.
    
    modification_date : `int`
        Modification (year, month, minute) to be serialized.
    
    modification_time : `int`
        Modification (hour, minute, second) to be serialized.
    
    name_binary : `bytes`
        The name of the file in binary.
    
    offset : `int`
        Offset of the file from the start. Set just before serialization of the file begins..
    
    size_compressed : `int`
        The compressed size of the file. It's incremented as data is passed through the compressor.
    
    size_uncompressed : `int`
        The un-compressed size of the file. It's incremented as data is passed through the compressor.
    """
    __slots__ = (
        'crc', 'flags', 'modification_date', 'modification_time', 'name_binary', 'offset', 'size_compressed',
        'size_uncompressed'
    )
    
    def __new__(cls, file, name_deduplicator):
        """
        Creates a new file state.
        
        Parameters
        ----------
        file : ``ZipStreamFile``
            The file to represent.
        
        name_deduplicator : `None | GeneratorType`
            Name deduplicator to use.
        """
        # Precalculate modification date & time
        modified_at = file.modified_at
        modification_date = (((modified_at.year - 1980) << 9) | (modified_at.month << 5) | modified_at.day) & 0xffff
        modification_time = ((modified_at.hour << 11) | (modified_at.minute << 5) | (modified_at.second >> 1)) & 0xffff
        
        # precalculate binary name
        name = file.name
        if (name_deduplicator is not None):
            name = name_deduplicator.send(name)
        
        name_binary = name.encode('utf8')
        
        # precalculate name
        flags = FLAG_DATA_DESCRIPTOR
        if len(name) != len(name_binary):
            flags |= FLAG_UTF8
        
        # Construct
        self = object.__new__(cls)
        self.crc = 0
        self.flags = flags
        self.modification_date = modification_date
        self.modification_time = modification_time
        self.name_binary = name_binary
        self.offset = 0
        self.size_compressed = 0
        self.size_uncompressed = 0
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return f'<{type(self).__name__} name = {self.name_binary!r}>'
