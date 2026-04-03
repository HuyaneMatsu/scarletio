from ..weak_value_dictionary import WeakValueDictionary

from .weak_helpers import WeakReferencable

import vampytest


# Test WeakValueDictionary

# Test constructor

def test__WeakValueDictionary__constructor():
    weak_value_dictionary = WeakValueDictionary()
    vampytest.assert_eq(len(weak_value_dictionary), 0)
    vampytest.assert_eq(sorted(weak_value_dictionary), [])


def test__WeakValueDictionary__constructor_empty():
    weak_value_dictionary = WeakValueDictionary([])
    vampytest.assert_eq(len(weak_value_dictionary), 0)
    vampytest.assert_eq(sorted(weak_value_dictionary), [])


def test__WeakValueDictionary__constructor_filled():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    vampytest.assert_eq(len(weak_value_dictionary), len(relations))
    vampytest.assert_eq(sorted(weak_value_dictionary.items()), sorted(relations.items()))


# test magic methods


def test__WeakValueDictionary__contains():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    key_1 = 0
    key_2 = 10
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    vampytest.assert_in(key_1, weak_value_dictionary)
    vampytest.assert_not_in(key_2, weak_value_dictionary)


def test__WeakValueDictionary__eq():
    relations_1 = {x: WeakReferencable(x) for x in range(3)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_value_dictionary_1 = WeakValueDictionary(relations_1)
    weak_value_dictionary_2 = WeakValueDictionary(relations_2)
    weak_value_dictionary_3 = WeakValueDictionary(relations_3)
    
    vampytest.assert_eq(weak_value_dictionary_1, weak_value_dictionary_1)
    vampytest.assert_eq(weak_value_dictionary_1, weak_value_dictionary_2, reverse = True)
    vampytest.assert_eq(weak_value_dictionary_1, weak_value_dictionary_3, reverse = True)
    
    vampytest.assert_eq(weak_value_dictionary_1, relations_1)
    vampytest.assert_eq(weak_value_dictionary_1, relations_2, reverse = True)
    vampytest.assert_eq(weak_value_dictionary_1, relations_3, reverse = True)
    
    
    vampytest.assert_is(weak_value_dictionary_1.__eq__([1, ]), NotImplemented)
    vampytest.assert_is(weak_value_dictionary_1.__eq__(1), NotImplemented)


def test__WeakValueDictionary__getitem():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    vampytest.assert_eq(weak_value_dictionary[2], WeakReferencable(2))
    
    with vampytest.assert_raises(KeyError):
        weak_value_dictionary[6]
    
    with vampytest.assert_raises(KeyError):
        weak_value_dictionary_empty[6]


def test__WeakValueDictionary__iter():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    vampytest.assert_eq(sorted(iter(weak_value_dictionary)), sorted(weak_value_dictionary.keys()))
    vampytest.assert_eq(sorted(iter(weak_value_dictionary_empty)), sorted(weak_value_dictionary_empty.keys()))


def test__WeakValueDictionary__len():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    vampytest.assert_eq(len(weak_value_dictionary), len(relations))
    vampytest.assert_eq(len(weak_value_dictionary_empty), 0)


def test__WeakValueDictionary__ne():
    relations_1 = {x: WeakReferencable(x) for x in range(3)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    weak_value_dictionary_1 = WeakValueDictionary(relations_1)
    weak_value_dictionary_2 = WeakValueDictionary(relations_2)
    weak_value_dictionary_3 = WeakValueDictionary(relations_3)
    
    vampytest.assert_ne(weak_value_dictionary_1, weak_value_dictionary_1, reverse = True)
    vampytest.assert_ne(weak_value_dictionary_1, weak_value_dictionary_2)
    vampytest.assert_ne(weak_value_dictionary_1, weak_value_dictionary_3)
    
    vampytest.assert_ne(weak_value_dictionary_1, relations_1, reverse = True)
    vampytest.assert_ne(weak_value_dictionary_1, relations_2)
    vampytest.assert_ne(weak_value_dictionary_1, relations_3)

    vampytest.assert_is(weak_value_dictionary_1.__ne__([1, ]), NotImplemented)
    vampytest.assert_is(weak_value_dictionary_1.__ne__(1), NotImplemented)


def test__WeakValueDictionary__setitem():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    
    key_1 = 4
    value_1 = WeakReferencable(4)
    
    key_2 = 2
    value_2 = WeakReferencable(6)
    
    key_3 = 6
    value_3 = 9
    
    weak_value_dictionary[key_1] = value_1
    vampytest.assert_eq(weak_value_dictionary[key_1], value_1)
    vampytest.assert_eq(len(weak_value_dictionary), 4)
    
    weak_value_dictionary[key_2] = value_2
    vampytest.assert_eq(weak_value_dictionary[key_2], value_2)
    vampytest.assert_eq(len(weak_value_dictionary), 4)
    
    with vampytest.assert_raises(TypeError):
        weak_value_dictionary[key_3] = value_3


# methods


def test__WeakValueDictionary__clear():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    test_case = WeakValueDictionary(relations)
    test_case.clear()
    vampytest.assert_eq(test_case, weak_value_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)
    
    
    test_case = WeakValueDictionary()
    test_case.clear()
    vampytest.assert_eq(test_case, weak_value_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)


def test__WeakValueDictionary__copy():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    weak_value_dictionary = WeakValueDictionary(relations)
    weak_value_dictionary_empty = WeakValueDictionary()
    
    test_case = weak_value_dictionary.copy()
    
    vampytest.assert_is_not(test_case, weak_value_dictionary)
    vampytest.assert_eq(test_case, weak_value_dictionary)
    
    test_case = weak_value_dictionary_empty.copy()
    vampytest.assert_is_not(test_case, weak_value_dictionary_empty)
    vampytest.assert_eq(test_case, weak_value_dictionary_empty)


def test__WeakValueDictionary__get():
    relations = {x: WeakReferencable(x) for x in range(3)}
    weak_value_dictionary = WeakValueDictionary(relations)
    
    key_1 = 1
    value_1 = WeakReferencable(1)
    
    key_2 = 6
    
    vampytest.assert_eq(weak_value_dictionary.get(key_1), value_1)
    vampytest.assert_is(weak_value_dictionary.get(key_2), None)


def test__WeakValueDictionary__items():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    item_1 = (2, WeakReferencable(2))
    item_2 = (6, WeakReferencable(6))
    item_3 = (2, WeakReferencable(6))
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    items = weak_value_dictionary.items()
    
    vampytest.assert_eq(len(items), len(weak_value_dictionary))
    vampytest.assert_eq(
        sorted(items),
        sorted((key, weak_value_dictionary[key]) for key in weak_value_dictionary.keys()),
    )
    vampytest.assert_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    items = weak_value_dictionary_empty.items()
    
    vampytest.assert_eq(len(items), len(weak_value_dictionary_empty))
    vampytest.assert_eq(
        sorted(items),
        sorted((key, weak_value_dictionary_empty[key]) for key in weak_value_dictionary_empty.keys()),
    )
    vampytest.assert_not_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)


def test__WeakValueDictionary__keys():
    relations = {x: WeakReferencable(x) for x in range(3)}
    key_1 = 2
    key_2 = 6
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    keys = weak_value_dictionary.keys()
    
    vampytest.assert_eq(len(keys), len(weak_value_dictionary))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_value_dictionary.items()))
    vampytest.assert_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


    weak_value_dictionary_empty = WeakValueDictionary()
    
    keys = weak_value_dictionary_empty.keys()
    
    vampytest.assert_eq(len(keys), len(weak_value_dictionary_empty))
    vampytest.assert_eq(set(keys), set(key for key, value in weak_value_dictionary_empty.items()))
    vampytest.assert_not_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


