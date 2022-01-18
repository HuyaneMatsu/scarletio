import pytest

from weak_helpers import WeakReferencable, sort_by_type_first_key

from scarletio import HybridValueDictionary


# Test HybridValueDictionary

# Test constructor

def test_HybridValueDictionary_constructor():
    hybrid_value_dictionary = HybridValueDictionary()
    assert len(hybrid_value_dictionary) == 0
    assert sorted(hybrid_value_dictionary) == []


def test_HybridValueDictionary_constructor_empty():
    hybrid_value_dictionary = HybridValueDictionary([])
    assert len(hybrid_value_dictionary) == 0
    assert sorted(hybrid_value_dictionary) == []


def test_HybridValueDictionary_constructor_filled():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    assert len(hybrid_value_dictionary) == len(relations)
    assert dict(hybrid_value_dictionary.items()) == relations


# test magic methods


def test_HybridValueDictionary_contains():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 0
    key_2 = 10
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    assert key_1 in hybrid_value_dictionary
    assert not (key_2 in hybrid_value_dictionary)


def test_HybridValueDictionary_eq():
    relations_1 = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    relations_2 = {0: WeakReferencable(0), 1: 1}
    relations_3 = {}
    
    hybrid_value_dictionary_1 = HybridValueDictionary(relations_1)
    hybrid_value_dictionary_2 = HybridValueDictionary(relations_2)
    hybrid_value_dictionary_3 = HybridValueDictionary(relations_3)
    
    assert hybrid_value_dictionary_1 == hybrid_value_dictionary_1
    assert not (hybrid_value_dictionary_1 == hybrid_value_dictionary_2)
    assert not (hybrid_value_dictionary_1 == hybrid_value_dictionary_3)
    
    assert hybrid_value_dictionary_1 == relations_1
    assert not (hybrid_value_dictionary_1 == relations_2)
    assert not (hybrid_value_dictionary_1 == relations_3)


def test_HybridValueDictionary_getitem():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    assert relations[2] == WeakReferencable(2)
    
    with pytest.raises(KeyError):
        hybrid_value_dictionary[6]
    
    with pytest.raises(KeyError):
        hybrid_value_dictionary_empty[6]


def test_HybridValueDictionary_iter():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    assert list(iter(hybrid_value_dictionary)) == list(hybrid_value_dictionary.keys())
    assert list(iter(hybrid_value_dictionary_empty)) == list(hybrid_value_dictionary_empty.keys())


def test_HybridValueDictionary_len():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    assert len(hybrid_value_dictionary) == len(relations)
    assert len(hybrid_value_dictionary_empty) == 0


def test_HybridValueDictionary_ne():
    relations_1 = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    hybrid_value_dictionary_1 = HybridValueDictionary(relations_1)
    hybrid_value_dictionary_2 = HybridValueDictionary(relations_2)
    hybrid_value_dictionary_3 = HybridValueDictionary(relations_3)
    
    assert not (hybrid_value_dictionary_1 != hybrid_value_dictionary_1)
    assert hybrid_value_dictionary_1 != hybrid_value_dictionary_2
    assert hybrid_value_dictionary_1 != hybrid_value_dictionary_3
    
    assert not (hybrid_value_dictionary_1 != relations_1)
    assert hybrid_value_dictionary_1 != relations_2
    assert hybrid_value_dictionary_1 != relations_3


def test_HybridValueDictionary_setitem():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    key_1 = 4
    value_1 = WeakReferencable(4)
    
    key_2 = 2
    value_2 = WeakReferencable(6)
    
    key_3 = 6
    value_3 = 9
    
    hybrid_value_dictionary[key_1] = value_1
    assert hybrid_value_dictionary[key_1] == value_1
    assert len(hybrid_value_dictionary) == 4
    
    
    hybrid_value_dictionary[key_2] = value_2
    assert hybrid_value_dictionary[key_2] == value_2
    assert len(hybrid_value_dictionary) == 4
    
    
    hybrid_value_dictionary[key_3] = value_3
    assert hybrid_value_dictionary[key_3] == value_3
    assert len(hybrid_value_dictionary) == 5


# methods


def test_HybridValueDictionary_clear():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    test_case = HybridValueDictionary(relations)
    test_case.clear()
    assert test_case == hybrid_value_dictionary_empty
    assert len(test_case) == 0
    
    
    test_case = HybridValueDictionary()
    test_case.clear()
    assert test_case == hybrid_value_dictionary_empty
    assert len(test_case) == 0


def test_HybridValueDictionary_copy():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    test_case = hybrid_value_dictionary.copy()
    
    assert test_case is not hybrid_value_dictionary
    assert test_case == hybrid_value_dictionary
    
    test_case = hybrid_value_dictionary_empty.copy()
    assert test_case is not hybrid_value_dictionary_empty
    assert test_case == hybrid_value_dictionary_empty


def test_HybridValueDictionary_get():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    key_1 = 1
    value_1 = 1
    
    key_2 = 6
    
    assert hybrid_value_dictionary.get(key_1) == value_1
    assert hybrid_value_dictionary.get(key_2) is None


