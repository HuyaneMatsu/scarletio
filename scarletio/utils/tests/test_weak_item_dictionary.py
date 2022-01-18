import pytest

from weak_helpers import WeakReferencable

from scarletio import WeakItemDictionary


# Test WeakItemDictionary

# Test constructor

def test_WeakItemDictionary_constructor():
    weak_item_dictionary = WeakItemDictionary()
    assert len(weak_item_dictionary) == 0
    assert sorted(weak_item_dictionary) == []


def test_WeakItemDictionary_constructor_empty():
    weak_item_dictionary = WeakItemDictionary([])
    assert len(weak_item_dictionary) == 0
    assert sorted(weak_item_dictionary.items()) == []


def test_WeakItemDictionary_constructor_filled():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary = WeakItemDictionary(relations)
    assert len(weak_item_dictionary) == len(relations)
    assert sorted(weak_item_dictionary.items()) == sorted(relations.items())


# test magic methods


def test_WeakItemDictionary_contains():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    key_1 = WeakReferencable(0)
    key_2 = WeakReferencable(10)
    key_3 = 62
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    assert key_1 in weak_item_dictionary
    assert not (key_2 in weak_item_dictionary)
    assert not (key_3 in weak_item_dictionary)


def test_WeakItemDictionary_eq():
    relations_1 = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    relations_2 = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_item_dictionary_1 = WeakItemDictionary(relations_1)
    weak_item_dictionary_2 = WeakItemDictionary(relations_2)
    weak_item_dictionary_3 = WeakItemDictionary(relations_3)
    
    assert weak_item_dictionary_1 == weak_item_dictionary_1
    assert not (weak_item_dictionary_1 == weak_item_dictionary_2)
    assert not (weak_item_dictionary_1 == weak_item_dictionary_3)
    
    assert weak_item_dictionary_1 == relations_1
    assert not (weak_item_dictionary_1 == relations_2)
    assert not (weak_item_dictionary_1 == relations_3)


def test_WeakItemDictionary_getitem():
    relations = {WeakReferencable(x): WeakReferencable(x+4) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    key_1 = WeakReferencable(2)
    value_1 = WeakReferencable(6)
    
    
    key_2 = WeakReferencable(6)
    
    key_3 = WeakReferencable(6)
    
    assert relations[key_1] == value_1
    
    with pytest.raises(KeyError):
        weak_item_dictionary[key_2]
    
    with pytest.raises(KeyError):
        weak_item_dictionary_empty[key_3]


def test_WeakItemDictionary_iter():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    assert sorted(iter(weak_item_dictionary)) == sorted(weak_item_dictionary.keys())
    assert sorted(iter(weak_item_dictionary_empty)) == sorted(weak_item_dictionary_empty.keys())


def test_WeakItemDictionary_len():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    assert len(weak_item_dictionary) == len(relations)
    assert len(weak_item_dictionary_empty) == 0


def test_WeakItemDictionary_ne():
    relations_1 = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    relations_2 = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_item_dictionary_1 = WeakItemDictionary(relations_1)
    weak_item_dictionary_2 = WeakItemDictionary(relations_2)
    weak_item_dictionary_3 = WeakItemDictionary(relations_3)
    
    assert not (weak_item_dictionary_1 != weak_item_dictionary_1)
    assert weak_item_dictionary_1 != weak_item_dictionary_2
    assert weak_item_dictionary_1 != weak_item_dictionary_3
    
    assert not (weak_item_dictionary_1 != relations_1)
    assert weak_item_dictionary_1 != relations_2
    assert weak_item_dictionary_1 != relations_3


def test_WeakItemDictionary_setitem():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    
    key_1 = WeakReferencable(4)
    value_1 = WeakReferencable(4)
    
    key_2 = WeakReferencable(3)
    value_2 = WeakReferencable(6)
    
    key_3 = 7
    value_3 = WeakReferencable(7)
    
    key_4 = WeakReferencable(7)
    value_4 = 7
    
    weak_item_dictionary[key_1] = value_1
    assert weak_item_dictionary[key_1] == value_1
    assert len(weak_item_dictionary) == 4
    
    weak_item_dictionary[key_2] = value_2
    assert weak_item_dictionary[key_2] == value_2
    assert len(weak_item_dictionary) == 5
    
    with pytest.raises(TypeError):
        weak_item_dictionary[key_3] = value_3
    
    with pytest.raises(TypeError):
        weak_item_dictionary[key_4] = value_4


# methods


def test_WeakItemDictionary_clear():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    test_case = WeakItemDictionary(relations)
    test_case.clear()
    assert test_case == weak_item_dictionary_empty
    assert len(test_case) == 0
    
    
    test_case = WeakItemDictionary()
    test_case.clear()
    assert test_case == weak_item_dictionary_empty
    assert len(test_case) == 0


def test_WeakItemDictionary_copy():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    test_case = weak_item_dictionary.copy()
    
    assert test_case is not weak_item_dictionary
    assert test_case == weak_item_dictionary
    
    test_case = weak_item_dictionary_empty.copy()
    assert test_case is not weak_item_dictionary_empty
    assert test_case == weak_item_dictionary_empty


def test_WeakItemDictionary_get():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    
    key_1 = WeakReferencable(1)
    value_1 = WeakReferencable(1)
    
    key_2 = WeakReferencable(6)
    
    assert weak_item_dictionary.get(key_1) == value_1
    assert weak_item_dictionary.get(key_2) is None


def test_WeakItemDictionary_items():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    item_1 = (WeakReferencable(2), WeakReferencable(2))
    item_2 = (WeakReferencable(6), WeakReferencable(6))
    item_3 = (WeakReferencable(2), WeakReferencable(6))
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    items = weak_item_dictionary.items()
    
    assert len(items) == len(weak_item_dictionary)
    assert sorted(items) == sorted((key, weak_item_dictionary[key]) for key in weak_item_dictionary.keys())
    assert item_1 in items
    assert not (item_2 in items)
    assert not (item_3 in items)
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    items = weak_item_dictionary_empty.values()
    
    assert len(items) == len(weak_item_dictionary_empty)
    assert sorted(items) == sorted((key, weak_item_dictionary[key]) for key in weak_item_dictionary.keys())
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)


