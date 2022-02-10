__all__ = ('CancelledError', 'InvalidStateError',)

from ..utils import include


get_future_state_name = include('get_future_state_name')


class CancelledError(BaseException):
    """The Future or Task was cancelled."""


class InvalidStateError(Exception):
    """
    The operation is not allowed in this state.
    
    Attributes
    ----------
    future : ``Future``.
        The future, from what's method the exception was raised.
    func_name : `str`
        The future's function's name, from where the exception was raised.
    _message : `None`, `str`
        Internal cache for the ``.message`` property.
    """
    def __init__(self, future, func_name, message=None):
        """
        Creates a new ``InvalidStateError``.
        
        Parameters
        ----------
        future : ``Future``.
            The future, from what's method the exception was raised.
        func_name : `str`
            The future's function's name, from where the exception was raised.
        message : `str`
            The exception's message. If not defined, then the exception will generate it by itself.
        """
        self.future = future
        self.func_name = func_name
        self._message = message
    
    def __repr__(self):
        """Returns the exception's representation."""
        return f'{self.__class__.__name__}: {self.message}'
    
    __str__ = __repr__
    
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
            future = self.future
            message = (
                f'`{future.__class__.__name__}.{self.func_name}` was called, when `.state` is {future._state} '
                f'({get_future_state_name(future._state)}) of {future!r}.'
            )
            self._message = message
        
        return message
