__all__ = ('FrameProxyBase',)


from ..expression_parsing import ExpressionKey


class FrameProxyBase:
    """
    Base class for frame proxies.
    
    Frame proxies are used to provide the same api for different types of frame representations.
    
    Attributes
    ----------
    expression_info : `None | ExpressionInfo`
        Additional expression information.
    """
    __slots__ = ('expression_info',)
    
    def __new__(cls):
        """
        Creates a new frame proxy.
        """
        self = object.__new__(cls)
        self.expression_info = None
        return self
    
    
    def __repr__(self):
        """Returns the frame proxy's representation."""
        return ''.join(['<', type(self).__name__, '>'])
    
    
    @property
    def builtins(self):
        """
        Returns the frame's builtins. Can return `None` if the variables were already omitted.
        
        Returns
        -------
        builtins : `None | dict<str, object>`
        """
        return None
    
    
    @property
    def globals(self):
        """
        Returns the frame's globals. Can return `None` if the variables were already omitted.
        
        Returns
        -------
        globals : `None | dict<str, object>`
        """
        return None
    
    
    @property
    def locals(self):
        """
        Returns the local variables of the frame. Can return `None` if the variables were already omitted.
        
        Returns
        -------
        locals : `None | dict<str, object>`
        """
        return None
    
    
    @property
    def code(self):
        """
        Returns the frame's code.
        
        Returns
        -------
        code : `None | CodeType`
        """
        return None
    
    
    @property
    def instruction_index(self):
        """
        Returns the frame's last attempted instruction index in the bytecode.
        
        Returns
        -------
        last_instruction_index : `int`
        """
        return 0
    
    
    @property
    def line_index(self):
        """
        Returns the frame's current line index in Python source code.
        
        Returns
        -------
        line_index : `int`
        """
        return 0
    
    
    @property
    def tracing_function(self):
        """
        Tracing function for the traceback's frame. Defaults to `None`.
        
        Returns
        -------
        tracing_function : `None | FunctionType`
        """
        return None
    
    
    @property
    def file_name(self):
        """
        Returns the frame's file name. Can be empty string.
        
        Returns
        -------
        file_name : `str`
        """
        code = self.code
        if code is None:
            file_name = ''
        else:
            file_name = code.co_filename
            if (file_name is None):
                file_name = ''
        
        return file_name
    
    
    @property
    def name(self):
        """
        Returns the frame's function's name. Can be empty string.
        
        Returns
        -------
        name : `str`
        """
        code = self.code
        if code is None:
            name = ''
        else:
            name = code.co_name
            if name is None:
                name = ''
        
        return name
    
    
    def __eq__(self, other):
        """Returns whether the two frame proxies are equal."""
        if not isinstance(other, FrameProxyBase):
            return NotImplemented
        
        return self._is_equal(other)
        
    
    def _is_equal(self, other):
        """
        Returns whether the two frame proxies are equal.
        
        Parameters
        ----------
        other : ``FrameProxyBase``
            The other instance.
        
        Returns
        -------
        is_equal : `bool`
        """
        if not self._is_alike(other):
            return False
        
        if self.builtins != other.builtins:
            return False
        
        if self.globals != other.globals:
            return False
        
        if self.locals != other.locals:
            return False
        
        if self.tracing_function != other.tracing_function:
            return False
        
        return True
    
    
    def __mod__(self, other):
        """Returns whether the two frame proxies are alike."""
        if not isinstance(other, FrameProxyBase):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def __rmod__(self, other):
        """Returns whether the two frame proxies are alike."""
        if not isinstance(other, FrameProxyBase):
            return NotImplemented
        
        return self._is_alike(other)
    
    
    def _is_alike(self, other):
        """
        Returns whether the two frame proxies are alike.
        
        Parameters
        ----------
        other : ``FrameProxyBase``
            The other instance.
        
        Returns
        -------
        is_alike : `bool`
        """
        if self.file_name != other.file_name:
            return False
        
        if self.line_index != other.line_index:
            return False
        
        if self.name != other.name:
            return False
        
        if self.instruction_index != other.instruction_index:
            return False
        
        return True
    
    
    @property
    def expression_key(self):
        """
        Returns the expression key for the frame.
        
        Returns
        -------
        expression_key : ``ExpressionKey``
        """
        return ExpressionKey(self.file_name, self.line_index, self.name, self.instruction_index)

    
    def has_variables(self):
        """
        Returns whether the frame proxy inherited variables on creation.
        
        Returns
        -------
        has_variables : `bool`
        """
        return False
    
    
    @property
    def line(self):
        """
        Returns the frame's line. Can be empty string. Also can contain line breaks.
        
        Returns
        -------
        line : `str`
        """
        expression_info = self.expression_info
        if expression_info is None:
            line = ''
        else:
            line = expression_info.line
        
        return line
    
    
    @property
    def lines(self):
        """
        Returns the frame's lines. Can be empty list.
        
        Returns
        -------
        lines : `list<str>`
        """
        expression_info = self.expression_info
        if expression_info is None:
            lines = []
        else:
            lines = expression_info.lines
        
        return lines
    
    
    @property
    def mention_count(self):
        """
        Returns how much times the frame is mentioned. Can be `0`.
        
        Returns
        -------
        mention_count : `int`
        """
        expression_info = self.expression_info
        if expression_info is None:
            mention_count = 0
        else:
            mention_count = expression_info.mention_count
        
        return mention_count
