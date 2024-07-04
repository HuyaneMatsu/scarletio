__all__ = ()

from re import compile as re_compile


class PrefixTrimmer:
    """
    Prefix trimmer used to identify and remove prefixes.
    
    Attributes
    ----------
    excludes : `None`, `frozenset` of `str`
        Strings to exclude from matching.
    prefix_continuous_pattern : `re.Pattern`
        Prefix pattern matching continuous lines.
    prefix_initial_pattern : `re.Pattern`
        Prefix pattern matching only the initial line.
    prefix_last_pattern : `str`
        Prefix pattern matching the last line only if ``.prefix_continuous_pattern`` fails.
    """
    __slots__ = ('excludes', 'prefix_continuous_pattern', 'prefix_initial_pattern', 'prefix_last_pattern')
    
    def __new__(cls, prefix_initial_pattern, prefix_continuous_pattern, prefix_last_pattern, excludes ):
        """
        Creates a new prefix trimmer.
        
        Parameters
        ----------
        prefix_initial_pattern : `str`
            Prefix pattern matching only the initial line.
            
            > Not compiled.
        
        prefix_continuous_pattern : `str`
            Prefix pattern matching continuous lines.
            
            > Not compiled.
        
        prefix_last_pattern : `str`
            Prefix pattern matching the last line only if ``.prefix_continuous_pattern`` fails.
            
            > Not compiled.
        
        excludes  : `None`, `list` of `str`
            Strings to exclude from matching.
        """
        prefix_continuous_pattern = re_compile(prefix_continuous_pattern)
        prefix_initial_pattern = re_compile(prefix_initial_pattern)
        prefix_last_pattern = re_compile(prefix_last_pattern)
        
        if (excludes is not None):
            excludes = frozenset(excludes)
            if not excludes:
                excludes  = None
        
        self = object.__new__(cls)
        self.excludes  = excludes 
        self.prefix_continuous_pattern = prefix_continuous_pattern
        self.prefix_initial_pattern = prefix_initial_pattern
        self.prefix_last_pattern = prefix_last_pattern
        return self
    
    
    def checkout(self, lines):
        """
        Checks out the given lines for prefix.
        
        Parameters
        ----------
        lines : `list` of `str`
            The input lines to check out.
        
        Returns
        -------
        matched : `bool`
            Whether the given lines have the specified prefix.
        """
        line_count = len(lines)
        if line_count == 0:
            return False
        
        if line_count == 1:
            return self._checkout_one(lines)
        
        return self._checkout_more(lines)
    
    
    def _checkout_one(self, lines):
        """
        Checks out the given lines for prefix.
        
        This method is called by ``.checkout`` if `len(lines) == 1`
        
        Parameters
        ----------
        lines : `list` of `str`
            The input lines to check out.
        
        Returns
        -------
        matched : `bool`
            Whether the given lines have the specified prefix.
        """
        line = lines[0]
        
        for pattern in (self.prefix_initial_pattern, self.prefix_continuous_pattern):
            if pattern.match(line) is not None:
                return True
        
        if self.prefix_last_pattern.fullmatch(line) is not None:
            return True
        
        return False
    
    
    def _checkout_more(self, lines):
        """
        Checks out the given lines for prefix.
        
        This method is called by ``.checkout`` if `len(lines) > 1`
        
        Parameters
        ----------
        lines : `list` of `str`
            The input lines to check out.
        
        Returns
        -------
        matched : `bool`
            Whether the given lines have the specified prefix.
        """
        prefix_continuous_pattern = self.prefix_continuous_pattern
        
        index = 1
        length = len(lines)
        
        while index < length:
            line = lines[index]
            index += 1
            
            if prefix_continuous_pattern.match(line) is not None:
                continue
            
            if index < length:
                return False
            
            if self.prefix_last_pattern.fullmatch(line) is None:
                return False
            
            break
        
        return True
    
    
    def check_is_excluded(self, string):
        """
        Checks whether the given string is excluded from the trimmer.
        
        Parameters
        ----------
        string : `str`
            The string to check.
        
        Returns
        -------
        is_excluded : `bool`
        """
        excludes = self.excludes
        if (excludes is not None):
            if string in excludes:
                return True
        
        return False
    
    
    def apply(self, lines):
        """
        Applies the trimming to the given lines.
        
        Parameters
        ----------
        lines : `list` of `str`
            The lines to trim.
        
        Returns
        -------
        new_lines : `list` of `str`
            The new lines.
        """
        new_lines = [*self._iter_apply(lines)]
        
        for line in new_lines:
            if line:
                all_empty = False
                break
        else:
            all_empty = True
        
        if all_empty:
            new_lines.clear()
        
        return new_lines
    
    
    def _iter_apply(self, lines):
        """
        Applies trimming on the given lines.
        
        Called by ``.apply`` to generate the new lines.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        lines : `list` of `str`
            The lines to trim.
        
        Yields
        ------
        line : `str`
        """
        if lines:
            yield from self._iter_apply_line_first(lines)
            yield from self._iter_apply_line_rest(lines)
    
    
    def _iter_apply_line_first(self, lines):
        """
        Applies first line trimming on the first line of the given lines.
        
        Called by ``._iter_apply`` if `len(lines) > 0`.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        lines : `list` of `str`
            The lines to trim.
        
        Yields
        ------
        line : `str`
        """
        line = lines[0]
        
        for pattern in (self.prefix_initial_pattern, self.prefix_continuous_pattern):
            matched = pattern.match(line)
            if (matched is not None):
                line = line[matched.end():]
                break
        
        else:
            if (len(lines) == 1) and (self.prefix_last_pattern.fullmatch(line) is not None):
                line = ''
        
        
        yield line
    
    
    def _iter_apply_line_rest(self, lines):
        """
        Applies continuous line trimming on all non-first lines.
        
        Called by ``._iter_apply`` if `len(lines) > 0`.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        lines : `list` of `str`
            The lines to trim.
        
        Yields
        ------
        line : `str`
        """
        prefix_continuous_pattern = self.prefix_continuous_pattern
        
        index = 1
        length = len(lines)
        
        while index < length:
            line = lines[index]
            index += 1
            
            matched = prefix_continuous_pattern.match(line)
            if (matched is not None):
                line = line[matched.end():]
            
            elif (index >= length) and (self.prefix_last_pattern.fullmatch(line) is not None):
                line = ''
            
            yield line


PREFIX_TRIMMERS = (
    PrefixTrimmer('In \\[\\d+\\]\\: ', ' +\\.\\.\\.\\: ', ' +\\.\\.\\.\\: ?', None), # scarletio
    PrefixTrimmer('\\>\\>\\> ', '\\.\\.\\. ', '\\.\\.\\. ?', ['...']), # cpython
    PrefixTrimmer('\\>\\>\\>\\> ', '\\.\\.\\.\\. ', '\\.\\.\\.\\. ?', None), # pypy
)


def trim_console_prefix(content):
    """
    Parameters
    ----------
    content : `str`
        The source content.
    
    Returns
    -------
    trimmed_content : `None`, `str`
        Returns `None` if nothing was trimmed.
    """
    prefix_trimmers = [
        prefix_trimmer for prefix_trimmer in PREFIX_TRIMMERS if not prefix_trimmer.check_is_excluded(content)
    ]
    
    lines = content.splitlines()
    
    for prefix_trimmer in prefix_trimmers:
        if prefix_trimmer.checkout(lines):
            lines = prefix_trimmer.apply(lines)
            break
    
    else:
        return None
    
    return '\n'.join(lines)
