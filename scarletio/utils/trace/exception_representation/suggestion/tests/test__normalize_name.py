import vampytest

from ..helpers_familiarity import _normalize_name


def _iter_options():
    yield 'koishi_bot_69'
    yield 'koishi_bot69'
    yield 'KoishiBot69'
    yield 'KOISHI_BOT_69'
    yield 'koishiBot69'


@vampytest._(vampytest.call_from(_iter_options()).returning('koishi_bot_69'))
def test__normalize_name(input_value):
    """
    Tests whether ``_normalize_name`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        The name to split.
    
    Returns
    -------
    output : `str`
    """
    output = _normalize_name(input_value)
    vampytest.assert_instance(output, str)
    return output
