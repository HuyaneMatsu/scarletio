import vampytest

from ..expression_info import get_expression_area, get_surround_area
from ..line_cache_session import LineCacheSession





def dummy_0000():
    hello



def dummy_0001():
    koishi = (
        1,
        2,
        3,
        4,
        5,
        6,
    )

def dummy_0003():
    koishi = (
        1,
        2,
        3,
        4,
        5,
        6,
    ), 0, (
        1,
        2,
        3,
        4,
        5,
        6,
    )





def dummy_0004():
    try:
        raise ValueError('pudding')
    except ValueError as exception:
        return exception




def _iter_options():
    yield (
        'expression, single line',
        10,
        (
            8,
            12,
            32,
            45,
        ),
    )
    
    yield (
        'long expression, parse downwards, shall not surround from downwards',
        15,
        (
            13,
            22,
            45,
            87,
        ),
    )
    
    yield (
        'long expression, parse upwards, shall not surround from upwards',
        22,
        (
            15,
            24,
            53,
            95,
        ),
    )
    
    yield (
        'long expression, parse both ways, shall not surround from any side',
        32,
        (
            25,
            39,
            95,
            162,
        ),
    )
    
    yield (
        'start at the start of the file, shall not surround upwards',
        0,
        (
            0,
            2,
            0,
            18,
        ),
    )
    
    yield (
        'start at the end of the file, shall not surround downwards',
        205,
        (
            203,
            205,
            839,
            842,
        ),
    )
    
    yield (
        'above end by 1 line',
        204,
        (
            202,
            205,
            838,
            842,
        ),
    )
    
    yield (
        'full line expression',
        47,
        (
            45,
            49,
            167,
            203,
        ),
    )



@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__get_surround_area(line_index):
    """
    Tests whether ``get_surround_area`` works as intended.
    
    Parameters
    ----------
    line_index : `int`
        The line's index to start parsing at.
    
    Returns
    -------
    output : `(int, int, int, int)`
    """
    with LineCacheSession():
        (
            file_info,
            expression_line_start_index,
            expression_line_end_index,
            expression_character_start_index,
            expression_character_end_index,
            expression_token_start_index,
            expression_token_end_index,
        ) = get_expression_area(__file__, line_index)
    
    output = get_surround_area(
        file_info.parse_result.tokens,
        line_index,
        expression_line_start_index,
        expression_line_end_index,
        expression_token_start_index,
        expression_token_end_index,
    )
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 4)
    
    (
        surround_line_start_index,
        surround_line_end_index,
        surround_token_start_index,
        surround_token_end_index,
    ) = output
    
    vampytest.assert_instance(surround_line_start_index, int)
    vampytest.assert_instance(surround_line_end_index, int)
    vampytest.assert_instance(surround_token_start_index, int)
    vampytest.assert_instance(surround_token_end_index, int)
    
    return (
        surround_line_start_index,
        surround_line_end_index,
        surround_token_start_index,
        surround_token_end_index,
    )




# marker
