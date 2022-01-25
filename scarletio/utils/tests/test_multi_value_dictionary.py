import pytest

from scarletio import MultiValueDictionary

# Test MultiValueDictionary

# Test constructor

def test_MultiValueDictionary_constructor():
    multi_value_dictionary = MultiValueDictionary()
    assert len(multi_value_dictionary) == 0
    assert sorted(multi_value_dictionary) == []


def test_MultiValueDictionary_constructor_empty():
    multi_value_dictionary = MultiValueDictionary([])
    assert len(multi_value_dictionary) == 0
    assert sorted(multi_value_dictionary) == []


def test_MultiValueDictionary_constructor_filled():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c'), ('b', 'b')]
    
    multi_value_dictionary = MultiValueDictionary(relations)
    assert len(multi_value_dictionary) == len(set(relation[0] for relation in relations))
    assert sorted(multi_value_dictionary.items()) == sorted(set(relations))


# Test magic methods


def test_MultiValueDictionary_contains():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    key_1 = 'a'
    key_2 = 'c'
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    assert key_1 in multi_value_dictionary
    assert not (key_2 in multi_value_dictionary)


def test_MultiValueDictionary_eq():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'a'), ('b', 'b')]
    relations_3 = []
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    multi_value_dictionary_3 = MultiValueDictionary(relations_3)
    
    assert multi_value_dictionary_1 == multi_value_dictionary_1
    assert not (multi_value_dictionary_1 == multi_value_dictionary_2)
    assert not (multi_value_dictionary_1 == multi_value_dictionary_3)
    
    assert multi_value_dictionary_1 == relations_1
    assert not (multi_value_dictionary_1 == relations_2)
    assert not (multi_value_dictionary_1 == relations_3)
    
    
    assert multi_value_dictionary_1.__eq__([1, ]) is NotImplemented
    assert multi_value_dictionary_1.__eq__(1) is NotImplemented


def test_MultiValueDictionary_ne():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'a'), ('b', 'b')]
    relations_3 = []
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    multi_value_dictionary_3 = MultiValueDictionary(relations_3)
    
    assert not (multi_value_dictionary_1 != multi_value_dictionary_1)
    assert multi_value_dictionary_1 != multi_value_dictionary_2
    assert multi_value_dictionary_1 != multi_value_dictionary_3
    
    assert not (multi_value_dictionary_1 != relations_1)
    assert multi_value_dictionary_1 != relations_2
    assert multi_value_dictionary_1 != relations_3
    
    
    assert multi_value_dictionary_1.__ne__([1, ]) is NotImplemented
    assert multi_value_dictionary_1.__ne__(1) is NotImplemented


def test_MultiValueDictionary_iter():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    assert sorted(iter(multi_value_dictionary)) == sorted(multi_value_dictionary.keys())
    assert sorted(iter(multi_value_dictionary_empty)) == sorted(multi_value_dictionary_empty.keys())


def test_MultiValueDictionary_len():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    assert len(multi_value_dictionary) == len(set(relation[0] for relation in relations))
    assert len(multi_value_dictionary_empty) == 0


def test_MultiValueDictionary_setitem():
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
    assert multi_value_dictionary[key_1] == expected_value_1
    assert len(multi_value_dictionary) == 3
    
    relations.append((key_1, value_1))
    assert sorted(multi_value_dictionary.items()) == sorted(relations)
    
    multi_value_dictionary[key_2] = value_2
    assert multi_value_dictionary[key_2] == expected_value_2
    assert len(multi_value_dictionary) == 3
    
    relations.append((key_2, value_2))
    assert sorted(multi_value_dictionary.items()) == sorted(relations)
    
    with pytest.raises(TypeError):
        multi_value_dictionary[key_3] = value_3


def test_MultiValueDictionary_getitem():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    assert multi_value_dictionary['a'] == 'a'
    
    with pytest.raises(KeyError):
        multi_value_dictionary['d']
    
    with pytest.raises(KeyError):
        multi_value_dictionary_empty['d']


def test_MultiValueDictionary_delitem():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    del multi_value_dictionary['a']
    assert multi_value_dictionary['a'] == 'c'
    
    del multi_value_dictionary['a']
    assert 'a' not in multi_value_dictionary
    
    with pytest.raises(KeyError):
        del multi_value_dictionary['a']
    
    
    with pytest.raises(KeyError):
        del multi_value_dictionary['d']
    
    with pytest.raises(KeyError):
        del multi_value_dictionary_empty['d']


# Test methods


def test_MultiValueDictionary_get_all():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = ['a', 'c']
    
    key_2 = 'c'
    
    assert multi_value_dictionary.get_all(key_1) == value_1
    
    # When item modified, source should not change.
    value_1.append('d')
    
    assert multi_value_dictionary.get_all(key_1) != value_1
    
    assert multi_value_dictionary.get_all(key_2) is None
    
    
    
def test_MultiValueDictionary_get_one():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = 'a'
    
    key_2 = 'c'
    
    assert multi_value_dictionary.get_one(key_1) == value_1
    assert multi_value_dictionary.get_one(key_2) is None


def test_MultiValueDictionary_get():
    assert MultiValueDictionary.get is MultiValueDictionary.get_one


def test_MultiValueDictionary_pop_all():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = ['a', 'c']
    
    key_2 = 'c'
    
    assert multi_value_dictionary.pop_all(key_1) == value_1
    assert len(multi_value_dictionary) == 1
    
    with pytest.raises(KeyError):
        multi_value_dictionary.pop_all(key_2)
    
    assert multi_value_dictionary.pop_all(key_2, None) is None


