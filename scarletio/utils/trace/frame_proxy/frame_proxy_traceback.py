__all__ = ('FrameProxyTraceback',)

from ...docs import copy_docs

from .frame_proxy_base import FrameProxyBase


class FrameProxyTraceback(FrameProxyBase):
    """
    Wraps a traceback's frame.
    
    Attributes
    ----------
    _traceback : ``TracebackType``
        The wrapped traceback frame.
    expression_info : `None | ExpressionInfo`
        Additional expression information.
    """
    __slots__ = ('_traceback',)
    
    def __new__(cls, traceback):
        """
        Creates a new traceback frame proxy.
        
        Parameters
        ----------
        traceback : ``TracebackType``
            The traceback frame to wrap.
        """
        self = object.__new__(cls)
        self._traceback = traceback
        self.expression_info = None
        return self
    
    
    @property
    @copy_docs(FrameProxyBase.builtins)
    def builtins(self):
        return self._traceback.tb_frame.f_builtins
    
    
    @property
    @copy_docs(FrameProxyBase.globals)
    def globals(self):
        return self._traceback.tb_frame.f_globals
    
    
    @property
    @copy_docs(FrameProxyBase.locals)
    def locals(self):
        return self._traceback.tb_frame.f_locals
    
    
    @property
    @copy_docs(FrameProxyBase.code)
    def code(self):
        return self._traceback.tb_frame.f_code
    
    
    @property
    @copy_docs(FrameProxyBase.instruction_index)
    def instruction_index(self):
        return self._traceback.tb_frame.f_lasti
    
    
    @property
    @copy_docs(FrameProxyBase.line_index)
    def line_index(self):
        return self._traceback.tb_lineno - 1
    
    
    @property
    @copy_docs(FrameProxyBase.tracing_function)
    def tracing_function(self):
        return self._traceback.tb_frame.f_trace
    
    
    @copy_docs(FrameProxyBase.has_variables)
    def has_variables(self):
        return True
