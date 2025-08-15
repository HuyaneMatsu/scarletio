__all__ = ('get_highlight_streamer',)

from ..async_utils import to_coroutine


def get_highlight_streamer(highlighter):
    """
    Gets a highlighter streamer for the given highlight formatter context.
    
    Examples
    --------
    ```py
    into = []
    
    # Create highlight streamer. Highlighter can also be given as `None`.
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    
    # On each `.asend(...)` the stream will produce one or more tokens that can be captured with a `list.extend` call
    into.extend(highlight_streamer.asend((HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_VARIABLE, 'value')))
    
    # After highlighting is done, use `.asend(None)` to end the stream. This will flush the tail of the stream.
    into.extend(highlight_streamer.asend(None))
    ```
    
    Parameters
    ----------
    highlighter : ``None | HighlightFormatterContext``
        Highlighter to use.
    
    Returns
    -------
    streamer : `CoroutineGeneratorType`
    """
    if highlighter is None:
        streamer = _highlight_streamer_none()
    
    else:
        streamer = _highlight_streamer(highlighter)
    
    # Begin the stream.
    for value in streamer.asend(None):
        pass
    
    return streamer


@to_coroutine
def _yield_back(value):
    """
    Yields back the given value.
    
    Parameters
    ----------
    value : `str`
        Value to yield back.
    
    Yields
    ------
    part : `str`
    """
    yield value


@to_coroutine
def _yield_from(values):
    """
    Yields the given values.
    
    Parameters
    ----------
    values : `GeneratorType`
        Values to yield back.
    
    Yields
    ------
    part : `str`
    """
    yield from values


@to_coroutine
def _highlight_step(highlighter, previous_detail, token_type, content):
    """
    A highlight step used to chain one highlight detail into another.
    
    This function is an awaitable generator.
    
    Parameters
    ----------
    highlighter : ``None | HighlightFormatterContext``
        Highlighter to use.
    
    previous_detail : `None | FormatterDetailBase`
        The detail of the previous content.
    
    token_type : `int`
        Token type to highlight the current content with.
    
    content : `str`
        Content to highlight.
    
    Yields
    ------
    part : `str`
    
    Returns
    -------
    current_detail : `None | FormatterDetailBase`
    """
    current_detail = highlighter.formatter_nodes[token_type].detail
    
    if previous_detail is None:
        if current_detail is None:
            yield content
        else:
            yield from current_detail.start()
            yield from current_detail.transform_content(content)
    else:
        if current_detail is None:
            yield from previous_detail.end()
            yield content
        else:
            if type(previous_detail) is type(current_detail):
                yield from previous_detail.transition(current_detail)
                yield from current_detail.transform_content(content)
            else:
                yield from previous_detail.end()
                yield from current_detail.start()
                yield from current_detail.transform_content(content)
    
    return current_detail


async def _highlight_streamer_none():
    """
    Highlight streamer without highlighter.
    
    This function is a coroutine generator.
    
    Accepts
    -------
    token_type_and_content : `(int, str)`
    
    Async Yields
    ------------
    N / A
    
    Yields
    ------
    part : `str`
    """
    while True:
        item = yield
        if item is None:
            break
        
        await _yield_back(item[1])
    
    # Use empty yield to avoid StopAsyncIteration
    yield


async def _highlight_streamer(highlighter):
    """
    Highlight streamer with highlighter.
    
    This function is a coroutine generator.
    
    Parameters
    ----------
    highlighter : ``None | HighlightFormatterContext``
        Highlighter to use.
    
    Accepts
    -------
    token_type_and_content : `(int, str)`
    
    Async Yields
    ------------
    N / A
    
    Yields
    ------
    part : `str`
    """
    previous_detail = None
    
    while True:
        item = yield
        if item is None:
            break
        
        previous_detail = await _highlight_step(highlighter, previous_detail, *item)
    
    if (previous_detail is not None):
        await _yield_from(previous_detail.end())
    
    # Use empty yield to avoid StopAsyncIteration
    yield
