import vampytest

from ..exceptions import InvalidStateError
from ..top_level import get_event_loop
from ..traps import Future


def test__InvalidStateError():
    """
    Tests whether ``InvalidStateError`` is a base exception.
    """
    vampytest.assert_subtype(InvalidStateError, BaseException)
    vampytest.assert_subtype(InvalidStateError, Exception)



def _assert_fields_set(error):
    """
    Asserts whether every fields are set of the given exception.
    
    Parameters
    ----------
    error : ``InvalidStateError``
        The error to check.
    """
    vampytest.assert_instance(error, InvalidStateError)
    vampytest.assert_instance(error._message, str, nullable = True)
    vampytest.assert_instance(error._message_given, bool)
    vampytest.assert_instance(error.future, Future)
    vampytest.assert_instance(error.location, str)


async def test__InvalidStateError__new__2_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 2 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    
    error = InvalidStateError(future, location)
    _assert_fields_set(error)
    
    vampytest.assert_is(error._message, None)
    vampytest.assert_false(error._message_given)
    vampytest.assert_is(error.future, future)
    vampytest.assert_eq(error.location, location)


async def test__InvalidStateError__new__3_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 3 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    _assert_fields_set(error)
    
    vampytest.assert_eq(error._message, message)
    vampytest.assert_true(error._message_given)
    vampytest.assert_is(error.future, future)
    vampytest.assert_eq(error.location, location)


async def test__InvalidStateError__repr__2_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 2 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    
    error = InvalidStateError(future, location)
    
    representation = repr(error)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in(error.__class__.__name__, representation)
    vampytest.assert_in(future.__class__.__name__, representation)
    vampytest.assert_in(location, representation)


async def test__InvalidStateError__repr__3_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 3 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    
    representation = repr(error)
    vampytest.assert_instance(representation, str)
    vampytest.assert_in(error.__class__.__name__, representation)
    vampytest.assert_in(message, representation)



async def test__InvalidStateError__str__2_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 2 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    
    error = InvalidStateError(future, location)
    
    string = str(error)
    vampytest.assert_instance(string, str)
    vampytest.assert_in(future.__class__.__name__, string)
    vampytest.assert_in(location, string)


async def test__InvalidStateError__str__3_parameters():
    """
    Tests whether ``InvalidStateError.__new__`` works as intended.
    
    Case: 3 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    
    string = str(error)
    vampytest.assert_instance(string, str)
    vampytest.assert_in(message, string)


async def test__InvalidStateError__message__2_parameters():
    """
    Tests whether ``InvalidStateError.message`` works as intended.
    
    Case: 2 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    
    error = InvalidStateError(future, location)
    
    message = error.message
    vampytest.assert_instance(message, str)
    vampytest.assert_eq(message, error._message)
    vampytest.assert_in(future.__class__.__name__, message)
    vampytest.assert_in(message, message)


async def test__InvalidStateError__message__3_parameters():
    """
    Tests whether ``InvalidStateError.message`` works as intended.
    
    Case: 3 parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    
    output = error.message
    vampytest.assert_instance(output, str)
    vampytest.assert_eq(message, output)


async def test__InvalidStateError__eq():
    """
    Tests whether ``InvalidStateError.__eq__`` works as intended.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    vampytest.assert_ne(error, object())
    vampytest.assert_eq(error, error)
    
    keyword_parameters = {
        'future': future,
        'location': location,
        'message': message,
    }
    
    for field_name, field_value in (
        ('future', Future(get_event_loop())),
        ('location', 'palace'),
        ('message', None),
    ):
        test_error = InvalidStateError(**{**keyword_parameters, field_name: field_value})
        vampytest.assert_ne(test_error, error)


async def test__InvalidStateError__hash__2_parameters():
    """
    Tests whether the ``InvalidStateError`` instance is hashable.
    
    Case: 2 Parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    
    error = InvalidStateError(future, location)
    
    hash_value = hash(error)
    vampytest.assert_instance(hash_value, int)


async def test__InvalidStateError__hash__3_parameters():
    """
    Tests whether the ``InvalidStateError`` instance is hashable.
    
    Case: 3 Parameters.
    
    This function is a coroutine.
    """
    future = Future(get_event_loop())
    location = 'hell'
    message = 'burn'
    
    error = InvalidStateError(future, location, message)
    
    hash_value = hash(error)
    vampytest.assert_instance(hash_value, int)
