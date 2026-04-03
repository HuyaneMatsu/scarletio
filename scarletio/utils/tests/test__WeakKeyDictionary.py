import gc

import vampytest

from ..weak_key_dictionary import WeakKeyDictionary

from .weak_helpers import WeakReferencable


# Test WeakKeyDictionary

# Test constructor

def test__WeakKeyDictionary__constructor():
    weak_key_dictionary = WeakKeyDictionary()
    vampytest.assert_eq(len(weak_key_dictionary), 0)
    vampytest.assert_eq(sorted(weak_key_dictionary), [])


def test__WeakKeyDictionary__constructor_empty():
    weak_key_dictionary = WeakKeyDictionary([])
    vampytest.assert_eq(len(weak_key_dictionary), 0)
    vampytest.assert_eq(sorted(weak_key_dictionary), [])


def test__WeakKeyDictionary__constructor_filled():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    vampytest.assert_eq(len(weak_key_dictionary), len(relations))
    vampytest.assert_eq(sorted(weak_key_dictionary.items()), sorted(relations.items()))


# test magic methods


def test__WeakKeyDictionary__contains():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(0)
    key_2 = WeakReferencable(10)
    key_3 = 62
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    vampytest.assert_in(key_1, weak_key_dictionary)
    vampytest.assert_not_in(key_2, weak_key_dictionary)
    vampytest.assert_not_in(key_3, weak_key_dictionary)


def test__WeakKeyDictionary__eq():
    relations_1 = {WeakReferencable(x): x for x in range(3)}
    relations_2 = {WeakReferencable(x): x for x in range(2)}
    relations_3 = {}
    
    weak_key_dictionary_1 = WeakKeyDictionary(relations_1)
    weak_key_dictionary_2 = WeakKeyDictionary(relations_2)
    weak_key_dictionary_3 = WeakKeyDictionary(relations_3)
    
    vampytest.assert_eq(weak_key_dictionary_1, weak_key_dictionary_1)
    vampytest.assert_eq(weak_key_dictionary_1, weak_key_dictionary_2, reverse = True)
    vampytest.assert_eq(weak_key_dictionary_1, weak_key_dictionary_3, reverse = True)
    
    vampytest.assert_eq(weak_key_dictionary_1, relations_1)
    vampytest.assert_eq(weak_key_dictionary_1, relations_2, reverse = True)
    vampytest.assert_eq(weak_key_dictionary_1, relations_3, reverse = True)


    vampytest.assert_is(weak_key_dictionary_1.__eq__([1, ]), NotImplemented)
    vampytest.assert_is(weak_key_dictionary_1.__eq__(1), NotImplemented)


def test__WeakKeyDictionary__getitem():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    vampytest.assert_eq(relations[WeakReferencable(2)], 2)
    
    with vampytest.assert_raises(KeyError):
        weak_key_dictionary[WeakReferencable(6)]
    
    with vampytest.assert_raises(KeyError):
        weak_key_dictionary_empty[WeakReferencable(6)]


def test__WeakKeyDictionary__iter():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    vampytest.assert_eq(sorted(iter(weak_key_dictionary)), sorted(weak_key_dictionary.keys()))
    vampytest.assert_eq(sorted(iter(weak_key_dictionary_empty)), sorted(weak_key_dictionary_empty.keys()))


def test__WeakKeyDictionary__len():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    vampytest.assert_eq(len(weak_key_dictionary), len(relations))
    vampytest.assert_eq(len(weak_key_dictionary_empty), 0)


def test__WeakKeyDictionary__ne():
    relations_1 = {WeakReferencable(x): x for x in range(3)}
    relations_2 = {WeakReferencable(x): x for x in range(2)}
    relations_3 = {}
    
    weak_key_dictionary_1 = WeakKeyDictionary(relations_1)
    weak_key_dictionary_2 = WeakKeyDictionary(relations_2)
    weak_key_dictionary_3 = WeakKeyDictionary(relations_3)
    
    vampytest.assert_ne(weak_key_dictionary_1, weak_key_dictionary_1, reverse = True)
    vampytest.assert_ne(weak_key_dictionary_1, weak_key_dictionary_2)
    vampytest.assert_ne(weak_key_dictionary_1, weak_key_dictionary_3)
    
    vampytest.assert_ne(weak_key_dictionary_1, relations_1, reverse = True)
    vampytest.assert_ne(weak_key_dictionary_1, relations_2)
    vampytest.assert_ne(weak_key_dictionary_1, relations_3)


    vampytest.assert_is(weak_key_dictionary_1.__ne__([1, ]), NotImplemented)
    vampytest.assert_is(weak_key_dictionary_1.__ne__(1), NotImplemented)


def test__WeakKeyDictionary__setitem():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    key = WeakReferencable(4)
    value = 4
    
    weak_key_dictionary[key] = value
    vampytest.assert_eq(weak_key_dictionary[key], value)
    vampytest.assert_eq(len(weak_key_dictionary), 4)
    
    key = WeakReferencable(3)
    value = 6
    weak_key_dictionary[key] = value
    
    gc.collect()
    
    vampytest.assert_eq(weak_key_dictionary[key], value)
    vampytest.assert_eq(len(weak_key_dictionary), 4)

    key = 6
    value = 9
    
    with vampytest.assert_raises(TypeError):
        weak_key_dictionary[key] = value

# methods