def test_WeakItemDictionary_keys():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    key_1 = WeakReferencable(2)
    key_2 = WeakReferencable(6)
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    keys = weak_item_dictionary.keys()
    
    assert len(keys) == len(weak_item_dictionary)
    assert set(keys) == set(key for key, value in weak_item_dictionary.items())
    assert key_1 in keys
    assert not (key_2 in keys)


    weak_item_dictionary_empty = WeakItemDictionary()
    
    keys = weak_item_dictionary_empty.keys()
    
    assert len(keys) == len(weak_item_dictionary_empty)
    assert set(keys) == set(key for key, value in weak_item_dictionary_empty.items())
    assert not (key_1 in keys)
    assert not (key_2 in keys)


def test_WeakItemDictionary_pop():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    key_1 = WeakReferencable(2)
    value_1 = WeakReferencable(2)
    
    key_2 = WeakReferencable(6)
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    assert weak_item_dictionary.pop(key_1) == value_1
    assert len(weak_item_dictionary) == 2
    
    
    with pytest.raises(KeyError):
        weak_item_dictionary.pop(key_2)
    
    assert len(weak_item_dictionary) == 2


def test_WeakItemDictionary_popitem():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    
    item_1 = (WeakReferencable(1), WeakReferencable(1))
    item_2 = (WeakReferencable(2), WeakReferencable(2))
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    popped_item_1 = weak_item_dictionary.popitem()
    assert (popped_item_1 == item_1) or (popped_item_1 == item_2)
    assert len(weak_item_dictionary) == 1
    
    popped_item_2 = weak_item_dictionary.popitem()
    assert (popped_item_2 == item_1) or (popped_item_2 == item_2)
    assert popped_item_1 != popped_item_2
    assert len(weak_item_dictionary) == 0
    
    with pytest.raises(KeyError):
        weak_item_dictionary.popitem()
    
    assert len(weak_item_dictionary) == 0


def test_WeakItemDictionary_setdefault():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    
    key_1 = WeakReferencable(6)
    value_1 = WeakReferencable(6)
    expected_value_1 = value_1
    
    key_2 = WeakReferencable(1)
    value_2 = WeakReferencable(6)
    expected_value_2 = WeakReferencable(1)
    
    key_3 = 7
    value_3 = 9
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    value = weak_item_dictionary.setdefault(key_1, value_1)
    assert value == expected_value_1
    assert len(weak_item_dictionary) == 3
    
    
    value = weak_item_dictionary.setdefault(key_2, value_2)
    assert value == expected_value_2
    assert len(weak_item_dictionary) == 3
    assert weak_item_dictionary[key_2] == expected_value_2

    with pytest.raises(TypeError):
        weak_item_dictionary.setdefault(key_3, value_3)


def test_WeakItemDictionary_update():
    relations_1 = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    relations_2 = {WeakReferencable(x): WeakReferencable(x+1) for x in range(3)}
    relations_3 = {WeakReferencable(x): WeakReferencable(x-1) for x in range(1)}
    
    relations_update_1_2 = relations_1.copy()
    relations_update_1_2.update(relations_2)
    
    relations_update_1_3 = relations_1.copy()
    relations_update_1_3.update(relations_3)
    
    weak_item_dictionary_1 = WeakItemDictionary(relations_1)
    weak_item_dictionary_2 = WeakItemDictionary(relations_2)
    weak_item_dictionary_3 = WeakItemDictionary(relations_3)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(weak_item_dictionary_1)
    assert test_case == relations_1
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(weak_item_dictionary_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(weak_item_dictionary_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_1)
    assert test_case == relations_1
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    assert test_case == relations_1
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    assert test_case == relations_update_1_2
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    assert test_case == relations_update_1_3


def test_WeakItemDictionary_values():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    values = weak_item_dictionary.values()
    
    assert len(values) == len(weak_item_dictionary)
    assert sorted(values) == sorted(value for key, value in weak_item_dictionary.items())
    assert value_1 in values
    assert not (value_2 in values)
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    values = weak_item_dictionary_empty.values()
    
    assert len(values) == len(weak_item_dictionary_empty)
    assert sorted(values) == sorted(value for key, value in weak_item_dictionary_empty.items())
    assert not (value_1 in values)
    assert not (value_2 in values)
