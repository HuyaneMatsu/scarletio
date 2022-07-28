__all__ = ('iter_highlight_code_lines',)

from .parser_context import HighlightParserContext


def iter_highlight_code_lines(lines, formatter_context):
    """
    Matches the given python code lines and iterates it's formatted representation.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    lines : `list` of `str`
        Lines to format.
    formatter_context : ``HighlightFormatterContext``
        Context to use for highlighting.
    
    Yields
    ------
    content : `str`
    """
    context = HighlightParserContext(lines)
    context.match()
    yield from context.generate_highlighted(formatter_context)
