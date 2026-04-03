import vampytest

from ...utils import MultiValueDictionary

from ..content_type import ContentType


def _assert_fields_set(content_type):
    """
    Asserts whether every fields of the content-type are set.
    
    Parameters
    ----------
    content_type : ``ContentType``
        The content-type to test.
    """
    vampytest.assert_instance(content_type, ContentType)
    vampytest.assert_instance(content_type.parameters, MultiValueDictionary, nullable = True)
    vampytest.assert_instance(content_type.sub_type, str, nullable = True)
    vampytest.assert_instance(content_type.suffix, str, nullable = True)
    vampytest.assert_instance(content_type.type, str, nullable = True)


def test__ContentType__new():
    """
    Tests whether ``ContentType.__new__`` works as intended.
    """
    type_ = 'koishi'
    sub_type = 'okuu'
    suffix = 'bird'
    parameters = MultiValueDictionary((
        ('bird', 'brain'),
        ('fishing', 'rod'),
    ))
    
    content_type = ContentType(
        type_,
        sub_type,
        suffix,
        parameters,
    )
    _assert_fields_set(content_type)
    
    vampytest.assert_eq(content_type.type, type_)
    vampytest.assert_eq(content_type.sub_type, sub_type)
    vampytest.assert_eq(content_type.suffix, suffix)
    vampytest.assert_eq(content_type.parameters, parameters)


def test__ContentType__create_empty():
    """
    Tests whether ``ContentType.create_empty`` works as intended.
    """
    content_type = ContentType.create_empty()
    _assert_fields_set(content_type)


def test__ContentType__repr():
    """
    Tests whether ``ContentType.__repr__`` works as intended.
    """
    type_ = 'koishi'
    sub_type = 'okuu'
    suffix = 'bird'
    parameters = MultiValueDictionary((
        ('bird', 'brain'),
        ('fishing', 'rod'),
    ))
    
    content_type = ContentType(
        type_,
        sub_type,
        suffix,
        parameters,
    )
    
    output = repr(content_type)
    
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(content_type).__name__, output)
    vampytest.assert_in(f'type = {type_!r}', output)
    vampytest.assert_in(f'sub_type = {sub_type!r}', output)
    vampytest.assert_in(f'suffix = {suffix!r}', output)
    vampytest.assert_in(f'parameters = {parameters!r}', output)


def _iter_options__eq():
    type_ = 'koishi'
    sub_type = 'okuu'
    suffix = 'bird'
    parameters = MultiValueDictionary((
        ('bird', 'brain'),
        ('fishing', 'rod'),
    ))
    
    keyword_parameters = {
        'type_': type_,
        'sub_type': sub_type,
        'suffix': suffix,
        'parameters': parameters,
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
            'type_': 'satori',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'sub_type': 'orin',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'suffix': 'miau',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'parameters': MultiValueDictionary((
                ('miau', 'nyan'),
                ('i', 'see you'),
            )),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ContentType__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``ContentType.__eq__`` works as intended.
    
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
    instance_0 = ContentType(**keyword_parameters_0)
    instance_1 = ContentType(**keyword_parameters_1)
    
    output = instance_0 == instance_1
    vampytest.assert_instance(output, bool)
    return output