def test_MultiValueDictionary_pop_one():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    key_1 = 'a'
    value_1 = 'a'
    
    key_2 = 'a'
    value_2 = 'c'
    
    key_3 = 'a'
    
    key_4 = 'c'
    
    assert multi_value_dictionary.pop_one(key_1) == value_1
    assert len(multi_value_dictionary) == 2
    
    assert multi_value_dictionary.pop_one(key_2) == value_2
    assert len(multi_value_dictionary) == 1
    
    with pytest.raises(KeyError):
        multi_value_dictionary.pop_one(key_3)
    
    
    with pytest.raises(KeyError):
        multi_value_dictionary.pop_one(key_4)
    
    assert multi_value_dictionary.pop_one(key_4, None) is None


def test_MultiValueDictionary_pop():
    assert MultiValueDictionary.pop is MultiValueDictionary.pop_one


def test_MultiValueDictionary_popitem():
    item_1 = ('a', 'a')
    item_2 = ('b', 'b')
    item_3 = ('a', 'c')
    relations = [item_1, item_2, item_3]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    popped_item_1 = multi_value_dictionary.popitem()
    assert popped_item_1 in relations
    
    popped_item_2 = multi_value_dictionary.popitem()
    assert popped_item_2 in relations
    
    popped_item_3 = multi_value_dictionary.popitem()
    assert popped_item_3 in relations
    
    with pytest.raises(KeyError):
        multi_value_dictionary.popitem()
    
    assert len(multi_value_dictionary) == 0
    
    assert sorted([popped_item_1, popped_item_2, popped_item_3]) == sorted(relations)


def test_MultiValueDictionary_setdefault():
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
    assert value == expected_value_1
    assert len(multi_value_dictionary) == 3
    
    
    value = multi_value_dictionary.setdefault(key_2, value_2)
    assert value == expected_value_2
    assert len(multi_value_dictionary) == 3
    assert multi_value_dictionary[key_2] == expected_value_2
    
    with pytest.raises(TypeError):
        multi_value_dictionary.setdefault(key_3, value_3)


def test_MultiValueDictionary_copy():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    multi_value_dictionary = MultiValueDictionary(relations)
    multi_value_dictionary_empty = MultiValueDictionary()
    
    test_case = multi_value_dictionary.copy()
    
    assert test_case is not multi_value_dictionary
    assert test_case == multi_value_dictionary
    
    test_case['a'] = 'd'
    assert test_case != multi_value_dictionary
    
    test_case = multi_value_dictionary_empty.copy()
    assert test_case is not multi_value_dictionary_empty
    assert test_case == multi_value_dictionary_empty


def _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary):
    items = []
    
    for key in multi_value_dictionary.keys():
        values = multi_value_dictionary.get_all(key)
        if (values is not None):
            for value in values:
                items.append((key, value))
    
    items.sort()
    return items


def test_MultiValueDictionary_items():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    item_1 = ('a', 'a')
    item_2 = ('a', 'c')
    item_3 = ('d', 'd')
    item_4 = ('b', 'd')
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    items = multi_value_dictionary.items()
    
    assert sorted(items) == _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary)
    assert item_1 in items
    assert item_2 in items
    assert not (item_3 in items)
    assert not (item_4 in items)
    
    multi_value_dictionary_empty = MultiValueDictionary()
    
    items = multi_value_dictionary_empty.items()
    
    assert sorted(items) == _build_sorted_multi_value_dictionary_items_by_keys(multi_value_dictionary_empty)
    assert not (item_1 in items)
    assert not (item_2 in items)
    assert not (item_3 in items)
    assert not (item_4 in items)


def test_MultiValueDictionary_values():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    value_1 = 'a'
    value_2 = 'd'
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    values = multi_value_dictionary.values()
    
    assert sorted(values) == sorted(value for key, value in multi_value_dictionary.items())
    assert value_1 in values
    assert not (value_2 in values)
    
    multi_value_dictionary_empty = MultiValueDictionary()
    
    values = multi_value_dictionary_empty.values()
    
    assert sorted(values) == sorted(value for key, value in multi_value_dictionary_empty.items())
    assert not (value_1 in values)
    assert not (value_2 in values)



def test_MultiValueDictionary_keys():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    key_1 = 'a'
    key_2 = 'd'
    
    
    multi_value_dictionary = MultiValueDictionary(relations)
    
    keys = multi_value_dictionary.keys()
    
    assert len(keys) == len(multi_value_dictionary)
    assert set(keys) == set(key for key, value in multi_value_dictionary.items())
    assert key_1 in keys
    assert not (key_2 in keys)


    multi_value_dictionary_empty = MultiValueDictionary()
    
    keys = multi_value_dictionary_empty.keys()
    
    assert len(keys) == len(multi_value_dictionary_empty)
    assert set(keys) == set(key for key, value in multi_value_dictionary_empty.items())
    assert not (key_1 in keys)
    assert not (key_2 in keys)


def test_MultiValueDictionary_kwargs():
    relations = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    multi_value_dictionary = MultiValueDictionary(relations)
    
    expected_kwargs = {key: value for key, value in relations}
    
    assert expected_kwargs == multi_value_dictionary.kwargs()


def test_MultiValueDictionary_extend():
    relations_1 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    relations_2 = [('a', 'e'), ('c', 'c'), ('c', 'k')]
    
    multi_value_dictionary_1 = MultiValueDictionary(relations_1)
    multi_value_dictionary_2 = MultiValueDictionary(relations_2)
    
    test_case = multi_value_dictionary_1.copy()
    test_case.extend(multi_value_dictionary_2)
    assert sorted(test_case.items()) == sorted(set(relations_1)|set(relations_2))
    
    test_case = multi_value_dictionary_1.copy()
    test_case.extend(dict(relations_2))
    assert sorted(test_case.items()) == sorted(set(relations_1)|set(dict(relations_2).items()))
