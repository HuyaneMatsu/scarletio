import vampytest

from ..editor_advanced import InputStream


def _assert_fields_set(stream):
    """
    Tests whether every field of the given input stream are set correctly.
    
    Parameters
    ----------
    stream : ``InputStream``
    """
    vampytest.assert_instance(stream, InputStream)
    vampytest.assert_instance(stream.content, str)
    vampytest.assert_instance(stream.index, int)


def test__InputStream__new():
    """
    Tests whether ``InputStream.__new__`` works as intended.
    """
    content = 'Koishi'
    
    stream = InputStream(content)
    _assert_fields_set(stream)
    vampytest.assert_eq(stream.content, content)
    vampytest.assert_eq(stream.index, 0)


def test__InputStream__repr():
    """
    Tests whether ``InputStream.__new__`` works as intended.
    """
    content = 'Koishi'
    
    stream = InputStream(content)
    
    vampytest.assert_instance(repr(stream), str)


@vampytest.call_with(None)
@vampytest.call_with(object())
def test__InputStream__eq__same_type(other):
    """
    Tests whether ``InputStream.__eq__`` works as intended.
    
    Parameters
    ----------
    other : `object`
        Object to compare to.
    
    Returns
    -------
    output : `bool`
    """
    stream = InputStream('')
    output = stream == other
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def _iter_options__eq__same_type():
    stream_0 = InputStream('')

    stream_1 = InputStream('')
    
    yield stream_0, stream_1, True
    
    stream_0 = InputStream('a')
    stream_0.index = 1
    
    stream_1 = InputStream('a')
    stream_1.index = 1
    
    yield stream_0, stream_1, True

    stream_0 = InputStream('')

    stream_1 = InputStream('a')
    
    yield stream_0, stream_1, False

    stream_0 = InputStream('a')

    stream_1 = InputStream('a')
    stream_1.index = 1
    
    yield stream_0, stream_1, False


@vampytest._(vampytest.call_from(_iter_options__eq__same_type()).returning_last())
def test__InputStream__eq__same_type(stream_0, stream_1):
    """
    Tests whether ``InputStream.__eq`` works as intended.
    
    Parameters
    ----------
    stream_0 : ``InputStream``
        Node to compare.
    stream_1 : ``InputStream``
        Node to compare.
    
    Returns
    -------
    output : `bool`
    """
    output = stream_0 == stream_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__peek():
    yield -2, None
    yield -1, 'a'
    yield 0, 'y'
    yield 1, 'o',
    yield 2, None


@vampytest._(vampytest.call_from(_iter_options__peek()).returning_last())
def test__InputStream__peek(count):
    """
    Tests whether ``InputStream.peek`` works as intended.
    
    Parameters
    ----------
    count : `int`
        How much to peek.
    
    Returns
    -------
    output : `None | str`
    """
    stream = InputStream('ayo')
    stream.index = 1
    
    return stream.peek(count)


def _iter_options__consume():
    yield -1, 1
    yield 0, 1
    yield 1, 2
    yield 2, 3
    yield 3, 3


@vampytest._(vampytest.call_from(_iter_options__consume()).returning_last())
def test__InputStream__consume(count):
    """
    Tests whether ``InputStream.consume`` works as intended.
    
    Parameters
    ----------
    count : `int`
        How much to consume.
    
    Returns
    -------
    output : `int`
    """
    stream = InputStream('ayo')
    stream.index = 1
    
    stream.consume(count)
    return stream.index


def _iter_options__read():
    yield -1, None
    yield 0, None
    yield 1, 'y'
    yield 2, 'yo'
    yield 3, 'yo'


@vampytest._(vampytest.call_from(_iter_options__read()).returning_last())
def test__InputStream__read(count):
    """
    Tests whether ``InputStream.read`` works as intended.
        
    Parameters
    ----------
    count : `int
        How much to read.
    
    Returns
    -------
    output : `None | str`
    """
    stream = InputStream('ayo')
    stream.index = 1
    
    return stream.read(count)


def _iter_options__is_at_end_of_stream():
    yield 0, False
    yield 1, False
    yield 2, False
    yield 3, True
    yield 4, True


@vampytest._(vampytest.call_from(_iter_options__is_at_end_of_stream()).returning_last())
def test__InputStream__is_at_end_of_stream(index):
    """
    Tests whether ``InputStream.is_at_end_of_stream`` works as intended.
        
    Parameters
    ----------
    count : `int
        The index of the stream.
    
    Returns
    -------
    output : `None | str`
    """
    stream = InputStream('ayo')
    stream.index = index
    
    return stream.is_at_end_of_stream()


def test__InputStream__copy():
    """
    Tests whether ``InputStream.__new__`` works as intended.
    """
    content = 'Koishi'
    index = 1
    
    stream = InputStream(content)
    stream.index = index
    
    copy = stream.copy()
    _assert_fields_set(copy)
    vampytest.assert_eq(copy.content, content)
    vampytest.assert_eq(copy.index, index)
