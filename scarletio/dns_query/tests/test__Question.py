import vampytest

from ..constants import (
    CLASS_CODE_CHAOS, CLASS_CODE_INTERNET, RESOURCE_RECORD_TYPE_AUTHORITATIVE_NAME_SERVER,
    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
)
from ..question import Question


def _assert_fields_set(question):
    """
    Asserts whether every fields are set of the given question.
    
    Parameters
    ----------
    question : ``Question``
        The instance to check.
    """
    vampytest.assert_instance(question, Question)
    vampytest.assert_instance(question.class_code, int)
    vampytest.assert_instance(question.labels, tuple, nullable = True)
    vampytest.assert_instance(question.resource_record_type, int)


def test__Question__new():
    """
    Tests whether ``Question.__new__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    
    question = Question(
        labels,
        class_code,
        resource_record_type,
    )
    _assert_fields_set(question)
    
    vampytest.assert_eq(question.class_code, class_code)
    vampytest.assert_eq(question.labels, labels)
    vampytest.assert_eq(question.resource_record_type, resource_record_type)


def test__Question__repr():
    """
    Tests whether ``Question.__repr__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    
    question = Question(
        labels,
        class_code,
        resource_record_type,
    )
    output = repr(question)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    
    keyword_parameters = {
        'labels': labels,
        'class_code': class_code,
        'resource_record_type': resource_record_type,
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
            'class_code': CLASS_CODE_CHAOS,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'resource_record_type': RESOURCE_RECORD_TYPE_AUTHORITATIVE_NAME_SERVER,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Question__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Question.__eq__`` works as intended.
    
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
    question_0 = Question(**keyword_parameters_0)
    question_1 = Question(**keyword_parameters_1)
    
    output = question_0 == question_1
    vampytest.assert_instance(output, bool)
    return output


def test__Question__hash():
    """
    Tests whether ``Question.__hash__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    
    question = Question(
        labels,
        class_code,
        resource_record_type,
    )
    output = hash(question)
    vampytest.assert_instance(output, int)
