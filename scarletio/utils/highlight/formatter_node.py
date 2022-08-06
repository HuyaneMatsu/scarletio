__all__ = ()


class FormatterNode:
    """
    Represents a formatter node for a specified token type.
    
    Attributes
    ----------
    id : `int`
        The node's identifier.
    detail : `None`, ``FormatterDetail``
        Details of the node for formatting.
    is_class_direct : `bool`
        Whether ``.type`` is set directly or is inherited.
    nodes : `None`, `dict` of (`int`, ``FormatterNode``) items
        Sub-nodes branching out from the source one.
    parent : `None`, ``FormatterNode``
        The parent node.
    """
    __slots__ = ('detail', 'id', 'is_class_direct', 'nodes', 'parent')
    
    def __new__(cls, formatter, id_):
        """
        Creates a new ``TokenClassNode`` with the given identifier.
        
        Parameters
        ----------
        formatter : ``HighlightFormatterContext``
            The owner formatter.
        id_ : `int`
            The identifier of the token.
        """
        self = object.__new__(cls)
        self.id = id_
        self.detail = None
        self.is_class_direct = False
        self.nodes = None
        self.parent = None
        
        formatter.formatter_nodes[id_] = self
        
        return self
    
    
    def __repr__(self):
        """Returns the token type node's representation."""
        result = ['<', self.__class__.__name__, ' id=', repr(self.id)]
        
        if self.is_class_direct:
            result.append(', detail=')
            result.append(repr(self.detail))
        
        nodes = self.nodes
        if (nodes is not None):
            result.append(', nodes=')
            result.append(repr(nodes))
        
        result.append('>')
        
        return ''.join(result)
    
    
    def add_node(self, node):
        """
        Adds a sub node.
        
        Parameters
        ----------
        node : ``FormatterNode``
        """
        node.parent = self
        
        nodes = self.nodes
        if nodes is None:
            self.nodes = nodes = {}
        
        nodes[node.id] = node
    
    
    def _set_detail(self, detail):
        """
        Sets the node's html class. This is an internal method called by ``.set_detail`` or by itself recursively
        to actually modify the attributes.
        
        This method shall be called only from a parent node.
        
        Parameters
        ----------
        detail : `None`, ``FormatterDetail``
            Details for formatting, set or `None` to remove.
        """
        self.detail = detail
        
        nodes = self.nodes
        if (nodes is not None):
            for node in nodes.values():
                if not node.is_class_direct:
                    node._set_detail(detail)
    
    
    def set_detail(self, detail):
        """
        Sets html class to the node.
        
        Parameters
        ----------
        detail : `None`, ``FormatterDetail``
            Details for formatting, set or `None` to remove.
        """
        if detail is None:
            if self.is_class_direct:
                self.is_class_direct = False
                parent = self.parent
                if (parent is not None):
                    detail = parent.detail
                    # Only continue if the html classes are different
                    if self.detail != detail:
                        self._set_detail(detail)
        
        else:
            self.is_class_direct = True
            self._set_detail(detail)
