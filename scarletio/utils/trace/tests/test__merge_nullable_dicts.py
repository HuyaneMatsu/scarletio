import vampytest

from ..formatters import _merge_nullable_dicts


def _iter_options():
    yield None, None, None
    yield {'koishi': 'hey'}, None, {'koishi': 'hey'}
    yield None, {'satori': 'mister'}, {'satori': 'mister'}
    yield {'koishi': 'hey'}, {'satori': 'mister'}, {'koishi': 'hey', 'satori': 'mister'}


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__merge_nullable_dicts(dict_0, dict_1):
    """
    Tests whether ``_merge_nullable_dicts`` works as intended.
    
    Parameters
    ----------
    dict_0 : `None | dict<str, object>`
        Dictionary to merge.
    dict_1 : `None | dict<str, object>`
        Dictionary ot merge.
    
    Returns
    -------
    output : `None | dict<str, object>`
    """
    return _merge_nullable_dicts(dict_0, dict_1)
