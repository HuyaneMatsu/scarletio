import vampytest

from ..rich_type import AttributeError, RichType


class TestType(metaclass = RichType, rich_type_feature_flags = ~0):
    __slots__ = ('nyan',)


def test__RichType__eq():
    a = object.__new__(TestType)
    a.nyan = 5
    
    b = object.__new__(TestType)
    b.nyan = 5
    
    c = object.__new__(TestType)
    c.nyan = 7
    
    vampytest.assert_eq(a, b)
    vampytest.assert_ne(a, c)


def test__RichType__repr():
    a = object.__new__(TestType)
    a.nyan = 5
    
    vampytest.assert_eq(
        repr(a),
        ''.join(['<', TestType.__name__, ' nyan = ', repr(5), '>']),
    )


def test__RichType__hash():
    a = object.__new__(TestType)
    a.nyan = 5
    
    vampytest.assert_instance(
        hash(a),
        int
    )


def test__RichType__getattr():
    a = object.__new__(TestType)
    a.nyan = 5
    
    try:
        a.wan
    except AttributeError as exception:
        vampytest.assert_eq(exception.instance, a)
        vampytest.assert_eq(exception.attribute_name, 'wan')
