__all__ = ('ExceptionProxyVirtual',)

from ..frame_grouping import normalize_frame_groups

from .exception_proxy_base import ExceptionProxyBase


class ExceptionProxyVirtual(ExceptionProxyBase):
    """
    Virtual exception proxy type.
    
    Attributes
    ----------
    exception_representation : `None | ExceptionRepresentationBase`
        The exception to proxy.
    frame_groups : `None | list<FrameGroup>`
        Cache field for the exception's frames in a grouped form.
    """
    __slots__ = ('exception_representation', 'frame_groups')
    
    def __new__(cls, exception_proxy, *, with_variables = False):
        """
        Creates a new exception proxy.
        
        Parameters
        ----------
        exception_proxy : ``ExceptionProxyBase``
            The exception proxy to proxy.
        with_variables : `bool` = `False`, Optional (Keyword only)
            Whether variables should also be inherited.
        """
        if isinstance(exception_proxy, cls):
            if exception_proxy.has_variables() <= with_variables:
                return exception_proxy
        
        frame_groups = exception_proxy.frame_groups
        if (frame_groups is not None):
            if with_variables:
                frame_groups = [frame_group.copy() for frame_group in frame_groups]
            else:
                frame_groups = [frame_group.copy_without_variables() for frame_group in frame_groups]
        
        self = object.__new__(cls)
        self.exception_representation = exception_proxy.exception_representation
        self.frame_groups = frame_groups
        return self
    
    
    @classmethod
    def from_fields(
        cls,
        *,
        exception_representation = ...,
        frame_groups = ...,
    ):
        """
        Creates a new virtual exception proxy from the given fields.
        
        Parameters
        ----------
        exception_representation : `None | ExceptionRepresentationBase`, Optional (Keyword only)
            The exception to proxy.
        frame_groups : `None | list<FrameGroup>`, Optional (Keyword only)
            Cache field for the exception's frames in a grouped form.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.exception_representation = None if exception_representation is ... else exception_representation
        self.frame_groups = None if frame_groups is ... else normalize_frame_groups(frame_groups)
        return self
