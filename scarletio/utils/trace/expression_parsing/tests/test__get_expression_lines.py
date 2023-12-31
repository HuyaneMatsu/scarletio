import vampytest

from ..line_cache_session import LineCacheSession
from ..parsing import get_expression_lines


"""



hello



mister = (
'hey')




hello(there)




hoy. \
there()



hello(
    there
)


'''
'''



'its me'




koishi = (
    {
)

"""

def _iter_options():
    yield (
        10,
        (
            ['hello'],
            0,
            True,
        ),
    )
    yield (
        15,
        (
            ['mister = (', '\'hey\')'],
            1,
            True,
        ),
    )
    yield (
        20,
        (
            ['hello(there)'],
            0,
            True,
        ),
    )
    yield (
        25,
        (
            ['hoy. \\', 'there()'],
            0,
            True,
        ),
    )
    yield (
        30,
        (
            ['hello(', '    there', ')'],
            0,
            True,
        ),
    )
    yield (
        35,
        (
            ['\'\'\'', '\'\'\''],
            0,
            True,
        )
    )
    yield (
        40,
        (
            ['\'its me\''],
            0,
            True,
        )
    )
    yield (
        45,
        (
            ['koishi = (', '    {', ')'],
            0,
            False,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_expression_lines(line_index):
    """
    Tests whether ``get_expression_lines`` works as intended.
    
    Parameters
    ----------
    line_index : `int`
        The line's index to start parsing at.
    
    Returns
    -------
    output : `list<str>`
    """
    with LineCacheSession():
        return get_expression_lines(__file__, line_index)
