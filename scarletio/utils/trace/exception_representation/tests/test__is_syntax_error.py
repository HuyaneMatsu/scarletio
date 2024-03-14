import vampytest

from ..syntax_error_helpers import is_syntax_error


def _iter_options():
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, True
    
    # message
    exception = SyntaxError()
    exception.args = (None, ('file_name.py', 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = (None, ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = (12.6, ('file_name.py', 5, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = (12.6, ('file_name.py', 5, 6, 'pass', 8, 9))
    yield exception, False
    
    # file_name
    exception = SyntaxError()
    exception.args = ('message', (None, 5, 6, 'pass'))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', (None, 5, 6, 'pass', 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', (12.6, 5, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', (12.6, 5, 6, 'pass', 8, 9))
    yield exception, False
    
    # line_number
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5.6, 6, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5.6, 6, 'pass', 8, 9))
    yield exception, False
    
    # offset
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6.5, 'pass'))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6.5, 'pass', 8, 9))
    yield exception, False
    
    # line
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, None))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, None, 8, 9))
    yield exception, True
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 12.6))
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 12.6, 8, 9))
    yield exception, False
    
    # end_line_number
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass', 12.6, 9))
    yield exception, False
    
    # end_offset
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass', 8, 12.6))
    yield exception, False
    
    # more parameters
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass'), 'mister')
    yield exception, False
    
    exception = SyntaxError()
    exception.args = ('message', ('file_name.py', 5, 6, 'pass', 8, 9), 'mister')
    yield exception, False
    
    # less parameters
    exception = SyntaxError()
    exception.args = ('message')
    yield exception, False
    
    # bad errors
    yield ValueError('message', ('file_name.py', 5, 6, 'pass')), False
    yield ValueError('message', ('file_name.py', 5, 6, 'pass', 8, 9)), False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_syntax_error(input_value):
    """
    Tests whether ``is_syntax_error`` works as intended.
    
    Parameters
    ----------
    input_value : ``BaseException``
        Exception instance to check.
    
    Returns
    -------
    output : `bool`
    """
    output =  is_syntax_error(input_value)
    vampytest.assert_instance(output, bool, accept_subtypes = False)
    return output
