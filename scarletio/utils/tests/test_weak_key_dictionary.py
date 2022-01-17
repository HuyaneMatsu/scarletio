import pytest

from weak_helpers import WeakReferencable

from scarletio import WeakKeyDictionary


# Test WeakKeyDictionary

# Test constructor

def test_WeakKeyDictionary_constructor():
    weak_key_dictionary = WeakKeyDictionary()
    assert len(weak_key_dictionary) == 0
    assert sorted(weak_key_dictionary) == []


def test_WeakKeyDictionary_constructor_empty():
    weak_key_dictionary = WeakKeyDictionary([])
    assert len(weak_key_dictionary) == 0
    assert sorted(weak_key_dictionary) == []


def test_WeakKeyDictionary_constructor_filled():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    assert len(weak_key_dictionary) == len(relations)
    assert sorted(weak_key_dictionary) == relations


# test magic methods


def test_WeakKeyDictionary_contains():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(0)
    key_2 = WeakReferencable(10)
    key_3 = 62
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    assert key_1 in weak_key_dictionary
    assert not (key_2 in weak_key_dictionary)
    assert not (key_3 in weak_key_dictionary)


def test_WeakKeyDictionary_eq():
    relations_1 = {WeakReferencable(x): x for x in range(3)}
    relations_2 = {WeakReferencable(x): x for x in range(2)}
    relations_3 = {}
    
    weak_key_dictionary_1 = WeakKeyDictionary(relations_1)
    weak_key_dictionary_2 = WeakKeyDictionary(relations_2)
    weak_key_dictionary_3 = WeakKeyDictionary(relations_3)
    
    assert weak_key_dictionary_1 == weak_key_dictionary_1
    assert not (weak_key_dictionary_1 == weak_key_dictionary_2)
    assert not (weak_key_dictionary_1 == weak_key_dictionary_3)
    
    assert weak_key_dictionary_1 == relations_1
    assert not (weak_key_dictionary_1 == relations_2)
    assert not (weak_key_dictionary_1 == relations_3)


def test_WeakKeyDictionary_getitem():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    assert relations[WeakReferencable(2)] == 2
    
    with pytest.raises(KeyError):
        weak_key_dictionary[WeakReferencable(6)]
    
    with pytest.raises(KeyError):
        weak_key_dictionary_empty[WeakReferencable(6)]


def test_WeakKeyDictionary_iter():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    assert list(iter(weak_key_dictionary)) == list(weak_key_dictionary.keys())
    assert list(iter(weak_key_dictionary_empty)) == list(weak_key_dictionary_empty.keys())


def test_WeakKeyDictionary_len():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    assert len(weak_key_dictionary) == len(relations)
    assert len(weak_key_dictionary_empty) == 0


def test_WeakKeyDictionary_ne():
    relations_1 = {WeakReferencable(x): x for x in range(3)}
    relations_2 = {WeakReferencable(x): x for x in range(2)}
    relations_3 = {}
    
    weak_key_dictionary_1 = WeakKeyDictionary(relations_1)
    weak_key_dictionary_2 = WeakKeyDictionary(relations_2)
    weak_key_dictionary_3 = WeakKeyDictionary(relations_3)
    
    assert not (weak_key_dictionary_1 != weak_key_dictionary_1)
    assert weak_key_dictionary_1 != weak_key_dictionary_2
    assert weak_key_dictionary_1 != weak_key_dictionary_3
    
    assert not (weak_key_dictionary_1 != relations_1)
    assert weak_key_dictionary_1 != relations_2
    assert weak_key_dictionary_1 != relations_3


def test_WeakKeyDictionary_setitem():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    key = WeakReferencable(4)
    value = 4
    
    relations[key] = value
    assert weak_key_dictionary[key] == value
    assert len(weak_key_dictionary) == 4
    
    key = WeakReferencable(3)
    value = 6
    
    weak_key_dictionary[key] = value
    assert weak_key_dictionary[key] == value
    assert len(weak_key_dictionary) == 4


# methods


def test_WeakKeyDictionary_clear():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    test_case = WeakKeyDictionary(relations)
    test_case.clear()
    assert test_case == weak_key_dictionary_empty
    assert len(test_case) == 0
    
    
    test_case = WeakKeyDictionary()
    test_case.clear()
    assert test_case == weak_key_dictionary_empty
    assert len(test_case) == 0


def test_WeakKeyDictionary_copy():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    test_case = weak_key_dictionary.copy()
    
    assert test_case is not weak_key_dictionary
    assert test_case == weak_key_dictionary
    
    test_case = weak_key_dictionary_empty.copy()
    assert test_case is not weak_key_dictionary_empty
    assert test_case == weak_key_dictionary_empty


def test_WeakKeyDictionary_get():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    key_1 = WeakReferencable(1)
    value_1 = 1
    
    key_2 = WeakReferencable(6)
    
    assert weak_key_dictionary.get(key_1) == value_1
    assert weak_key_dictionary.get(key_2) is None