def test__WeakKeyDictionary__clear():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    test_case = WeakKeyDictionary(relations)
    test_case.clear()
    vampytest.assert_eq(test_case, weak_key_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)
    
    
    test_case = WeakKeyDictionary()
    test_case.clear()
    vampytest.assert_eq(test_case, weak_key_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakKeyDictionary__copy():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    test_case = weak_key_dictionary.copy()
    
    vampytest.assert_is_not(test_case, weak_key_dictionary)
    vampytest.assert_eq(test_case, weak_key_dictionary)
    
    test_case = weak_key_dictionary_empty.copy()
    vampytest.assert_is_not(test_case, weak_key_dictionary_empty)
    vampytest.assert_eq(test_case, weak_key_dictionary_empty)


def test__WeakKeyDictionary__get():
    relations = {WeakReferencable(x): x for x in range(3)}
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    key_1 = WeakReferencable(1)
    value_1 = 1
    
    key_2 = WeakReferencable(6)
    
    vampytest.assert_eq(weak_key_dictionary.get(key_1), value_1)
    vampytest.assert_is(weak_key_dictionary.get(key_2), None)


def test__WeakKeyDictionary__items():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    item_1 = (WeakReferencable(2), 2)
    item_2 = (WeakReferencable(6), 6)
    item_3 = (WeakReferencable(2), 6)
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    items = weak_key_dictionary.items()
    
    vampytest.assert_eq(len(items), len(weak_key_dictionary))
    vampytest.assert_eq(sorted(items), sorted((key, weak_key_dictionary[key]) for key in weak_key_dictionary.keys()))
    vampytest.assert_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    items = weak_key_dictionary_empty.values()
    
    vampytest.assert_eq(len(items), len(weak_key_dictionary_empty))
    vampytest.assert_eq(sorted(items), sorted((key, weak_key_dictionary_empty[key]) for key in weak_key_dictionary_empty.keys()))
    vampytest.assert_not_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)


def test__WeakKeyDictionary__keys():
    relations = {WeakReferencable(x): x for x in range(3)}
    key_1 = WeakReferencable(2)
    key_2 = WeakReferencable(6)
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    keys = weak_key_dictionary.keys()
    
    vampytest.assert_eq(len(keys), len(weak_key_dictionary))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_key_dictionary.items()))
    vampytest.assert_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


    weak_key_dictionary_empty = WeakKeyDictionary()
    
    keys = weak_key_dictionary_empty.keys()
    
    vampytest.assert_eq(len(keys), len(weak_key_dictionary_empty))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_key_dictionary_empty.items()))
    vampytest.assert_not_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


def test__WeakKeyDictionary__pop():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    key_1 = WeakReferencable(2)
    value_1 = 2
    
    key_2 = WeakReferencable(6)
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    vampytest.assert_eq(weak_key_dictionary.pop(key_1), value_1)
    vampytest.assert_eq(len(weak_key_dictionary), 2)
    
    
    with vampytest.assert_raises(KeyError):
        weak_key_dictionary.pop(key_2)
    
    vampytest.assert_eq(len(weak_key_dictionary), 2)


def test__WeakKeyDictionary__popitem():
    item_1 = (WeakReferencable(1), 1)
    item_2 = (WeakReferencable(2), 2)
    relations = dict([item_1, item_2])
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    popped_item_1 = weak_key_dictionary.popitem()
    vampytest.assert_true((popped_item_1 == item_1) or (popped_item_1 == item_2))
    vampytest.assert_eq(len(weak_key_dictionary), 1)
    
    popped_item_2 = weak_key_dictionary.popitem()
    vampytest.assert_true((popped_item_2 == item_1) or (popped_item_2 == item_2))
    vampytest.assert_ne(popped_item_1, popped_item_2)
    vampytest.assert_eq(len(weak_key_dictionary), 0)
    
    with vampytest.assert_raises(KeyError):
        weak_key_dictionary.popitem()
    
    vampytest.assert_eq(len(weak_key_dictionary), 0)


def test__WeakKeyDictionary__setdefault():
    relations = {WeakReferencable(x): x for x in range(2)}
    
    key_1 = WeakReferencable(6)
    value_1 = 6
    expected_value_1 = value_1
    
    key_2 = WeakReferencable(1)
    value_2 = 6
    expected_value_2 = 1
    
    key_3 = 7
    value_3 = 9
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    value = weak_key_dictionary.setdefault(key_1, value_1)
    vampytest.assert_eq(value, expected_value_1)
    vampytest.assert_eq(len(weak_key_dictionary), 3)
    
    
    value = weak_key_dictionary.setdefault(key_2, value_2)
    vampytest.assert_eq(value, expected_value_2)
    vampytest.assert_eq(len(weak_key_dictionary), 3)
    vampytest.assert_eq(weak_key_dictionary[key_2], expected_value_2)

    with vampytest.assert_raises(TypeError):
        weak_key_dictionary.setdefault(key_3, value_3)


def test__WeakKeyDictionary__update():
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
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(weak_key_dictionary_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(weak_key_dictionary_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_1)
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(relations_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_key_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    vampytest.assert_eq(test_case, relations_update_1_3)


    test_case = WeakKeyDictionary()
    with vampytest.assert_raises(TypeError):
        test_case.update([1, ])
    
    with vampytest.assert_raises(TypeError):
        test_case.update(1)

    with vampytest.assert_raises(ValueError):
        test_case.update([(1,), ])


def test__WeakKeyDictionary__values():
    relations = {WeakReferencable(x): x for x in range(3)}
    
    value_1 = 2
    value_2 = 6
    
    
    weak_key_dictionary = WeakKeyDictionary(relations)
    
    values = weak_key_dictionary.values()
    
    vampytest.assert_eq(len(values), len(weak_key_dictionary))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_key_dictionary.items()))
    vampytest.assert_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
    
    weak_key_dictionary_empty = WeakKeyDictionary()
    
    values = weak_key_dictionary_empty.values()
    
    vampytest.assert_eq(len(values), len(weak_key_dictionary_empty))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_key_dictionary_empty.items()))
    vampytest.assert_not_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
