__all__ = ('FrameProxyVirtual',)

from ...docs import copy_docs

from .frame_proxy_base import FrameProxyBase


class FrameProxyVirtual(FrameProxyBase):
    """
    Virtual frame proxy.
    
    Attributes
    ----------
    builtins : `None | dict<str, object>`
        The frame's builtins. Can be `None` if the variables were already omitted.
    code : `None | CodeType`
        The frame's code.
    expression_info : `None | ExpressionInfo`
        Additional expression information.
    file_name : `str`
        The represented frame's file name. Can be empty string.
    globals : `None | dict<str, object>`
        The frame's builtins. Can be `None` if the variables were already omitted.
    line_index : `int`
        The frame's current line index in Python source code.
    instruction_index : `None`
        The frame's last attempted instruction index in the bytecode.
    locals : `None | dict<str, object>`
        The local variables of the frame. Can be `None` if the variables were already omitted.
    name : `str`
        The frame's function's name. Can be empty string.
    tracing_function : `None | FunctionType`
        Tracing function for the traceback's frame. Defaults to `None`.
    """
    __slots__ = (
        'builtins', 'code', 'file_name', 'globals', 'instruction_index', 'line_index', 'locals', 'name',
        'tracing_function'
    )
    
    def __new__(cls, frame_proxy, *, with_variables = False):
        """
        Creates a new frame proxy.
        
        Parameters
        ----------
        frame_proxy : ``FrameProxyBase``
            The frame to freeze.
        with_variables : `bool` = `False`, Optional (Keyword only)
            Whether variables should also be inherited.
        """
        if isinstance(frame_proxy, cls):
            if frame_proxy.has_variables() <= with_variables:
                return frame_proxy
        
        self = object.__new__(cls)
        self.builtins = frame_proxy.builtins if with_variables else None
        self.code = frame_proxy.code
        self.expression_info = frame_proxy.expression_info
        self.file_name = frame_proxy.file_name
        self.globals = frame_proxy.globals if with_variables else None
        self.instruction_index = frame_proxy.instruction_index
        self.line_index = frame_proxy.line_index
        self.locals = frame_proxy.locals if with_variables else None
        self.name = frame_proxy.name
        self.tracing_function = frame_proxy.tracing_function if with_variables else None
        return self
    
    
    @classmethod
    def from_fields(
        cls,
        *,
        builtins = ...,
        code = ...,
        expression_info = ...,
        file_name = ...,
        globals = ...,
        instruction_index = ...,
        line_index = ...,
        locals = ...,
        name = ...,
        tracing_function = ...,
    ):
        """
        Creates a new frame proxy from the given values.
        
        Parameters
        ----------
        builtins : `None | dict<str, object>`, Optional (Keyword only)
            The frame's builtins.
        code : `None | CodeType`, Optional (Keyword only)
            The frame's code.
        expression_info : `None | ExpressionInfo`, Optional (Keyword only)
            Additional expression information.
        file_name : `str`, Optional (Keyword only)
            The represented file's name.
        globals : `None | dict<str, object>`, Optional (Keyword only)
            The frame's builtins.
        instruction_index : `None`, Optional (Keyword only)
            The frame's last attempted instruction index in the bytecode.
        line_index : `int`, Optional (Keyword only)
            The frame's current line index in Python source code.
        locals : `None | dict<str, object>`, Optional (Keyword only)
            The local variables of the frame.
        name : `str`
            The frame's function's name.
        tracing_function : `None | FunctionType`, Optional (Keyword only)
            Tracing function for the traceback's frame.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.builtins = None if builtins is ... else builtins
        self.code = None if code is ... else code
        self.expression_info = None if expression_info is ... else expression_info
        self.file_name = '' if file_name is ... else file_name
        self.globals = None if globals is ... else globals
        self.instruction_index = 0 if instruction_index is ... else instruction_index
        self.line_index = 0 if line_index is ... else line_index
        self.locals = None if locals is ... else locals
        self.name = '' if name is ... else name
        self.tracing_function = None if tracing_function is ... else tracing_function
        return self
    
    
    @copy_docs(FrameProxyBase.has_variables)
    def has_variables(self):
        if self.builtins is not None:
            return True
        
        if self.globals is not None:
            return True
        
        if self.locals is not None:
            return True
        
        return False
