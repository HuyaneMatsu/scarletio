import vampytest

from ..representation_helpers import _get_type_name


class _TestTypeMetaType_0(type):
    @property
    def __name__(self): return 'koishi'


class _TestType_0(metaclass = _TestTypeMetaType_0):
    pass


class _TestType_1:
    pass


class _TesttStringType(str):
    pass


_TestType_1.__name__ = _TesttStringType('satori')


def _iter_options():
    yield BaseException, 'BaseException'
    yield _TestType_0, '_TestType_0'
    yield _TestType_1, 'satori'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_type_name(input_value):
    """
    Tests whether ``_get_type_name`` works as intended.
    
    Parameters
    ----------
    input_value : `type`
        Input value to test with.
    
    Returns
    -------
    output : `str`
    """
    output = _get_type_name(input_value)
    vampytest.assert_instance(output, str, accept_subtypes = False)
    return output
