__all__ = ('HighlightFormatterContext',)

from .ansi import create_ansi_format_code
from .formatter_detail import FormatterDetail, formatter_ansi_code, formatter_html
from .formatter_node import FormatterNode

from .token import Token
from .token_types import TOKEN_STRUCTURE

ANSI_RESET_CODE = create_ansi_format_code()


class HighlightFormatterContext:
    """
    Formatter context which holds details for formatting.
    
    Attributes
    ----------
    formatter_nodes : `dict` of (`int, ``FormatterNode``) items
        The registered formatter nodes.
    """
    __slots__ = ('formatter_nodes',)
    
    def __new__(cls):
        """
        Creates a new formatter context.
        """
        self = object.__new__(cls)
        self.formatter_nodes = {}
        
        self._build_type_token_nodes(TOKEN_STRUCTURE)
        
        return self
    
    
    def _build_type_token_nodes(self, dictionary):
        """
        Builds a token node type structure from the given dictionary.
        
        Parameters
        ----------
        dictionary : `dict` of (`int`, `None` or repeat) items
            A dictionary, which describes the node structure.
        """
        for key, value in dictionary.items():
            node = FormatterNode(self, key)
            if (value is not None):
                self._build_type_token_child(node, value)
    
    
    def _build_type_token_child(self, parent, dictionary):
        """
        Builds token node type structure extending the given parent.
        
        Parameters
        ----------
        parent : ``FormatterNode``
            The parent node.
        dictionary : `dict` of (`int`, `None` or repeat) items
            A dictionary, which describes the node structure.
        """
        for key, value in dictionary.items():
            node = FormatterNode(self, key)
            parent.add_node(node)
            if (value is not None):
                self._build_type_token_child(node, value)
    

    def __repr__(self):
        """Returns the formatter's representation."""
        return f'<{self.__class__.__name__} nodes: {len(self.formatter_nodes)}>'
    
    
    def highlight_as(self, content, token_type):
        """
        Highlights the given text as it would be a token of the given type.
        
        Parameters
        -----------
        content : `str`
            The content to highlight.
        token_type : `int`
            The token type to use.
        """
        detail = self.formatter_nodes[token_type].detail
        if (detail is None):
            return content
        
        else:
            return ''.join([*detail(Token(token_type, content))])
    
    
    def generate_highlighted(self, token):
        """
        Generates highlighted content from the given token.
        
        This method is an iterable generator.
        
        Parameters
        ----------
        token : ``Token``
            The token to generate it's highlighted version.
        
        Yields
        ------
        content : `str`
        """
        detail = self.formatter_nodes[token.type].detail
        if (detail is None):
            value = token.value
            if (value is not None):
                yield value
        
        else:
            yield from detail(token)
    
    
    def set_highlight_html_all(self):
        """
        Sets html formatting for all nodes of the context.
        """
        detail = FormatterDetail(formatter_html, None)
        for node in self.formatter_nodes.values():
            node.set_detail(detail, direct = False)
            
    
    def set_highlight_html_class(self, token_type_identifier, html_class):
        """
        Sets html class formatting for the given node.
        
        Parameters
        ----------
        token_type_identifier : `int`
            The node's identifier.
        html_class : `None`, `str`
            The html class to set.
        
        Raises
        ------
        TypeError
            - If `token_type_identifier` was not given as `int`.
            - If `html_class` was not given neither as `None` nor as `str`.
        ValueError
            If `token_type_identifier` was not given as any of the predefined values. Check ``TOKEN_TYPES`` for more
                details.
        """
        if (html_class is not None) and (not isinstance(html_class, str)):
            raise TypeError(
                f'`html_class` can be `None`, `str`, got {html_class.__class__.__name__}; {html_class!r}.'
            )
        
        self.set_highlight_detail(
            token_type_identifier,
            FormatterDetail(formatter_html, html_class)
        )
    
    
    def set_highlight_ansi_code(self, token_type_identifier, ansi_code):
        """
        Sets ansi formatting for the given node.
        
        Parameters
        ----------
        token_type_identifier : `int`
            The node's identifier.
        ansi_code : `None`, `str`
            The format code to set.
        
        Raises
        ------
        TypeError
            - If `token_type_identifier` was not given as `int`.
            - If `ansi_code` was not given neither as `None` nor as `str`.
        ValueError
            If `token_type_identifier` was not given as any of the predefined values. Check ``TOKEN_TYPES`` for more
                details.
        """
        if (ansi_code is not None) and (not isinstance(ansi_code, str)):
            raise TypeError(
                f'`ansi_code` can be `None`, `str`, got {ansi_code.__class__.__name__}; {ansi_code!r}.'
            )
        
        self.set_highlight_detail(
            token_type_identifier,
            FormatterDetail(formatter_ansi_code, (ansi_code, ANSI_RESET_CODE))
        )
    
    
    def set_highlight_detail(self, token_type_identifier, detail):
        """
        Sets detail for the given node.
        
        Parameters
        ----------
        token_type_identifier : `int`
            The node's identifier.
        detail : `None`, ``FormatterDetail``
            The detail to set.
        
        Raises
        ------
        TypeError
            - If `token_type_identifier` was not given as `int`.
        ValueError
            If `token_type_identifier` was not given as any of the predefined values. Check ``TOKEN_TYPES`` for more
                details.
        """
        if not isinstance(token_type_identifier, int):
            raise TypeError(
                f'`token_type_identifier` can be `int`, got '
                f'{token_type_identifier.__class__.__name__}; {token_type_identifier!r}.'
            )
        
        try:
            node = self.formatter_nodes[token_type_identifier]
        except KeyError:
            raise ValueError(
                f'`token_type_identifier` was not given as any of the predefined values, got '
                f'{token_type_identifier!r}.'
            ) from None
        
        node.set_detail(detail)
