import vampytest

from ..response_parsing_error import ResponseParsingError


def _assert_fields_set(response_parsing_error):
    """
    Asserts whether every fields are set of the given response parsing error.
    
    Parameters
    ----------
    response_parsing_error : ``ResponseParsingError``
        Response parsing error.
    """
    vampytest.assert_instance(response_parsing_error, ResponseParsingError)
    vampytest.assert_instance(response_parsing_error.args, tuple)
    vampytest.assert_instance(response_parsing_error.characters_written, int)
    vampytest.assert_instance(response_parsing_error.filename, str, nullable = True)
    vampytest.assert_instance(response_parsing_error.filename2, str, nullable = True)
    vampytest.assert_instance(response_parsing_error.errno, int, nullable = True)
    vampytest.assert_instance(response_parsing_error.parsing_error_code, int)
    vampytest.assert_instance(response_parsing_error.parsing_error_response_data, bytes)
    vampytest.assert_instance(response_parsing_error.parsing_error_metadata, tuple)
    vampytest.assert_instance(response_parsing_error.strerror, str, nullable = True)


def test__ResponseParsingError__new():
    """
    Tests whether ``ResponseParsingError.__new__`` works as intended..
    """
    parsing_error_code = 1
    parsing_error_response_data = b''
    parsing_error_metadata = (0, 13)
    
    response_parsing_error = ResponseParsingError(
        parsing_error_code,
        parsing_error_response_data,
        parsing_error_metadata,
    )
    _assert_fields_set(response_parsing_error)
    
    vampytest.assert_eq(response_parsing_error.parsing_error_code, parsing_error_code)
    vampytest.assert_eq(response_parsing_error.parsing_error_response_data, parsing_error_response_data)
    vampytest.assert_eq(response_parsing_error.parsing_error_metadata, parsing_error_metadata)


def test__ResponseParsingError__repr():
    """
    Tests whether ``ResponseParsingError.__repr__`` works as intended..
    """
    parsing_error_code = 1
    parsing_error_response_data = b''
    parsing_error_metadata = (0, 13)
    
    response_parsing_error = ResponseParsingError(
        parsing_error_code,
        parsing_error_response_data,
        parsing_error_metadata,
    )
    
    output = repr(response_parsing_error)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    parsing_error_code = 1
    parsing_error_response_data = b''
    parsing_error_metadata = (0, 13)
    
    keyword_parameters = {
        'parsing_error_code': parsing_error_code,
        'parsing_error_response_data': parsing_error_response_data,
        'parsing_error_metadata': parsing_error_metadata,
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
            'parsing_error_code': 2,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'parsing_error_response_data': b'a',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'parsing_error_metadata': (0, 14),
        },
        False,
    )
    

@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ResponseParsingError__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``ResponseParsingError.__eq__`` works as intended.
    
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
    response_parsing_error_0 = ResponseParsingError(**keyword_parameters_0)
    response_parsing_error_1 = ResponseParsingError(**keyword_parameters_1)
    
    output = response_parsing_error_0 == response_parsing_error_1
    vampytest.assert_instance(output, bool)
    return output
