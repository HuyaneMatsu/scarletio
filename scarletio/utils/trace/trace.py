__all__ = ('render_exception_into', 'render_frames_into',)

from ..async_utils import to_coroutine
from ..cause_group import CauseGroup
from ..highlight import HIGHLIGHT_TOKEN_TYPES, get_highlight_streamer

from .exception_proxy import ExceptionProxyRich
from .frame_grouping import group_frames
from .frame_ignoring import should_keep_frame
from .frame_proxy import convert_frames_to_frame_proxies, populate_frame_proxies
from .rendering import produce_frame_groups, produce_exception_proxy


def render_frames_into(frames, extend = None, *, filter = None, highlighter = None):
    """
    Renders the given frames into a list of strings.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase | FrameType | TraceBack>`
        The frames to render.
    
    extend : `None`, `list<str>` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
    
    highlighter : ``None | HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Stores how the output should be highlighted.
    
    Returns
    -------
    extend : `list<str>`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    highlight_streamer = get_highlight_streamer(highlighter)
    for item in _produce_frames(frames, filter):
        extend.extend(highlight_streamer.asend(item))
        
    extend.extend(highlight_streamer.asend(None))
    
    return extend


def _produce_frames(frames, filter):
    """
    Renders the given frames into a list of strings.
    
    This function is an iterable coroutine.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase | FrameType | TraceBack>`
        The frames to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    Yields
    ------
    token_type_and_part : `(int, str)` 
    """
    frames = convert_frames_to_frame_proxies(frames)
    populate_frame_proxies(frames)
    frames = [frame for frame in frames if should_keep_frame(frame, filter = filter)]
    frame_groups = group_frames(frames)
    
    yield from produce_frame_groups(frame_groups)


REASON_TYPE_NONE = 0
REASON_TYPE_CAUSE = 1
REASON_TYPE_CONTEXT = 2
REASON_TYPE_CAUSE_GROUP = 3


def render_exception_into(exception, extend = None, *, filter = None, highlighter = None):
    """
    Renders the given exception's frames into a list of strings.
    
    Parameters
    ----------
    exception : `None | BaseException`
        The exception to render.
    
    extend : `None`, `list<str>` = `None`, Optional
        Whether the frames should be rendered into an already existing list.
    
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
    
    highlighter : ``None | HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Stores how the output should be highlighted.
    
    Returns
    -------
    extend : `list<str>`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    highlight_streamer = get_highlight_streamer(highlighter)
    
    for item in _produce_exception(exception, filter):
        extend.extend(highlight_streamer.asend(item))
    
    extend.extend(highlight_streamer.asend(None))
    
    return extend


def _produce_exception(exception, filter):
    """
    Renders the given exception's frames into a list of strings.
    
    This function is generator.
    
    Parameters
    ----------
    exception : `None | BaseException`
        The exception to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    Yields
    ------
    token_type_and_part : `(int, str)`
    """
    renderer_queue = []
    renderer_queue.append(_produce_exception_step(exception, filter))
    
    while renderer_queue:
        renderer = renderer_queue[-1]
        
        try:
            exception = yield from renderer.asend(None)
        except StopAsyncIteration:
            del renderer_queue[-1]
            continue
        
        renderer_queue.append(_produce_exception_step(exception, filter))
        continue


async def _produce_exception_step(exception, filter):
    """
    Produces the given exception's frames into a list of strings.
    When meets a nested exception to render (in a cause group), yields it back.
    
    This function is a coroutine generator.
    
    Parameters
    ----------
    exception : `None | BaseException`
        The exception to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    Async Yields
    ------------
    exception : `BaseException`
    
    Yields
    ------
    token_type_and_part : `(int, str)`
    """
    exceptions = []
    reason_type = REASON_TYPE_NONE
    while True:
        exceptions.append((exception, reason_type))
        
        cause_exception = exception.__cause__
        if (cause_exception is not None):
            exception = cause_exception
            if isinstance(exception, CauseGroup):
                reason_type = REASON_TYPE_CAUSE_GROUP
            else:
                reason_type = REASON_TYPE_CAUSE
            continue
        
        if not exception.__suppress_context__:
            context_exception = exception.__context__
            if (context_exception is not None):
                exception = context_exception
                reason_type = REASON_TYPE_CONTEXT
                continue
        
        # no other cases
        break
    
    
    for exception, reason_type in reversed(exceptions):
        if reason_type == REASON_TYPE_CAUSE_GROUP:
            await _yield_title_and_line_break(
                f'The following {len(exception)} exceptions where the reason of the exception following them:', 2,
            )
            
            for index, cause in enumerate(exception, 1):
                await _yield((HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE, f'[Exception {index}] '))
                
                yield cause
                
                if index != len(exception):
                    await _yield((HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK, '\n'))
        
        else:
            await _yield_title_and_line_break('Traceback (most recent call last):', 1)
            
            exception_proxy = ExceptionProxyRich(exception)
            populate_frame_proxies([*exception_proxy.iter_frames_no_repeat()])
            exception_proxy.drop_ignored_frames(filter = filter)
            await produce_exception_proxy(exception_proxy)
            
            if reason_type == REASON_TYPE_NONE:
                break
        
        if reason_type == REASON_TYPE_CAUSE:
            title = 'The above exception was the direct cause of the following exception:'
        
        elif reason_type == REASON_TYPE_CONTEXT:
            title = 'During handling of the above exception another exception occurred:'
        
        elif reason_type == REASON_TYPE_CAUSE_GROUP:
            title = f'The above {len(exception)} exception was the direct cause of the following exception:'
        
        else:
            title = None
        
        await _yield((HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK, '\n'))
        
        if (title is not None):
            await _yield_title_and_line_break(title, 2)
        
        continue


@to_coroutine
def _yield(token_type_and_part):
    """
    Yields the given token type and part tuple.
    
    This function is a generator.
    
    Parameters
    ----------
    token_type_and_part : `(int, str)`
        Item to yield back.
    
    Yields
    ------
    token_type_and_part : `(int, str)`
    """
    yield token_type_and_part


@to_coroutine
def _yield_title_and_line_break(title, line_break_count):
    """
    Yields back the given title and `n` amount of line break.
    
    This function is a generator.
    
    Parameters
    ----------
    title : `str`
        Title to yield back.
    
    line_break_count : `int`
        The amount of line breaks to yield back.
    
    Yields
    ------
    token_type_and_part : `(int, str)`
    """
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE, title
    
    for _ in range(line_break_count):
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK, '\n'
