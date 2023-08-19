__all__ = ()

import sys

from .compilation import maybe_compile
from .editor_base import _validate_buffer, EditorBase

from ....utils import copy_docs


class EditorSimple(EditorBase):
    """
    Simple `input` based editor.
    
    Attributes
    ----------
    auto_completer : ``AutoCompleter``
        Auto completer to use.
    buffer : `list` of `str`
        A precreated buffer which commands the initial lines of the input to write.
    compiled_code : `None`, ``CodeType``
        The compiled inputted code.
    file_name : `str`
        File name of the code produced by the editor.
    prefix_initial : `str`
        First line's prefix.
    prefix_continuous : `str`
        Non-first line's prefix.
    prefix_length : `int`
        As how long should the prefix's length be interpreted.
    """
    __slots__ = ('buffer', )
    
    @copy_docs(EditorBase.__new__)
    def __new__(
        cls, buffer, file_name, prefix_initial, prefix_continuous, prefix_length, highlighter, history, auto_completer
    ):
        buffer = _validate_buffer(buffer)
        
        self = EditorBase.__new__(
            cls, buffer, file_name, prefix_initial, prefix_continuous, prefix_length, highlighter, history,
            auto_completer
        )
        self.buffer = buffer
        return self
    
    
    @copy_docs(EditorBase.__call__)
    def __call__(self):
        try:
            import readline
        except ImportError:
            pass
        
        buffer = self.buffer
        
        while True:
            if buffer:
                prefix = self.prefix_continuous
            else:
                prefix = self.prefix_initial
            
            try:
                line = input(prefix)  
            except EOFError as err:
                sys.stdout.write('\n')
                raise SystemExit() from err
            
            if not buffer:
                line = line.rstrip()
                if not line:
                    continue
            
            buffer.append(line)
            
            compiled_code = maybe_compile(buffer, self.file_name)
            if compiled_code is None:
                continue
            
            self.compiled_code = compiled_code
            break
        
        return self.compiled_code
    
    
    @copy_docs(EditorBase.get_buffer)
    def get_buffer(self):
        return self.buffer
