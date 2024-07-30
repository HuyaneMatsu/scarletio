__all__ = ('render_exception_into', 'render_frames_into',)

from ..cause_group import CauseGroup

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
    frames = convert_frames_to_frame_proxies(frames)
    populate_frame_proxies(frames)
    
    if extend is None:
        extend = []
    
    frames = [frame for frame in frames if should_keep_frame(frame, filter = filter)]
    frame_groups = group_frames(frames)
    
    render_frame_groups_into(frame_groups, extend, highlighter)
    
    return extend


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
            extend = add_trace_title_into(
                f'The following {len(exception)} exceptions where the reason of the exception following them:',
                extend,
                highlighter,
            )
            extend.append('\n\n')
            
            for index, cause in enumerate(exception, 1):
                extend = add_trace_title_into(f'[Exception {index}] ', extend, highlighter)
                extend = render_exception_into(cause, extend = extend, filter = filter, highlighter = highlighter)
                
                if index != len(exception):
                    extend.append('\n')
        
        else:
            extend = add_trace_title_into('Traceback (most recent call last):', extend, highlighter)
            extend.append('\n')
            
            exception_proxy = ExceptionProxyRich(exception)
            populate_frame_proxies([*exception_proxy.iter_frames_no_repeat()])
            exception_proxy.drop_ignored_frames(filter = filter)
            extend = render_exception_proxy_into(exception_proxy, extend, highlighter)
            
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
        
        extend.append('\n')
        
        if (title is not None):
            extend = add_trace_title_into(title, extend, highlighter)
            extend.append('\n\n')
        continue
    
    return extend
