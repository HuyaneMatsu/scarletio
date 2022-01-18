import pytest

from weak_helpers import WeakReferencable

from scarletio import WeakValueDictionary


# Test WeakValueDictionary

# Test constructor

def test_WeakValueDictionary_constructor():
    weak_value_dictionary = WeakValueDictionary()
    assert len(weak_value_dictionary) == 0
    assert sorted(weak_value_dictionary) == []


def test_WeakValueDictionary_constructor_empty():
    weak_value_dictionary = WeakValueDictionary([])
    assert len(weak_value_dictionary) == 0
    assert sorted(weak_value_dictionary) == []


def test_WeakValueDictionary_constructor_filled():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    assert len(weak_value_dictionary) == len(relations)
    assert sorted(weak_value_dictionary) == relations


# test magic methods


def test_WeakValueDictionary_contains():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    key_1 = 0
    key_2 = 10
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    assert key_1 in weak_value_dictionary
    assert not (key_2 in weak_value_dictionary)


def test_WeakValueDictionary_eq():
    relations_1 = {x: WeakReferencable(x) for x in range(3)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_value_dictionary_1 = WeakValueDictionary(relations_1)
    weak_value_dictionary_2 = WeakValueDictionary(relations_2)
    weak_value_dictionary_3 = WeakValueDictionary(relations_3)
    
    assert weak_value_dictionary_1 == weak_value_dictionary_1
    assert not (weak_value_dictionary_1 == weak_value_dictionary_2)
    assert not (weak_value_dictionary_1 == weak_value_dictionary_3)
    
    assert weak_value_dictionary_1 == relations_1
    assert not (weak_value_dictionary_1 == relations_2)
    assert not (weak_value_dictionary_1 == relations_3)


def test_WeakValueDictionary_getitem():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert relations[2] == WeakReferencable(2)
    
    with pytest.raises(KeyError):
        weak_value_dictionary[6]
    
    with pytest.raises(KeyError):
        weak_value_dictionary_empty[6]


def test_WeakValueDictionary_iter():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert list(iter(weak_value_dictionary)) == list(weak_value_dictionary.keys())
    assert list(iter(weak_value_dictionary_empty)) == list(weak_value_dictionary_empty.keys())


def test_WeakValueDictionary_len():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert len(weak_value_dictionary) == len(relations)
    assert len(weak_value_dictionary_empty) == 0


def test_WeakValueDictionary_ne():
    relations_1 = {x: WeakReferencable(x) for x in range(3)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_value_dictionary_1 = WeakValueDictionary(relations_1)
    weak_value_dictionary_2 = WeakValueDictionary(relations_2)
    weak_value_dictionary_3 = WeakValueDictionary(relations_3)
    
    assert not (weak_value_dictionary_1 != weak_value_dictionary_1)
    assert weak_value_dictionary_1 != weak_value_dictionary_2
    assert weak_value_dictionary_1 != weak_value_dictionary_3
    
    assert not (weak_value_dictionary_1 != relations_1)
    assert weak_value_dictionary_1 != relations_2
    assert weak_value_dictionary_1 != relations_3


def test_WeakValueDictionary_setitem():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    
    key = 4
    value = WeakReferencable(4)
    
    relations[key] = value
    assert weak_value_dictionary[key] == value
    assert len(weak_value_dictionary) == 4
    
    key = 3
    value = WeakReferencable(6)
    
    weak_value_dictionary[key] = value
    assert weak_value_dictionary[key] == value
    assert len(weak_value_dictionary) == 4
    
    key = 6
    value = 9
    
    with pytest.raises(TypeError):
        weak_value_dictionary[key] = value


# methods


def test_WeakValueDictionary_clear():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    test_case = WeakValueDictionary(relations)
    test_case.clear()
    assert test_case == weak_value_dictionary_empty
    assert len(test_case) == 0
    
    
    test_case = WeakValueDictionary()
    test_case.clear()
    assert test_case == weak_value_dictionary_empty
    assert len(test_case) == 0


def test_WeakValueDictionary_copy():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    test_case = weak_value_dictionary.copy()
    
    assert test_case is not weak_value_dictionary
    assert test_case == weak_value_dictionary
    
    test_case = weak_value_dictionary_empty.copy()
    assert test_case is not weak_value_dictionary_empty
    assert test_case == weak_value_dictionary_empty


def test_WeakValueDictionary_get():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    
    key_1 = 1
    value_1 = WeakReferencable(1)
    
    key_2 = 6
    
    assert weak_value_dictionary.get(key_1) == value_1
    assert weak_value_dictionary.get(key_2) is None


def test_WeakValueDictionary_items():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    item_1 = (2, WeakReferencable(2))
    item_2 = (6, WeakReferencable(6))
    item_3 = (2, WeakReferencable(6))
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    items = weak_value_dictionary.items()
    
    assert len(items) == len(weak_value_dictionary)
    assert sorted(items) == sorted((key, weak_value_dictionary[key]) for key in weak_value_dictionary.keys())
    assert item_1 in items
    assert not (item_2 in items)
    assert not (item_3 in items)
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    items = weak_value_dictionary_empty.values()
    
    assert len(items) == len(weak_value_dictionary_empty)
    assert sorted(items) == sorted((key, weak_value_dictionary[key]) for key in weak_value_dictionary.keys())
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)


def test_WeakValueDictionary_keys():
    relations = {x: WeakReferencable(x) for x in range(3)}
    key_1 = 2
    key_2 = 6
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    keys = weak_value_dictionary.keys()
    
    assert len(keys) == len(weak_value_dictionary)
    assert set(keys) == set(key for key, value in weak_value_dictionary.items())
    assert key_1 in keys
    assert not (key_2 in keys)


    weak_value_dictionary_empty = WeakValueDictionary()
    
    keys = weak_value_dictionary_empty.keys()
    
    assert len(keys) == len(weak_value_dictionary_empty)
    assert set(keys) == set(key for key, value in weak_value_dictionary_empty.items())
    assert not (key_1 in keys)
    assert not (key_2 in keys)


def test_WeakValueDictionary_pop():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    key_1 = 2
    value_1 = WeakReferencable(2)
    
    key_2 = 6
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    assert weak_value_dictionary.pop(key_1) == value_1
    assert len(weak_value_dictionary) == 2
    
    
    with pytest.raises(KeyError):
        weak_value_dictionary.pop(key_2)
    
    assert len(weak_value_dictionary) == 2


def test_WeakValueDictionary_popitem():
    relations = {x: WeakReferencable(x) for x in range(2)}
    
    item_1 = (1, WeakReferencable(1))
    item_2 = (2, WeakReferencable(2))
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    popped_item_1 = weak_value_dictionary.popitem()
    assert (popped_item_1 == item_1) or (popped_item_1 == item_2)
    assert len(weak_value_dictionary) == 1
    
    popped_item_2 = weak_value_dictionary.popitem()
    assert (popped_item_2 == item_1) or (popped_item_2 == item_2)
    assert popped_item_1 != popped_item_2
    assert len(weak_value_dictionary) == 0
    
    with pytest.raises(KeyError):
        weak_value_dictionary.popitem()
    
    assert len(weak_value_dictionary) == 0


def test_WeakValueDictionary_setdefault():
    relations = {x: WeakReferencable(x) for x in range(2)}
    
    key_1 = 6
    value_1 = WeakReferencable(6)
    expected_value_1 = value_1
    
    key_2 = 1
    value_2 = WeakReferencable(6)
    expected_value_2 = WeakReferencable(1)
    
    key_3 = 7
    value_3 = 9
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    value = weak_value_dictionary.setdefault(key_1, value_1)
    assert value == expected_value_1
    assert len(weak_value_dictionary) == 3
    
    
    value = weak_value_dictionary.setdefault(key_2, value_2)
    assert value == expected_value_2
    assert len(weak_value_dictionary) == 3
    assert weak_value_dictionary[key_2] == expected_value_2
    
    with pytest.raises(TypeError):
        weak_value_dictionary.setdefault(key_3, value_3)


def test_WeakValueDictionary_update():
    relations_1 = {x: WeakReferencable(x) for x in range(2)}
    relations_2 = {x: WeakReferencable(x+1) for x in range(3)}
    relations_3 = {x: WeakReferencable(x-1) for x in range(1)}
    
    relations_update_1_2 = relations_1.copy()
    relations_update_1_2.update(relations_2)
    
    relations_update_1_3 = relations_1.copy()
    relations_update_1_3.update(relations_3)
    
    weak_value_dictionary_1 = WeakValueDictionary(relations_1)
    weak_value_dictionary_2 = WeakValueDictionary(relations_2)
    weak_value_dictionary_3 = WeakValueDictionary(relations_3)
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(weak_value_dictionary_1)
    assert test_case == relations_1
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(weak_value_dictionary_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(weak_value_dictionary_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_1)
    assert test_case == relations_1
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    assert test_case == relations_1
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    assert test_case == relations_update_1_2
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    assert test_case == relations_update_1_3


def test_WeakValueDictionary_values():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    values = weak_value_dictionary.values()
    
    assert len(values) == len(weak_value_dictionary)
    assert sorted(values) == sorted(value for key, value in weak_value_dictionary.items())
    assert value_1 in values
    assert not (value_2 in values)
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    values = weak_value_dictionary_empty.values()
    
    assert len(values) == len(weak_value_dictionary_empty)
    assert sorted(values) == sorted(value for key, value in weak_value_dictionary_empty.items())
    assert not (value_1 in values)
    assert not (value_2 in values)
