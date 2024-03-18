import vampytest

from ...utils import IgnoreCaseMultiValueDictionary, MultiValueDictionary, to_json

from ..form_data import FORM_DATA_FIELD_TYPE_JSON, FORM_DATA_FIELD_TYPE_NONE, FormDataField
from ..headers import CONTENT_LENGTH, CONTENT_TRANSFER_ENCODING, CONTENT_TYPE


def _assert_fields_set(form_data_field):
    """
    Asserts whether every fields are set of the given form data field.
    
    Parameters
    ----------
    form_data_field : ``FormDataField``
    """
    vampytest.assert_instance(form_data_field, FormDataField)
    vampytest.assert_instance(form_data_field.type, int)
    vampytest.assert_instance(form_data_field.type_options, MultiValueDictionary)
    vampytest.assert_instance(form_data_field.headers, IgnoreCaseMultiValueDictionary)
    vampytest.assert_instance(form_data_field.value, object)


def test__FormDataField__new():
    """
    Tests whether ``FormDataField.__new__`` works as intended.
    """
    field_type = FORM_DATA_FIELD_TYPE_NONE
    type_options = MultiValueDictionary([('name', 'mister')])
    headers = IgnoreCaseMultiValueDictionary([('Content-Transfer-Encoding', 'application/octet-stream')])
    value = b'mister'
    
    form_data_field = FormDataField(field_type, type_options, headers, value)
    _assert_fields_set(form_data_field)
    
    vampytest.assert_eq(form_data_field.type, field_type)
    vampytest.assert_eq(form_data_field.type_options, type_options)
    vampytest.assert_eq(form_data_field.headers, headers)
    vampytest.assert_eq(form_data_field.value, value)



def _iter_options__get_value():
    yield FORM_DATA_FIELD_TYPE_NONE, b'mister', b'mister'
    yield FORM_DATA_FIELD_TYPE_JSON, {'hey': 'mister'}, to_json({'hey': 'mister'})


@vampytest._(vampytest.call_from(_iter_options__get_value()).returning_last())
def test__FormDataField__get_value(field_type, value):
    """
    Tests whether ``FormDataField.get_value`` works as intended.
    
    Parameters
    ----------
    field_type : `int`
        The field's type.
    value : `object`
        The field's value.
    
    Returns
    -------
    output : `object`
    """
    form_data_field = FormDataField(field_type, MultiValueDictionary(), IgnoreCaseMultiValueDictionary(), value)
    return form_data_field.get_value()


def test__FormDataField__repr():
    """
    Tests whether ``FormDataField.__repr__`` works as intended.
    """
    field_type = FORM_DATA_FIELD_TYPE_JSON
    type_options = MultiValueDictionary([('name', 'mister')])
    headers = IgnoreCaseMultiValueDictionary([('Content-Transfer-Encoding', 'application/octet-stream')])
    value = {'hey': 'mister'}
    
    form_data_field = FormDataField(field_type, type_options, headers, value)
    
    output = repr(form_data_field)
    
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(form_data_field).__name__, output)
    vampytest.assert_in('type = json', output)
    vampytest.assert_in('headers = ', output)
    vampytest.assert_in('type_options = ', output)
    vampytest.assert_in('value = ', output)


def _iter_options__eq__same_type():
    keyword_parameters = {
        'field_type': FORM_DATA_FIELD_TYPE_NONE,
        'type_options': MultiValueDictionary([('name', 'mister')]),
        'headers': IgnoreCaseMultiValueDictionary([('Content-Transfer-Encoding', 'application/octet-stream')]),
        'value': 'mister',
    }
    
    yield keyword_parameters, keyword_parameters, True
    yield keyword_parameters, {**keyword_parameters, 'field_type': FORM_DATA_FIELD_TYPE_JSON}, False
    yield keyword_parameters, {**keyword_parameters, 'type_options': MultiValueDictionary()}, False
    yield keyword_parameters, {**keyword_parameters, 'headers': IgnoreCaseMultiValueDictionary()}, False
    yield keyword_parameters, {**keyword_parameters, 'value': 'hey'}, False


@vampytest._(vampytest.call_from(_iter_options__eq__same_type()).returning_last())
def test__FormDataField__eq__same_type(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormDataField.__eq__`` works as intended.
    
    Case: same type.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool˙
    """
    form_data_field_0 = FormDataField(**keyword_parameters_0)
    form_data_field_1 = FormDataField(**keyword_parameters_1)
    
    output = form_data_field_0 == form_data_field_1
    vampytest.assert_instance(output, bool)
    return output
    

def test__FormDataField__eq__different_type():
    """
    Tests whether ``FormDataField.__eq__`` works as intended.
    
    Case: different type.
    """
    field_type = FORM_DATA_FIELD_TYPE_NONE
    type_options = MultiValueDictionary()
    headers = IgnoreCaseMultiValueDictionary()
    value = b'mister'
    
    form_data_field = FormDataField(field_type, type_options, headers, value)
    
    output = form_data_field == object()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
