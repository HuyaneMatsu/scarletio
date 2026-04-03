import vampytest

from ..constants import (
    CLASS_CODE_INTERNET, RESOURCE_RECORD_TYPE_IP_V4_ADDRESS, RESPONSE_CODE_FORMAT_ERROR, RESPONSE_CODE_OK
)
from ..resource_record import ResourceRecord
from ..result import Result
from ..question import Question


def _assert_fields_set(result):
    """
    Asserts whether the given result has all of its fields set.
    
    Parameters
    ----------
    result : ``Result``
        The instance to check.
    """
    vampytest.assert_instance(result, Result)
    vampytest.assert_instance(result.additional_resource_records, tuple, nullable = True)
    vampytest.assert_instance(result.answers, tuple, nullable = True)
    vampytest.assert_instance(result.authority_resource_records, tuple, nullable = True)
    vampytest.assert_instance(result.data_verified, bool)
    vampytest.assert_instance(result.questions, tuple, nullable = True)
    vampytest.assert_instance(result.recursion_available, bool)
    vampytest.assert_instance(result.response_code, int)
    vampytest.assert_instance(result.transaction_id, int)
    vampytest.assert_instance(result.truncated, bool)


def test__Result__new():
    """
    Tests whether ``Result.__new__`` works as intended.
    """
    transaction_id = 56
    data_verified = False
    truncated = False
    recursion_available = True
    response_code = RESPONSE_CODE_OK
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
        ),
    )
    
    answers = (
        ResourceRecord(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'abcd',
        ),
    )
    
    authority_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'nyan',
        ),
    )
    
    additional_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'ner',
        ),
    )
    
    result = Result(
        transaction_id,
        data_verified,
        truncated,
        recursion_available,
        response_code,
        questions,
        answers,
        authority_resource_records,
        additional_resource_records,
    )
    _assert_fields_set(result)
    vampytest.assert_eq(result.transaction_id, transaction_id)
    vampytest.assert_eq(result.data_verified, data_verified)
    vampytest.assert_eq(result.truncated, truncated)
    vampytest.assert_eq(result.recursion_available, recursion_available)
    vampytest.assert_eq(result.recursion_available, recursion_available)
    vampytest.assert_eq(result.questions, questions)
    vampytest.assert_eq(result.answers, answers)
    vampytest.assert_eq(result.authority_resource_records, authority_resource_records)
    vampytest.assert_eq(result.additional_resource_records, additional_resource_records)


def test__Result__repr():
    """
    Tests whether ``Result.__repr__`` works as intended.
    """
    transaction_id = 56
    data_verified = False
    truncated = False
    recursion_available = True
    response_code = RESPONSE_CODE_OK
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
        ),
    )
    
    answers = (
        ResourceRecord(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'abcd',
        ),
    )
    
    authority_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'nyan',
        ),
    )
    
    additional_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'ner',
        ),
    )
    
    result = Result(
        transaction_id,
        data_verified,
        truncated,
        recursion_available,
        response_code,
        questions,
        answers,
        authority_resource_records,
        additional_resource_records,
    )
    
    output = repr(result)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    transaction_id = 56
    data_verified = False
    truncated = False
    recursion_available = True
    response_code = RESPONSE_CODE_OK
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
        ),
    )
    
    answers = (
        ResourceRecord(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'abcd',
        ),
    )
    
    authority_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'nyan',
        ),
    )
    
    additional_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'ner',
        ),
    )
    
    keyword_parameters = {
        'transaction_id': transaction_id,
        'data_verified': data_verified,
        'truncated': truncated,
        'recursion_available': recursion_available,
        'response_code': response_code,
        'questions': questions,
        'answers': answers,
        'authority_resource_records': authority_resource_records,
        'additional_resource_records': additional_resource_records,
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
            'transaction_id': 133,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'data_verified': True,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'truncated': True,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'recursion_available': False,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'response_code': RESPONSE_CODE_FORMAT_ERROR,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'questions': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'answers': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'authority_resource_records': None,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'additional_resource_records': None,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Result__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Result.__eq__`` works as intended.
    
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
    result_0 = Result(**keyword_parameters_0)
    result_1 = Result(**keyword_parameters_1)
    
    output = result_0 == result_1
    vampytest.assert_instance(output, bool)
    return output


def test__Result__hash():
    """
    Tests whether ``Result.__hash__`` works as intended.
    """
    transaction_id = 56
    data_verified = False
    truncated = False
    recursion_available = True
    response_code = RESPONSE_CODE_OK
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
        ),
    )
    
    answers = (
        ResourceRecord(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'abcd',
        ),
    )
    
    authority_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'nyan',
        ),
    )
    
    additional_resource_records = (
        ResourceRecord(
            None,
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
            123,
            b'ner',
        ),
    )
    
    result = Result(
        transaction_id,
        data_verified,
        truncated,
        recursion_available,
        response_code,
        questions,
        answers,
        authority_resource_records,
        additional_resource_records,
    )
    
    output = hash(result)
    vampytest.assert_instance(output, int)
