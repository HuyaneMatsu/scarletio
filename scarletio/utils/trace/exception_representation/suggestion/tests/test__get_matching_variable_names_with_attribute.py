import vampytest

from ....frame_proxy import FrameProxyVirtual

from ..matching_variable_names_with_attribute import get_matching_variable_names_with_attribute


def _iter_options():
    yield 'komaji', None
    yield 'komeiji', None
    yield '__getattr__', None
    yield 'lower', ['hey', 'komeiji']
    yield (
        '__doc__',
        [
            '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
            '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__',
            '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__slots__', 'hey', 'komachi',
            'komeiji'
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_matching_variable_names_with_attribute(name):
    """
    Tests whether ``get_matching_variable_names_with_attribute`` works as intended.
    
    Parameters
    ----------
    name : `str`
        The variable's name to check.
    
    Returns
    -------
    matches : `list<str>`
    """
    frame = FrameProxyVirtual.from_fields(
        locals = {
            '__slots__': None,
            '__module__': None,
            'hey': 'mister',
            'komeiji': 'koishi',
            'komachi': None,
            **{name: None for name in dir(object)}
        }
    )
    
    output = get_matching_variable_names_with_attribute(frame, name)
    
    vampytest.assert_instance(output, list, nullable = True)
    if (output is not None):
        for element in output:
            vampytest.assert_instance(element, str)
    
    return output
