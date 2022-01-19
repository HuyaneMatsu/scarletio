import pytest

from weak_helpers import WeakReferencable

from scarletio import WeakMap

# Test WeakMap

# Test constructor

def test_WeakMap_constructor():
    weak_map = WeakMap()
    assert len(weak_map) == 0
    assert sorted(weak_map) == []


def test_WeakMap_constructor_empty():
    weak_map = WeakMap([])
    assert len(weak_map) == 0
    assert sorted(weak_map) == []


def test_WeakMap_constructor_filled():
    objects_ = [WeakReferencable(x) for x in range(3)]

    weak_map = WeakMap(objects_)
    assert len(weak_map) == len(objects_)
    assert sorted(weak_map) == objects_


# Test magic methods


def test_WeakMap_contains():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    object_1 = objects_1[0]
    object_2 = WeakReferencable(10)
    object_3 = 62
    
    weak_map = WeakMap(objects_1)
    
    assert object_1 in weak_map
    assert not (object_2 in weak_map)
    assert not (object_3 in weak_map)


def test_WeakMap_delitem():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    object_1 = objects_1[0]
    object_2 = WeakReferencable(6)
    
    weak_map = WeakMap(objects_1)
    
    del weak_map[object_1]
    assert len(weak_map) == 2
    
    with pytest.raises(KeyError):
        del weak_map[object_2]
    
    assert len(weak_map) == 2


def test_WeakMap_eq():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    assert weak_map_1 == weak_map_1
    assert not (weak_map_1 == weak_map_2)
    assert not (weak_map_1 == weak_map_3)
    
    assert weak_map_1 == objects_1
    assert not (weak_map_1 == objects_2)
    assert not (weak_map_1 == objects_3)

    assert weak_map_1.__eq__(1) is NotImplemented


def test_WeakMap_getitem():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(6)
    
    object_3 = WeakReferencable(2)
    object_3_expected = objects_1[2]
    
    weak_map = WeakMap(objects_1)
    
    assert weak_map[object_1] == object_1_expected
    
    with pytest.raises(KeyError):
        weak_map[object_2]
    
    assert weak_map[object_3] == object_3_expected


def test_WeakMap_iter():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    
    assert sorted(weak_map_1) == objects_1
    assert sorted(weak_map_2) == objects_2


def test_WeakMap_len():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    
    assert len(weak_map_1) == len(objects_1)
    assert len(weak_map_2) == len(objects_2)


def test_WeakMap_ne():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = []
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    assert not (weak_map_1 != weak_map_1)
    assert weak_map_1 != weak_map_2
    assert weak_map_1 != weak_map_3
    
    assert not (weak_map_1 != objects_1)
    assert weak_map_1 != objects_2
    assert weak_map_1 != objects_3
    
    assert weak_map_1.__ne__(1) is NotImplemented


# Test Methods


def test_WeakMap_clear():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map = WeakMap(objects_1)
    
    weak_map_empty = WeakMap()
    
    weak_map.clear()
    
    assert len(weak_map) == 0
    assert weak_map == weak_map_empty


def test_WeakMap_copy():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    weak_map_empty = WeakMap()
    
    test_case = weak_map_1.copy()
    
    assert weak_map_1 is not test_case
    assert weak_map_1 == test_case
    
    test_case = weak_map_empty.copy()
    
    assert weak_map_empty is not test_case
    assert weak_map_empty == test_case


def test_WeakMap_get():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    
    object_4 = 7
    
    assert weak_map_1.get(object_1) is object_1_expected
    assert weak_map_1.get(object_2) is object_2_expected
    assert weak_map_1.get(object_3) is None
    assert weak_map_1.get(object_4) is None


def test_WeakMap_pop():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    
    object_4 = 8
    
    assert weak_map_1.pop(object_1) is object_1_expected
    assert len(weak_map_1) == 2
    
    assert weak_map_1.pop(object_2) is object_2_expected
    assert len(weak_map_1) == 1
    
    
    with pytest.raises(KeyError):
        weak_map_1.pop(object_3)
    assert len(weak_map_1) == 1

    assert weak_map_1.pop(object_3, None) is None
    assert len(weak_map_1) == 1
    
    
    assert weak_map_1.pop(object_4, None) is None
    assert len(weak_map_1) == 1

    with pytest.raises(KeyError):
        weak_map_1.pop(object_4)
    assert len(weak_map_1) == 1


def test_WeakMap_set():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    weak_map_1 = WeakMap(objects_1)
    
    object_1 = objects_1[0]
    object_1_expected = object_1
    
    object_2 = WeakReferencable(1)
    object_2_expected = objects_1[1]
    
    object_3 = WeakReferencable(6)
    object_3_expected = object_3
    
    object_4 = 7
    
    assert weak_map_1.set(object_1) is object_1_expected
    assert len(weak_map_1) == 3
    
    assert weak_map_1.set(object_2) is object_2_expected
    assert len(weak_map_1) == 3
    
    assert weak_map_1.set(object_3) is object_3_expected
    assert len(weak_map_1) == 4
    
    with pytest.raises(TypeError):
        weak_map_1.set(object_4)
    assert len(weak_map_1) == 4


def test_WeakMap_ior():
    objects_1 = [WeakReferencable(x) for x in range(3)]
    objects_2 = [WeakReferencable(x) for x in range(2)]
    objects_3 = [WeakReferencable(x) for x in range(4)]
    
    weak_map_1 = WeakMap(objects_1)
    weak_map_2 = WeakMap(objects_2)
    weak_map_3 = WeakMap(objects_3)
    
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_1)
    assert test_case == weak_map_1
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_2)
    assert test_case == weak_map_1
    
    test_case = weak_map_1.copy()
    test_case.update(weak_map_3)
    assert test_case == objects_3
    

    test_case = weak_map_1.copy()
    test_case.update(objects_1)
    assert test_case == weak_map_1
    
    test_case = weak_map_1.copy()
    test_case.update(objects_2)
    assert test_case == weak_map_1
    
    test_case = weak_map_1.copy()
    test_case.update(objects_3)
    assert test_case == objects_3
    
    
    test_case = WeakMap()
    with pytest.raises(TypeError):
        test_case.update([1, ])
    
    with pytest.raises(TypeError):
        test_case.update(1)
