__all__ = ('get_highlight_streamer',)

from ..async_utils import to_coroutine


def get_highlight_streamer(highlighter):
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
    yield value


@to_coroutine
def _yield_from(values):
    yield from values


@to_coroutine
def _highlight_step(highlighter, previous_detail, token_type, content):
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
    while True:
        item = yield
        if item is None:
            break
        
        await _yield_back(item[1])
    
    # Use empty yield to avoid StopAsyncIteration
    yield


async def _highlight_streamer(highlighter):
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
