from ..weak_set import WeakSet

from .weak_helpers import WeakReferencable

import vampytest


# Test WeakSet

# Test constructor

def test__WeakSet__constructor():
    weak_set = WeakSet()
    vampytest.assert_eq(len(weak_set), 0)
    vampytest.assert_eq(sorted(weak_set), [])


def test__WeakSet__constructor_empty():
    weak_set = WeakSet([])
    vampytest.assert_eq(len(weak_set), 0)
    vampytest.assert_eq(sorted(weak_set), [])


def test__WeakSet__constructor_filled():
    objects_ = [WeakReferencable(x) for x in range(3)]

    weak_set = WeakSet(objects_)
    vampytest.assert_eq(len(weak_set), len(objects_))
    vampytest.assert_eq(sorted(weak_set), objects_)

# Test magic methods

def test__WeakSet__and():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy() & weak_set_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() & weak_set_2
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy() & weak_set_3
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = weak_set_1.copy() & objects_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() & objects_2
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy() & objects_3
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = WeakSet()
    
    vampytest.assert_is(test_case.__and__(1), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    intersection = test_case.__and__([1])
    vampytest.assert_is_not(intersection, NotImplemented)
    vampytest.assert_eq(len(intersection), 0)


def test__WeakSet__contains():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(10)
    object_3 = 62
    
    weak_set = WeakSet(objects_1)
    
    vampytest.assert_in(object_1, weak_set)
    vampytest.assert_not_in(object_2, weak_set)
    vampytest.assert_not_in(object_3, weak_set)


def test__WeakSet__eq():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    vampytest.assert_eq(weak_set_1, weak_set_1)
    vampytest.assert_eq(weak_set_1, weak_set_2, reverse = True)
    vampytest.assert_eq(weak_set_1, weak_set_3, reverse = True)
    
    vampytest.assert_eq(weak_set_1, objects_1)
    vampytest.assert_eq(weak_set_1, objects_2, reverse = True)
    vampytest.assert_eq(weak_set_1, objects_3, reverse = True)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__eq__(1), NotImplemented)
    vampytest.assert_eq(test_case.__eq__([1]), False)


def test__WeakSet__ge():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert weak_set_1 >= weak_set_1
    assert weak_set_1 >= weak_set_2
    assert not (weak_set_1 >= weak_set_3)
    
    assert weak_set_1 >= objects_1
    assert weak_set_1 >= objects_2
    assert not (weak_set_1 >= objects_3)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__ge__(1), NotImplemented)
    vampytest.assert_eq(test_case.__ge__([1]), False)


def test__WeakSet__gt():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert not (weak_set_1 > weak_set_1)
    assert weak_set_1 > weak_set_2
    assert not (weak_set_1 > weak_set_3)
    
    assert not (weak_set_1 > objects_1)
    assert weak_set_1 > objects_2
    assert not (weak_set_1 > objects_3)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__gt__(1), NotImplemented)
    vampytest.assert_eq(test_case.__gt__([1]), False)


def test__WeakSet__iand():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [WeakReferencable(1), 1]
    objects_5 = [WeakReferencable(1), {}]
    
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case &= weak_set_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case &= weak_set_2
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy()
    test_case &= weak_set_3
    vampytest.assert_eq(test_case, weak_set_1)
    

    test_case = weak_set_1.copy()
    test_case &= objects_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case &= objects_2
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy()
    test_case &= objects_3
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__iand__(1), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__iand__([1]), test_case)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__iand__(objects_4), test_case)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__iand__(objects_5), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__ior():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [WeakReferencable(1), 1]
    objects_5 = [WeakReferencable(1), {}]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case |= weak_set_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case |= weak_set_2
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case |= weak_set_3
    vampytest.assert_eq(test_case, objects_3)
    

    test_case = weak_set_1.copy()
    test_case |= objects_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case |= objects_2
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case |= objects_3
    vampytest.assert_eq(test_case, objects_3)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__ior__(1), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__ior__([1]), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)

    vampytest.assert_is(test_case.__ior__(objects_4), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__ior__(objects_5), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__isub():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    weak_set_1_2_sub = WeakSet(set(objects_1) - set(objects_2))
    
    
    test_case = weak_set_1.copy()
    test_case -= weak_set_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case -= weak_set_2
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy()
    test_case -= weak_set_3
    vampytest.assert_eq(test_case, weak_set_empty)
    

    test_case = weak_set_1.copy()
    test_case -= objects_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case -= objects_2
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy()
    test_case -= objects_3
    vampytest.assert_eq(test_case, weak_set_empty)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__isub__(1), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    vampytest.assert_is(test_case.__isub__([1]), test_case)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__iter():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    
    vampytest.assert_eq(sorted(weak_set_1), objects_1)
    vampytest.assert_eq(sorted(weak_set_2), objects_2)


def test__WeakSet__ixor():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(1), 1]
    objects_4 = [WeakReferencable(1), {}]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = WeakSet(set(objects_1) ^ set(objects_2))
    
    
    test_case = weak_set_1.copy()
    test_case ^= weak_set_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case ^= weak_set_2
    vampytest.assert_eq(test_case, objects_1_2_xor)
    

    test_case = weak_set_1.copy()
    test_case ^= objects_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case ^= objects_2
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__ixor__(1), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__ixor__([1]), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)

    vampytest.assert_is(test_case.__ior__(objects_3), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)
    
    vampytest.assert_is(test_case.__ior__(objects_4), NotImplemented)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__le():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert weak_set_1 <= weak_set_1
    assert not (weak_set_1 <= weak_set_2)
    assert weak_set_1 <= weak_set_3
    
    assert weak_set_1 <= objects_1
    assert not (weak_set_1 <= objects_2)
    assert weak_set_1 <= objects_3
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__le__(1), NotImplemented)
    vampytest.assert_eq(test_case.__le__([1]), True)