def test_WeakKeyDictionary_items():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    item_1 = (WeakReferencable(2), 2)
    item_2 = (WeakReferencable(6), 6)
    item_3 = (WeakReferencable(2), 6)
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    items = weak_key_dictionary.items()
    
    assert len(items) == len(weak_key_dictionary)
    assert sorted(items) == sorted((key, weak_key_dictionary[key]) for key in weak_key_dictionary.keys())
    assert item_1 in items
    assert not (item_2 in items)
    assert not (item_3 in items)
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    items = weak_key_dictionary_empty.values()
    
    assert len(items) == len(weak_key_dictionary_empty)
    assert sorted(items) == sorted((key, weak_key_dictionary[key]) for key in weak_key_dictionary.keys())
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)


def test_WeakKeyDictionary_keys():
    relations = {WeakReferencable(x): x for x in range(3)}
    key_1 = WeakReferencable(2)
    key_2 = WeakReferencable(6)
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    keys = weak_key_dictionary.keys()
    
    assert len(keys) == len(weak_key_dictionary)
    assert set(keys) == set(key for key, value in weak_key_dictionary.items())
    assert key_1 in keys
    assert not (key_2 in keys)


    weak_key_dictionary_empty = WeakKeyDictionary()
    
    keys = weak_key_dictionary_empty.keys()
    
    assert len(keys) == len(weak_key_dictionary_empty)
    assert set(keys) == set(key for key, value in weak_key_dictionary_empty.items())
    assert not (key_1 in keys)
    assert not (key_2 in keys)


def test_WeakKeyDictionary_pop():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(2)
    value_1 = 2
    
    key_2 = WeakReferencable(6)
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    assert weak_key_dictionary.pop(key_1) == value_1
    assert len(weak_key_dictionary) == 2
    
    
    with pytest.raises(KeyError):
        weak_key_dictionary.pop(key_2)
    
    assert len(weak_key_dictionary) == 2


def test_WeakKeyDictionary_popitem():
    relations = {WeakReferencable(x): x for x in range(2)}
    
    item_1 = (WeakReferencable(1), 1)
    item_2 = (WeakReferencable(2), 2)
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    popped_item_1 = weak_key_dictionary.popitem()
    assert (popped_item_1 == item_1) or (popped_item_1 == item_2)
    assert len(weak_key_dictionary) == 1
    
    popped_item_2 = weak_key_dictionary.popitem()
    assert (popped_item_2 == item_1) or (popped_item_2 == item_2)
    assert popped_item_1 != popped_item_2
    assert len(weak_key_dictionary) == 0
    
    with pytest.raises(KeyError):
        weak_key_dictionary.popitem()
    
    assert len(weak_key_dictionary) == 0


def test_WeakKeyDictionary_setdefault():
    relations = {WeakReferencable(x): x for x in range(2)}
    
    key_1 = WeakReferencable(6)
    value_1 = 6
    expected_value_1 = value_1
    
    key_2 = WeakReferencable(1)
    value_2 = 6
    expected_value_2 = 1
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    value = weak_key_dictionary.set_default(key_1, value_1)
    assert value == expected_value_1
    assert len(weak_key_dictionary) == 3
    
    
    value = weak_key_dictionary.set_default(key_2, value_2)
    assert value == expected_value_2
    assert len(weak_key_dictionary) == 3
    assert weak_key_dictionary[key_2] == expected_value_2


def test_WeakKeyDictionary_update():
    relations_1 = {WeakReferencable(x): x for x in range(2)}
    relations_2 = {WeakReferencable(x): x+1 for x in range(3)}
    relations_3 = {WeakReferencable(x): x-1 for x in range(1)}
    
    relations_update_1_2 = relations_1.copy()
    relations_update_1_2.update(relations_2)
    
    relations_update_1_3 = relations_1.copy()
    relations_update_1_3.update(relations_3)
    
    weak_key_dictionary_1 = WeakKeyDictionary(relations_1)
    weak_key_dictionary_2 = WeakKeyDictionary(relations_2)
    weak_key_dictionary_3 = WeakKeyDictionary(relations_3)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(weak_key_dictionary_1)
    assert test_case == relations_1
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(weak_key_dictionary_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(weak_key_dictionary_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_1)
    assert test_case == relations_1
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_2)
    assert test_case == relations_update_1_2
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_3)
    assert test_case == relations_update_1_3
    
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    assert test_case == relations_1
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    assert test_case == relations_update_1_2
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    assert test_case == relations_update_1_3


def test_WeakKeyDictionary_values():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    value_1 = 2
    value_2 = 6
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    values = weak_key_dictionary.values()
    
    assert len(values) == len(weak_key_dictionary)
    assert sorted(values) == sorted(value for key, value in weak_key_dictionary.items())
    assert value_1 in values
    assert not (value_2 in values)
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    values = weak_key_dictionary_empty.values()
    
    assert len(values) == len(weak_key_dictionary_empty)
    assert sorted(values) == sorted(value for key, value in weak_key_dictionary_empty.items())
    assert not (value_1 in values)
    assert not (value_2 in values)