def test__WeakValueDictionary__pop():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    key_1 = 2
    value_1 = WeakReferencable(2)
    
    key_2 = 6
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    vampytest.assert_eq(weak_value_dictionary.pop(key_1), value_1)
    vampytest.assert_eq(len(weak_value_dictionary), 2)
    
    
    with vampytest.assert_raises(KeyError):
        weak_value_dictionary.pop(key_2)
    
    vampytest.assert_eq(len(weak_value_dictionary), 2)


def test__WeakValueDictionary__popitem():
    item_1 = (1, WeakReferencable(1))
    item_2 = (2, WeakReferencable(2))
    
    relations = dict([item_1, item_2])
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    popped_item_1 = weak_value_dictionary.popitem()
    vampytest.assert_true((popped_item_1 == item_1) or (popped_item_1 == item_2))
    vampytest.assert_eq(len(weak_value_dictionary), 1)
    
    popped_item_2 = weak_value_dictionary.popitem()
    vampytest.assert_true((popped_item_2 == item_1) or (popped_item_2 == item_2))
    vampytest.assert_ne(popped_item_1, popped_item_2)
    vampytest.assert_eq(len(weak_value_dictionary), 0)
    
    with vampytest.assert_raises(KeyError):
        weak_value_dictionary.popitem()
    
    vampytest.assert_eq(len(weak_value_dictionary), 0)


def test__WeakValueDictionary__setdefault():
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
    vampytest.assert_eq(value, expected_value_1)
    vampytest.assert_eq(len(weak_value_dictionary), 3)
    
    
    value = weak_value_dictionary.setdefault(key_2, value_2)
    vampytest.assert_eq(value, expected_value_2)
    vampytest.assert_eq(len(weak_value_dictionary), 3)
    vampytest.assert_eq(weak_value_dictionary[key_2], expected_value_2)
    
    with vampytest.assert_raises(TypeError):
        weak_value_dictionary.setdefault(key_3, value_3)


def test__WeakValueDictionary__update():
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
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(weak_value_dictionary_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(weak_value_dictionary_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_1)
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = weak_value_dictionary_1.copy()
    test_case.update(relations_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = WeakValueDictionary()
    with vampytest.assert_raises(TypeError):
        test_case.update([1, ])
    
    with vampytest.assert_raises(TypeError):
        test_case.update(1)

    with vampytest.assert_raises(ValueError):
        test_case.update([(1,), ])


def test__WeakValueDictionary__values():
    relations = {x: WeakReferencable(x) for x in range(3)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    weak_value_dictionary = WeakValueDictionary(relations)
    
    values = weak_value_dictionary.values()
    
    vampytest.assert_eq(len(values), len(weak_value_dictionary))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_value_dictionary.items()))
    vampytest.assert_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
    
    weak_value_dictionary_empty = WeakValueDictionary()
    
    values = weak_value_dictionary_empty.values()
    
    vampytest.assert_eq(len(values), len(weak_value_dictionary_empty))
    vampytest.assert_eq(sorted(values), sorted(value for key, value in weak_value_dictionary_empty.items()))
    vampytest.assert_not_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
