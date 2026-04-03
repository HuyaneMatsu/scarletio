import vampytest

from ..constants import CLASS_CODE_INTERNET, RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
from ..resource_record import ResourceRecord
from ..query import Query
from ..question import Question


def _assert_fields_set(query):
    """
    Asserts whether the given query has all of its fields set.
    
    Parameters
    ----------
    query : ``Query``
        The instance to check.
    """
    vampytest.assert_instance(query, Query)
    vampytest.assert_instance(query.additional_resource_records, tuple, nullable = True)
    vampytest.assert_instance(query.data_verification_desired, bool)
    vampytest.assert_instance(query.questions, tuple, nullable = True)
    vampytest.assert_instance(query.recursion_desired, bool)
    vampytest.assert_instance(query.transaction_id, int)


def test__Query__new():
    """
    Tests whether ``Query.__new__`` works as intended.
    """
    transaction_id = 56
    recursion_desired = True
    data_verification_desired = False
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
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
    
    query = Query(
        transaction_id,
        recursion_desired,
        data_verification_desired,
        questions,
        additional_resource_records,
    )
    _assert_fields_set(query)
    vampytest.assert_eq(query.transaction_id, transaction_id)
    vampytest.assert_eq(query.recursion_desired, recursion_desired)
    vampytest.assert_eq(query.data_verification_desired, data_verification_desired)
    vampytest.assert_eq(query.questions, questions)
    vampytest.assert_eq(query.additional_resource_records, additional_resource_records)


def test__Query__repr():
    """
    Tests whether ``Query.__repr__`` works as intended.
    """
    transaction_id = 56
    recursion_desired = True
    data_verification_desired = False
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
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
    
    query = Query(
        transaction_id,
        recursion_desired,
        data_verification_desired,
        questions,
        additional_resource_records,
    )
    
    output = repr(query)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    transaction_id = 56
    recursion_desired = True
    data_verification_desired = False
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
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
        'recursion_desired': recursion_desired,
        'data_verification_desired': data_verification_desired,
        'questions': questions,
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
            'transaction_id': 12,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'recursion_desired': False,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'data_verification_desired': True,
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
            'additional_resource_records': None,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Query__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Query.__eq__`` works as intended.
    
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
    query_0 = Query(**keyword_parameters_0)
    query_1 = Query(**keyword_parameters_1)
    
    output = query_0 == query_1
    vampytest.assert_instance(output, bool)
    return output


def test__Query__hash():
    """
    Tests whether ``Query.__hash__`` works as intended.
    """
    transaction_id = 56
    recursion_desired = True
    data_verification_desired = False
    questions = (
        Question(
            (b'komeiji', b'koishi'),
            CLASS_CODE_INTERNET,
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
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
    
    query = Query(
        transaction_id,
        recursion_desired,
        data_verification_desired,
        questions,
        additional_resource_records,
    )
    
    output = hash(query)
    vampytest.assert_instance(output, int)
