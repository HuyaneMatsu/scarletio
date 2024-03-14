from io import IOBase

import vampytest

from ...utils import IgnoreCaseMultiValueDictionary, MultiValueDictionary

from ..form_data import FormData


class TestType(IOBase):
    __slots__ = ('name',)
    
    def __new__(cls, name):
        self = IOBase.__new__(cls)
        self.name = name
        return self


def _assert_fields_set(form_data):
    """
    Asserts whether every fields of the form_data are set.
    
    Parameters
    ----------
    form_data : ``FormData``
        The form_data to test.
    """
    vampytest.assert_instance(form_data, FormData)
    vampytest.assert_instance(form_data.fields, list)
    vampytest.assert_instance(form_data.multipart, bool)
    vampytest.assert_instance(form_data.quote_fields, bool)


def test__FormData__new():
    """
    Tests whether ``FormData.__new__`` works as intended.
    """
    quote_fields = False
    
    form_data = FormData(quote_fields)
    _assert_fields_set(form_data)
    vampytest.assert_eq(form_data.quote_fields, quote_fields)


def _iter_options__add_field__passing():
    instance_0 = TestType('koishi')
    
    yield (
        'hey',
        b'mister',
        {},
        (
            [
                (
                    MultiValueDictionary([('name', 'hey'), ('file_name', 'hey')]),
                    IgnoreCaseMultiValueDictionary(),
                    b'mister',
                ),
            ],
            True,
        )
    )
    
    yield (
        'hey',
        instance_0,
        {},
        (
            [
                (
                    MultiValueDictionary([('name', 'hey'), ('file_name', 'koishi')]),
                    IgnoreCaseMultiValueDictionary(),
                    instance_0,
                ),
            ],
            True,
        )
    )
    
    yield (
        'hey',
        b'mister',
        {'transfer_encoding': 'application/octet-stream'},
        (
            [
                (
                    MultiValueDictionary([('name', 'hey')]),
                    IgnoreCaseMultiValueDictionary([('Content-Transfer-Encoding', 'application/octet-stream')]),
                    b'mister',
                ),
            ],
            True,
        )
    )
    
    yield (
        'hey',
        'mister',
        {},
        (
            [
                (
                    MultiValueDictionary([('name', 'hey')]),
                    IgnoreCaseMultiValueDictionary(),
                    'mister',
                ),
            ],
            False,
        )
    )
    
    yield (
        'hey',
        b'mister',
        {'content_type': 'text/plain', 'file_name': 'satori', 'transfer_encoding': 'application/octet-stream'},
        (
            [
                (
                    MultiValueDictionary([('name', 'hey'), ('file_name', 'satori')]),
                    IgnoreCaseMultiValueDictionary([
                        ('Content-Type', 'text/plain'),
                        ('Content-Transfer-Encoding', 'application/octet-stream'),
                    ]),
                    b'mister',
                ),
            ],
            True,
        )
    )


def _iter_options__type_error__passing():
    yield 'hey', b'mister', {'file_name': 1}
    yield 'hey', b'mister', {'content_type': 1}
    yield 'hey', b'mister', {'transfer_encoding': 1}


@vampytest._(vampytest.call_from(_iter_options__add_field__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__type_error__passing()).raising(TypeError))
def test__FormData__add_field(name, value, keyword_parameters):
    """
    Tests whether ``FormData.add_fields`` work as intended.
    
    Parameters
    ----------
    name : `str`
        The field's name.
    value : `object`
        The field's value.
    keyword_parameters : `dict<str, object>`
        Additional keyword parameters
    """
    form_data = FormData()
    form_data.add_field(name, value, **keyword_parameters)
    return form_data.fields, form_data.multipart


def test__FormData__eq__empty():
    """
    Tests whether ``FormData.__eq__`` works as intended.
    
    Case: Empty.
    """
    form_data_0 = FormData()
    form_data_1 = FormData()
    vampytest.assert_eq(form_data_0, form_data_1)


def test__FormData__eq__filled():
    """
    Tests whether ``FormData.__eq__`` works as intended.
    
    Case: Filled
    """
    form_data_0 = FormData()
    form_data_0.add_field('hey', b'mister')
    form_data_1 = FormData()
    form_data_1.add_field('hey', b'mister')
    vampytest.assert_eq(form_data_0, form_data_1)


def test__FormData__eq__different_type():
    """
    Tests whether ``FormData.__eq__`` works as intended.
    
    Case: Empty.
    """
    form_data_0 = FormData()
    vampytest.assert_ne(form_data_0, object())


def test__FormData__eq__different():
    """
    Tests whether ``FormData.__eq__`` works as intended.
    
    Case: Empty.
    """
    form_data_0 = FormData()
    form_data_0.add_field('hey', b'mister')
    form_data_1 = FormData()
    form_data_1.add_field('hey', 'mister')
    vampytest.assert_ne(form_data_0, form_data_1)


def test__FormData__repr():
    """
    Tests whether ``FormData.__repr__`` works as intended
    """
    form_data = FormData()
    form_data.add_field('hey', b'mister')
    
    output = repr(form_data)
    
    vampytest.assert_instance(output, str)
    vampytest.assert_in(' fields = ', output)
    vampytest.assert_in(' multipart = ', output)
    vampytest.assert_in(' quote_fields = ', output)


@vampytest.skip()
def test__FormData__generate_form_data():
    """
    Tests whether ``FormData._generate_form_data`` works as intended
    """
    raise NotImplementedError('Payload writes must become testable first.')


@vampytest.skip()
def test__FormData__generate_form_urlencoded():
    """
    Tests whether ``FormData._generate_form_urlencoded`` works as intended
    """
    raise NotImplementedError('Payload writes must become testable first.')


@vampytest.skip()
def test__FormData__generate_form():
    """
    Tests whether ``FormData.generate_form`` works as intended
    """
    raise NotImplementedError('Payload writes must become testable first.')
