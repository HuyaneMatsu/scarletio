import pytest

from weak_helpers import WeakReferencable

from scarletio import WeakSet


# Test WeakSet

# Test constructor

def test_WeakSet_constructor():
    weak_set = WeakSet()
    assert len(weak_set) == 0
    assert sorted(weak_set) == []


def test_WeakSet_constructor_empty():
    weak_set = WeakSet([])
    assert len(weak_set) == 0
    assert sorted(weak_set) == []


def test_WeakSet_constructor_filled():
    objects_ = [WeakReferencable(x) for x in range(3)]

    weak_set = WeakSet(objects_)
    assert len(weak_set) == len(objects_)
    assert sorted(weak_set) == objects_

# Test magic methods

def test_WeakSet_and():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy() & weak_set_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() & weak_set_2
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy() & weak_set_3
    assert test_case == weak_set_1
    
    
    test_case = weak_set_1.copy() & objects_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() & objects_2
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy() & objects_3
    assert test_case == weak_set_1
    
    
    test_case = WeakSet()
    
    assert test_case.__and__(1) is NotImplemented
    assert len(test_case) == 0
    
    intersection = test_case.__and__([1])
    assert intersection is not NotImplemented
    assert len(intersection) == 0


def test_WeakSet_contains():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(10)
    object_3 = 62
    
    weak_set = WeakSet(objects_1)
    
    assert object_1 in weak_set
    assert not (object_2 in weak_set)
    assert not (object_3 in weak_set)


def test_WeakSet_eq():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    assert weak_set_1 == weak_set_1
    assert not (weak_set_1 == weak_set_2)
    assert not (weak_set_1 == weak_set_3)
    
    assert weak_set_1 == objects_1
    assert not (weak_set_1 == objects_2)
    assert not (weak_set_1 == objects_3)
    
    
    test_case = WeakSet()
    assert test_case.__eq__(1) is NotImplemented
    assert test_case.__eq__([1]) == False


def test_WeakSet_ge():
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
    assert test_case.__ge__(1) is NotImplemented
    assert test_case.__ge__([1]) == False


def test_WeakSet_gt():
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
    assert test_case.__gt__(1) is NotImplemented
    assert test_case.__gt__([1]) == False


def test_WeakSet_iand():
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
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case &= weak_set_2
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy()
    test_case &= weak_set_3
    assert test_case == weak_set_1
    

    test_case = weak_set_1.copy()
    test_case &= objects_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case &= objects_2
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy()
    test_case &= objects_3
    assert test_case == weak_set_1
    
    
    test_case = WeakSet()
    assert test_case.__iand__(1) is NotImplemented
    assert len(test_case) == 0
    
    assert test_case.__iand__([1]) is test_case
    assert len(test_case) == 0
    
    assert test_case.__iand__(objects_4) is test_case
    assert len(test_case) == 0
    
    assert test_case.__iand__(objects_5) is NotImplemented
    assert len(test_case) == 0


def test_WeakSet_ior():
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
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case |= weak_set_2
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case |= weak_set_3
    assert test_case == objects_3
    

    test_case = weak_set_1.copy()
    test_case |= objects_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case |= objects_2
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case |= objects_3
    assert test_case == objects_3
    
    
    test_case = WeakSet()
    assert test_case.__ior__(1) is NotImplemented
    assert len(test_case) == 0
    
    assert test_case.__ior__([1]) is NotImplemented
    assert len(test_case) == 0

    assert test_case.__ior__(objects_4) is NotImplemented
    assert len(test_case) == 0
    
    assert test_case.__ior__(objects_5) is NotImplemented
    assert len(test_case) == 0


def test_WeakSet_isub():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case -= weak_set_2
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy()
    test_case -= weak_set_3
    assert test_case == weak_set_empty
    

    test_case = weak_set_1.copy()
    test_case -= objects_1
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case -= objects_2
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy()
    test_case -= objects_3
    assert test_case == weak_set_empty
    
    
    test_case = WeakSet()
    assert test_case.__isub__(1) is NotImplemented
    assert len(test_case) == 0
    assert test_case.__isub__([1]) is test_case
    assert len(test_case) == 0


