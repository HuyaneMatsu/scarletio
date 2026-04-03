import vampytest

from ..constants import IP_TYPE_IP_V4, IP_TYPE_IP_V6
from ..resolve_configuration import SortListElement


def _assert_fields_set(sort_list_element):
    """
    Asserts whether the given instance has all of its fields set.
    
    Parameters
    ----------
    sort_list_element : ``SortListElement``
        The instance to check.
    """
    vampytest.assert_instance(sort_list_element, SortListElement)
    vampytest.assert_instance(sort_list_element.ip_mask, int)
    vampytest.assert_instance(sort_list_element.ip_type, int)
    vampytest.assert_instance(sort_list_element.ip_value, int)


def test__SortListElement__new():
    """
    Tests whether ``SortListElement.__new__`` works as intended.
    """
    ip_type = IP_TYPE_IP_V4
    ip_value = 56
    ip_mask = 12
    
    sort_list_element = SortListElement(
        ip_type,
        ip_value,
        ip_mask,
    )
    
    _assert_fields_set(sort_list_element)
    
    vampytest.assert_eq(sort_list_element.ip_type, ip_type)
    vampytest.assert_eq(sort_list_element.ip_value, ip_value)
    vampytest.assert_eq(sort_list_element.ip_mask, ip_mask)


def test__SortListElement__repr():
    """
    Tests whether ``SortListElement.__repr__`` works as intended.
    """
    ip_type = IP_TYPE_IP_V4
    ip_value = 56
    ip_mask = 12
    
    sort_list_element = SortListElement(
        ip_type,
        ip_value,
        ip_mask,
    )
    
    output = repr(sort_list_element)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    ip_type = IP_TYPE_IP_V4
    ip_value = 56
    ip_mask = 12
    
    keyword_parameters = {
        'ip_type': ip_type,
        'ip_value': ip_value,
        'ip_mask': ip_mask,
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
            'ip_type': IP_TYPE_IP_V6,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ip_value': 0,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ip_mask': 0,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__SortListElement__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``SortListElement.__eq__`` works as intended.
    
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
    sort_list_element_0 = SortListElement(**keyword_parameters_0)
    sort_list_element_1 = SortListElement(**keyword_parameters_1)
    
    output = sort_list_element_0 == sort_list_element_1
    vampytest.assert_instance(output, bool)
    return output