def test__WeakSet__len():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    
    vampytest.assert_eq(len(weak_set_1), len(objects_1))
    vampytest.assert_eq(len(weak_set_2), len(objects_2))


def test__WeakSet__lt():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert not (weak_set_1 < weak_set_1)
    assert not (weak_set_1 < weak_set_2)
    assert weak_set_1 < weak_set_3
    
    assert not (weak_set_1 < objects_1)
    assert not (weak_set_1 < objects_2)
    assert weak_set_1 < objects_3
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__lt__(1), NotImplemented)
    vampytest.assert_eq(test_case.__lt__([1]), True)


def test__WeakSet__ne():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(2)]
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    vampytest.assert_ne(weak_set_1, weak_set_1, reverse = True)
    vampytest.assert_ne(weak_set_1, weak_set_2)
    vampytest.assert_ne(weak_set_1, weak_set_empty)
    vampytest.assert_ne(weak_set_1, objects_1, reverse = True)
    vampytest.assert_ne(weak_set_2, objects_2, reverse = True)
    vampytest.assert_ne(weak_set_1, objects_2)

    test_case = WeakSet()
    vampytest.assert_is(test_case.__ne__(1), NotImplemented)
    vampytest.assert_eq(test_case.__ne__([1]), True)


def test__WeakSet__or():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy() | weak_set_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() | weak_set_2
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() | weak_set_3
    vampytest.assert_eq(test_case, weak_set_3)
    
    
    test_case = weak_set_1.copy() | objects_1
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() | objects_2
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy() | objects_3
    vampytest.assert_eq(test_case, weak_set_3)
    
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__or__(1), NotImplemented)
    vampytest.assert_is(test_case.__or__([1]), NotImplemented)


def test__WeakSet__rand():
    vampytest.assert_is(WeakSet.__rand__, WeakSet.__and__)


def test__WeakSet__rsub():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    
    
    weak_set_1_1_sub = WeakSet()
    weak_set_2_1_sub = WeakSet(set(objects_2) - set(objects_1))
    weak_set_3_1_sub = WeakSet(set(objects_3) - set(objects_1))
    
    test_case = objects_1 - weak_set_1.copy()
    vampytest.assert_eq(test_case, weak_set_1_1_sub)
    
    test_case = objects_2 - weak_set_1.copy()
    vampytest.assert_eq(test_case, weak_set_2_1_sub)
    
    test_case = objects_3 - weak_set_1.copy()
    vampytest.assert_eq(test_case, weak_set_3_1_sub)
    
    test_case = WeakSet()
    vampytest.assert_is(test_case.__rsub__(1), NotImplemented)
    vampytest.assert_is(test_case.__rsub__([1]), NotImplemented)


def test__WeakSet__rxor():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = WeakSet(set(objects_1) ^ set(objects_2))
    
    test_case = weak_set_1.copy() ^ weak_set_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy() ^ weak_set_2
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    
    test_case = weak_set_1.copy() ^ objects_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy() ^ objects_2
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    
    vampytest.assert_is(weak_set_empty.__rxor__(1), NotImplemented)
    vampytest.assert_is(weak_set_empty.__rxor__([1]), NotImplemented)


def test__WeakSet__sub():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [1]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    weak_set_1_2_sub = WeakSet(set(objects_1) - set(objects_2))
    
    test_case = weak_set_1.copy() - weak_set_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy() - weak_set_2
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy() - weak_set_3
    vampytest.assert_eq(test_case, weak_set_empty)
    
    
    test_case = weak_set_1.copy() - objects_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy() - objects_2
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy() - objects_3
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy() - objects_4
    vampytest.assert_eq(test_case, weak_set_1)
    
    vampytest.assert_is(weak_set_empty.__sub__(1), NotImplemented)


