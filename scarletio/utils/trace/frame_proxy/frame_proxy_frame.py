__all__ = ('FrameProxyFrame',)

from ...docs import copy_docs

from .frame_proxy_base import FrameProxyBase


class FrameProxyFrame(FrameProxyBase):
    """
    Wraps a frame.
    
    Attributes
    ----------
    _frame : ``FrameType``
        The wrapped frame.
    expression_info : `None | ExpressionInfo`
        Additional expression information.
    """
    __slots__ = ('_frame',)
    
    def __new__(cls, frame):
        """
        Creates a new frame proxy.
        
        Parameters
        ----------
        frame : ``FrameType``
            The frame to wrap.
        """
        self = object.__new__(cls)
        self._frame = frame
        self.expression_info = None
        return self
    
    
    @property
    @copy_docs(FrameProxyBase.builtins)
    def builtins(self):
        return self._frame.f_builtins
    
    
    @property
    @copy_docs(FrameProxyBase.globals)
    def globals(self):
        return self._frame.f_globals
    
    
    @property
    @copy_docs(FrameProxyBase.locals)
    def locals(self):
        return self._frame.f_locals
    
    
    @property
    @copy_docs(FrameProxyBase.code)
    def code(self):
        return self._frame.f_code
    
    
    @property
    @copy_docs(FrameProxyBase.instruction_index)
    def instruction_index(self):
        return self._frame.f_lasti
    
    
    @property
    @copy_docs(FrameProxyBase.line_index)
    def line_index(self):
        return self._frame.f_lineno - 1
    
    
    @property
    @copy_docs(FrameProxyBase.tracing_function)
    def tracing_function(self):
        return self._frame.f_trace
    
    
    @copy_docs(FrameProxyBase.has_variables)
    def has_variables(self):
        return True
