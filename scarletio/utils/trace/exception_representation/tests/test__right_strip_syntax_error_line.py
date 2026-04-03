import vampytest

from ..syntax_error_helpers import right_strip_syntax_error_line


def _iter_options():
    # nothing to strip
    yield (
        ('message', ('koishi.py', 5, 6, 'pass')),
        ('message', ('koishi.py', 5, 6, 'pass')),
    )
    yield (
        ('message', ('koishi.py', 5, 6, 'pass', 8, 9)),
        ('message', ('koishi.py', 5, 6, 'pass', 8, 9)),
    )
    
    # extra on left (should do nothing)
    yield (
        ('message', ('koishi.py', 5, 6, '    pass')),
        ('message', ('koishi.py', 5, 6, '    pass')),
    )
    yield (
        ('message', ('koishi.py', 5, 6, '    pass', 8, 9)),
        ('message', ('koishi.py', 5, 6, '    pass', 8, 9)),
    )
    
    # extra on right (should strip)
    yield (
        ('message', ('koishi.py', 5, 6, 'pass    ')),
        ('message', ('koishi.py', 5, 6, 'pass')),
    )
    yield (
        ('message', ('koishi.py', 5, 6, 'pass    ', 8, 9)),
        ('message', ('koishi.py', 5, 6, 'pass', 8, 9)),
    )
    
    # no line
    yield (
        ('message', ('koishi.py', 5, 6, None)),
        ('message', ('koishi.py', 5, 6, None)),
    )
    yield (
        ('message', ('koishi.py', 5, 6, None, 8, 9)),
        ('message', ('koishi.py', 5, 6, None, 8, 9)),
    )
    

@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__right_strip_syntax_error_line(input_parameters):
    """
    Tests whether ``right_strip_syntax_error_line`` works as intended.
    
    Parameters
    ----------
    input_parameters : `tuple`
        Parameters to create syntax error instance from.
    
    Returns
    -------
    output : `tuple`
    """
    syntax_error = SyntaxError()
    syntax_error.args = input_parameters
    right_strip_syntax_error_line(syntax_error)
    return syntax_error.args
