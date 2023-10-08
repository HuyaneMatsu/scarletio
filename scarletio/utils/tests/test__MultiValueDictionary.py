from ..multi_value_dictionary import MultiValueDictionary

import vampytest


# Test MultiValueDictionary

# Test constructor

def test__MultiValueDictionary__constructor():
    multi_value_dictionary = MultiValueDictionary()
    vampytest.assert_eq(len(multi_value_dictionary), 0)
    vampytest.assert_eq(sorted(multi_value_dictionary), [])


def test__MultiValueDictionary__constructor_empty():
    multi_value_dictionary = MultiValueDictionary([])
    vampytest.assert_eq(len(multi_value_dictionary), 0)
    vampytest.assert_eq(sorted(multi_value_dictionary), [])


def test__MultiValueDictionary__constructor_filled():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c'), ('b', 'b')]
    
    multi_value_dictionary = MultiValueDictionary(relations)
    vampytest.assert_eq(len(multi_value_dictionary), len(set(relation[0] for relation in relations)))
    vampytest.assert_eq(sorted(multi_value_dictionary.items()), sorted(set(relations)))


# Test magic methods


def test__MultiValueDictionary__contains():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    key_1 = 'a'
    key_2 = 'c'
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    vampytest.assert_in(key_1, multi_value_dictionary)
    vampytest.assert_not_in(key_2, multi_value_dictionary)


def test__MultiValueDictionary__eq():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'a'), ('b', 'b')]
    relations_3 = []
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    multi_value_dictionary_3 = MultiValueDictionary(relations_3)
    
    vampytest.assert_eq(multi_value_dictionary_1, multi_value_dictionary_1)
    vampytest.assert_eq(multi_value_dictionary_1, multi_value_dictionary_2, reverse = True)
    vampytest.assert_eq(multi_value_dictionary_1, multi_value_dictionary_3, reverse = True)
    
    vampytest.assert_eq(multi_value_dictionary_1, relations_1)
    vampytest.assert_eq(multi_value_dictionary_1, relations_2, reverse = True)
    vampytest.assert_eq(multi_value_dictionary_1, relations_3, reverse = True)
    
    
    vampytest.assert_is(multi_value_dictionary_1.__eq__([1, ]), NotImplemented)
    vampytest.assert_is(multi_value_dictionary_1.__eq__(1), NotImplemented)


def test__MultiValueDictionary__ne():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'a'), ('b', 'b')]
    relations_3 = []
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    multi_value_dictionary_3 = MultiValueDictionary(relations_3)
    
    vampytest.assert_ne(multi_value_dictionary_1, multi_value_dictionary_1, reverse = True)
    vampytest.assert_ne(multi_value_dictionary_1, multi_value_dictionary_2)
    vampytest.assert_ne(multi_value_dictionary_1, multi_value_dictionary_3)
    
    vampytest.assert_ne(multi_value_dictionary_1, relations_1, reverse = True)
    vampytest.assert_ne(multi_value_dictionary_1, relations_2)
    vampytest.assert_ne(multi_value_dictionary_1, relations_3)
    
    
    vampytest.assert_is(multi_value_dictionary_1.__ne__([1, ]), NotImplemented)
    vampytest.assert_is(multi_value_dictionary_1.__ne__(1), NotImplemented)


def test__MultiValueDictionary__iter():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    vampytest.assert_eq(sorted(iter(multi_value_dictionary)), sorted(multi_value_dictionary.keys()))
    vampytest.assert_eq(sorted(iter(multi_value_dictionary_empty)), sorted(multi_value_dictionary_empty.keys()))


def test__MultiValueDictionary__len():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    vampytest.assert_eq(len(multi_value_dictionary), len(set(relation[0] for relation in relations)))
    vampytest.assert_eq(len(multi_value_dictionary_empty), 0)


def test__MultiValueDictionary__setitem():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'd'
    value_1 = 'd'
    expected_value_1 = value_1
    
    key_2 = 'b'
    value_2 = 'd'
    expected_value_2 = 'b'
    
    key_3 = {}
    value_3 = 'g'
    
    multi_value_dictionary[key_1] = value_1
    vampytest.assert_eq(multi_value_dictionary[key_1], expected_value_1)
    vampytest.assert_eq(len(multi_value_dictionary), 3)
    
    relations.append((key_1, value_1))
    vampytest.assert_eq(sorted(multi_value_dictionary.items()), sorted(relations))
    
    multi_value_dictionary[key_2] = value_2
    vampytest.assert_eq(multi_value_dictionary[key_2], expected_value_2)
    vampytest.assert_eq(len(multi_value_dictionary), 3)
    
    relations.append((key_2, value_2))
    vampytest.assert_eq(sorted(multi_value_dictionary.items()), sorted(relations))
    
    with vampytest.assert_raises(TypeError):
        multi_value_dictionary[key_3] = value_3


