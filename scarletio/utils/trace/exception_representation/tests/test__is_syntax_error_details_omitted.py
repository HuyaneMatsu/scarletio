import vampytest

from ..syntax_error_helpers import is_syntax_error_details_omitted


def _set_exception_details_to_slots(exception, details):
    """
    Sets the syntax exception details as slots.
    
    Parameters
    ----------
    exception : ``SyntaxError`
        The exception to modify
    
    details : `(object, object, object, object) | (object, object, object, object, object, object)`
        A tuple of length 4 or 6.
    """
    file_name = details[0]
    line_number = details[1]
    offset = details[2]
    line = details[3]
    
    if len(details) == 4:
        end_line_number = line_number
        end_offset = offset + 1
    
    else:
        end_line_number = 0
        end_offset = 0
    
    exception.filename = file_name
    exception.lineno = line_number
    exception.offset = offset
    exception.text = line
    
    if hasattr(SyntaxError, 'end_lineno') and hasattr(SyntaxError, 'end_offset'):
        exception.end_lineno = end_line_number
        exception.end_offset = end_offset


def _iter_options():
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, True
    
    # message
    exception = SyntaxError()
    exception.args = (None, )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = (None, )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = (12.6, )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = (12.6, )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, False
    
    # file_name
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, (None, 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, (None, 5, 6, 'pass', 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, (12.6, 5, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, (12.6, 5, 6, 'pass', 8, 9))
    yield exception, False
    
    # line_number
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5.5, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5.5, 6, 'pass', 8, 9))
    yield exception, False
    
    # offset
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6.5, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6.5, 'pass', 8, 9))
    yield exception, False
    
    # line
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, None))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, None, 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 12.6))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', )
    _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 12.6, 8, 9))
    yield exception, False

    if hasattr(SyntaxError, 'end_lineno') and hasattr(SyntaxError, 'end_offset'):
        # end_line_number
        exception = SyntaxError()
        exception.args = ('message', )
        _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass', 8.5, 9))
        yield exception, False
        
        # end_offset
        exception = SyntaxError()
        exception.args = ('message', )
        _set_exception_details_to_slots(exception, ('file_name.py', 5, 6, 'pass', 8, 9.5))
        yield exception, False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_syntax_error_details_omitted(input_value):
    """
    Tests whether ``is_syntax_error_details_omitted`` works as intended.
    
    Parameters
    ----------
    input_value : ``SyntaxError``
        Exception instance to check.
    
    Returns
    -------
    output : `bool`
    """
    output =  is_syntax_error_details_omitted(input_value)
    vampytest.assert_instance(output, bool, accept_subtypes = False)
    return output
