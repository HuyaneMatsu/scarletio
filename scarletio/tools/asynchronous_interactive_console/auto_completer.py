__all__ = ()

BUILTINS = (
    'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BlockingIOError', 'BrokenPipeError',
    'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
    'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'Ellipsis',
    'EnvironmentError', 'Exception', 'False', 'FileExistsError', 'FileNotFoundError', 'FloatingPointError',
    'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning', 'IndentationError', 'IndexError',
    'InterruptedError', 'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError',
    'ModuleNotFoundError', 'NameError', 'None', 'NotADirectoryError', 'NotImplemented', 'NotImplementedError',
    'OSError', 'OverflowError', 'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError',
    'RecursionError', 'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration',
    'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TimeoutError',
    'True', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError',
    'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError',
    '__import__', 'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray', 'bytes', 'callable',
    'chr', 'classmethod', 'compile', 'complex', 'copyright', 'credits', 'delattr', 'dict', 'dir', 'divmod',
    'enumerate', 'eval', 'exec', 'exit', 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
    'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'license', 'list',
    'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
    'property', 'quit', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
    'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip'
)


class AutoCompleter:
    """
    Auto completer used in editors.
    
    Attributes
    ----------
    variables : `dict<str, object>`
        Variables to auto-complete from.
    """
    __slots__ = ('_variables',)
    
    def __new__(cls, variables):
        """
        Creates a new editor auto completer.
        
        Parameters
        ----------
        variables : `dict<str, object>`
            Variables to auto-complete from.
        """
        self = object.__new__(cls)
        self._variables = variables
        return self
    
    
    def __repr__(self):
        """Returns the auto completer's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        repr_parts.append(' variables: ')
        repr_parts.append(repr(len(self._variables)))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def get_common_prefix(self, string):
        """
        Gets the first matching option.
        
        Parameters
        ----------
        string : `str`
            The string to match.
        
        Returns
        -------
        match : `None`, `str`
        """
        matches = {*self._iter_matches(string)}
        matches_count = len(matches)
        
        if matches_count == 0:
            return None
        
        first_match = next(iter(matches))
        if matches_count == 1:
            return first_match
        
        shortest_match_length = min(len(match) for match in matches)
        
        index = len(string)
        
        while index < shortest_match_length:
            character = first_match[index]
            if not all(match[index] == character for match in matches):
                break
                
            index += 1
            continue
        
        if index == len(string):
            return None
        
        return first_match[:index]
    
    
    def _iter_matches(self, string):
        """
        Iterates over the variable names matching the given string.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        string : `str`
            The string to match.
        
        Yields
        ------
        matched_name : `str`
        """
        for variable_name in self._iter_variable_names():
            if variable_name.startswith(string) and variable_name != string:
                yield variable_name
    
    
    def _iter_variable_names(self):
        """
        Iterates over the variable names registered to the auto completer. Might yield duplicates.
        
        This method is an iterable generator.
        
        Yields
        ------
        variable_name : `str`
        """
        yield from self._variables.keys()
        yield from BUILTINS
