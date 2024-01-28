__all__ = ('ExceptionRepresentationSyntaxError',)

from ...docs import copy_docs

from .exception_representation_base import ExceptionRepresentationBase
from .representation_helpers import _get_type_name


class ExceptionRepresentationSyntaxError(ExceptionRepresentationBase):
    """
    Holds a valid syntax error's representation.
    
    Attributes
    ----------
    file_name : `str`
        The file's name where the exception occurred.
    line : `str`
        The line where the syntax is invalid. Can be empty string.
    line_index : `int`
        The line's index in the file.
    message : `str`
        Error message. Can not be empty string.
    pointer_start_offset : `int`
        The offset after the pointer starts.
    pointer_length : `int`
        The pointer's length. Can be `0` if it should not be shown.
    type_name : `str`
        The represented exception's type's name.
    """
    __slots__ = ('file_name', 'line', 'line_index', 'message', 'pointer_start_offset', 'pointer_length', 'type_name')
    
    def __new__(cls, exception, frame):
        """
        Creates a new exception representation.
        
        Parameters
        ----------
        exception : `SyntaxError`
            Exception to represent.
        frame : `None | FrameProxyBase`
            The frame the exception is raised from.
        """
        message, frames = exception.args
        
        if (message is None):
            message = ''
        
        file_name = frames[0]
        line_index = frames[1] - 1
        pointer_start_offset = frames[2] - 1
        line = frames[3]
        
        if len(frames) == 6:
            pointer_end_offset = frames[5] - 1
        else:
            pointer_end_offset = pointer_start_offset + 1
        
        if (file_name is None):
            file_name = ''
        
        if (line is None):
            line = ''
            pointer_start_offset = 0
            pointer_length = 0
            
        else:
            line = line.rstrip()
            
            left_stripped_count = 0
            for character in line:
                if character in {' ', '\n', '\t', '\f'}:
                    left_stripped_count += 1
                    continue
                
                break
            
            line = line[left_stripped_count:]
            
            pointer_start_offset -= left_stripped_count
            pointer_end_offset -= left_stripped_count
        
            if pointer_start_offset < 0:
                pointer_start_offset = 0
            
            if pointer_end_offset < 0:
                pointer_end_offset = 0
            
            if pointer_start_offset >= pointer_end_offset:
                pointer_start_offset = 0
                pointer_length = 0
            else:
                pointer_length = pointer_end_offset - pointer_start_offset
        
        type_name = _get_type_name(type(exception))
        
        self = object.__new__(cls)
        self.file_name = file_name
        self.line = line
        self.line_index = line_index
        self.message = message
        self.pointer_length = pointer_length
        self.pointer_start_offset = pointer_start_offset
        self.type_name = type_name
        return self
    
    
    @classmethod
    def from_fields(
        cls,
        *,
        file_name = ...,
        line = ...,
        line_index = ...,
        message = ...,
        pointer_start_offset = ...,
        pointer_length = ...,
        type_name = ...,
    ):
        """
        Creates a new syntax error representation from the given fields.
        
        Attributes
        ----------
        file_name : `str`, Optional (Keyword only)
            The file's name where the exception occurred.
        line : `str`, Optional (Keyword only)
            The line where the syntax is invalid. Can be empty string.
        line_index : `int`, Optional (Keyword only)
            The line's index in the file.
        message : `str`, Optional (Keyword only)
            Error message. Can not be empty string.
        pointer_start_offset : `int`, Optional (Keyword only)
            The offset after the pointer starts.
        pointer_length : `int`, Optional (Keyword only)
            The pointer's length. Can be `0` if it should not be shown.
        type_name : `str`, Optional (Keyword only)
            The represented exception's type's name.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.file_name = '' if file_name is ... else file_name
        self.line = '' if line is ... else line
        self.line_index = 0 if line_index is ... else line_index
        self.message = '' if message is ... else message
        self.pointer_start_offset = 0 if pointer_start_offset is ... else pointer_start_offset
        self.pointer_length = 0 if pointer_length is ... else pointer_length
        self.type_name = SyntaxError.__name__ if type_name is ... else type_name
        return self
    
    
    @copy_docs(ExceptionRepresentationBase._populate_repr_parts)
    def _populate_repr_parts(self, repr_parts):
        # type_name
        repr_parts.append(' type_name = ')
        repr_parts.append(repr(self.type_name))
        
        # message
        message = self.message
        if (message is not None):
            repr_parts.append(', message = ')
            repr_parts.append(repr(message))
        
        # location
        file_name = self.file_name
        line_index = self.line_index
        if file_name and line_index >= 0:
            repr_parts.append(', file_name = ')
            repr_parts.append(repr(file_name))
            repr_parts.append(', line_index = ')
            repr_parts.append(repr(self.line_index))
        
        
        # line & pointer
        line = self.line
        if line:
            repr_parts.append(', line = ')
            repr_parts.append(repr(line))
            
            pointer_length = self.pointer_length
            if pointer_length:
                repr_parts.append(', pointer_start_offset = ')
                repr_parts.append(repr(self.pointer_start_offset))
                
                repr_parts.append(', pointer_length = ')
                repr_parts.append(repr(pointer_length))
    
    
    @copy_docs(ExceptionRepresentationBase._is_equal)
    def _is_equal(self, other):
        if self.type_name != other.type_name:
            return False
        
        if self.message != other.message:
            return False
        
        if self.file_name != other.file_name:
            return False
        
        if self.line_index != other.line_index:
            return False
        
        if self.line != other.line:
            return False
        
        if self.pointer_start_offset != other.pointer_start_offset:
            return False
        
        if self.pointer_length != other.pointer_length:
            return False
        
        return True
