import vampytest

from ..constants import URL_PART_FLAG_DECODED_SET, URL_PART_FLAG_ENCODED_SET
from ..url_part_base_parsed import URLPartBaseParsed


def _assert_fields_set(part):
    """
    Asserts whether every fields are set of the given part.
    
    Parameters
    ----------
    part : ``URLPartBaseParsed``
        The part to check.
    """
    vampytest.assert_instance(part._decoded, str, nullable = True)
    vampytest.assert_instance(part._encoded, str, nullable = True)
    vampytest.assert_instance(part._flags, int)
    vampytest.assert_instance(part.parsed, object, nullable = True)


def test__URLPartBaseParsed__new():
    """
    Tests whether ``URLPartBaseParsed.__new__`` works as intended.
    """
    with vampytest.assert_raises(RuntimeError):
        URLPartBaseParsed()


def _iter_options__eq():
    decoded = 'koishi '
    encoded = 'koishi%20'
    parsed = 'koishi '
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        True,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        True,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        True,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        decoded,
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        decoded,
        True,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        parsed,
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        'satori',
        False,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        None,
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        None,
        True,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        None,
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        None,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__URLPartBaseParsed__eq(constructor_0, parameter_0, constructor_1, parameter_1):
    """
    Tests whether ``URLPartBaseParsed.__eq__`` works as intended.
    
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
    part_0 = constructor_0(URLPartBaseParsed, parameter_0)
    part_1 = constructor_1(URLPartBaseParsed, parameter_1)
    output = part_0 == part_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__parse():
    yield None, False, None
    yield None, True, None
    yield 'koishi%20', False, 'koishi%20'
    yield 'koishi%20', True, 'koishi '


@vampytest._(vampytest.call_from(_iter_options__parse()).returning_last())
def test__URLPartBaseParsed__parse(value, encoded):
    """
    Tests whether ``URLPartBaseParsed._parse`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to parse.
    
    encoded : `bool`
        Whether we are parsing an encoded value.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPartBaseParsed._parse(value, encoded)
    vampytest.assert_instance(output, object, nullable = True)
    return output


def _iter_options__serialize():
    yield None, False, None
    yield None, True, None
    yield 'koishi ', False, 'koishi '
    yield 'koishi ', True, 'koishi%20'


@vampytest._(vampytest.call_from(_iter_options__serialize()).returning_last())
def test__URLPartBaseParsed__serialize(value, encoded):
    """
    Tests whether ``URLPartBaseParsed._serialize`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to serialize.
    
    encoded : `bool`
        Whether an encoded value is requested.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPartBaseParsed._serialize(value, encoded)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def test__URLPartBaseParsed__create_from_decoded():
    """
    Tests whether ``URLPartBaseParsed.create_from_decoded`` works as intended.
    """
    decoded = 'koishi '
    
    part = URLPartBaseParsed.create_from_decoded(decoded)
    _assert_fields_set(part)
    vampytest.assert_eq(part.parsed, decoded)
    

def test__URLPartBaseParsed__create_from_encoded():
    """
    Tests whether ``URLPartBaseParsed.create_from_encoded`` works as intended.
    """
    encoded = 'koishi%20'
    decoded = 'koishi '
    
    part = URLPartBaseParsed.create_from_encoded(encoded)
    _assert_fields_set(part)
    vampytest.assert_eq(part.parsed, decoded)


def test__URLPartBaseParsed__create_from_parsed():
    """
    Tests whether ``URLPartBaseParsed.create_from_parsed`` works as intended.
    """
    parsed = 'koishi'
    
    part = URLPartBaseParsed.create_from_parsed(parsed)
    _assert_fields_set(part)
    vampytest.assert_eq(part.parsed, parsed)


def _iter_options__decoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    parsed = 'koishi '
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        decoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        decoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        parsed,
        decoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__decoded()).returning_last())
def test__URLPartBaseParsed__decoded(constructor, parameter):
    """
    Tests whether ``URLPartBaseParsed.decoded`` works as intended.
    
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
    part =  constructor(URLPartBaseParsed, parameter)
    
    output = part.decoded
    
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(part._decoded, output)
    vampytest.assert_true(part._flags & URL_PART_FLAG_DECODED_SET)
    return output


def _iter_options__encoded():
    decoded = 'koishi '
    encoded = 'koishi%20'
    parsed = 'koishi '
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        encoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        encoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        parsed,
        encoded,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__encoded()).returning_last())
def test__URLPartBaseParsed__encoded(constructor, parameter):
    """
    Tests whether ``URLPartBaseParsed.encoded`` works as intended.
    
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
    part =  constructor(URLPartBaseParsed, parameter)
    
    output = part.encoded
    
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(part._encoded, output)
    vampytest.assert_true(part._flags & URL_PART_FLAG_ENCODED_SET)
    return output




def _iter_options__parsed():
    decoded = 'koishi '
    encoded = 'koishi%20'
    parsed = 'koishi '
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        decoded,
        parsed,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        encoded,
        parsed,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        parsed,
        parsed,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_decoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_encoded'].__func__,
        None,
        None,
    )
    
    yield (
        URLPartBaseParsed.__dict__['create_from_parsed'].__func__,
        None,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options__parsed()).returning_last())
def test__URLPartBaseParsed__parsed(constructor, parameter):
    """
    Tests whether ``URLPartBaseParsed.parsed`` works as intended.
    
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
    part =  constructor(URLPartBaseParsed, parameter)
    
    output = part.parsed
    
    vampytest.assert_instance(output, str, nullable = True)
    vampytest.assert_eq(part.parsed, output)
    return output
