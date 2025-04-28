__all__ = ('render_exception_into', 'render_frames_into',)

from ..cause_group import CauseGroup
from ..highlight import HIGHLIGHT_TOKEN_TYPES, get_highlight_streamer

from .exception_proxy import ExceptionProxyRich
from .frame_grouping import group_frames
from .frame_ignoring import should_keep_frame
from .frame_proxy import convert_frames_to_frame_proxies, populate_frame_proxies
from .rendering import render_frame_groups_into, add_trace_title_into, render_exception_proxy_into


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
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Stores how the output should be highlighted.
    
    Returns
    -------
    extend : `list<str>`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    highlight_streamer = get_highlight_streamer(highlighter)
    extend = _render_frames_into(frames, filter, highlight_streamer, extend)
    extend.extend(highlight_streamer.asend(None))
    
    return extend


def _render_frames_into(frames, filter, highlight_streamer, into):
    """
    Renders the given frames into a list of strings.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase | FrameType | TraceBack>`
        The frames to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    highlight_streamer : `CoroutineGenerator`
        Highlight streamer to highlight the produced tokens.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Returns
    -------
    into : `list<str>`
    """
    frames = convert_frames_to_frame_proxies(frames)
    populate_frame_proxies(frames)
    frames = [frame for frame in frames if should_keep_frame(frame, filter = filter)]
    frame_groups = group_frames(frames)
    
    render_frame_groups_into(frame_groups, highlight_streamer, into)
    
    return into


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
    
    highlighter : `None`, ``HighlightFormatterContext`` = `None`, Optional (Keyword only)
        Stores how the output should be highlighted.
    
    Returns
    -------
    extend : `list<str>`
        The rendered frames as a `list` of it's string parts.
    """
    if extend is None:
        extend = []
    
    highlight_streamer = get_highlight_streamer(highlighter)
    extend = _render_exception_into(exception, filter, highlight_streamer, extend)
    extend.extend(highlight_streamer.asend(None))
    
    return extend


def _render_exception_into(exception, filter, highlight_streamer, into):
    """
    Renders the given exception's frames into a list of strings.
    
    This function is generator.
    
    Parameters
    ----------
    exception : `None | BaseException`
        The exception to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    highlight_streamer : `CoroutineGenerator`
        Highlight streamer to highlight the produced tokens.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Returns
    -------
    into : `list<str>`
    """
    renderer_queue = []
    renderer_queue.append(_render_exception_into_step(exception, filter, highlight_streamer, into))
    
    while renderer_queue:
        renderer = renderer_queue[-1]
        exception = next(renderer, None)
        if exception is None:
            del renderer_queue[-1]
            continue
        
        renderer_queue.append(_render_exception_into_step(exception, filter, highlight_streamer, into))
        continue
    
    return into


def _render_exception_into_step(exception, filter, highlight_streamer, into):
    """
    Renders the given exception's frames into a list of strings.
    When meets a nested exception to render (in a cause group), yields it back.
    
    This function is generator.
    
    Parameters
    ----------
    exception : `None | BaseException`
        The exception to render.
    
    filter : `None | callable`
        Additional filter to check whether a frame should be shown.
    
    highlight_streamer : `CoroutineGenerator`
        Highlight streamer to highlight the produced tokens.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Yields
    ------
    exception : ``BaseException``
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
            into = add_trace_title_into(
                f'The following {len(exception)} exceptions where the reason of the exception following them:',
                highlight_streamer,
                into,
            )
            for _ in range(2):
                into.extend(highlight_streamer.asend((
                    HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK,
                    '\n',
                )))
            
            for index, cause in enumerate(exception, 1):
                into = add_trace_title_into(f'[Exception {index}] ', highlight_streamer, into)
                yield cause
                
                if index != len(exception):
                    into.append('\n')
        
        else:
            into = add_trace_title_into('Traceback (most recent call last):', highlight_streamer, into)
            into.extend(highlight_streamer.asend((
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK,
                '\n',
            )))
            
            exception_proxy = ExceptionProxyRich(exception)
            populate_frame_proxies([*exception_proxy.iter_frames_no_repeat()])
            exception_proxy.drop_ignored_frames(filter = filter)
            into = render_exception_proxy_into(exception_proxy, highlight_streamer, into)
            
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
        
        into.extend(highlight_streamer.asend((
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK,
            '\n',
        )))
        
        if (title is not None):
            into = add_trace_title_into(title, highlight_streamer, into)
            for _ in range(2):
                into.extend(highlight_streamer.asend((
                    HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINE_BREAK,
                    '\n',
                )))
        
        continue
