import vampytest

from ..helpers import parse_labels_from_name


def _iter_options__passing():
    yield '', None
    yield '.', None
    yield '@', None
    yield '@.', None
    yield 'komeiji.koishi', (b'komeiji', b'koishi')
    yield 'űűű', ('űűű'.encode('idna'),)
    yield '\\\\\\.yay', (b'\\.yay',)
    yield '\\032', (b' ',)
    yield 'aya.', (b'aya',)


def _iter_options__value_error():
    yield '\\'
    yield '\\2'
    yield '\\20'
    yield '\\300'
    yield '..'
    yield '.ayaya'
    yield '.aya.'


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__value_error()).raising(ValueError))
def test__parse_labels_from_name(name):
    """
    Tests whether ``parse_labels_from_name`` works as intended.
    
    Parameters
    ----------
    name : `str`
        Name to parse.
    
    Returns
    -------
    output : `None | tuple<bytes>`
    
    Raises
    ------
    ValueError
    """
    output = parse_labels_from_name(name)
    vampytest.assert_instance(output, tuple, nullable = True)
    if (output is not None):
        for element in output:
            vampytest.assert_instance(element, bytes)
    
    return output
