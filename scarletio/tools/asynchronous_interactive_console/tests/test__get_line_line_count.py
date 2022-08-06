import vampytest

from ..editor_advanced import get_line_line_count


def test__get_line_line_count__1():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 100; old: 100, new: 50
    """
    count = get_line_line_count(100, 100, 50, 7)
    vampytest.assert_eq(count, 2)


def test__get_line_line_count__2():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 200; old: 10, new: 50
    """
    count = get_line_line_count(200, 100, 50, 7)
    vampytest.assert_eq(count, 4)


def test__get_line_line_count__3():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 190; old: 100, new: 70
    """
    count = get_line_line_count(180, 100, 70, 7)
    vampytest.assert_eq(count, 4)


def test__get_line_line_count__4():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 199; old: 100, new: 70
    """
    count = get_line_line_count(199, 100, 70, 7)
    vampytest.assert_eq(count, 4)


def test__get_line_line_count__5():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 180; old: 100, new: 70
    """
    count = get_line_line_count(198, 100, 70, 7)
    vampytest.assert_eq(count, 4)


def test__get_line_line_count__6():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 150; old: 100, new: 70
    """
    count = get_line_line_count(150, 100, 70, 7)
    vampytest.assert_eq(count, 3)


def test__get_line_line_count__7():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 170; old: 100, new: 70
    """
    count = get_line_line_count(170, 100, 70, 7)
    vampytest.assert_eq(count, 3)


def test__get_line_line_count__8():
    """
    Tests whether ``get_line_line_count`` returns correct value when lines are pushed in.
    
    Case: length: 171; old: 100, new: 70
    """
    count = get_line_line_count(172, 100, 70, 7)
    vampytest.assert_eq(count, 4)
