import vampytest

from ..constants import URL_PART_FLAG_DECODED_SET, URL_PART_FLAG_ENCODED_SET
from ..url_part_base import URLPartBase


def _assert_fields_set(part):
    """
    Asserts whether every fields are set of the given part.
    
    Parameters
    ----------
    part : ``URLPartBase``
        The part to check.
    """
    vampytest.assert_instance(part._decoded, str, nullable = True)
    vampytest.assert_instance(part._encoded, str, nullable = True)
    vampytest.assert_instance(part._flags, int)


def test__URLPartBase__new():
    """
    Tests whether ``URLPartBase.__new__`` works as intended.
    """
    with vampytest.assert_raises(RuntimeError):
        URLPartBase()


def test__URLPartBase__repr():
    """
    Tests whether ``URLPartBase.__new__`` works as intended.
    """
    decoded = 'koishi'
    
    part = URLPartBase.create_from_decoded(decoded)
    
    output = repr(part)
    
    vampytest.assert_in(type(part).__name__, output)
    vampytest.assert_in(f'decoded = {decoded!r}', output)


def _iter_options__eq():
    decoded = 'koishi'
    encoded = 'koishi'
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        URLPartBase.__dict__['create_from_encoded'].__func__,
        encoded,
        True,
    )
    
    yield (
        URLPartBase.__dict__['create_from_encoded'].__func__,
        encoded,
        URLPartBase.__dict__['create_from_encoded'].__func__,
        encoded,
        True,
    )
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        True,
    )
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        URLPartBase.__dict__['create_from_decoded'].__func__,
        'satori',
        False,
    )
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        None,
        URLPartBase.__dict__['create_from_encoded'].__func__,
        None,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__URLPartBase__eq(constructor_0, parameter_0, constructor_1, parameter_1):
    """
    Tests whether ``URLPartBase.__eq__`` works as intended.
    
    Parameters
    ----------
    constructor_0 : `FunctionType`
        Constructor to call.
    
    parameter_0 : `object`
        Parameter to call the constructor with.
    
    constructor_1 : `FunctionType`
        Constructor to call.
    
    parameter_1 : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `bool`
    """
    part_0 = constructor_0(URLPartBase, parameter_0)
    part_1 = constructor_1(URLPartBase, parameter_1)
    output = part_0 == part_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__encode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'koishi ', 'koishi%20'


@vampytest._(vampytest.call_from(_iter_options__encode()).returning_last())
def test__URLPartBase__encode(value):
    """
    Tests whether ``URLPartBase._encode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to encode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPartBase._encode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__decode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'koishi%20', 'koishi '


@vampytest._(vampytest.call_from(_iter_options__decode()).returning_last())
def test__URLPartBase__decode(value):
    """
    Tests whether ``URLPartBase._decode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to decode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPartBase._decode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def test__URLPartBase__create_from_decoded():
    """
    Tests whether ``URLPartBase.create_from_decoded`` works as intended.
    """
    decoded = 'koishi'
    
    part = URLPartBase.create_from_decoded(decoded)
    _assert_fields_set(part)
    vampytest.assert_eq(part._decoded, decoded)
    vampytest.assert_eq(part._flags, URL_PART_FLAG_DECODED_SET)
    

def test__URLPartBase__create_from_encoded():
    """
    Tests whether ``URLPartBase.create_from_encoded`` works as intended.
    """
    encoded = 'koishi'
    
    part = URLPartBase.create_from_encoded(encoded)
    _assert_fields_set(part)
    vampytest.assert_eq(part._encoded, encoded)
    vampytest.assert_eq(part._flags, URL_PART_FLAG_ENCODED_SET)


def _iter_options__decoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        decoded,
    )
    
    yield (
        URLPartBase.__dict__['create_from_encoded'].__func__,
        encoded,
        decoded,
    )
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBase.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLPartBase__decoded(constructor, parameter):
    """
    Tests whether ``URLPartBase.decoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    part =  constructor(URLPartBase, parameter)
    
    output = part.decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(part._decoded, output)
    vampytest.assert_true(part._flags & URL_PART_FLAG_DECODED_SET)
    return output


def _iter_options__encoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        decoded,
        encoded,
    )
    
    yield (
        URLPartBase.__dict__['create_from_encoded'].__func__,
        encoded,
        encoded,
    )
    
    yield (
        URLPartBase.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBase.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLPartBase__encoded(constructor, parameter):
    """
    Tests whether ``URLPartBase.encoded`` works as intended.
    
    Parameters
    ----------
    constructor : `FunctionType`
        Constructor to call.
    
    parameter : `object`
        Parameter to call the constructor with.
    
    Returns
    -------
    output : `None | str`
    """
    part =  constructor(URLPartBase, parameter)
    
    output = part.encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(part._encoded, output)
    vampytest.assert_true(part._flags & URL_PART_FLAG_ENCODED_SET)
    return output
