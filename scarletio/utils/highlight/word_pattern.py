__all__ = ()


class WordNode:
    """
    A words' character node when building regex.
    
    Attributes
    ----------
    character : `str`
        The represented character by the node.
    is_final : `bool`
        Whether the node is the end of a word.
    nodes : `dict` of (`str`, ``WordNode``) items
        Sub nodes branching out.
    parent : `None`, ``WordNode``
        The parent node.
    """
    __slots__ = ('character', 'is_final', 'nodes', 'parent')
    
    def __new__(cls, character, is_final, parent):
        """
        Creates a new ``WordNode`` with the given `character`.
        
        Parameters
        ----------
        character : `str`
            The character of the node.
        is_final : `bool`
            Whether the node is the end of a word.
        """
        self = object.__new__(cls)
        self.character = character
        self.nodes = None
        self.is_final = is_final
        self.parent = parent
        return self
    
    
    def __repr__(self):
        """Returns the word node's representation."""
        result = ['<', self.__class__.__name__, ' of ', repr(self.character)]
        if self.is_final:
            result.append(' (final)')
        
        nodes = self.nodes
        if (nodes is not None):
            result.append(' nodes = ')
            result.append(repr(nodes))
        
        result.append('>')
        
        return ''.join(result)
    
    
    def add_node(self, characters, character_index):
        """
        Adds a sub-node to the node.
        
        Attributes
        ----------
        characters : `list` of `str`
            A list of characters to add as nodes.
        character_index : `int`
            The character's index to use from `characters`.
        """
        character = characters[character_index]
        character_index += 1
        if len(characters) == character_index:
            is_final = True
        else:
            is_final = False
        
        nodes = self.nodes
        if (nodes is None):
            self.nodes = nodes = {}
        
        try:
            node = nodes[character]
        except KeyError:
            node = WordNode(character, is_final, self)
            self.nodes[character] = node
        else:
            if is_final:
                node.is_final = True
        
        if (not is_final):
            node.add_node(characters, character_index)
    
    
    def _match_index(self, string, index):
        """
        Matches the pattern from the given string.
        
        Parameters
        ----------
        string : `str`
            The string to match from.
        index : `int`
            The starter index to match since. Defaults to `0`.
        
        Returns
        -------
        matched_count : `int`
            The amount of matched characters.
            
            `-1` is returned of nothing is matched.
        """
        if len(string) > index:
            character = string[index]
            
            nodes = self.nodes
            if (nodes is not None):
                try:
                    node = nodes[character]
                except KeyError:
                    pass
                else:
                    match_index = node._match_index(string, index + 1)
                    if match_index != -1:
                        return match_index + 1
        
        if self.is_final:
            return 1
        
        return -1
    
    def match(self, string, index = 0):
        """
        Matches pattern from the given string.
        
        Parameters
        ----------
        string : `str`
            The string to match from.
        index : `int` = `0`, Optional
            The starter index to match since. Defaults to `0`.
        
        Returns
        -------
        matched : `None`, `str`
            The matched string, if any.
        """
        if len(string) > index:
            character = string[index]
            
            nodes = self.nodes
            if (nodes is not None):
                try:
                    node = nodes[character]
                except KeyError:
                    pass
                else:
                    match_index = node._match_index(string, index + 1)
                    if match_index != -1:
                        return string[index : index + match_index]
        
        if self.is_final:
            return ''
        
        return None


def create_word_pattern(words):
    """
    Creates 1 regex pattern from many words.
    
    Parameters
    ----------
    words : `iterable` of `str`
        The words to create regex pattern from.
    
    Returns
    -------
    regex_pattern : ``WordNode``
        The generated pattern.
    """
    word_node = WordNode('', False, None)
    for word in words:
        if word:
            word_node.add_node(list(word), 0)
        else:
            word_node.is_final = True
    
    return word_node
