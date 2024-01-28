import vampytest

from ..helpers_familiarity import _iter_split_name_to_words


def _iter_options():
    yield 'koishi_bot_69', ['koishi', 'bot', '69']
    yield 'koishi_bot69', ['koishi', 'bot', '69']
    yield 'KoishiBot69', ['Koishi', 'Bot', '69']
    yield 'KOISHI_BOT_69', ['KOISHI', 'BOT', '69']
    yield 'koishiBot69', ['koishi', 'Bot', '69']


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_split_name_to_words(input_value):
    """
    Tests whether ``_iter_split_name_to_words`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        The name to split.
    
    Returns
    -------
    output : `list<str>`
    """
    output = [*_iter_split_name_to_words(input_value)]
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
