from ..ignore_case_multi_value_dictionary import IgnoreCaseMultiValueDictionary

import vampytest

# Test IgnoreCaseString

def test__IgnoreCaseMultiValueDictionary__constructor():
    multi_value_dictionary = IgnoreCaseMultiValueDictionary()
    vampytest.assert_eq(len(multi_value_dictionary), 0)
    vampytest.assert_eq(sorted(multi_value_dictionary), [])


def test__IgnoreCaseMultiValueDictionary__constructor_empty():
    multi_value_dictionary = IgnoreCaseMultiValueDictionary([])
    vampytest.assert_eq(len(multi_value_dictionary), 0)
    vampytest.assert_eq(sorted(multi_value_dictionary), [])


def test__IgnoreCaseMultiValueDictionary__constructor_filled():
    relations_1 = [('a', 'a'), ('b', 'b'), ('A', 'c'), ('B', 'b')]
    relations_2 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    multi_value_dictionary = IgnoreCaseMultiValueDictionary(relations_1)
    vampytest.assert_eq(len(multi_value_dictionary), len(set(relation[0] for relation in relations_2)))
    vampytest.assert_eq(sorted(multi_value_dictionary.items()), sorted(relations_2))