def test__MultiValueDictionary__getitem():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    vampytest.assert_eq(multi_value_dictionary['a'], 'a')
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary['d']
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary_empty['d']


def test__MultiValueDictionary__delitem():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    del multi_value_dictionary['a']
    vampytest.assert_eq(multi_value_dictionary['a'], 'c')
    
    del multi_value_dictionary['a']
    vampytest.assert_not_in('a', multi_value_dictionary)
    
    with vampytest.assert_raises(KeyError):
        del multi_value_dictionary['a']
    
    
    with vampytest.assert_raises(KeyError):
        del multi_value_dictionary['d']
    
    with vampytest.assert_raises(KeyError):
        del multi_value_dictionary_empty['d']


# Test methods


def test__MultiValueDictionary__get_all():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = ['a', 'c']
    
    key_2 = 'c'
    
    vampytest.assert_eq(multi_value_dictionary.get_all(key_1), value_1)
    
    # When item modified, source should not change.
    value_1.append('d')
    
    vampytest.assert_ne(multi_value_dictionary.get_all(key_1), value_1)
    
    vampytest.assert_is(multi_value_dictionary.get_all(key_2), None)
    
    
    
def test__MultiValueDictionary__get_one():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = 'a'
    
    key_2 = 'c'
    
    vampytest.assert_eq(multi_value_dictionary.get_one(key_1), value_1)
    vampytest.assert_is(multi_value_dictionary.get_one(key_2), None)


def test__MultiValueDictionary__get():
    vampytest.assert_is(MultiValueDictionary.get, MultiValueDictionary.get_one)


def test__MultiValueDictionary__pop_all():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = ['a', 'c']
    
    key_2 = 'c'
    
    vampytest.assert_eq(multi_value_dictionary.pop_all(key_1), value_1)
    vampytest.assert_eq(len(multi_value_dictionary), 1)
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary.pop_all(key_2)
    
    vampytest.assert_is(multi_value_dictionary.pop_all(key_2, None), None)


def test__MultiValueDictionary__pop_one():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = 'a'
    
    key_2 = 'a'
    value_2 = 'c'
    
    key_3 = 'a'
    
    key_4 = 'c'
    
    vampytest.assert_eq(multi_value_dictionary.pop_one(key_1), value_1)
    vampytest.assert_eq(len(multi_value_dictionary), 2)
    
    vampytest.assert_eq(multi_value_dictionary.pop_one(key_2), value_2)
    vampytest.assert_eq(len(multi_value_dictionary), 1)
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary.pop_one(key_3)
    
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary.pop_one(key_4)
    
    vampytest.assert_is(multi_value_dictionary.pop_one(key_4, None), None)


def test__MultiValueDictionary__pop():
    vampytest.assert_is(MultiValueDictionary.pop, MultiValueDictionary.pop_one)


def test__MultiValueDictionary__popitem():
    item_1 = ('a', 'a')
    item_2 = ('b', 'b')
    item_3 = ('a', 'c')
    relations = [item_1, item_2, item_3]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    popped_item_1 = multi_value_dictionary.popitem()
    vampytest.assert_in(popped_item_1, relations)
    
    popped_item_2 = multi_value_dictionary.popitem()
    vampytest.assert_in(popped_item_2, relations)
    
    popped_item_3 = multi_value_dictionary.popitem()
    vampytest.assert_in(popped_item_3, relations)
    
    with vampytest.assert_raises(KeyError):
        multi_value_dictionary.popitem()
    
    vampytest.assert_eq(len(multi_value_dictionary), 0)
    
    vampytest.assert_eq(sorted([popped_item_1, popped_item_2, popped_item_3]), sorted(relations))


