import vampytest

from ..familiar_instance_attribute_names import _get_instance_attributes


class TestType0:
    __slots__ = ()
    
    hey = 'mister'
    komeiji = 'koishi'
    komachi = None


class TestType1:
    __slots__ = ()
    
    def __dir__(self):
        return ['sakuya', 'remilia']


class TestType2:
    __slots__ = ()
    
    def __dir__(self):
        raise ValueError


def _iter_options():
    extra = ['__module__', '__slots__']
    
    yield TestType0(), sorted({*dir(object()), *extra, 'hey', 'komeiji', 'komachi'})
    yield TestType1(), sorted({*dir(object()), *extra, 'sakuya', 'remilia'})
    yield TestType2(), sorted({*dir(object()), *extra})


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_instance_attributes(input_value):
    """
    Tests whether ``_get_instance_attributes`` works as intended.
    
    Parameters
    ----------
    input_value : `object`
        Input value to test on.
    
    Returns
    -------
    output : `list<str>`
    """
    output = _get_instance_attributes(input_value)
    vampytest.assert_instance(output, set)
    for element in output:
        vampytest.assert_instance(element, str)
    return sorted(output)
