from ..hybrid_value_dictionary import HybridValueDictionary

from .weak_helpers import WeakReferencable, sort_by_type_first_key

import vampytest


# Test HybridValueDictionary

# Test constructor

def test__HybridValueDictionary__constructor():
    hybrid_value_dictionary = HybridValueDictionary()
    vampytest.assert_eq(len(hybrid_value_dictionary), 0)
    vampytest.assert_eq(sorted(hybrid_value_dictionary), [])


def test__HybridValueDictionary__constructor_empty():
    hybrid_value_dictionary = HybridValueDictionary([])
    vampytest.assert_eq(len(hybrid_value_dictionary), 0)
    vampytest.assert_eq(sorted(hybrid_value_dictionary), [])


def test__HybridValueDictionary__constructor_filled():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    vampytest.assert_eq(len(hybrid_value_dictionary), len(relations))
    vampytest.assert_eq(dict(hybrid_value_dictionary.items()), relations)


# test magic methods


def test__HybridValueDictionary__contains():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 0
    key_2 = 10
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    vampytest.assert_contains(key_1, hybrid_value_dictionary)
    vampytest.assert_not_in(key_2, hybrid_value_dictionary)


def test__HybridValueDictionary__eq():
    relations_1 = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    relations_2 = {0: WeakReferencable(0), 1: 1}
    relations_3 = {}
    
    hybrid_value_dictionary_1 = HybridValueDictionary(relations_1)
    hybrid_value_dictionary_2 = HybridValueDictionary(relations_2)
    hybrid_value_dictionary_3 = HybridValueDictionary(relations_3)
    
    vampytest.assert_eq(hybrid_value_dictionary_1, hybrid_value_dictionary_1)
    vampytest.assert_eq(hybrid_value_dictionary_1, hybrid_value_dictionary_2, reverse = True)
    vampytest.assert_eq(hybrid_value_dictionary_1, hybrid_value_dictionary_3, reverse = True)
    
    vampytest.assert_eq(hybrid_value_dictionary_1, relations_1)
    vampytest.assert_eq(hybrid_value_dictionary_1, relations_2, reverse = True)
    vampytest.assert_eq(hybrid_value_dictionary_1, relations_3, reverse = True)
    
    vampytest.assert_is(hybrid_value_dictionary_1.__eq__([1, ]), NotImplemented)
    vampytest.assert_is(hybrid_value_dictionary_1.__eq__(1), NotImplemented)


def test__HybridValueDictionary__getitem():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    vampytest.assert_eq(relations[2], WeakReferencable(2))
    
    with vampytest.assert_raises(KeyError):
        hybrid_value_dictionary[6]
    
    with vampytest.assert_raises(KeyError):
        hybrid_value_dictionary_empty[6]


def test__HybridValueDictionary__iter():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    vampytest.assert_eq(sorted(iter(hybrid_value_dictionary)), sorted(hybrid_value_dictionary.keys()))
    vampytest.assert_eq(sorted(iter(hybrid_value_dictionary_empty)), sorted(hybrid_value_dictionary_empty.keys()))


def test__HybridValueDictionary__len():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    vampytest.assert_eq(len(hybrid_value_dictionary), len(relations))
    vampytest.assert_eq(len(hybrid_value_dictionary_empty), 0)


def test__HybridValueDictionary__ne():
    relations_1 = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    relations_2 = {x: WeakReferencable(x) for x in range(2)}
    relations_3 = {}
    
    hybrid_value_dictionary_1 = HybridValueDictionary(relations_1)
    hybrid_value_dictionary_2 = HybridValueDictionary(relations_2)
    hybrid_value_dictionary_3 = HybridValueDictionary(relations_3)
    
    vampytest.assert_ne(hybrid_value_dictionary_1, hybrid_value_dictionary_1, reverse = True)
    vampytest.assert_ne(hybrid_value_dictionary_1, hybrid_value_dictionary_2)
    vampytest.assert_ne(hybrid_value_dictionary_1, hybrid_value_dictionary_3)
    
    vampytest.assert_ne(hybrid_value_dictionary_1, relations_1, reverse = True)
    vampytest.assert_ne(hybrid_value_dictionary_1, relations_2)
    vampytest.assert_ne(hybrid_value_dictionary_1, relations_3)
    
    vampytest.assert_is(hybrid_value_dictionary_1.__ne__([1, ]), NotImplemented)
    vampytest.assert_is(hybrid_value_dictionary_1.__ne__(1), NotImplemented)


