__all__ = ()

from ....utils import RichAttributeErrorBaseType


class LineRenderIntermediate(RichAttributeErrorBaseType):
    """
    Represents intermediate information about how a line is rendered.
    
    Attributes
    ----------
    parts : `list<(int, str)>`
        The parts the line consists of.
    """
    __slots__ = ('parts',)
    
    def __new__(cls, prefix_length, prefix):
        """
        Creates a new line render instance.
        
        Parameters
        ----------
        prefix_length : `int`
            The length of the prefix.
        prefix : `str`
            The prefix.
            Prefixes might contain commands in them, so their length and value is separated.
        """
        self = object.__new__(cls)
        self.parts = [(prefix_length, prefix)]
        return self
    
    
    def add_command(self, command):
        """
        Adds a command to the line render.
        The visual representation of these lines equal to `0`.
        
        Parameters
        ----------
        command : `str`
            The command to add.
        """
        self.parts.append((0, command))
    
    
    def add_part(self, part):
        """
        Adds a part to the line render.
        The visual representation of these lines equal to their length.
        
        Parameters
        ----------
        part : `str`
            The part to add.
        """
        self.parts.append((len(part), part))
    
    
    def __eq__(self, other):
        """Returns whether the two renders are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.parts == other.parts
    
    
    def __repr__(self):
        """Returns the line render's representation."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' parts = ')
        repr_parts.append(repr(self.parts))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def iter_parts(self):
        """
        Iterates over the added parts. This also includes commands too.
        
        This method is an iterable generator.
        
        Yields
        ------
        part : `str`
        """
        for element in self.parts:
            yield element[1]
    
    
    def iter_items(self):
        """
        Iterates over the added items. This includes whether a part is a command and the part itself.
        
        This method is an iterable generator.
        
        Yields
        ------
        length, part : (int, str)
        """
        yield from self.parts
    
    
    def get_length(self):
        """
        Returns the length of the line. This does not equal to its part count.
        
        Returns
        -------
        length : `int`
        """
        return sum(part[0] for part in self.parts)
