__all__ = ('convert_frames_to_frame_proxies', 'get_exception_frames', 'populate_frame_proxies',)

from types import FrameType, TracebackType

from ..expression_parsing import ExpressionInfo, LineCacheSession, get_expression_info

from .frame_proxy_base import FrameProxyBase
from .frame_proxy_frame import FrameProxyFrame
from .frame_proxy_traceback import FrameProxyTraceback


def convert_frames_to_frame_proxies(frames):
    """
    Converts the given frames into frame proxies.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase | FrameType | TracebackType>`
        The frames to convert.
    
    Returns
    -------
    frame_proxies : `list<FrameProxyBase>`
    
    Raises
    ------
    TypeError
        - Unknown frame type.
    """
    frame_proxies = []
    
    for frame in frames:
        if isinstance(frame, FrameProxyBase):
            frame_proxy = frame
        
        elif isinstance(frame, FrameType):
            frame_proxy = FrameProxyFrame(frame)
        
        elif isinstance(frame, TracebackType):
            frame_proxy = FrameProxyTraceback(frame)
        
        else:
            raise TypeError(
                f'Unknown frame type, got {type(frame).__name__}; {frame!r}; frames = {frames!r}.'
            )
        
        frame_proxies.append(frame_proxy)
    
    return frame_proxies


def get_exception_frames(exception):
    """
    Gets the frames of the given exception.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to trace back.
    
    Returns
    -------
    frames : `list<FrameProxyBase>`
        A list of `frame` compatible exception frames.
    """
    frames = []
    traceback = exception.__traceback__
    
    while True:
        if traceback is None:
            break
        
        frame = FrameProxyTraceback(traceback)
        frames.append(frame)
        traceback = traceback.tb_next
    
    return frames


def populate_frame_proxies(frames):
    """
    Populates the given frame proxies.
    
    Parameters
    ----------
    frames : `list<FrameProxyBase>`
        The frame proxies to populate.
    """
    expressions = {}
    
    for frame in frames:
        expression_key = frame.expression_key
        expression_info = frame.expression_info
        
        if expression_info is None:
            expressions.setdefault(expression_key, None)
        else:
            expressions[expression_key] = expression_info.copy()
    
    with LineCacheSession():
        for expression_key, expression_value in expressions.items():
            if expression_value is None:
                expressions[expression_key] = get_expression_info(expression_key)
    
    for frame in frames:
        expression_key = frame.expression_key
        
        try:
            expression_info = expressions[expression_key]
        except KeyError:
            # A frame changed while we were rendering, create a dummy 
            expression_info = ExpressionInfo(expression_key, [], 0, True)
            expressions.setdefault(expression_key, expression_info)
        
        expression_info.do_mention()
        frame.expression_info = expression_info
