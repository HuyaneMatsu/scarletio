import vampytest

from ..content_type import ContentTypeParsingError


def _assert_fields_set(content_type):
    """
    Asserts whether every fields of the content-type parsing error are set.
    
    Parameters
    ----------
    content_type : ``ContentTypeParsingError``
        The content-type parsing error to test.
    """
    vampytest.assert_instance(content_type, ContentTypeParsingError)
    vampytest.assert_instance(content_type.expected, str)
    vampytest.assert_instance(content_type.index, int)
    vampytest.assert_instance(content_type.string, str)


def test__ContentTypeParsingError__new():
    """
    Tests whether ``ContentTypeParsingError.__new__`` works as intended.
    """
    string = 'koishi'
    index = 4
    expected = ';.'
    
    content_type = ContentTypeParsingError(
        string,
        index,
        expected,
    )
    _assert_fields_set(content_type)
    
    vampytest.assert_eq(content_type.string, string)
    vampytest.assert_eq(content_type.index, index)
    vampytest.assert_eq(content_type.expected, expected)


def test__ContentTypeParsingError__repr():
    """
    Tests whether ``ContentTypeParsingError.__repr__`` works as intended.
    """
    string = 'koishi'
    index = 4
    expected = ';.'
    
    content_type = ContentTypeParsingError(
        string,
        index,
        expected,
    )
    
    output = repr(content_type)
    
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(content_type).__name__, output)
    vampytest.assert_in(f'string = {string!r}', output)
    vampytest.assert_in(f'index = {index!r}', output)
    vampytest.assert_in(f'expected = {expected!r}', output)


def _iter_options__eq():
    string = 'koishi'
    index = 4
    expected = ';.'
    
    keyword_expected = {
        'string': string,
        'index': index,
        'expected': expected,
    }
    
    yield (
        keyword_expected,
        keyword_expected,
        True,
    )
    
    yield (
        keyword_expected,
        {
            **keyword_expected,
            'string': 'satori',
        },
        False,
    )
    
    yield (
        keyword_expected,
        {
            **keyword_expected,
            'index': 2,
        },
        False,
    )
    
    yield (
        keyword_expected,
        {
            **keyword_expected,
            'expected': '-',
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ContentTypeParsingError__eq(keyword_expected_0, keyword_expected_1):
    """
    Tests whether ``ContentTypeParsingError.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_expected_0 : `dict<str, object>`
        Keyword expected to create instance with.
    
    keyword_expected_1 : `dict<str, object>`
        Keyword expected to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    instance_0 = ContentTypeParsingError(**keyword_expected_0)
    instance_1 = ContentTypeParsingError(**keyword_expected_1)
    
    output = instance_0 == instance_1
    vampytest.assert_instance(output, bool)
    return output
