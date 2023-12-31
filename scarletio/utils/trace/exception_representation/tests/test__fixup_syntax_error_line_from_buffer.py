import vampytest

from ..syntax_error_helpers import fixup_syntax_error_line_from_buffer


def _iter_options():
    buffer = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    # nothing to fixup
    yield (
        ('message', ('koishi.py', 5, 6, 'pass')),
        buffer,
        ('message', ('koishi.py', 5, 6, 'pass')),
    )
    yield (
        ('message', ('koishi.py', 5, 6, 'pass', 8, 9)),
        buffer,
        ('message', ('koishi.py', 5, 6, 'pass', 8, 9)),
    )
    
    # fixup
    yield (
        ('message', ('koishi.py', 5, 6, None)),
        buffer,
        ('message', ('koishi.py', 5, 6, 'e')),
    )
    yield (
        ('message', ('koishi.py', 5, 6, None, 8, 9)),
        buffer,
        ('message', ('koishi.py', 5, 6, 'e', 8, 9)),
    )

    # index over
    yield (
        ('message', ('koishi.py', 10, 6, None)),
        buffer,
        ('message', ('koishi.py', 10, 6, None)),
    )
    yield (
        ('message', ('koishi.py', 10, 6, None, 8, 9)),
        buffer,
        ('message', ('koishi.py', 10, 6, None, 8, 9)),
    )

    # index under
    yield (
        ('message', ('koishi.py', -1, 6, None)),
        buffer,
        ('message', ('koishi.py', -1, 6, None)),
    )
    yield (
        ('message', ('koishi.py', -1, 6, None, 8, 9)),
        buffer,
        ('message', ('koishi.py', -1, 6, None, 8, 9)),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__fixup_syntax_error_line_from_buffer(input_parameters, buffer):
    """
    Tests whether ``fixup_syntax_error_line_from_buffer`` works as intended.
    
    Parameters
    ----------
    input_parameters : `tuple`
        Parameters to create syntax error instance from.
    buffer : `list<str>`
        Buffer containing the respective lines of the file.
    
    Returns
    -------
    output : `tuple`
    """
    syntax_error = SyntaxError()
    syntax_error.args = input_parameters
    fixup_syntax_error_line_from_buffer(syntax_error, buffer)
    return syntax_error.args
