import vampytest

from ...utils import IgnoreCaseMultiValueDictionary

from ..helpers import freeze_headers


def _iter_options():
    yield (
        None,
        None,
    )
    
    yield (
        IgnoreCaseMultiValueDictionary(),
        None,
    )
    
    yield (
        IgnoreCaseMultiValueDictionary([
            ('hey', 'mister'),
            ('scarlet', 'remilia'),
            ('scarlet', 'flandre'),
            ('hey', 'sister'),
        ]),
        (
            ('hey', ('mister', 'sister')),
            ('scarlet', ('remilia', 'flandre')),
        )
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
async def test__freeze_headers(input_value):
    """
    Tests whether ``freeze_headers`` works as intended.
    
    Parameters
    ----------
    input_value : `None | IgnoreCaseMultiValueDictionary`
        Input value to test with.
    
    Returns
    -------
    output : `bool`
    """
    output = freeze_headers(input_value)
    vampytest.assert_instance(output, tuple, nullable = True)
    return output
