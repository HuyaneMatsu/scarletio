import vampytest

from ..cause_group import CauseGroup


def test__CauseGroup__new__none():
    """
    Tests whether ``CauseGroup.__new__`` works as intended.
    
    Case: no exceptions given.
    """
    output = CauseGroup()
    
    vampytest.assert_is(output, None)


def test__CauseGroup__new__single():
    """
    Tests whether ``CauseGroup.__new__`` works as intended.
    
    Case: single exception given.
    """
    exception_0 = ValueError(12)
    output = CauseGroup(exception_0)
    
    vampytest.assert_is(output, exception_0)


def test__CauseGroup__new__multiple():
    """
    Tests whether ``CauseGroup.__new__`` works as intended.
    
    Case: multiple exception given.
    """
    exception_0 = ValueError(12)
    exception_1 = ValueError(13)
    
    output = CauseGroup(exception_0, exception_1)
    
    vampytest.assert_instance(output, CauseGroup)
    vampytest.assert_instance(output.causes, tuple)
    vampytest.assert_eq(len(output.causes), 2)
    vampytest.assert_eq(output.causes, (exception_0, exception_1))


def test__CauseGroup__new__multiple_type():
    """
    Tests whether ``CauseGroup.__new__`` works as intended.
    
    Case: multiple exception given, one is a type.
    """
    exception_0 = ValueError
    exception_1 = ValueError(13)
    
    output = CauseGroup(exception_0, exception_1)
    
    vampytest.assert_instance(output, CauseGroup)
    vampytest.assert_instance(output.causes, tuple)
    vampytest.assert_eq(len(output.causes), 2)
    vampytest.assert_instance(output.causes[0], exception_0)
    vampytest.assert_eq(output.causes[1], exception_1)


def test__CauseGroup__new__multiple_error():
    """
    Tests whether ``CauseGroup.__new__`` works as intended.
    
    Case: multiple exception given, invalid type given.
    """
    exception_0 = object
    exception_1 = ValueError(13)
    
    with vampytest.assert_raises(TypeError):
        CauseGroup(exception_0, exception_1)


def test__CauseGroup__iter():
    """
    Tests whether ``CauseGroup.__iter__`` works as intended.
    """
    exception_0 = ValueError(12)
    exception_1 = ValueError(13)
    
    cause_group = CauseGroup(exception_0, exception_1)
    output = [*cause_group]
    vampytest.assert_eq(output, [exception_0, exception_1])


def test__CauseGroup__len():
    """
    Tests whether ``CauseGroup.__len__`` works as intended.
    """
    exception_0 = ValueError(12)
    exception_1 = ValueError(13)
    
    cause_group = CauseGroup(exception_0, exception_1)
    output = len(cause_group)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, 2)


def test__CauseGroup__eq():
    """
    Tests whether ``CauseGroup.__eq__`` works as intended.
    """
    exception_0 = ValueError(12)
    exception_1 = ValueError(13)
    exception_2 = ValueError(14)
    
    cause_group_0 = CauseGroup(exception_0, exception_1)
    cause_group_1 = CauseGroup(exception_0, exception_1)
    cause_group_2 = CauseGroup(exception_2, exception_1)
    
    vampytest.assert_eq(cause_group_0, cause_group_1)
    vampytest.assert_ne(cause_group_0, cause_group_2)


def test__CauseGroup__repr():
    """
    Tests whether ``CauseGroup.__repr__`` works as intended.
    """
    exception_0 = ValueError(12)
    exception_1 = ValueError(13)
    
    cause_group = CauseGroup(exception_0, exception_1)
    
    output = repr(cause_group)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in(type(cause_group).__name__, output)
    vampytest.assert_in(repr(exception_0), output)
    vampytest.assert_in(repr(exception_1), output)
