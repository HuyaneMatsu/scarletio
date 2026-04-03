import vampytest

from ..layer import Layer

def _assert_fields_set(layer):
    """
    Asserts whether the layer has all of its fields set.
    
    Parameters
    ----------
    layer : ``Layer``
        Instance to test.
    """
    vampytest.assert_instance(layer, Layer)
    vampytest.assert_instance(layer.layer_outer_index, int)
    vampytest.assert_instance(layer.token_end_index, int)
    vampytest.assert_instance(layer.token_start_index, int)


def test__Layer__new():
    """
    Tests whether ``Layer.__new__`` works as intended.
    """
    layer_outer_index = 3
    token_start_index = 1
    token_end_index = 2
    
    layer = Layer(
        layer_outer_index,
        token_start_index,
        token_end_index,
    )
    
    _assert_fields_set(layer)
    
    vampytest.assert_eq(layer.layer_outer_index, layer_outer_index)
    vampytest.assert_eq(layer.token_start_index, token_start_index)
    vampytest.assert_eq(layer.token_end_index, token_end_index)


def test__Layer__repr():
    """
    Tests whether ``Layer.__repr__`` works as intended.
    """
    layer_outer_index = 3
    token_start_index = 1
    token_end_index = 2
    
    layer = Layer(
        layer_outer_index,
        token_start_index,
        token_end_index,
    )
    
    output = repr(layer)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    layer_outer_index = 3
    token_start_index = 1
    token_end_index = 2
    
    keyword_parameters = {
        'layer_outer_index': layer_outer_index,
        'token_start_index': token_start_index,
        'token_end_index': token_end_index,
    }
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'layer_outer_index': 4,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'token_start_index': 0,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'token_end_index': 4,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__Layer__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``Layer.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    Layer_0 = Layer(**keyword_parameters_0)
    Layer_1 = Layer(**keyword_parameters_1)
    
    output = Layer_0 == Layer_1
    vampytest.assert_instance(output, bool)
    return output
