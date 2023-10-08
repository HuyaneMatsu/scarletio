from ..weak_item_dictionary import WeakItemDictionary

from .weak_helpers import WeakReferencable

import vampytest


# Test WeakItemDictionary

# Test constructor

def test__WeakItemDictionary__constructor():
    weak_item_dictionary = WeakItemDictionary()
    vampytest.assert_eq(len(weak_item_dictionary), 0)
    vampytest.assert_eq(sorted(weak_item_dictionary), [])


def test__WeakItemDictionary__constructor_empty():
    weak_item_dictionary = WeakItemDictionary([])
    vampytest.assert_eq(len(weak_item_dictionary), 0)
    vampytest.assert_eq(sorted(weak_item_dictionary.items()), [])


def test__WeakItemDictionary__constructor_filled():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary = WeakItemDictionary(relations)
    vampytest.assert_eq(len(weak_item_dictionary), len(relations))
    vampytest.assert_eq(sorted(weak_item_dictionary.items()), sorted(relations.items()))


# test magic methods


def test__WeakItemDictionary__contains():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    key_1 = WeakReferencable(0)
    key_2 = WeakReferencable(10)
    key_3 = 62
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    vampytest.assert_in(key_1, weak_item_dictionary)
    vampytest.assert_not_in(key_2, weak_item_dictionary)
    vampytest.assert_not_in(key_3, weak_item_dictionary)


def test__WeakItemDictionary__eq():
    relations_1 = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    relations_2 = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_item_dictionary_1 = WeakItemDictionary(relations_1)
    weak_item_dictionary_2 = WeakItemDictionary(relations_2)
    weak_item_dictionary_3 = WeakItemDictionary(relations_3)
    
    vampytest.assert_eq(weak_item_dictionary_1, weak_item_dictionary_1)
    vampytest.assert_eq(weak_item_dictionary_1, weak_item_dictionary_2, reverse = True)
    vampytest.assert_eq(weak_item_dictionary_1, weak_item_dictionary_3, reverse = True)
    
    vampytest.assert_eq(weak_item_dictionary_1, relations_1)
    vampytest.assert_eq(weak_item_dictionary_1, relations_2, reverse = True)
    vampytest.assert_eq(weak_item_dictionary_1, relations_3, reverse = True)

    vampytest.assert_is(weak_item_dictionary_1.__eq__([1, ]), NotImplemented)
    vampytest.assert_is(weak_item_dictionary_1.__eq__(1), NotImplemented)


def test__WeakItemDictionary__getitem():
    relations = {WeakReferencable(x): WeakReferencable(x + 4) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    key_1 = WeakReferencable(2)
    value_1 = WeakReferencable(6)
    
    
    key_2 = WeakReferencable(6)
    
    key_3 = WeakReferencable(6)
    
    vampytest.assert_eq(relations[key_1], value_1)
    
    with vampytest.assert_raises(KeyError):
        weak_item_dictionary[key_2]
    
    with vampytest.assert_raises(KeyError):
        weak_item_dictionary_empty[key_3]


def test__WeakItemDictionary__iter():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    vampytest.assert_eq(sorted(iter(weak_item_dictionary)), sorted(weak_item_dictionary.keys()))
    vampytest.assert_eq(sorted(iter(weak_item_dictionary_empty)), sorted(weak_item_dictionary_empty.keys()))


def test__WeakItemDictionary__len():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    vampytest.assert_eq(len(weak_item_dictionary), len(relations))
    vampytest.assert_eq(len(weak_item_dictionary_empty), 0)


def test__WeakItemDictionary__ne():
    relations_1 = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    relations_2 = {WeakReferencable(x): WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_item_dictionary_1 = WeakItemDictionary(relations_1)
    weak_item_dictionary_2 = WeakItemDictionary(relations_2)
    weak_item_dictionary_3 = WeakItemDictionary(relations_3)
    
    vampytest.assert_ne(weak_item_dictionary_1, weak_item_dictionary_1, reverse = True)
    vampytest.assert_ne(weak_item_dictionary_1, weak_item_dictionary_2)
    vampytest.assert_ne(weak_item_dictionary_1, weak_item_dictionary_3)
    
    vampytest.assert_ne(weak_item_dictionary_1, relations_1, reverse = True)
    vampytest.assert_ne(weak_item_dictionary_1, relations_2)
    vampytest.assert_ne(weak_item_dictionary_1, relations_3)

    vampytest.assert_is(weak_item_dictionary_1.__ne__([1, ]), NotImplemented)
    vampytest.assert_is(weak_item_dictionary_1.__ne__(1), NotImplemented)


def test__WeakItemDictionary__setitem():
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
    vampytest.assert_eq(weak_item_dictionary[key_1], value_1)
    vampytest.assert_eq(len(weak_item_dictionary), 4)
    
    weak_item_dictionary[key_2] = value_2
    vampytest.assert_eq(weak_item_dictionary[key_2], value_2)
    vampytest.assert_eq(len(weak_item_dictionary), 5)
    
    with vampytest.assert_raises(TypeError):
        weak_item_dictionary[key_3] = value_3
    
    with vampytest.assert_raises(TypeError):
        weak_item_dictionary[key_4] = value_4


# methods


def test__WeakItemDictionary__clear():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    test_case = WeakItemDictionary(relations)
    test_case.clear()
    vampytest.assert_eq(test_case, weak_item_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)
    
    
    test_case = WeakItemDictionary()
    test_case.clear()
    vampytest.assert_eq(test_case, weak_item_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakItemDictionary__copy():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    weak_item_dictionary = WeakItemDictionary(relations)
    weak_item_dictionary_empty = WeakItemDictionary()
    
    test_case = weak_item_dictionary.copy()
    
    vampytest.assert_is_not(test_case, weak_item_dictionary)
    vampytest.assert_eq(test_case, weak_item_dictionary)
    
    test_case = weak_item_dictionary_empty.copy()
    vampytest.assert_is_not(test_case, weak_item_dictionary_empty)
    vampytest.assert_eq(test_case, weak_item_dictionary_empty)


def test__WeakItemDictionary__get():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    weak_item_dictionary = WeakItemDictionary(relations)
    
    key_1 = WeakReferencable(1)
    value_1 = WeakReferencable(1)
    
    key_2 = WeakReferencable(6)
    
    vampytest.assert_eq(weak_item_dictionary.get(key_1), value_1)
    vampytest.assert_is(weak_item_dictionary.get(key_2), None)


def test__WeakItemDictionary__items():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    item_1 = (WeakReferencable(2), WeakReferencable(2))
    item_2 = (WeakReferencable(6), WeakReferencable(6))
    item_3 = (WeakReferencable(2), WeakReferencable(6))
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    items = weak_item_dictionary.items()
    
    vampytest.assert_eq(len(items), len(weak_item_dictionary))
    vampytest.assert_eq(sorted(items), sorted((key, weak_item_dictionary[key]) for key in weak_item_dictionary.keys()))
    vampytest.assert_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    items = weak_item_dictionary_empty.values()
    
    vampytest.assert_eq(len(items), len(weak_item_dictionary_empty))
    vampytest.assert_eq(sorted(items), sorted((key, weak_item_dictionary_empty[key]) for key in weak_item_dictionary_empty.keys()))
    vampytest.assert_not_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)


def test__WeakItemDictionary__keys():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    key_1 = WeakReferencable(2)
    key_2 = WeakReferencable(6)
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    keys = weak_item_dictionary.keys()
    
    vampytest.assert_eq(len(keys), len(weak_item_dictionary))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_item_dictionary.items()))
    vampytest.assert_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


    weak_item_dictionary_empty = WeakItemDictionary()
    
    keys = weak_item_dictionary_empty.keys()
    
    vampytest.assert_eq(len(keys), len(weak_item_dictionary_empty))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_item_dictionary_empty.items()))
    vampytest.assert_not_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