def test__HybridValueDictionary__setitem():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    key_1 = 4
    value_1 = WeakReferencable(4)
    
    key_2 = 2
    value_2 = WeakReferencable(6)
    
    key_3 = 6
    value_3 = 9
    
    hybrid_value_dictionary[key_1] = value_1
    vampytest.assert_eq(hybrid_value_dictionary[key_1], value_1)
    vampytest.assert_eq(len(hybrid_value_dictionary), 4)
    
    
    hybrid_value_dictionary[key_2] = value_2
    vampytest.assert_eq(hybrid_value_dictionary[key_2], value_2)
    vampytest.assert_eq(len(hybrid_value_dictionary), 4)
    
    
    hybrid_value_dictionary[key_3] = value_3
    vampytest.assert_eq(hybrid_value_dictionary[key_3], value_3)
    vampytest.assert_eq(len(hybrid_value_dictionary), 5)


# methods


def test__HybridValueDictionary__clear():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    test_case = HybridValueDictionary(relations)
    test_case.clear()
    vampytest.assert_eq(test_case, hybrid_value_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)
    
    
    test_case = HybridValueDictionary()
    test_case.clear()
    vampytest.assert_eq(test_case, hybrid_value_dictionary_empty)
    vampytest.assert_eq(len(test_case), 0)


def test__HybridValueDictionary__copy():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    test_case = hybrid_value_dictionary.copy()
    
    vampytest.assert_is_not(test_case, hybrid_value_dictionary)
    vampytest.assert_eq(test_case, hybrid_value_dictionary)
    
    test_case = hybrid_value_dictionary_empty.copy()
    vampytest.assert_is_not(test_case, hybrid_value_dictionary_empty)
    vampytest.assert_eq(test_case, hybrid_value_dictionary_empty)


def test__HybridValueDictionary__get():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    key_1 = 1
    value_1 = 1
    
    key_2 = 6
    
    vampytest.assert_eq(hybrid_value_dictionary.get(key_1), value_1)
    vampytest.assert_is(hybrid_value_dictionary.get(key_2), None)


def test__HybridValueDictionary__items():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    item_1 = (2, WeakReferencable(2))
    item_2 = (6, 6)
    item_3 = (2, WeakReferencable(6))
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    items = hybrid_value_dictionary.items()
    
    vampytest.assert_eq(len(items), len(hybrid_value_dictionary))
    vampytest.assert_eq(
        sorted(items),
        sorted((key, hybrid_value_dictionary[key]) for key in hybrid_value_dictionary.keys()),
    )
    vampytest.assert_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    items = hybrid_value_dictionary_empty.items()
    
    vampytest.assert_eq(len(items), len(hybrid_value_dictionary_empty))
    vampytest.assert_eq(sorted(items), sorted(
        (key, hybrid_value_dictionary_empty[key]) for key in hybrid_value_dictionary_empty.keys())
    )
    vampytest.assert_not_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)


def test__HybridValueDictionary__keys():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    key_1 = 2
    key_2 = 6
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    keys = hybrid_value_dictionary.keys()
    
    vampytest.assert_eq(len(keys), len(hybrid_value_dictionary))
    vampytest.assert_eq(set(keys), set(key for key, value in hybrid_value_dictionary.items()))
    vampytest.assert_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    keys = hybrid_value_dictionary_empty.keys()
    
    vampytest.assert_eq(len(keys), len(hybrid_value_dictionary_empty))
    vampytest.assert_eq(set(keys), set(key for key, value in hybrid_value_dictionary_empty.items()))
    vampytest.assert_not_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


def test__HybridValueDictionary__pop():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 2
    value_1 = WeakReferencable(2)
    
    key_2 = 6
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    vampytest.assert_eq(hybrid_value_dictionary.pop(key_1), value_1)
    vampytest.assert_eq(len(hybrid_value_dictionary), 2)
    
    
    with vampytest.assert_raises(KeyError):
        hybrid_value_dictionary.pop(key_2)
    
    vampytest.assert_eq(len(hybrid_value_dictionary), 2)


