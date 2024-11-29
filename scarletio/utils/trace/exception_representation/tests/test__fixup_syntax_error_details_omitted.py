import vampytest

from ..syntax_error_helpers import fixup_syntax_error_details_omitted


def test__fixup_syntax_error_details_omitted():
    """
    Tests whether ``fixup_syntax_error_details_omitted`` works as intended.
    """
    message = 'message'
    file_name = 'file_name.py'
    line_number = 5
    offset = 6
    line = 'pass'
    end_line_number = 7
    end_offset = 8
    length_6 = hasattr(SyntaxError, 'end_lineno') and hasattr(SyntaxError, 'end_offset')
    
    exception = SyntaxError()
    exception.args = (message, )
    exception.filename = file_name
    exception.lineno = line_number
    exception.offset = offset
    exception.text = line
    
    if length_6:
        exception.end_lineno = end_line_number
        exception.end_offset = end_offset
    
    fixup_syntax_error_details_omitted(exception)
    
    details = (file_name, line_number, offset, line)
    if length_6:
        details = (*details, end_line_number, end_offset)
    
    vampytest.assert_eq(exception.args, (message, details))
