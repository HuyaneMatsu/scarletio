import vampytest

from ....frame_proxy import FrameProxyVirtual

from ..familiar_variable_names import get_familiar_variable_names


def _iter_options():
    yield 'komaji', (False, ['komeiji', 'komachi'])
    yield 'komeiji', (True, None)
    yield '__getattr__', (False, ['__setattr__', '__getattribute__', '__delattr__'])


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_familiar_variable_names(name):
    """
    Tests whether ``get_familiar_variable_names`` works as intended.
    
    Parameters
    ----------
    name : `str`
        The variable's name to check.
    
    Returns
    -------
    variable_exists_just_was_not_set : `bool`
    familiar_variable_names : `list<str>`
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
    
    output = get_familiar_variable_names(frame, name)
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], bool)
    vampytest.assert_instance(output[1], list, nullable = True)
    
    if output[1] is not None:
        for element in output[1]:
            vampytest.assert_instance(element, str)
    
    return output
