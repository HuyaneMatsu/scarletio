import vampytest

from ..familiar_instance_attribute_names import get_familiar_instance_attribute_names


class TestType0:
    __slots__ = ()
    
    hey = 'mister'
    komeiji = 'koishi'
    komachi = None


def _iter_options():
    yield 'komaji', (False, ['komeiji', 'komachi'])
    yield 'komeiji', (True, None)
    yield '__getattr__', (False, ['__setattr__', '__getattribute__', '__delattr__'])


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_familiar_instance_attribute_names(name):
    """
    Tests whether ``get_familiar_instance_attribute_names`` works as intended.
    
    Parameters
    ----------
    name : `str`
        The attribute's name to check.
    
    Returns
    -------
    attribute_exists_just_was_not_set : `bool`
    familiar_attribute_names : `list<str>`
    """
    output = get_familiar_instance_attribute_names(TestType0(), name)
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], bool)
    vampytest.assert_instance(output[1], list, nullable = True)
    
    if output[1] is not None:
        for element in output[1]:
            vampytest.assert_instance(element, str)
    
    return output
