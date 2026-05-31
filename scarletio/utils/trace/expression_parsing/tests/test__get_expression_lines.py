import vampytest

from ..expression_info import get_expression_area
from ..file_info import FileInfo
from ..line_cache_session import LineCacheSession




def dummy_0000():
    hello


def dummy_0001():
    mister = (
    'hey')



def dummy_0002():
    hello(there)



def dummy_0003():
    hoy. \
    there()


def dummy_0004():
    hello(
        there
    )
def dummy_0005():
    '''
    '''



def dummy_0006():
    'its me'



def dummy_0007():
    koishi = (
        {
    })

def dummy_0008():
    try:
        raise ValueError('pudding')
    except ValueError as exception:
        return exception


def _iter_options():
    yield (
        'expression, single line',
        10,
        (
            __file__,
            10,
            10,
            173,
            183,
            46,
            49,
        ),
    )
    
    yield (
        'multi line with brace, upwards',
        15,
        (
            __file__,
            14,
            15,
            203,
            229,
            58,
            71,
        ),
    )
    
    yield (
        'function call with braces, single line',
        20,
        (
            __file__,
            20,
            20,
            250,
            267,
            81,
            87,
        ),
    )
    
    yield (
        'expression, line broke (breaking currently ignored',
        25,
        (
            __file__,
            25,
            25,
            288,
            299,
            97,
            103,
        ),
    )
    
    yield (
        'expression with brace, multi line',
        30,
        (
            __file__,
            30,
            32,
            331,
            362,
            117,
            127,
        ),
    )
    
    yield (
        'triple quite string, multi line, extend downwards',
        35,
        (
            __file__,
            34,
            35,
            380,
            396,
            134,
            140,
        )
    )
    
    yield (
        'single quote string, single line',
        40,
        (
            __file__,
            40,
            40,
            417,
            430,
            150,
            155,
        )
    )
    
    yield (
        'assignation with braces, multi line',
        45,
        (
            __file__,
            45,
            47,
            451,
            483,
            165,
            179,
        ),
    )
    
    yield (
        'full line length expression',
        51,
        (
            __file__,
            51,
            51,
            511,
            547,
            191,
            201,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__get_expression_area(line_index):
    """
    Tests whether ``get_expression_area`` works as intended.
    
    Parameters
    ----------
    line_index : `int`
        The line's index to start parsing at.
    
    Returns
    -------
    output : `(str, int, int, int, int, int, int)`
    """
    with LineCacheSession():
        output = get_expression_area(__file__, line_index)
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 7)
    
    (
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
    ) = output
    
    vampytest.assert_instance(file_info, FileInfo)
    vampytest.assert_instance(expression_line_start_index, int)
    vampytest.assert_instance(expression_line_end_index, int)
    vampytest.assert_instance(expression_character_start_index, int)
    vampytest.assert_instance(expression_character_end_index, int)
    vampytest.assert_instance(expression_token_start_index, int)
    vampytest.assert_instance(expression_token_end_index, int)
    
    return (
        file_info.file_name,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
    )
