from ..weak_map import WeakMap

from .weak_helpers import WeakReferencable

import vampytest


# Test WeakMap

# Test constructor

def test__WeakMap__constructor():
    weak_map = WeakMap()
    vampytest.assert_eq(len(weak_map), 0)
    vampytest.assert_eq(sorted(weak_map), [])


def test__WeakMap__constructor_empty():
    weak_map = WeakMap([])
    vampytest.assert_eq(len(weak_map), 0)
    vampytest.assert_eq(sorted(weak_map), [])


def test__WeakMap__constructor_filled():
    objects_ = [WeakReferencable(x) for x in range(3)]

    weak_map = WeakMap(objects_)
    vampytest.assert_eq(len(weak_map), len(objects_))
    vampytest.assert_eq(sorted(weak_map), objects_)


# Test magic methods


def test__WeakMap__contains():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(10)
    object_3 = 62
    
    weak_map = WeakMap(objects_1)
    
    vampytest.assert_in(object_1, weak_map)
    vampytest.assert_not_in(object_2, weak_map)
    vampytest.assert_not_in(object_3, weak_map)


def test__WeakMap__delitem():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    object_1 = objects_1[0]
    object_2 = WeakReferencable(6)
    
    weak_map = WeakMap(objects_1)
    
    del weak_map[object_1]
    vampytest.assert_eq(len(weak_map), 2)
    
    with vampytest.assert_raises(KeyError):
        del weak_map[object_2]
    
    vampytest.assert_eq(len(weak_map), 2)


def test__WeakMap__eq():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    vampytest.assert_eq(weak_map_1, weak_map_1)
    vampytest.assert_eq(weak_map_1, weak_map_2, reverse = True)
    vampytest.assert_eq(weak_map_1, weak_map_3, reverse = True)
    
    vampytest.assert_eq(weak_map_1, objects_1)
    vampytest.assert_eq(weak_map_1, objects_2, reverse = True)
    vampytest.assert_eq(weak_map_1, objects_3, reverse = True)

    vampytest.assert_is(weak_map_1.__eq__(1), NotImplemented)


def test__WeakMap__getitem():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(6)
    
    object_3 = WeakReferencable(2)
    object_3_expected = objects_1[2]
    
    weak_map = WeakMap(objects_1)
    
    vampytest.assert_eq(weak_map[object_1], object_1_expected)
    
    with vampytest.assert_raises(KeyError):
        weak_map[object_2]
    
    vampytest.assert_eq(weak_map[object_3], object_3_expected)


def test__WeakMap__iter():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    
    vampytest.assert_eq(sorted(weak_map_1), objects_1)
    vampytest.assert_eq(sorted(weak_map_2), objects_2)


def test__WeakMap__len():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    
    vampytest.assert_eq(len(weak_map_1), len(objects_1))
    vampytest.assert_eq(len(weak_map_2), len(objects_2))


def test__WeakMap__ne():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    vampytest.assert_ne(weak_map_1, weak_map_1, reverse = True)
    vampytest.assert_ne(weak_map_1, weak_map_2)
    vampytest.assert_ne(weak_map_1, weak_map_3)
    
    vampytest.assert_ne(weak_map_1, objects_1, reverse = True)
    vampytest.assert_ne(weak_map_1, objects_2)
    vampytest.assert_ne(weak_map_1, objects_3)
    
    vampytest.assert_is(weak_map_1.__ne__(1), NotImplemented)


# Test Methods


def test__WeakMap__clear():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map = WeakMap(objects_1)
    
    weak_map_empty = WeakMap()
    
    weak_map.clear()
    
    vampytest.assert_eq(len(weak_map), 0)
    vampytest.assert_eq(weak_map, weak_map_empty)


def test__WeakMap__copy():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    weak_map_empty = WeakMap()
    
    test_case = weak_map_1.copy()
    
    vampytest.assert_is_not(weak_map_1, test_case)
    vampytest.assert_eq(weak_map_1, test_case)
    
    test_case = weak_map_empty.copy()
    
    vampytest.assert_is_not(weak_map_empty, test_case)
    vampytest.assert_eq(weak_map_empty, test_case)


def test__WeakMap__get():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    
    object_4 = 7
    
    vampytest.assert_is(weak_map_1.get(object_1), object_1_expected)
    vampytest.assert_is(weak_map_1.get(object_2), object_2_expected)
    vampytest.assert_is(weak_map_1.get(object_3), None)
    vampytest.assert_is(weak_map_1.get(object_4), None)


def test__WeakMap__pop():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    
    object_4 = 8
    
    vampytest.assert_is(weak_map_1.pop(object_1), object_1_expected)
    vampytest.assert_eq(len(weak_map_1), 2)
    
    vampytest.assert_is(weak_map_1.pop(object_2), object_2_expected)
    vampytest.assert_eq(len(weak_map_1), 1)
    
    
    with vampytest.assert_raises(KeyError):
        weak_map_1.pop(object_3)
    vampytest.assert_eq(len(weak_map_1), 1)

    vampytest.assert_is(weak_map_1.pop(object_3, None), None)
    vampytest.assert_eq(len(weak_map_1), 1)
    
    
    vampytest.assert_is(weak_map_1.pop(object_4, None), None)
    vampytest.assert_eq(len(weak_map_1), 1)

    with vampytest.assert_raises(KeyError):
        weak_map_1.pop(object_4)
    vampytest.assert_eq(len(weak_map_1), 1)


def test__WeakMap__set():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    object_3_expected = object_3
    
    object_4 = 7
    
    vampytest.assert_is(weak_map_1.set(object_1), object_1_expected)
    vampytest.assert_eq(len(weak_map_1), 3)
    
    vampytest.assert_is(weak_map_1.set(object_2), object_2_expected)
    vampytest.assert_eq(len(weak_map_1), 3)
    
    vampytest.assert_is(weak_map_1.set(object_3), object_3_expected)
    vampytest.assert_eq(len(weak_map_1), 4)
    
    with vampytest.assert_raises(TypeError):
        weak_map_1.set(object_4)
    vampytest.assert_eq(len(weak_map_1), 4)


def test__WeakMap__ior():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_1)
    vampytest.assert_eq(test_case, weak_map_1)
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_2)
    vampytest.assert_eq(test_case, weak_map_1)
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_3)
    vampytest.assert_eq(test_case, objects_3)
    

    test_case = weak_map_1.copy()
    test_case.update(objects_1)
    vampytest.assert_eq(test_case, weak_map_1)
    
    test_case = weak_map_1.copy()
    test_case.update(objects_2)
    vampytest.assert_eq(test_case, weak_map_1)
    
    test_case = weak_map_1.copy()
    test_case.update(objects_3)
    vampytest.assert_eq(test_case, objects_3)
    
    
    test_case = WeakMap()
    with vampytest.assert_raises(TypeError):
        test_case.update([1, ])
    
    with vampytest.assert_raises(TypeError):
        test_case.update(1)
