import vampytest

from ..repeat_strategies import get_repeat_with_strategy_bot, get_repeat_with_strategy_top


class R(str):
    __mod__ = str.__eq__
    
    def __getitem__(self, index_or_slice):
        return type(self)(str.__getitem__(self, index_or_slice))


def iter_options():
    # no input
    yield get_repeat_with_strategy_bot, None, None
    yield get_repeat_with_strategy_top, None, None
    # 1x2 but short
    yield get_repeat_with_strategy_bot, R('caad'), None
    yield get_repeat_with_strategy_top, R('caad'), None
    # No repeat
    yield get_repeat_with_strategy_bot, R('abcd'), None
    yield get_repeat_with_strategy_top, R('abcd'), None
    # 1x4 in middle
    yield get_repeat_with_strategy_bot, R('abccccab'), (2, 1, 4)
    yield get_repeat_with_strategy_top, R('abccccab'), (2, 1, 4)
    # 2x2 in middle
    yield get_repeat_with_strategy_bot, R('abcdcdab'), (2, 2, 2)
    yield get_repeat_with_strategy_top, R('abcdcdab'), (2, 2, 2)
    # 3x2 at start
    yield get_repeat_with_strategy_bot, R('abcabcd'), (0, 3, 2)
    yield get_repeat_with_strategy_top, R('abcabcd'), (0, 3, 2)
    # 3x2 at end
    yield get_repeat_with_strategy_bot, R('dabcabc'), (1, 3, 2)
    yield get_repeat_with_strategy_top, R('dabcabc'), (1, 3, 2)
    # 2x2 but alignment matters
    yield get_repeat_with_strategy_bot, R('ayaya'), (1, 2, 2)
    yield get_repeat_with_strategy_top, R('ayaya'), (0, 2, 2)


@vampytest._(vampytest.call_from(iter_options()).returning_last())
def test__get_repeat(strategy, input_value):
    """
    Tests whether ``get_repeat_with_strategy_bot`` works as intended.
    
    Parameters
    ----------
    strategy : `FunctionType`
        Strategy to get repeat with.
    input_value : ``R``
        Value to get repeat on.
    
    Returns
    -------
    output : `None | (int, int, int)`
    """
    return strategy(input_value)
