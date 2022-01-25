import pytest

from scarletio import IgnoreCaseMultiValueDictionary

# Test IgnoreCaseString

def test_IgnoreCaseMultiValueDictionary_constructor():
    multi_value_dictionary = IgnoreCaseMultiValueDictionary()
    assert len(multi_value_dictionary) == 0
    assert sorted(multi_value_dictionary) == []


def test_IgnoreCaseMultiValueDictionary_constructor_empty():
    multi_value_dictionary = IgnoreCaseMultiValueDictionary([])
    assert len(multi_value_dictionary) == 0
    assert sorted(multi_value_dictionary) == []


def test_IgnoreCaseMultiValueDictionary_constructor_filled():
    relations_1 = [('a', 'a'), ('b', 'b'), ('A', 'c'), ('B', 'b')]
    relations_2 = [('a', 'a'), ('b', 'b'), ('a', 'c')]
    
    multi_value_dictionary = IgnoreCaseMultiValueDictionary(relations_1)
    assert len(multi_value_dictionary) == len(set(relation[0] for relation in relations_2))
    assert sorted(multi_value_dictionary.items()) == sorted(relations_2)