def test_WeakSet_iter():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    
    assert sorted(weak_set_1) == objects_1
    assert sorted(weak_set_2) == objects_2


def test_WeakSet_ixor():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case ^= weak_set_2
    assert test_case == objects_1_2_xor
    

    test_case = weak_set_1.copy()
    test_case ^= objects_1
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case ^= objects_2
    assert test_case == objects_1_2_xor
    
    test_case = WeakSet()
    assert test_case.__ixor__(1) is NotImplemented
    assert len(test_case) == 0
    
    assert test_case.__ixor__([1]) is NotImplemented
    assert len(test_case) == 0

    assert test_case.__ior__(objects_3) is NotImplemented
    assert len(test_case) == 0
    
    assert test_case.__ior__(objects_4) is NotImplemented
    assert len(test_case) == 0


def test_WeakSet_le():
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
    assert test_case.__le__(1) is NotImplemented
    assert test_case.__le__([1]) == True


def test_WeakSet_len():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    
    assert len(weak_set_1) == len(objects_1)
    assert len(weak_set_2) == len(objects_2)


def test_WeakSet_lt():
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
    assert test_case.__lt__(1) is NotImplemented
    assert test_case.__lt__([1]) == True


def test_WeakSet_ne():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(2)]
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    assert not (weak_set_1 != weak_set_1)
    assert weak_set_1 != weak_set_2
    assert weak_set_1 != weak_set_empty
    assert not (weak_set_1 != objects_1)
    assert not (weak_set_2 != objects_2)
    assert weak_set_1 != objects_2

    test_case = WeakSet()
    assert test_case.__ne__(1) is NotImplemented
    assert test_case.__ne__([1]) == True


def test_WeakSet_or():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy() | weak_set_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() | weak_set_2
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() | weak_set_3
    assert test_case == weak_set_3
    
    
    test_case = weak_set_1.copy() | objects_1
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() | objects_2
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy() | objects_3
    assert test_case == weak_set_3
    
    
    test_case = WeakSet()
    assert test_case.__or__(1) is NotImplemented
    assert test_case.__or__([1]) is NotImplemented


def test_WeakSet_rand():
    assert WeakSet.__rand__ is WeakSet.__and__


def test_WeakSet_rsub():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    
    
    weak_set_1_1_sub = WeakSet()
    weak_set_2_1_sub = WeakSet(set(objects_2) - set(objects_1))
    weak_set_3_1_sub = WeakSet(set(objects_3) - set(objects_1))
    
    test_case = objects_1 - weak_set_1.copy()
    assert test_case == weak_set_1_1_sub
    
    test_case = objects_2 - weak_set_1.copy()
    assert test_case == weak_set_2_1_sub
    
    test_case = objects_3 - weak_set_1.copy()
    assert test_case == weak_set_3_1_sub
    
    test_case = WeakSet()
    assert test_case.__rsub__(1) is NotImplemented
    assert test_case.__rsub__([1]) is NotImplemented


def test_WeakSet_rxor():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = WeakSet(set(objects_1) ^ set(objects_2))
    
    test_case = weak_set_1.copy() ^ weak_set_1
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy() ^ weak_set_2
    assert test_case == objects_1_2_xor
    
    
    test_case = weak_set_1.copy() ^ objects_1
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy() ^ objects_2
    assert test_case == objects_1_2_xor
    
    
    assert weak_set_empty.__rxor__(1) is NotImplemented
    assert weak_set_empty.__rxor__([1]) is NotImplemented


def test_WeakSet_sub():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy() - weak_set_2
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy() - weak_set_3
    assert test_case == weak_set_empty
    
    
    test_case = weak_set_1.copy() - objects_1
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy() - objects_2
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy() - objects_3
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy() - objects_4
    assert test_case == weak_set_1
    
    assert weak_set_empty.__sub__(1) is NotImplemented


def test_WeakSet_xor():
    assert WeakSet.__xor__ is WeakSet.__rxor__


# Test methods


