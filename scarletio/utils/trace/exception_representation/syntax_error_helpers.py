__all__ = ()

from itertools import islice


# Pulled from C 3.11
#
# args = Py_BuildValue("(O(OiiNii))", errmsg, tok->filename, tok->lineno,
#                      col_offset, errtext, tok->lineno, end_col_offset);
# if (args) {
#     PyErr_SetObject(PyExc_SyntaxError, args);
#
# file_name is annotated as `O`, so it probably can be `None` as well.
# also: line_number == end_line_number, so we can ignore it.
#
# On older Python versions `line` can also be `None`. How stupid!
#
#
# At some cases exception is built differently tho:
#
# PyErr_Format(PyExc_SyntaxError, DUPLICATE_ARGUMENT, name);
# SET_ERROR_LOCATION(st->st_filename, loc);
#
# Here the exception's details are omitted instead they are set as slots only.
# Because we do not use the slots instead pull the details from its parameters, we have to fix exception up.

def _are_details_valid(details):
    """
    Checks whether the syntax error details are valid.
    
    Parameters
    ----------
    details : `(object, object, object, object) | (object, object, object, object, object, object)`
        A tuple of length 4 or 6.
    
    Returns
    -------
    details_valid : `bool`
    """
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
    

def is_syntax_error(exception):
    """
    Returns whether the given exception is a syntax error with the expected structure.
    
    Parameters
    ----------
    exception : `BaseException`
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
    
    return _are_details_valid(details)


def _get_details_from_slots(syntax_error):
    """
    Gets the syntax error's details from its members instead of its parameters.
    
    Parameters
    ----------
    syntax_error : ``SyntaxError``
        Syntax error to get details of.
    
    Returns
    -------
    details : `(object, object, object, object) | (object, object, object, object, object, object)`
        A tuple of length 4 or 6.
    """
    details = (syntax_error.filename, syntax_error.lineno, syntax_error.offset, syntax_error.text)
    
    if hasattr(SyntaxError, 'end_lineno') and hasattr(SyntaxError, 'end_offset'):
        details = (*details, syntax_error.end_lineno, syntax_error.end_offset)
    
    return details


def is_syntax_error_details_omitted(exception):
    """
    Returns whether the syntax error's has ots details omitted, but they are set in slots instead.
    
    Parameters
    ----------
    exception : ``SyntaxError``
        The exception to check.
    
    Returns
    -------
    details_omitted : `bool`
    """
    exception_parameters = type(exception).args.__get__(exception, type(exception))
    if (not isinstance(exception_parameters, tuple)) or (len(exception_parameters) != 1):
        return False
    
    message, = exception_parameters
    if (message is not None) and (not isinstance(message, str)):
        return False
    
    details = _get_details_from_slots(exception)
    return _are_details_valid(details)


def fixup_syntax_error_details_omitted(syntax_error):
    """
    Fixes up the syntax error's details if they are omitted.
    
    Parameters
    ----------
    syntax_error : ``SyntaxError``
        Syntax error to check.
    """
    syntax_error.args = (syntax_error.args[0], _get_details_from_slots(syntax_error))


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
    message, details = syntax_error.args
    line = details[3]
    if line is not None:
        return
    
    line_number = details[1]
    buffer_length = len(buffer)
    # `line_number` means `line_index + 1`
    if (line_number > buffer_length) or (line_number < 1):
        return
    
    line = buffer[line_number - 1]
    syntax_error.args = (message, (*islice(details, 0, 3), line, *islice(details, 4, 6)))


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
