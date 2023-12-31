import vampytest

from ..representation_helpers import _get_value_representation


class _TestType_0:
    def __repr__(self):
        raise TypeError


class _TesttStringType(str):
    pass


class _TestType_1:
    def __repr__(self):
        return _TesttStringType('koishi')


def _iter_options():
    yield 12.6, '12.6'
    yield _TestType_0(), '<_TestType_0>'
    yield _TestType_1(), 'koishi'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_value_representation(input_value):
    """
    Tests whether ``_get_value_representation`` works as intended.
    
    Parameters
    -----------
    input_value : `object`
        The value to get its representation of.
    
    Returns
    -------
    output : `str`
    """
    output = _get_value_representation(input_value)
    vampytest.assert_instance(output, str, accept_subtypes = False)
    return output