def test_WeakSet_add():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_3 = 7
    
    test_case = WeakSet(objects_1)
    test_case.add(object_1)
    
    expected_state = set(objects_1)
    expected_state.add(object_1)
    
    assert test_case == expected_state
    
    
    test_case = WeakSet(objects_1)
    test_case.add(object_2)
    
    expected_state = set(objects_1)
    expected_state.add(object_2)
    
    assert test_case == expected_state
    
    with pytest.raises(TypeError):
        test_case.add(object_3)


def test_WeakSet_clear():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_set_1 = WeakSet(objects_1)
    
    weak_set_empty = WeakSet()
    
    weak_set_1.clear()
    
    assert len(weak_set_1) == 0
    assert weak_set_1 == weak_set_empty


def test_WeakSet_copy():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_set_1 = WeakSet(objects_1)
    
    weak_set_empty = WeakSet()
    
    test_case = weak_set_1.copy()
    
    assert weak_set_1 is not test_case
    assert weak_set_1 == test_case
    
    test_case = weak_set_empty.copy()
    
    assert weak_set_empty is not test_case
    assert weak_set_empty == test_case


def test_WeakSet_difference():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy().difference(weak_set_2)
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy() - weak_set_3
    assert test_case == weak_set_empty
    
    
    test_case = weak_set_1.copy().difference(objects_1)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy().difference(objects_2)
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy().difference(objects_3)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy().difference(objects_4)
    assert test_case == weak_set_1
    
    with pytest.raises(TypeError):
        weak_set_empty.difference(1)


def test_WeakSet_difference_update():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case.difference_update(weak_set_2)
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy()
    test_case.difference_update(weak_set_3)
    assert test_case == weak_set_empty
    

    test_case = weak_set_1.copy()
    test_case.difference_update(objects_1)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case.difference_update(objects_2)
    assert test_case == weak_set_1_2_sub
    
    test_case = weak_set_1.copy()
    test_case.difference_update(objects_3)
    assert test_case == weak_set_empty
    
    
    with pytest.raises(TypeError):
        assert test_case.difference_update(1)
    assert len(test_case) == 0
    
    test_case.difference_update([1])
    assert len(test_case) == 0


def test_WeakSet_discard():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_3 = 7
    
    test_case = WeakSet(objects_1)
    test_case.discard(object_1)
    
    expected_state = set(objects_1)
    expected_state.discard(object_1)
    
    assert test_case == expected_state
    
    
    test_case = WeakSet(objects_1)
    test_case.discard(object_2)
    
    expected_state = set(objects_1)
    expected_state.discard(object_2)
    
    assert test_case == expected_state
    
    
    test_case.discard(object_3)
    assert test_case == expected_state


def test_WeakSet_intersection():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    test_case = weak_set_1.copy().intersection(weak_set_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().intersection(weak_set_2)
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy().intersection(weak_set_3)
    assert test_case == weak_set_1
    
    
    test_case = weak_set_1.copy().intersection(objects_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().intersection(objects_2)
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy().intersection(objects_3)
    assert test_case == weak_set_1
    
    
    test_case = WeakSet()
    
    with pytest.raises(TypeError):
        assert test_case.intersection(1)
    
    intersection = test_case.intersection([1])
    assert len(intersection) == 0


def test_WeakSet_intersection_update():

    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_2)
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(weak_set_3)
    assert test_case == weak_set_1
    

    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_2)
    assert test_case == weak_set_2
    
    test_case = weak_set_1.copy()
    test_case.intersection_update(objects_3)
    assert test_case == weak_set_1
    
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.intersection_update(1)
    assert len(test_case) == 0
    
    test_case.intersection_update([1])
    assert len(test_case) == 0


def test_WeakSet_isdisjoint():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4, 6)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    weak_set_empty = WeakSet()
    
    assert weak_set_1.isdisjoint(weak_set_1) == False
    assert weak_set_1.isdisjoint(weak_set_2) == False
    assert weak_set_1.isdisjoint(weak_set_3) == True
    assert weak_set_1.isdisjoint(weak_set_empty) == True


    assert weak_set_1.isdisjoint(objects_1) == False
    assert weak_set_1.isdisjoint(objects_2) == False
    assert weak_set_1.isdisjoint(objects_3) == True
    assert weak_set_1.isdisjoint([]) == True


