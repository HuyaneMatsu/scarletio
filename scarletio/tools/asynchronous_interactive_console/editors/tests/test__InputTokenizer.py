import vampytest

from ..editor_advanced import InputStream, InputTokenizer



def _assert_fields_set(tokenizer):
    """
    Tests whether ``Tokenizer`` works as intended.
    
    Parameters
    ----------
    tokenizer : ``InputTokenizer``
        The tokenizer to check.
    
    Parameters
    ----------
    tokenizer : ``InputTokenizer``
    """
    vampytest.assert_instance(tokenizer, InputTokenizer)
    vampytest.assert_instance(tokenizer.stream, InputStream)
    

def test__InputTokenizer__new():
    """
    Tests whether ``InputTokenizer.__new__`` works as intended.
    """
    stream = InputStream('Koishi')
    tokenizer = InputTokenizer(stream)
    _assert_fields_set(tokenizer)
    vampytest.assert_eq(tokenizer.stream, stream)


def test__InputTokenizer__repr():
    """
    Tests whether ``InputTokenizer.__repr__`` works as intended.
    """
    stream = InputStream('Koishi')
    tokenizer = InputTokenizer(stream)
    
    vampytest.assert_instance(repr(tokenizer), str)


def _iter_options__next():
    
    stream = InputStream('')
    yield stream, None
    
    stream = InputStream('\n')
    yield stream, '\n'
    
    stream = InputStream('\n')
    stream.index = 1
    yield stream, None


@vampytest._(vampytest.call_from(_iter_options__next()).returning_last())
def test__InputTokenizer__next(stream):
    """
    Tests whether ``InputTokenizer.next`` works as intended.
    
    Parameters
    ----------
    stream : ``InputStream``
        Stream to create the tokenizer with.
    
    Returns
    -------
    output : `None | str`
    """
    output = InputTokenizer(stream).next()
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__is_length_greater_than():
    
    stream = InputStream('')
    yield stream, False
    
    stream = InputStream('\n')
    yield stream, False
    
    stream = InputStream('\n\n')
    yield stream, True
    
    stream = InputStream('\n\n')
    stream.index = 1
    yield stream, False


@vampytest._(vampytest.call_from(_iter_options__is_length_greater_than()).returning_last())
def test__InputTokenizer__is_length_greater_than(stream):
    """
    Tests whether ``InputTokenizer.is_length_greater_than`` works as intended.
    
    Parameters
    ----------
    stream : ``InputStream``
        Stream to create the tokenizer with.
    
    Returns
    -------
    output : `bool`
    """
    output = InputTokenizer(stream).is_length_greater_than(1)
    vampytest.assert_instance(output, bool)
    return output
