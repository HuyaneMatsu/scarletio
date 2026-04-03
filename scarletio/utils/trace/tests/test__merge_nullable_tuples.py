import vampytest

from ..formatters import _merge_nullable_tuples


def _iter_options():
    yield None, None, None
    yield ('koishi', ), None, ('koishi', )
    yield None, ('satori', ), ('satori', )
    yield ('koishi', ), ('satori', ), ('koishi', 'satori')


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__merge_nullable_tuples(tuple_0, tuple_1):
    """
    Tests whether ``_merge_nullable_tuples`` works as intended.
    
    Parameters
    ----------
    tuple_0 : `None | tuple`
        Tuple to merge.
    tuple_1 : `None | tuple`
        Tuple ot merge.
    
    Returns
    -------
    output : `None | tuple`
    """
    return _merge_nullable_tuples(tuple_0, tuple_1)