def test__WeakSet__xor():
    vampytest.assert_is(WeakSet.__xor__, WeakSet.__rxor__)


# Test methods


def test__WeakSet__add():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_3 = 7
    
    test_case = WeakSet(objects_1)
    test_case.add(object_1)
    
    expected_state = set(objects_1)
    expected_state.add(object_1)
    
    vampytest.assert_eq(test_case, expected_state)
    
    
    test_case = WeakSet(objects_1)
    test_case.add(object_2)
    
    expected_state = set(objects_1)
    expected_state.add(object_2)
    
    vampytest.assert_eq(test_case, expected_state)
    
    with vampytest.assert_raises(TypeError):
        test_case.add(object_3)


def test__WeakSet__clear():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_set_1 = WeakSet(objects_1)
    
    weak_set_empty = WeakSet()
    
    weak_set_1.clear()
    
    vampytest.assert_eq(len(weak_set_1), 0)
    vampytest.assert_eq(weak_set_1, weak_set_empty)


def test__WeakSet__copy():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_set_1 = WeakSet(objects_1)
    
    weak_set_empty = WeakSet()
    
    test_case = weak_set_1.copy()
    
    vampytest.assert_is_not(weak_set_1, test_case)
    vampytest.assert_eq(weak_set_1, test_case)
    
    test_case = weak_set_empty.copy()
    
    vampytest.assert_is_not(weak_set_empty, test_case)
    vampytest.assert_eq(weak_set_empty, test_case)