def test_WeakSet_issubset():
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
    with pytest.raises(TypeError):
        test_case.issubset(1)
    
    assert test_case.issubset([1]) == True


def test_WeakSet_issuperset():
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
    with pytest.raises(TypeError):
        test_case.issuperset(1)
    
    assert test_case.issuperset([1]) == False


def test_WeakSet_pop():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    test_case = WeakSet(objects_1)
    
    popped = test_case.pop()
    
    assert len(test_case) == len(objects_1) - 1
    assert popped in objects_1
    
    
    test_case = WeakSet()
    
    with pytest.raises(KeyError):
        test_case.remove(test_case.pop())


def test_WeakSet_remove():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(4)
    object_4 = 7
    
    test_case = WeakSet(objects_1)
    
    test_case.remove(object_1)
    
    expected_state = set(objects_1)
    expected_state.discard(object_1)
    
    assert test_case == expected_state
    
    
    test_case = WeakSet(objects_1)
    
    with pytest.raises(KeyError):
        test_case.remove(object_2)
    
    expected_state = set(objects_1)
    expected_state.discard(object_2)
    
    assert test_case == expected_state
    
    with pytest.raises(KeyError):
        test_case.remove(object_4)


def test_WeakSet_symmetric_difference():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_empty = WeakSet()
    
    objects_1_2_xor = WeakSet(set(objects_1).symmetric_difference(set(objects_2)))
    
    test_case = weak_set_1.copy().symmetric_difference(weak_set_1)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy().symmetric_difference(weak_set_2)
    assert test_case == objects_1_2_xor
    
    
    test_case = weak_set_1.copy().symmetric_difference(objects_1)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy().symmetric_difference(objects_2)
    assert test_case == objects_1_2_xor
    
    
    with pytest.raises(TypeError):
        weak_set_empty.symmetric_difference(1)
    
    with pytest.raises(TypeError):
        weak_set_empty.symmetric_difference([1])


def test_WeakSet_symmetric_difference_update():
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
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(weak_set_2)
    assert test_case == objects_1_2_xor
    
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(objects_1)
    assert test_case == weak_set_empty
    
    test_case = weak_set_1.copy()
    test_case.symmetric_difference_update(objects_2)
    assert test_case == objects_1_2_xor
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.symmetric_difference_update(1)
    assert len(test_case) == 0
    
    with pytest.raises(TypeError):
        test_case.symmetric_difference_update([1])
    assert len(test_case) == 0
    
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.symmetric_difference_update(objects_3)
    assert len(test_case) == 1


def test_WeakSet_union():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy().union(weak_set_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().union(weak_set_2)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().union(weak_set_3)
    assert test_case == weak_set_3
    
    
    test_case = weak_set_1.copy().union(objects_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().union(objects_2)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy().union(objects_3)
    assert test_case == weak_set_3
    
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.union(1)
    
    with pytest.raises(TypeError):
        test_case.union([1])


def test_WeakSet_update():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    objects_4 = [WeakReferencable(2), {}]
    
    weak_set_1 = WeakSet(objects_1)
    weak_set_2 = WeakSet(objects_2)
    weak_set_3 = WeakSet(objects_3)
    
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_2)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.update(weak_set_3)
    assert test_case == objects_3
    

    test_case = weak_set_1.copy()
    test_case.update(objects_1)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.update(objects_2)
    assert test_case == weak_set_1
    
    test_case = weak_set_1.copy()
    test_case.update(objects_3)
    assert test_case == objects_3
    
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.update(1)
    assert len(test_case) == 0
    
    with pytest.raises(TypeError):
        test_case.update([1])
    assert len(test_case) == 0
    
    test_case = WeakSet()
    with pytest.raises(TypeError):
        test_case.update(objects_4)
    assert len(test_case) == 1
