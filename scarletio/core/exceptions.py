__all__ = ('CancelledError', 'InvalidStateError',)

from ..utils import include


get_future_state_name = include('get_future_state_name')


class CancelledError(BaseException):
    """
    The future or task was cancelled.
    """
    __slots__ = ()


def _create_invalid_state_error_message(error):
    """
    Helper function to create the error message for invalid state errors.
    
    Parameters
    ----------
    error : ``InvalidStateError``
        The invalid state error to create message for.
    
    Returns
    -------
    message : `str`
    """
    future = error.future
    location = error.location
    return (
        f'`{future.__class__.__name__}.{location}` was called, when `._state` is {future._state} '
        f'({get_future_state_name(future._state)}) of {future!r}.'
    )


class InvalidStateError(Exception):
    """
    The operation is not allowed in this state.
    
    Attributes
    ----------
    _message : `None`, `str`
        Internal cache for the ``.message`` property.
    
    _message_given : `bool`
        Whether message was given when constructing.
    
    future : ``Future``.
        The future, from what's method the exception was raised.
    
    location : `str`
        The future's function's name, from where the exception was raised.
    """
    __slots__ = ('_message', '_message_given', 'future', 'location')
    
    # This is to support keyword parameters
    __init__ = object.__init__
    
    def __new__(cls, future, location, message = None):
        """
        Creates a new ``InvalidStateError``.
        
        Parameters
        ----------
        future : ``Future``.
            The future, from what's method the exception was raised.
        location : `str`
            The future's function's name, from where the exception was raised.
        message : `str`
            The exception's message. If not defined, then the exception will generate it by itself.
        """
        self = Exception.__new__(cls, future, location, message)
        self.future = future
        self.location = location
        self._message = message
        self._message_given = message is not None
        return self
    
    
    def __repr__(self):
        """Returns the exception's representation."""
        return f'{self.__class__.__name__}: {self.message}'
    
    
    def __str__(self):
        """Returns the exception's message."""
        return self.message
    
    
    @property
    def message(self):
        """
        Returns the exception's message.
        
        Returns
        -------
        message : `str`
        
        Notes
        -----
        If the exception was created wia ``.__init__``, without giving defining the `message` parameter, then the
        exception's message is generated only when this property is retrieved for the first time.
        """
        message = self._message
        if message is None:
            message = _create_invalid_state_error_message(self)
            self._message = message
        
        return message
    
    
    def __eq__(self, other):
        """Returns whether the two exceptions are equal."""
        if type(other) is not type(self):
            return NotImplemented
        
        if self.future is not other.future:
            return False
        
        if self.location != other.location:
            return False
        
        message_given = self._message_given
        if message_given != other._message_given:
            return False
        
        if message_given and self._message != other._message:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the exception's hash value."""
        hash_value = 0
        
        # future
        hash_value ^= hash(self.future)
        
        # location
        hash_value ^= hash(self.location)
        
        # message
        if self._message_given:
            hash_value ^= hash(self._message)
        
        return hash_value
