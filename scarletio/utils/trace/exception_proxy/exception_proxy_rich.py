__all__ = ('ExceptionProxyRich',)

from ..exception_representation import get_exception_representation
from ..frame_grouping import group_frames
from ..frame_proxy import get_exception_frames

from .exception_proxy_base import ExceptionProxyBase


class ExceptionProxyRich(ExceptionProxyBase):
    """
    Rich exception proxy type.
    
    Attributes
    ----------
    exception_representation : `None | ExceptionRepresentationBase`
        The exception to proxy.
    frame_groups : `None | list<FrameGroup>`
        Cache field for the exception's frames in a grouped form.
    """
    __slots__ = ('exception_representation', 'frame_groups')
    
    def __new__(cls, exception):
        """
        Creates a new exception proxy.
        
        Parameters
        ----------
        exception : ``BaseException``
            The exception to proxy.
        """
        frames = get_exception_frames(exception)
        frame_groups = group_frames(frames)
        
        exception_representation = get_exception_representation(exception, frames)
        
        self = object.__new__(cls)
        self.exception_representation = exception_representation
        self.frame_groups = frame_groups
        return self
