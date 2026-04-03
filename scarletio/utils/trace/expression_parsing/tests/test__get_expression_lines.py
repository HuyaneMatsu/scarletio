import vampytest

from ..line_cache_session import LineCacheSession
from ..expression_info import get_expression_area





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



def _iter_options():
    yield (
        10,
        (
            __file__,
            10,
            10,
            141,
            151,
            37,
            40,
        ),
    )
    yield (
        15,
        (
            __file__,
            14,
            15,
            171,
            197,
            49,
            62,
        ),
    )
    yield (
        20,
        (
            __file__,
            20,
            20,
            218,
            235,
            72,
            78,
        ),
    )
    yield (
        25,
        (
            __file__,
            25,
            25,
            256,
            267,
            88,
            94,
        ),
    )
    yield (
        30,
        (
            __file__,
            30,
            32,
            299,
            330,
            108,
            118,
        ),
    )
    yield (
        35,
        (
            __file__,
            34,
            35,
            348,
            364,
            125,
            131,
        )
    )
    yield (
        40,
        (
            __file__,
            40,
            40,
            385,
            398,
            141,
            146,
        )
    )
    yield (
        45,
        (
            __file__,
            45,
            47,
            419,
            451,
            156,
            170,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
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
    return (output[0].file_name, output[1], output[2], output[3], output[4], output[5], output[6])
