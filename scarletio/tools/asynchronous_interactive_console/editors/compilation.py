__all__ = ()

import sys, warnings

from ....utils import add_console_input
from ....utils.trace.exception_representation.syntax_error_helpers import is_syntax_error, right_strip_syntax_error_line


PYTHON_COMPILE_FLAG_DONT_IMPLY_DEDENT = 1 << 9
PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT = 1 << 13
PYTHON_COMPILE_FLAG_ALLOW_INCOMPLETE_INPUT = 1 << 14


if sys.version_info < (3, 8):
    PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT = 0


try:
    compile('', '', 'single', PYTHON_COMPILE_FLAG_ALLOW_INCOMPLETE_INPUT)
except ValueError:
    PYTHON_COMPILE_FLAG_ALLOW_INCOMPLETE_INPUT = 0
except SyntaxError:
    pass


PYTHON_COMPILE_FLAGS_USED = (
    PYTHON_COMPILE_FLAG_DONT_IMPLY_DEDENT |
    PYTHON_COMPILE_FLAG_ALLOW_TOP_LEVEL_AWAIT |
    PYTHON_COMPILE_FLAG_ALLOW_INCOMPLETE_INPUT
)


def maybe_compile(buffer, file_name):
    """
    Tries to compile the given source code.
    
    Parameters
    ----------
    buffer : `list` of `str`
        The source code buffer to try to compile.
    file_name : `str`
        The file to compile the code under.
    
    Returns
    -------
    code : `None`, `CodeType`
    
    Raises
    ------
    SyntaxError
    """
    if is_source_empty(buffer):
        return None
    
    source = '\n'.join([line.rstrip() for line in buffer])
    
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        
        try:
            try:
                code_object = _try_compile(source, file_name, True)
            except IndentationError:
                raise
            
            except SyntaxError as err:
                exception_1 = err
            
            else:
                if (code_object is not None):
                    add_console_input(file_name, source)
                    return code_object
                
                exception_1 = None
            
            try:
                code_object = _try_compile(source, file_name, False)
            except IndentationError:
                raise
            
            except SyntaxError as err:
                exception_2 = err
            
            else:
                if (code_object is not None):
                    add_console_input(file_name, source)
                    return code_object
                
                exception_2 = None
            
            if (exception_1 is None):
                if (exception_2 is not None):
                    raise exception_2
            
            else:
                if (exception_2 is not None):
                    if is_syntax_error(exception_1):
                        right_strip_syntax_error_line(exception_1)
                    
                    if is_syntax_error(exception_2):
                        right_strip_syntax_error_line(exception_2)
                    
                    if exception_1.args == exception_2.args:
                        raise SyntaxError(*exception_1.args)
        
        finally:
            exception_1 = None
            exception_2 = None
    
    return None


def _try_compile(source, file_name, single_expression_mode):
    """
    Tries to compile the given source code.
    
    Parameters
    ----------
    source : `str`
        The source code to try to compile.
    file_name : `str`
        The file to compile the code under.
    single_expression_mode : `bool`
        Whether we expect a single expression.
    
    Returns
    -------
    code : `CodeType`
    
    Raises
    ------
    SyntaxError
    """
    try:
        return compile(
            source,
            file_name,
            'single' if single_expression_mode else 'exec',
            PYTHON_COMPILE_FLAGS_USED,
        )
    except SyntaxError as err:
        exception_representation = repr(err)
        
        if single_expression_mode:
            if 'multiple statements' in exception_representation:
                return None
        
        if PYTHON_COMPILE_FLAG_ALLOW_INCOMPLETE_INPUT:
            reason = 'incomplete input'
        else:
            reason = 'unexpected EOF'
        
        if reason in exception_representation:
            return None
        
        raise
    
    # Memory error if: too many nested parentheses
    # Value error if: cannot convert a value
    except (MemoryError, ValueError, OverflowError) as err:
        raise SyntaxError(*err.args) from err
    

def is_source_empty(buffer):
    """
    Returns whether the given source code is empty or nah.
    
    Parameters
    ----------
    buffer : `str`
        The source code buffer.
    
    Returns
    -------
    is_source_empty : `bool`
    """
    for line in buffer:
        for character in line:
            if character in {'\r', '\n', ' ', '\t'}:
                continue
        
            if character == '#':
                break
            
            return False
    
    return True
