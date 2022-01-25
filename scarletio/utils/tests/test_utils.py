from bisect import bisect

import pytest

from scarletio import any_to_any, change_on_switch, get_short_executable, relative_index, where


# test any_to_any

def test_any_to_any():
    container_0 = {0}
    container_1 = {}
    container_2 = {1, 2}
    container_3 = {2, 3}
    
    assert any_to_any(container_0, container_0) == True
    assert any_to_any(container_0, container_1) == False
    assert any_to_any(container_0, container_2) == False
    assert any_to_any(container_0, container_3) == False
    
    assert any_to_any(container_1, container_1) == False
    assert any_to_any(container_1, container_2) == False
    assert any_to_any(container_1, container_3) == False
    
    assert any_to_any(container_2, container_3) == True


def test_get_short_executable():
    executable = get_short_executable()
    assert isinstance(executable, str)



def where_key_0(value):
    return False

def here_key_1(value):
    return value == 1

def test_where():
    container = [0, 1, 2]
    
    with pytest.raises(LookupError):
        assert where(container, where_key_0)
    
    
    assert where(container, here_key_1) == 1


def test_relative_index():
    container_0 = [1, 2, 3, 4]
    container_1 = []
    container_2 = [1, 6, 10]
    
    assert relative_index(container_0, -1) == bisect(container_0, -1)
    assert relative_index(container_0, 20) == bisect(container_0, 20)
    assert relative_index(container_1, 2) == bisect(container_1, 2)
    assert relative_index(container_2, 8) == bisect(container_2, 8)