def test_HybridValueDictionary_items():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    item_1 = (2, WeakReferencable(2))
    item_2 = (6, 6)
    item_3 = (2, WeakReferencable(6))
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    items = hybrid_value_dictionary.items()
    
    assert len(items) == len(hybrid_value_dictionary)
    assert sorted(items) == sorted((key, hybrid_value_dictionary[key]) for key in hybrid_value_dictionary.keys())
    assert item_1 in items
    assert not (item_2 in items)
    assert not (item_3 in items)
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    items = hybrid_value_dictionary_empty.items()
    
    assert len(items) == len(hybrid_value_dictionary_empty)
    assert sorted(items) == sorted(
        (key, hybrid_value_dictionary_empty[key]) for key in hybrid_value_dictionary_empty.keys()
    )
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)


def test_HybridValueDictionary_keys():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    key_1 = 2
    key_2 = 6
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    keys = hybrid_value_dictionary.keys()
    
    assert len(keys) == len(hybrid_value_dictionary)
    assert set(keys) == set(key for key, value in hybrid_value_dictionary.items())
    assert key_1 in keys
    assert not (key_2 in keys)


    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    keys = hybrid_value_dictionary_empty.keys()
    
    assert len(keys) == len(hybrid_value_dictionary_empty)
    assert set(keys) == set(key for key, value in hybrid_value_dictionary_empty.items())
    assert not (key_1 in keys)
    assert not (key_2 in keys)


def test_HybridValueDictionary_pop():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 2
    value_1 = WeakReferencable(2)
    
    key_2 = 6
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    assert hybrid_value_dictionary.pop(key_1) == value_1
    assert len(hybrid_value_dictionary) == 2
    
    
    with pytest.raises(KeyError):
        hybrid_value_dictionary.pop(key_2)
    
    assert len(hybrid_value_dictionary) == 2


def test_HybridValueDictionary_popitem():
    item_1 = (1, 1)
    item_2 = (2, WeakReferencable(2))
    
    relations = dict([item_1, item_2])
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    popped_item_1 = hybrid_value_dictionary.popitem()
    assert (popped_item_1 == item_1) or (popped_item_1 == item_2)
    assert len(hybrid_value_dictionary) == 1
    
    popped_item_2 = hybrid_value_dictionary.popitem()
    assert (popped_item_2 == item_1) or (popped_item_2 == item_2)
    assert popped_item_1 != popped_item_2
    assert len(hybrid_value_dictionary) == 0
    
    with pytest.raises(KeyError):
        hybrid_value_dictionary.popitem()
    
    assert len(hybrid_value_dictionary) == 0


def test_HybridValueDictionary_setdefault():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 6
    value_1 = WeakReferencable(6)
    expected_value_1 = value_1
    
    key_2 = 1
    value_2 = 6
    expected_value_2 = 1
    
    key_3 = 7
    value_3 = 9
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    value = hybrid_value_dictionary.setdefault(key_1, value_1)
    assert value == expected_value_1
    assert len(hybrid_value_dictionary) == 4
    
    
    value = hybrid_value_dictionary.setdefault(key_2, value_2)
    assert value == expected_value_2
    assert len(hybrid_value_dictionary) == 4
    assert hybrid_value_dictionary[key_2] == expected_value_2
    
    with pytest.raises(TypeError):
        hybrid_value_dictionary.setdefault(key_3, value_3)


def test_HybridValueDictionary_update():
    relations_1 = {0: WeakReferencable(0), 1: 1}
    relations_2 = {0: 2, 1: WeakReferencable(4)}
    relations_3 = {1: WeakReferencable(-1)}
    
    relations_update_1_2 = relations_1.copy()
    relations_update_1_2.update(relations_2)
    
    relations_update_1_3 = relations_1.copy()
    relations_update_1_3.update(relations_3)
    
    hybrid_value_dictionary_1 = HybridValueDictionary(relations_1)
    hybrid_value_dictionary_2 = HybridValueDictionary(relations_2)
    hybrid_value_dictionary_3 = HybridValueDictionary(relations_3)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(hybrid_value_dictionary_1)
    assert test_case == relations_1
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(hybrid_value_dictionary_2)
    assert test_case == relations_update_1_2
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(hybrid_value_dictionary_3)
    assert test_case == relations_update_1_3
    
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_1)
    assert test_case == relations_1
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_2)
    assert test_case == relations_update_1_2
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_3)
    assert test_case == relations_update_1_3
    
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    assert test_case == relations_1
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    assert test_case == relations_update_1_2
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    assert test_case == relations_update_1_3


def test_HybridValueDictionary_values():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    values = hybrid_value_dictionary.values()
    
    assert len(values) == len(hybrid_value_dictionary)
    assert sorted(values) == sorted(value for key, value in hybrid_value_dictionary.items())
    assert value_1 in values
    assert not (value_2 in values)
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    values = hybrid_value_dictionary_empty.values()
    
    assert len(values) == len(hybrid_value_dictionary_empty)
    assert sorted(values, key=sort_by_type_first_key) == sorted(
        (value for key, value in hybrid_value_dictionary_empty.items()),
        key = sort_by_type_first_key,
    )
    
    assert not (value_1 in values)
    assert not (value_2 in values)
