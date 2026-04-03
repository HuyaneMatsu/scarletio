import vampytest

from ..helpers import build_name_from_labels


def _iter_options():
    yield None, '@'
    yield (b'komeiji', b'koishi'), 'komeiji.koishi'
    yield ('űűű'.encode('idna'),), 'űűű'
    yield (b'\\.yay',), '\\\\\\.yay'
    yield (b' ',), '\\032'
    yield (b'aya',), 'aya'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__build_name_from_labels(name):
    """
    Tests whether ``build_name_from_labels`` works as intended.
    
    Parameters
    ----------
    labels : `None | tuple<bytes>`
        Labels to convert.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    """
    output = build_name_from_labels(name)
    vampytest.assert_instance(output, str)
    return output