def test__WeakItemDictionary__pop():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    key_1 = WeakReferencable(2)
    value_1 = WeakReferencable(2)
    
    key_2 = WeakReferencable(6)
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    vampytest.assert_eq(weak_item_dictionary.pop(key_1), value_1)
    vampytest.assert_eq(len(weak_item_dictionary), 2)
    
    
    with vampytest.assert_raises(KeyError):
        weak_item_dictionary.pop(key_2)
    
    vampytest.assert_eq(len(weak_item_dictionary), 2)


def test__WeakItemDictionary__popitem():
    item_1 = (WeakReferencable(1), WeakReferencable(1))
    item_2 = (WeakReferencable(2), WeakReferencable(2))
    relations = dict([item_1, item_2])
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    popped_item_1 = weak_item_dictionary.popitem()
    vampytest.assert_true((popped_item_1 == item_1) or (popped_item_1 == item_2))
    vampytest.assert_eq(len(weak_item_dictionary), 1)
    
    popped_item_2 = weak_item_dictionary.popitem()
    vampytest.assert_true((popped_item_2 == item_1) or (popped_item_2 == item_2))
    vampytest.assert_ne(popped_item_1, popped_item_2)
    vampytest.assert_eq(len(weak_item_dictionary), 0)
    
    with vampytest.assert_raises(KeyError):
        weak_item_dictionary.popitem()
    
    vampytest.assert_eq(len(weak_item_dictionary), 0)


def test__WeakItemDictionary__setdefault():
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
    vampytest.assert_eq(value, expected_value_1)
    vampytest.assert_eq(len(weak_item_dictionary), 3)
    
    
    value = weak_item_dictionary.setdefault(key_2, value_2)
    vampytest.assert_eq(value, expected_value_2)
    vampytest.assert_eq(len(weak_item_dictionary), 3)
    vampytest.assert_eq(weak_item_dictionary[key_2], expected_value_2)

    with vampytest.assert_raises(TypeError):
        weak_item_dictionary.setdefault(key_3, value_3)


def test__WeakItemDictionary__update():
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
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(weak_item_dictionary_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(weak_item_dictionary_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_1)
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(relations_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_item_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    vampytest.assert_eq(test_case, relations_update_1_3)


    test_case = WeakItemDictionary()
    with vampytest.assert_raises(TypeError):
        test_case.update([1, ])
    
    with vampytest.assert_raises(TypeError):
        test_case.update(1)

    with vampytest.assert_raises(ValueError):
        test_case.update([(1,), ])


def test__WeakItemDictionary__values():
    relations = {WeakReferencable(x): WeakReferencable(x) for x in range(3)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    weak_item_dictionary = WeakItemDictionary(relations)
    
    values = weak_item_dictionary.values()
    
    vampytest.assert_eq(len(values), len(weak_item_dictionary))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_item_dictionary.items()))
    vampytest.assert_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
    
    weak_item_dictionary_empty = WeakItemDictionary()
    
    values = weak_item_dictionary_empty.values()
    
    vampytest.assert_eq(len(values), len(weak_item_dictionary_empty))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_item_dictionary_empty.items()))
    vampytest.assert_not_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
