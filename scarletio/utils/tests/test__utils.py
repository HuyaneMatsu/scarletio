from bisect import bisect

from ..utils import any_to_any, change_on_switch, get_short_executable, relative_index, where

import vampytest


# test any_to_any

def test__any_to_any():
    container_0 = {0}
    container_1 = {}
    container_2 = {1, 2}
    container_3 = {2, 3}
    
    vampytest.assert_eq(any_to_any(container_0, container_0), True)
    vampytest.assert_eq(any_to_any(container_0, container_1), False)
    vampytest.assert_eq(any_to_any(container_0, container_2), False)
    vampytest.assert_eq(any_to_any(container_0, container_3), False)
    
    vampytest.assert_eq(any_to_any(container_1, container_1), False)
    vampytest.assert_eq(any_to_any(container_1, container_2), False)
    vampytest.assert_eq(any_to_any(container_1, container_3), False)
    
    vampytest.assert_eq(any_to_any(container_2, container_3), True)


def test__get_short_executable():
    executable = get_short_executable()
    assert isinstance(executable, str)



def where_key_0(value):
    return False

def here_key_1(value):
    return value == 1

def test__where():
    container = [0, 1, 2]
    
    with vampytest.assert_raises(LookupError):
        where(container, where_key_0)
    
    
    vampytest.assert_eq(where(container, here_key_1), 1)


def test__relative_index():
    container_0 = [1, 2, 3, 4]
    container_1 = []
    container_2 = [1, 6, 10]
    
    vampytest.assert_eq(relative_index(container_0, -1), bisect(container_0, -1))
    vampytest.assert_eq(relative_index(container_0, 20), bisect(container_0, 20))
    vampytest.assert_eq(relative_index(container_1, 2), bisect(container_1, 2))
    vampytest.assert_eq(relative_index(container_2, 8), bisect(container_2, 8))
