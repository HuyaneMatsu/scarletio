import vampytest

from ..display_state import CONTINUOUS_LINE_POSTFIX, _get_line_line_count_reduced


def _iter_options():
    # 0 length
    # MIAU 
    # 5 - 1
    # to 10 -> 9
    # MIAU
    # should return 1 line still
    yield 0, 10, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 1
    
    # 1 length
    # MIAU h
    # 5 - 1
    #      ^
    #      1
    # to 10 -> 9
    # MIAU h
    # should return 1 line still
    yield 1, 10, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 1
    
    
    # n length
    # MIAU hey miste
    # 5 - 1
    #      ^^^^^^^^^
    #      9
    # to 10 -> 9
    # MIAU hey miste
    # should return 1 line still
    yield 9, 10, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 1
    
    # n + 1 length
    # MIA hey mister
    # ^^^^
    # 5 - 1
    #     ^^^^^^^^^^
    #     10
    #               ^
    #               1?
    # to 10 -> 9
    # MIAU hey mister
    # ^^^^
    # add new prefix in calculation
    # should be 2
    yield 10, 10, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 1
    
    # n + 2 length
    # MIA hey mister\
    # ^^^^
    # 5 - 1
    #     ^^^^^^^^^^
    #     10
    #               ^
    #               1?
    # MIAU h
    # ^^^^
    # 5 - 1
    #      ^
    #      1
    #  
    # to 10 -> 9
    # MIAU hey mister
    # MIAU h
    # add new prefix in calculation
    # should be 3
    yield 11, 10, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 3
    
    # n + 1 length
    # MIA hey mister hey mis
    # ^^^^
    # 5 - 1
    #     ^^^^^^^^^^^^^^^^^^
    #     18
    #                       ^
    #                       1?
    # to 30 -> 9
    # MIAU hey mister
    #  hey mis
    # add new prefix in calculation
    # should be 2
    yield 18, 30, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 2
    
    # n + 1 length
    # MIA hey mister hey mist
    # ^^^^
    # 5 - 1
    #     ^^^^^^^^^^^^^^^^^^^
    #     19
    #                        ^
    #                        1?
    # to 30 -> 9
    # MIAU hey mister
    #  hey mister
    # ^^^^
    # add new prefix in calculation
    # should be 3
    yield 19, 30, 9, 5 - len(CONTINUOUS_LINE_POSTFIX), 2


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_line_line_count_reduced(line_length, content_width, new_content_width, prefix_length):
    """
    Tests whether ``_get_line_line_count_reduced`` works as intended.
    
    Parameters
    ----------
    line_length : `int`
        The line's length.
    content_width : `int`
        The content field's width.
    
    Returns
    -------
    output : `int`
    """
    output = _get_line_line_count_reduced(line_length, content_width, new_content_width, prefix_length)
    
    vampytest.assert_instance(output, int)
    
    return output
