import vampytest

from ....frame_proxy import FrameProxyVirtual

from ..matching_variable_name import exists_matching_variable_name


def _iter_options():
    yield 'komaji', False
    yield 'komeiji', True
    yield '__getattr__', False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__exists_matching_variable_name(name):
    """
    Tests whether ``exists_matching_variable_name`` works as intended.
    
    Parameters
    ----------
    name : `str`
        The variable's name to check.
    
    Returns
    -------
    exists_matching_variable_name : `bool`
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
    
    output = exists_matching_variable_name(frame, name)
    
    vampytest.assert_instance(output, bool)
    return output
