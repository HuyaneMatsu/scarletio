import vampytest

from ..location import Location


def _assert_fields_set(location):
    """
    Asserts whether every fields of the given location are correctly set.
    """
    vampytest.assert_instance(location, Location)
    vampytest.assert_instance(location.content_character_index, int)
    vampytest.assert_instance(location.length, int)
    vampytest.assert_instance(location.line_character_index, int)
    vampytest.assert_instance(location.line_index, int)


def test__Location__new():
    """
    Tests whether ``Location.__new__`` works as intended.
    """
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    location = Location(
        content_character_index,
        line_index,
        line_character_index,
        length,
    )
    
    _assert_fields_set(location)
    
    vampytest.assert_eq(location.content_character_index, content_character_index)
    vampytest.assert_eq(location.length, length)
    vampytest.assert_eq(location.line_character_index, line_character_index)
    vampytest.assert_eq(location.line_index, line_index)


def test__Location__repr():
    """
    Tests whether ``Location.__repr__`` works as intended.
    """
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    location = Location(
        content_character_index,
        line_index,
        line_character_index,
        length,
    )
    
    output = repr(location)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    content_character_index = 2
    line_index = 1
    line_character_index = 1
    length = 6
    
    keyword_parameters = {
        'content_character_index': content_character_index,
        'line_index': line_index,
        'line_character_index': line_character_index,
        'length': length,
    }
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'content_character_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'line_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'line_character_index': 10,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'length': 10,
        },
        False,
    )



@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Location__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Location.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    location_0 = Location(**keyword_parameters_0)
    location_1 = Location(**keyword_parameters_1)
    
    output = location_0 == location_1
    vampytest.assert_instance(output, bool)
    return output
