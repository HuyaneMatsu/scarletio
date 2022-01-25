import pytest

from scarletio import IgnoreCaseString

# Test IgnoreCaseString

# Test constructor

def test_IgnoreCaseString_constructor():
    ignore_case_string = IgnoreCaseString()
    assert len(ignore_case_string) == 0
    assert ignore_case_string == ''


def test_IgnoreCaseString_constructor_empty():
    ignore_case_string = IgnoreCaseString('')
    assert len(ignore_case_string) == 0
    assert ignore_case_string == ''


def test_IgnoreCaseString_constructor_filled():
    string = 'value'
    ignore_case_string = IgnoreCaseString(string)
    assert len(ignore_case_string) == len(string)
    assert ignore_case_string == string

# Test magic methods

def test_IgnoreCaseString_eq():
    string = 'vAlUe'

    ignore_case_string = IgnoreCaseString(string)
    assert ignore_case_string == string
    assert ignore_case_string == string.lower()
    assert ignore_case_string == string.upper()
