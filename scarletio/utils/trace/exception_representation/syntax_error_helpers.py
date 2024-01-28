__all__ = ()


def is_syntax_error(exception):
    """
    Returns whether the given exception is a syntax error with the expected structure.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to check.
    
    Returns
    -------
    is_syntax_error : `bool`
    """
    if not issubclass(type(exception), SyntaxError):
        return False
    
    exception_parameters = type(exception).args.__get__(exception, type(exception))
    if (not isinstance(exception_parameters, tuple)) or (len(exception_parameters) != 2):
        return False
    
    message, details = exception_parameters
    if (message is not None) and (not isinstance(message, str)):
        return False
    
    if (not isinstance(details, tuple)) or (len(details) not in (4, 6)):
        return False
    
    # Pulled from C 3.11
    #
    #     args = Py_BuildValue("(O(OiiNii))", errmsg, tok->filename, tok->lineno,
    #                          col_offset, errtext, tok->lineno, end_col_offset);
    #
    # file_name is annotated as `O`, so it probably can be `None` as well.
    # also: line_number == end_line_number, so we can ignore it.
    #
    # On older Python versions `line` can also be `None`. How stupid!
    
    file_name = details[0]
    line_number = details[1]
    offset = details[2]
    line = details[3]
    
    if (file_name is not None) and (not isinstance(file_name, str)):
        return False
    
    if not isinstance(line_number, int):
        return False
    
    if not isinstance(offset, int):
        return False
    
    if (line is not None) and (not isinstance(line, str)):
        return False
    
    if len(details) == 4:
        return True
    
    end_line_number = details[4]
    end_offset = details[5]
    
    if not isinstance(end_line_number, int):
        return False
    
    if not isinstance(end_offset, int):
        return False
    
    return True


def fixup_syntax_error_line_from_buffer(syntax_error, buffer):
    """
    Tries to fix up the syntax error's missing line.
    
    Should be only called if ``is_syntax_error`` returned `True` on the given exception.
    
    Parameters
    ----------
    syntax_error : ``SyntaxError``
        Respective SyntaxError
    buffer : `list` of `str`
        Buffer containing the respective lines of the file.
    """
    message, (file_name, line_number, offset, line, *end) = syntax_error.args
    if line is not None:
        return
    
    buffer_length = len(buffer)
    # `line_number` means `line_index + 1`
    if (line_number > buffer_length) or (line_number < 1):
        return
    
    line = buffer[line_number - 1]
    syntax_error.args = (message, (file_name, line_number, offset, line, *end))


def right_strip_syntax_error_line(syntax_error):
    """
    Right strips the syntax error's line. This can be useful when comparing two syntax errors, but one has new line
    character at the end.
    
    Should be only called if ``is_syntax_error`` returned `True` on the given exception.
    
    Parameters
    ----------
    syntax_error : `SyntaxError`
        The syntax error to strip.
    """
    message, (file_name, line_number, offset, line, *end) = syntax_error.args
    if line is None:
        return
    
    line = line.rstrip()
    
    syntax_error.args = (message, (file_name, line_number, offset, line, *end))