def test__MultiValueDictionary__setdefault():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    key_1 = 'd'
    value_1 = 'd'
    expected_value_1 = value_1
    
    key_2 = 'a'
    value_2 = 'd'
    expected_value_2 = 'a'
    
    key_3 = {}
    value_3 = 'e'
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    value = multi_value_dictionary.setdefault(key_1, value_1)
    vampytest.assert_eq(value, expected_value_1)
    vampytest.assert_eq(len(multi_value_dictionary), 3)
    
    
    value = multi_value_dictionary.setdefault(key_2, value_2)
    vampytest.assert_eq(value, expected_value_2)
    vampytest.assert_eq(len(multi_value_dictionary), 3)
    vampytest.assert_eq(multi_value_dictionary[key_2], expected_value_2)
    
    with vampytest.assert_raises(TypeError):
        multi_value_dictionary.setdefault(key_3, value_3)


def test__MultiValueDictionary__copy():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    test_case = multi_value_dictionary.copy()
    
    vampytest.assert_is_not(test_case, multi_value_dictionary)
    vampytest.assert_eq(test_case, multi_value_dictionary)
    
    test_case['a'] = 'd'
    vampytest.assert_ne(test_case, multi_value_dictionary)
    
    test_case = multi_value_dictionary_empty.copy()
    vampytest.assert_is_not(test_case, multi_value_dictionary_empty)
    vampytest.assert_eq(test_case, multi_value_dictionary_empty)


def _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary):
    items = []
    
    for key in multi_value_dictionary.keys():
        values = multi_value_dictionary.get_all(key)
        if (values is not None):
            for value in values:
                items.append((key, value))
    
    items.sort()
    return items


def test__MultiValueDictionary__items():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    item_1 = ('a', 'a')
    item_2 = ('a', 'c')
    item_3 = ('d', 'd')
    item_4 = ('b', 'd')
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    items = multi_value_dictionary.items()
    
    vampytest.assert_eq(sorted(items), _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary))
    vampytest.assert_in(item_1, items)
    vampytest.assert_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    vampytest.assert_not_in(item_4, items)
    
    multi_value_dictionary_empty = MultiValueDictionary()
    
    items = multi_value_dictionary_empty.items()
    
    vampytest.assert_eq(sorted(items), _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary_empty))
    vampytest.assert_not_in(item_1, items)
    vampytest.assert_not_in(item_2, items)
    vampytest.assert_not_in(item_3, items)
    vampytest.assert_not_in(item_4, items)


def test__MultiValueDictionary__values():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    value_1 = 'a'
    value_2 = 'd'
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    values = multi_value_dictionary.values()
    
    vampytest.assert_eq(sorted(values), sorted(value for key, value in multi_value_dictionary.items()))
    vampytest.assert_in(value_1, values)
    vampytest.assert_not_in(value_2, values)
    
    multi_value_dictionary_empty = MultiValueDictionary()
    
    values = multi_value_dictionary_empty.values()
    
    vampytest.assert_eq(sorted(values), sorted(value for key, value in multi_value_dictionary_empty.items()))
    vampytest.assert_not_in(value_1, values)
    vampytest.assert_not_in(value_2, values)



def test__MultiValueDictionary__keys():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    key_1 = 'a'
    key_2 = 'd'
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    keys = multi_value_dictionary.keys()
    
    vampytest.assert_eq(len(keys), len(multi_value_dictionary))
    vampytest.assert_eq(set(keys), set(key for key, value in multi_value_dictionary.items()))
    vampytest.assert_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


    multi_value_dictionary_empty = MultiValueDictionary()
    
    keys = multi_value_dictionary_empty.keys()
    
    vampytest.assert_eq(len(keys), len(multi_value_dictionary_empty))
    vampytest.assert_eq(set(keys), set(key for key, value in multi_value_dictionary_empty.items()))
    vampytest.assert_not_in(key_1, keys)
    vampytest.assert_not_in(key_2, keys)


def test__MultiValueDictionary__kwargs():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    expected_kwargs = {key: value for key, value in relations}
    
    vampytest.assert_eq(expected_kwargs, multi_value_dictionary.kwargs())


def test__MultiValueDictionary__extend():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'e'), ('c', 'c'), ('c', 'k')]
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    
    test_case = multi_value_dictionary_1.copy()
    test_case.extend(multi_value_dictionary_2)
    vampytest.assert_eq(sorted(test_case.items()), sorted(set(relations_1)|set(relations_2)))
    
    test_case = multi_value_dictionary_1.copy()
    test_case.extend(dict(relations_2))
    vampytest.assert_eq(sorted(test_case.items()), sorted(set(relations_1)|set(dict(relations_2).items())))
