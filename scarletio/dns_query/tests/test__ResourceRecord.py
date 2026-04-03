import vampytest

from ..constants import (
    CLASS_CODE_CHAOS, CLASS_CODE_INTERNET, RESOURCE_RECORD_TYPE_AUTHORITATIVE_NAME_SERVER,
    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
)
from ..resource_record import ResourceRecord


def _assert_fields_set(resource_record):
    """
    Asserts whether every fields are set of the given resource record.
    
    Parameters
    ----------
    resource_record : ``ResourceRecord``
        The instance to check.
    """
    vampytest.assert_instance(resource_record, ResourceRecord)
    vampytest.assert_instance(resource_record.class_code, int)
    vampytest.assert_instance(resource_record.labels, tuple, nullable = True)
    vampytest.assert_instance(resource_record.resource_record_type, int)
    vampytest.assert_instance(resource_record.validity_duration, int)
    vampytest.assert_instance(resource_record.data, bytes, nullable = True)


def test__ResourceRecord__new():
    """
    Tests whether ``ResourceRecord.__new__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    validity_duration = 123
    data = b'abcd'
    
    resource_record = ResourceRecord(
        labels,
        class_code,
        resource_record_type,
        validity_duration,
        data,
    )
    _assert_fields_set(resource_record)
    
    vampytest.assert_eq(resource_record.class_code, class_code)
    vampytest.assert_eq(resource_record.labels, labels)
    vampytest.assert_eq(resource_record.resource_record_type, resource_record_type)
    vampytest.assert_eq(resource_record.validity_duration, validity_duration)
    vampytest.assert_eq(resource_record.data, data)


def test__ResourceRecord__repr():
    """
    Tests whether ``ResourceRecord.__repr__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    validity_duration = 123
    data = b'abcd'
    
    resource_record = ResourceRecord(
        labels,
        class_code,
        resource_record_type,
        validity_duration,
        data,
    )
    output = repr(resource_record)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    validity_duration = 123
    data = b'abcd'
    
    keyword_parameters = {
        'labels': labels,
        'class_code': class_code,
        'resource_record_type': resource_record_type,
        'validity_duration': validity_duration,
        'data': data,
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
            'labels': None,
        },
        False,
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
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'validity_duration': 122222,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'data': None,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ResourceRecord__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``ResourceRecord.__eq__`` works as intended.
    
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
    resource_record_0 = ResourceRecord(**keyword_parameters_0)
    resource_record_1 = ResourceRecord(**keyword_parameters_1)
    
    output = resource_record_0 == resource_record_1
    vampytest.assert_instance(output, bool)
    return output


def test__ResourceRecord__hash():
    """
    Tests whether ``ResourceRecord.__hash__`` works as intended.
    """
    labels = (b'komeiji', b'koishi')
    class_code = CLASS_CODE_INTERNET
    resource_record_type = RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
    validity_duration = 123
    data = b'abcd'
    
    resource_record = ResourceRecord(
        labels,
        class_code,
        resource_record_type,
        validity_duration,
        data,
    )
    output = hash(resource_record)
    vampytest.assert_instance(output, int)
