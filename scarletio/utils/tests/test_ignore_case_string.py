from ..ignore_case_string import IgnoreCaseString

import vampytest


# Test IgnoreCaseString

# Test constructor

def test_IgnoreCaseString_constructor():
    ignore_case_string = IgnoreCaseString()
    vampytest.assert_eq(len(ignore_case_string), 0)
    vampytest.assert_eq(ignore_case_string, '')


def test_IgnoreCaseString_constructor_empty():
    ignore_case_string = IgnoreCaseString('')
    vampytest.assert_eq(len(ignore_case_string), 0)
    vampytest.assert_eq(ignore_case_string, '')


def test_IgnoreCaseString_constructor_filled():
    string = 'value'
    ignore_case_string = IgnoreCaseString(string)
    vampytest.assert_eq(len(ignore_case_string), len(string))
    vampytest.assert_eq(ignore_case_string, string)

# Test magic methods

def test_IgnoreCaseString_eq():
    string = 'vAlUe'

    ignore_case_string = IgnoreCaseString(string)
    vampytest.assert_eq(ignore_case_string, string)
    vampytest.assert_eq(ignore_case_string, string.lower())
    vampytest.assert_eq(ignore_case_string, string.upper())
