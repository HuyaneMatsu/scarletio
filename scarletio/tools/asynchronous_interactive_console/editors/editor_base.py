__all__ = ()

from ....utils import RichAttributeErrorBaseType


def _validate_buffer(buffer):
    """
    Parameters
    ----------
    buffer : `None`, `list` of `str`
        A precreated buffer which commands the initial lines of the input to write.
    
    Returns
    -------
    buffer : `list` of `str`
    
    Raises
    ------
    TypeError
        - If `buffer`'s type is incorrect.
    """
    if (buffer is not None) and (not isinstance(buffer, list)):
        raise TypeError(
            f'buffer can be `None`, `list`, got {buffer.__class__.__name__}; {buffer!r}.'
    )
    
    if buffer is None:
        buffer = []
    
    return buffer


class EditorBase(RichAttributeErrorBaseType):
    """
    Base editor implementation.
    
    Attributes
    ----------
    auto_completer : ``AutoCompleter``
        Auto completer to use.
    compiled_code : `None`, ``CodeType``
        The compiled inputted code.
    file_name : `str`
        File name of the code produced by the editor.
    prefix_initial : `str`
        First line's prefix.
    prefix_continuous : `str`
        Non-first line's prefix.
    prefix_length : `int`
        As how long should the prefix's length be interpreted.
    """
    __slots__ = (
        'auto_completer', 'compiled_code', 'file_name', 'prefix_initial', 'prefix_continuous', 'prefix_length'
    )
    
    def __new__(
        cls, buffer, file_name, prefix_initial, prefix_continuous, prefix_length, highlighter, history, auto_completer
    ):
        """
        Creates a new editor. Initialises with given buffer.
        
        Parameters
        ----------
        buffer : `None`, `list` of `str`
            A precreated buffer which commands the initial lines of the input to write.
        file_name : `str`
            File name of the code produced by the editor.
        prefix_initial : `str`
            First line's prefix.
        prefix_continuous : `str`
            Non-first line's prefix.
        prefix_length : `int`
            As how long should the prefix's length be interpreted.
        highlighter : `None`, ``HighlightFormatterContext``
            Formatter storing highlighting details.
        history : ``History``
            History used for caching inputs.
        auto_completer : ``AutoCompleter``
            Auto completer to use.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        """
        self = object.__new__(cls)
        self.auto_completer = auto_completer
        self.compiled_code = None
        self.file_name = file_name
        self.prefix_initial = prefix_initial
        self.prefix_continuous = prefix_continuous
        self.prefix_length = prefix_length
        return self
    
    
    def __repr__(self):
        """Returns the editor's representation."""
        return f'<{self.__class__.__name__}>'
    
    
    def __call__(self):
        """
        Executes the editor's loop.
        
        Returns
        -------
        compiled_code : `None`, ``CodeType``
            the compiled code.
        
        Raises
        ------
        KeyboardInterrupt
        SystemExit
        SyntaxError
        """
        return self.compiled_code
    
    
    def get_buffer(self):
        """
        Returns the editor's buffer.
        
        Returns
        -------
        buffer : `list` of `str`
        """
        return []
    
    
    def is_empty(self):
        """
        Returns whether the editor is empty.
        
        Returns
        -------
        is_empty : `bool`
        """
        for line in self.get_buffer():
            for character in line:
                if character not in {'\n', ' ', '\t', '\r'}:
                    return False
        
        return True
    
    
    def get_stripped_buffer(self):
        """
        Returns the stripped content of the editor.
        
        Returns
        -------
        buffer : `list` of `str`
        """
        lines = [line.rstrip() for line in self.get_buffer()]
        
        while lines and (not lines[0]):
            del lines[0]
        
        while lines and (not lines[-1]):
            del lines [-1]
        
        return lines
    
    
    @classmethod
    def has_history_support(cls):
        """
        Returns whether the editor supports history lookups.
        
        If it does not, it's input should not be saved.
        
        Returns
        -------
        has_history_support : `bool`
        """
        return False
