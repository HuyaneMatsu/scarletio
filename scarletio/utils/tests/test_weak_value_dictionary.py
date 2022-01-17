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
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    assert len(weak_value_dictionary) == len(relations)
    assert sorted(weak_value_dictionary) == relations


# test magic methods


def test_WeakValueDictionary_contains():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(0)
    key_2 = WeakReferencable(10)
    key_3 = 62
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    assert key_1 in weak_value_dictionary
    assert not (key_2 in weak_value_dictionary)
    assert not (key_3 in weak_value_dictionary)


def test_WeakValueDictionary_eq():
    relations_1 = {WeakReferencable(x): x for x in range(3)}
    relations_2 = {WeakReferencable(x): x for x in range(2)}
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
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert relations[WeakReferencable(2)] == 2
    
    with pytest.raises(KeyError):
        weak_value_dictionary[WeakReferencable(6)]
    
    with pytest.raises(KeyError):
        weak_value_dictionary_empty[WeakReferencable(6)]


def test_WeakValueDictionary_iter():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert iter(weak_value_dictionary) == weak_value_dictionary.keys()
    assert iter(weak_value_dictionary_empty) == weak_value_dictionary_empty.keys()


def test_WeakValueDictionary_len():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    assert len(weak_value_dictionary) == len(relations)
    assert len(weak_value_dictionary_empty) == 0


def test_WeakValueDictionary_setitem():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    
    key = WeakReferencable(4)
    value = 4
    
    relations[key] = value
    assert weak_value_dictionary[key] == value
    assert len(weak_value_dictionary) == 4
    
    key = WeakReferencable(3)
    value = 6
    
    weak_value_dictionary[key] = value
    assert weak_value_dictionary[key] == value
    assert len(weak_value_dictionary) == 4


# methods


def test_WeakValueDictionary_clear():
    relations = {WeakReferencable(x): x for x in range(3)}
    
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
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    test_case = weak_value_dictionary.copy()
    
    assert test_case is not weak_value_dictionary
    assert test_case == weak_value_dictionary
    
    test_case = weak_value_dictionary_empty.copy()
    assert test_case is not weak_value_dictionary_empty
    assert test_case == weak_value_dictionary_empty


def test_WeakValueDictionary_items():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    item_1 = (WeakReferencable(2), 2)
    item_2 = (WeakReferencable(6), 6)
    item_3 = (WeakReferencable(2), 6)
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    items = weak_value_dictionary.items()
    
    assert len(items) == len(weak_value_dictionary)
    assert sorted(items) == sorted((key, weak_value_dictionary[key])  for key in weak_value_dictionary.keys())
    assert item_1 in items
    assert not (item_2 in items)
    assert not (item_3 in items)
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    items = weak_value_dictionary_empty.values()
    
    assert len(items) == len(weak_value_dictionary_empty)
    assert sorted(items) == sorted((key, weak_value_dictionary[key])  for key in weak_value_dictionary.keys())
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)


def test_WeakValueDictionary_keys():
    relations = {WeakReferencable(x): x for x in range(3)}
    key_1 = WeakReferencable(2)
    key_2 = WeakReferencable(6)
    
    
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
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(2)
    value_1 = 2
    
    key_2 = WeakReferencable(6)
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    assert weak_value_dictionary.pop(key_1) == value_1
    assert len(weak_value_dictionary) == 2
    
    
    with pytest.raises(KeyError):
        weak_value_dictionary.pop(key_2)
    
    assert len(weak_value_dictionary) == 2


def test_WeakValueDictionary_popitem():
    relations = {WeakReferencable(x): x for x in range(2)}
    
    item_1 = (WeakReferencable(1), 1)
    item_2 = (WeakReferencable(1), 1)
    
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
    relations = {WeakReferencable(x): x for x in range(2)}
    
    key_1 = WeakReferencable(6)
    value_1 = 6
    expected_value_1 = value_1
    
    key_2 = WeakReferencable(1)
    value_2 = 6
    expected_value_2 = 1
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    value = weak_value_dictionary.set_default(key_1, value_1)
    assert value == expected_value_1
    assert len(weak_value_dictionary) == 3
    
    
    value = weak_value_dictionary.set_default(key_2, value_2)
    assert value == expected_value_2
    assert len(weak_value_dictionary) == 3
    assert weak_value_dictionary[key_2] == expected_value_2


def test_WeakValueDictionary_update():
    relations_1 = {WeakReferencable(x): x for x in range(2)}
    relations_2 = {WeakReferencable(x): x+1 for x in range(3)}
    relations_3 = {WeakReferencable(x): x-1 for x in range(1)}
    
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
    relations = {WeakReferencable(x): x for x in range(3)}
    
    value_1 = 2
    value_2 = 6
    
    
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