def test__WeakSet__difference():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [1]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    weak_set_1_2_sub = WeakSet(set(objects_1) - set(objects_2))
    
    test_case = weak_set_1.copy() - weak_set_1
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy().difference(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy() - weak_set_3
    vampytest.assert_eq(test_case, weak_set_empty)
    
    
    test_case = weak_set_1.copy().difference(objects_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy().difference(objects_2)
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy().difference(objects_3)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy().difference(objects_4)
    vampytest.assert_eq(test_case, weak_set_1)
    
    with vampytest.assert_raises(TypeError):
        weak_set_empty.difference(1)


def test__WeakSet__difference_update():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    weak_set_1_2_sub = WeakSet(set(objects_1) - set(objects_2))
    
    
    test_case = weak_set_1.copy()
    test_case.difference_update(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case.difference_update(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy()
    test_case.difference_update(weak_set_3)
    vampytest.assert_eq(test_case, weak_set_empty)
    

    test_case = weak_set_1.copy()
    test_case.difference_update(objects_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case.difference_update(objects_2)
    vampytest.assert_eq(test_case, weak_set_1_2_sub)
    
    test_case = weak_set_1.copy()
    test_case.difference_update(objects_3)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    
    with vampytest.assert_raises(TypeError):
        assert test_case.difference_update(1)
    vampytest.assert_eq(len(test_case), 0)
    
    test_case.difference_update([1])
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__discard():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_3 = 7
    
    test_case = WeakSet(objects_1)
    test_case.discard(object_1)
    
    expected_state = set(objects_1)
    expected_state.discard(object_1)
    
    vampytest.assert_eq(test_case, expected_state)
    
    
    test_case = WeakSet(objects_1)
    test_case.discard(object_2)
    
    expected_state = set(objects_1)
    expected_state.discard(object_2)
    
    vampytest.assert_eq(test_case, expected_state)
    
    
    test_case.discard(object_3)
    vampytest.assert_eq(test_case, expected_state)


def test__WeakSet__intersection():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    test_case = weak_set_1.copy().intersection(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().intersection(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy().intersection(weak_set_3)
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = weak_set_1.copy().intersection(objects_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().intersection(objects_2)
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy().intersection(objects_3)
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = WeakSet()
    
    with vampytest.assert_raises(TypeError):
        assert test_case.intersection(1)
    
    intersection = test_case.intersection([1])
    vampytest.assert_eq(len(intersection), 0)


def test__WeakSet__intersection_update():

    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_3)
    vampytest.assert_eq(test_case, weak_set_1)
    

    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_2)
    vampytest.assert_eq(test_case, weak_set_2)
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_3)
    vampytest.assert_eq(test_case, weak_set_1)
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.intersection_update(1)
    vampytest.assert_eq(len(test_case), 0)
    
    test_case.intersection_update([1])
    vampytest.assert_eq(len(test_case), 0)


def test__WeakSet__isdisjoint():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4, 6)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    vampytest.assert_eq(weak_set_1.isdisjoint(weak_set_1), False)
    vampytest.assert_eq(weak_set_1.isdisjoint(weak_set_2), False)
    vampytest.assert_eq(weak_set_1.isdisjoint(weak_set_3), True)
    vampytest.assert_eq(weak_set_1.isdisjoint(weak_set_empty), True)


    vampytest.assert_eq(weak_set_1.isdisjoint(objects_1), False)
    vampytest.assert_eq(weak_set_1.isdisjoint(objects_2), False)
    vampytest.assert_eq(weak_set_1.isdisjoint(objects_3), True)
    vampytest.assert_eq(weak_set_1.isdisjoint([]), True)


def test__WeakSet__issubset():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert weak_set_1.issubset(weak_set_1)
    assert not (weak_set_1.issubset(weak_set_2))
    assert weak_set_1.issubset(weak_set_3)
    
    assert weak_set_1.issubset(objects_1)
    assert not (weak_set_1.issubset(objects_2))
    assert weak_set_1.issubset(objects_3)
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.issubset(1)
    
    vampytest.assert_eq(test_case.issubset([1]), True)


def test__WeakSet__issuperset():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert weak_set_1.issuperset(weak_set_1)
    assert weak_set_1.issuperset(weak_set_2)
    assert not (weak_set_1.issuperset(weak_set_3))
    
    assert weak_set_1.issuperset(objects_1)
    assert weak_set_1.issuperset(objects_2)
    assert not (weak_set_1.issuperset(objects_3))
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.issuperset(1)
    
    vampytest.assert_eq(test_case.issuperset([1]), False)


def test__WeakSet__pop():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    test_case = WeakSet(objects_1)
    
    popped = test_case.pop()
    
    vampytest.assert_eq(len(test_case), len(objects_1) - 1)
    vampytest.assert_in(popped, objects_1)
    
    
    test_case = WeakSet()
    
    with vampytest.assert_raises(KeyError):
        test_case.remove(test_case.pop())


def test__WeakSet__remove():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_4 = 7
    
    test_case = WeakSet(objects_1)
    
    test_case.remove(object_1)
    
    expected_state = set(objects_1)
    expected_state.discard(object_1)
    
    vampytest.assert_eq(test_case, expected_state)
    
    
    test_case = WeakSet(objects_1)
    
    with vampytest.assert_raises(KeyError):
        test_case.remove(object_2)
    
    expected_state = set(objects_1)
    expected_state.discard(object_2)
    
    vampytest.assert_eq(test_case, expected_state)
    
    with vampytest.assert_raises(KeyError):
        test_case.remove(object_4)


def test__WeakSet__symmetric_difference():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = WeakSet(set(objects_1).symmetric_difference(set(objects_2)))
    
    test_case = weak_set_1.copy().symmetric_difference(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy().symmetric_difference(weak_set_2)
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    
    test_case = weak_set_1.copy().symmetric_difference(objects_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy().symmetric_difference(objects_2)
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    
    with vampytest.assert_raises(TypeError):
        weak_set_empty.symmetric_difference(1)
    
    with vampytest.assert_raises(TypeError):
        weak_set_empty.symmetric_difference([1])


def test__WeakSet__symmetric_difference_update():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(2), {}]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = set(objects_1)
    objects_1_2_xor.symmetric_difference_update(set(objects_2))
    weak_set_1_2_xor = WeakSet(objects_1_2_xor)
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(weak_set_2)
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(objects_1)
    vampytest.assert_eq(test_case, weak_set_empty)
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(objects_2)
    vampytest.assert_eq(test_case, objects_1_2_xor)
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.symmetric_difference_update(1)
    vampytest.assert_eq(len(test_case), 0)
    
    with vampytest.assert_raises(TypeError):
        test_case.symmetric_difference_update([1])
    vampytest.assert_eq(len(test_case), 0)
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.symmetric_difference_update(objects_3)
    vampytest.assert_eq(len(test_case), 1)


def test__WeakSet__union():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy().union(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().union(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().union(weak_set_3)
    vampytest.assert_eq(test_case, weak_set_3)
    
    
    test_case = weak_set_1.copy().union(objects_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().union(objects_2)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy().union(objects_3)
    vampytest.assert_eq(test_case, weak_set_3)
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.union(1)
    
    with vampytest.assert_raises(TypeError):
        test_case.union([1])


def test__WeakSet__update():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [WeakReferencable(2), {}]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_2)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_3)
    vampytest.assert_eq(test_case, objects_3)
    

    test_case = weak_set_1.copy()
    test_case.update(objects_1)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.update(objects_2)
    vampytest.assert_eq(test_case, weak_set_1)
    
    test_case = weak_set_1.copy()
    test_case.update(objects_3)
    vampytest.assert_eq(test_case, objects_3)
    
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.update(1)
    vampytest.assert_eq(len(test_case), 0)
    
    with vampytest.assert_raises(TypeError):
        test_case.update([1])
    vampytest.assert_eq(len(test_case), 0)
    
    test_case = WeakSet()
    with vampytest.assert_raises(TypeError):
        test_case.update(objects_4)
    vampytest.assert_eq(len(test_case), 1)
