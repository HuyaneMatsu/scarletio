import vampytest

from ..protocol import _get_released_from_held_back


def _iter_options():
    yield None                     , 11, (None                     , None                     )
    yield [b'hey', b' mis', b'ter'], 11, (None                     , [b'hey', b' mis', b'ter'])
    yield [b'hey', b' mis', b'ter'], 10, (None                     , [b'hey', b' mis', b'ter'])
    yield [b'hey', b' mis', b'ter'],  9, ([b'h']                   , [b'ey', b' mis', b'ter'] )
    yield [b'hey', b' mis', b'ter'],  8, ([b'he']                  , [b'y', b' mis', b'ter']  )
    yield [b'hey', b' mis', b'ter'],  7, ([b'hey']                 , [b' mis', b'ter']        )
    yield [b'hey', b' mis', b'ter'],  6, ([b'hey', b' ']           , [b'mis', b'ter']         )
    yield [b'hey', b' mis', b'ter'],  5, ([b'hey', b' m']          , [b'is', b'ter']          )
    yield [b'hey', b' mis', b'ter'],  4, ([b'hey', b' mi']         , [b's', b'ter']           )
    yield [b'hey', b' mis', b'ter'],  3, ([b'hey', b' mis']        , [b'ter']                 )
    yield [b'hey', b' mis', b'ter'],  2, ([b'hey', b' mis', b't']  , [b'er']                  )
    yield [b'hey', b' mis', b'ter'],  1, ([b'hey', b' mis', b'te'] , [b'r']                   )
    yield [b'hey', b' mis', b'ter'],  0, ([b'hey', b' mis', b'ter'], None                     )
    yield [b'hey', b' mis', b'ter'], -1, ([b'hey', b' mis', b'ter'], None                     )
    yield None                     , -1, (None                     , None                     )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_released_from_held_back(held_back, amount_to_keep):
    """
    Tests whether ``_get_released_from_held_back`` works as intended.
    
    Parameters
    ----------
    held_back : `None | list<bytes | memoryview>`
        The held back chunks.
    
    amount_to_keep : `int`
        The amount of bytes to hold back.
    
    Returns
    -------
    output : `(None | list<bytes>, None | list<bytes>)`
    """
    if (held_back is not None):
        held_back = held_back.copy()
    
    
    output = _get_released_from_held_back(held_back, amount_to_keep)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    
    output_0, output_1 = output
    
    if (output_0 is not None):
        output_0 = [bytes(value) for value in output_0]
    
    if (output_1 is not None):
        output_1 = [bytes(value) for value in output_1]
    
    return output_0, output_1