def test__HybridValueDictionary__popitem():
    item_1 = (1, 1)
    item_2 = (2, WeakReferencable(2))
    
    relations = dict([item_1, item_2])
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    popped_item_1 = hybrid_value_dictionary.popitem()
    vampytest.assert_true((popped_item_1 == item_1) or (popped_item_1 == item_2))
    vampytest.assert_eq(len(hybrid_value_dictionary), 1)
    
    popped_item_2 = hybrid_value_dictionary.popitem()
    vampytest.assert_true((popped_item_2 == item_1) or (popped_item_2 == item_2))
    vampytest.assert_ne(popped_item_1, popped_item_2)
    vampytest.assert_eq(len(hybrid_value_dictionary), 0)
    
    with vampytest.assert_raises(KeyError):
        hybrid_value_dictionary.popitem()
    
    vampytest.assert_eq(len(hybrid_value_dictionary), 0)


def test__HybridValueDictionary__setdefault():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    key_1 = 6
    value_1 = WeakReferencable(6)
    expected_value_1 = value_1
    
    key_2 = 1
    value_2 = 6
    expected_value_2 = 1
    
    key_3 = 7
    value_3 = 9
    expected_value_3 = value_3
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    value = hybrid_value_dictionary.setdefault(key_1, value_1)
    vampytest.assert_eq(value, expected_value_1)
    vampytest.assert_eq(len(hybrid_value_dictionary), 4)
    
    
    value = hybrid_value_dictionary.setdefault(key_2, value_2)
    vampytest.assert_eq(value, expected_value_2)
    vampytest.assert_eq(len(hybrid_value_dictionary), 4)
    vampytest.assert_eq(hybrid_value_dictionary[key_2], expected_value_2)
    
    value = hybrid_value_dictionary.setdefault(key_3, value_3)
    vampytest.assert_eq(value, expected_value_3)
    vampytest.assert_eq(len(hybrid_value_dictionary), 5)
    vampytest.assert_eq(hybrid_value_dictionary[key_3], expected_value_3)


def test__HybridValueDictionary__update():
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
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(hybrid_value_dictionary_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(hybrid_value_dictionary_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_1)
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_2)
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(relations_3)
    vampytest.assert_eq(test_case, relations_update_1_3)
    
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_1.items()))
    vampytest.assert_eq(test_case, relations_1)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_2.items()))
    vampytest.assert_eq(test_case, relations_update_1_2)
    
    test_case = hybrid_value_dictionary_1.copy()
    test_case.update(list(relations_3.items()))
    vampytest.assert_eq(test_case, relations_update_1_3)
    

    test_case = HybridValueDictionary()
    with vampytest.assert_raises(TypeError):
        test_case.update([1, ])
    
    with vampytest.assert_raises(TypeError):
        test_case.update(1)

    with vampytest.assert_raises(ValueError):
        test_case.update([(1,), ])


def test__HybridValueDictionary__values():
    relations = {0: WeakReferencable(0), 1: 1, 2: WeakReferencable(2)}
    
    value_1 = WeakReferencable(2)
    value_2 = WeakReferencable(6)
    
    
    hybrid_value_dictionary = HybridValueDictionary(relations)
    
    values = hybrid_value_dictionary.values()
    
    vampytest.assert_eq(len(values), len(hybrid_value_dictionary))
    vampytest.assert_eq(
        sorted(values, key = sort_by_type_first_key),
        sorted(
            (value for key, value in hybrid_value_dictionary.items()),
            key = sort_by_type_first_key,
        ),
    )
    vampytest.assert_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
    
    hybrid_value_dictionary_empty = HybridValueDictionary()
    
    values = hybrid_value_dictionary_empty.values()
    
    vampytest.assert_eq(len(values), len(hybrid_value_dictionary_empty))
    vampytest.assert_eq(
        sorted(values, key = sort_by_type_first_key),
        sorted(
            (value for key, value in hybrid_value_dictionary_empty.items()),
            key = sort_by_type_first_key,
        )
    )
    
    vampytest.assert_not_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
