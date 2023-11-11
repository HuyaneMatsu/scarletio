__all__ = ('Handle', 'TimerHandle', 'TimerWeakHandle',)

from types import MethodType

from ...utils import WeakCallable, WeakReferer, ignore_frame, include, weak_method


ignore_frame(__spec__.origin, '_run', 'self.func(*self.args)', )


write_exception_async = include('write_exception_async')


class Handle:
    """
    Object returned by a callback registration method:
    - ``EventThread.call_soon``
    - ``EventThread.call_soon_thread_safe``.
    
    Attributes
    ----------
    func : `callable`
        The wrapped function.
    args : `tuple` of `object`
        Parameters to call ``.func`` with.
    cancelled : `bool`
        Whether the handle is cancelled.
    """
    __slots__ = ('func', 'args', 'cancelled',)
    
    def __init__(self, func, args):
        """
        Creates a new ``Handle`` with the given parameters.
        
        Parameters
        ----------
        func : `callable`
            The function. to wrap.
        args : `tuple` of `object`
            Parameters to call `func` with.
        """
        self.func = func
        self.args = args
        self.cancelled = False
    
    
    def __repr__(self):
        """Returns the handle's representation."""
        return self._create_repr(False, None)
    
    
    def _get_repr_without(self, without):
        """
        Returns the representation of the handle without showing the representation of the given object.
        
        Parameters
        ----------
        without : `object`
            The value to ignore.
        
        Returns
        -------
        representation : `str`
        """
        return self._create_repr(True, without)
    
    
    def _create_repr(self, expect, expected_value):
        """
        Returns the representation of the handle.
        
        Parameters
        -----------
        expect : `bool`
            Whether `expected_value` should be ignored.
        expected_value : `object`
            The value to ignore.
        """
        repr_parts = [
            '<',
            self.__class__.__name__,
        ]
        
        if self.cancelled:
            repr_parts.append(' cancelled')
        
        else:
            repr_parts.append(' func = ')
            func = self.func
            if expect and (func is expected_value):
                func_repr = '...'
            
            else:
                func_repr = repr(func)
            
            repr_parts.append(func_repr)
            repr_parts.append('(')
            
            parameters = self.args
            limit = len(parameters)
            if limit:
                index = 0
                while True:
                    parameter = parameters[index]
                    
                    func = self.func
                    if expect and (func is expected_value):
                        parameter_repr = '...'
                    
                    else:
                        parameter_repr = repr(parameter)
                        
                    repr_parts.append(parameter_repr)
                    
                    index += 1
                    if index == limit:
                        break
                    
                    repr_parts.append(', ')
                    continue
            
            repr_parts.append(')')
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    
    def cancel(self):
        """Cancels the handle if not yet cancelled."""
        if not self.cancelled:
            self.cancelled = True
            self.func = None
            self.args = None
    
    
    def _run(self):
        """
        Calls the handle's function with it's parameters. If exception occurs meanwhile, renders it.
        
        Notes
        -----
        This method should be called only inside of an ``EventThread``.
        """
        try:
            self.func(*self.args)
        except BaseException as err:
            write_exception_async(
                err,
                [
                    'Exception occurred at ',
                    self.__class__.__name__,
                    '._run\nAt running ',
                    repr(self.func),
                    '\n',
                ]
            )
        
        finally:
            self = None  # Needed to break cycles when an exception occurs.
    
    
    def iter_positional_parameters(self):
        """
        Iterates over the handle's positional parameters.
        
        This method is an iterable generator.
        
        Yields
        ------
        parameter : `object`
        """
        args = self.args
        if (args is not None):
            yield from args


class TimerHandle(Handle):
    """
    Object returned by a callback registration method:
    - ``EventThread.call_after``
    - ``EventThread.call_at``.
    
    Attributes
    ----------
    func : `callable`
        The wrapped function.
    args : `tuple` of `object`
        Parameters to call ``.func`` with.
    cancelled : `bool`
        Whether the handle is cancelled.
    when : `float`
        The respective loop's time, when the handle should be called.
    """
    __slots__ = ('when',)
    
    def __init__(self, when, func, args):
        """
        Creates a new ``TimerHandle`` with the given parameters.
        
        Parameters
        ----------
        when : `float`
            The respective loop's time, when the handle should be called.
        func : `callable`
            The function. to wrap.
        args : `tuple` of `object`
            Parameters to call `func` with.
        """
        self.func = func
        self.args = args
        self.cancelled = False
        self.when = when
    
    def __repr__(self):
        """Returns the timer handle's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
        ]
        
        if self.cancelled:
            repr_parts.append(' cancelled')
        else:
            repr_parts.append(' func = ')
            repr_parts.append(repr(self.func))
            repr_parts.append('(')
            
            args = self.args
            limit = len(args)
            if limit:
                index = 0
                while True:
                    arg = args[index]
                    repr_parts.append(repr(arg))
                    
                    index += 1
                    if index == limit:
                        break
                    
                    repr_parts.append(', ')
                    continue
            
            repr_parts.append(')')
            repr_parts.append(', when = ')
            repr_parts.append(repr(self.when))
        
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    def __hash__(self):
        """Returns the hash of the time, when the handle will be called."""
        return hash(self.when)
    
    def __gt__(self, other):
        """Returns whether this timer handle should be called later than the other."""
        return self.when > other.when
    
    def __ge__(self, other):
        """Returns whether this timer handle should be called later than the other, or whether the two are equal."""
        if self.when > other.when:
            return True
        
        return self.__eq__(other)
    
    def __eq__(self, other):
        """Returns whether the two timer handles are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return (
            self.when       == other.when       and
            self.func       == other.func       and
            self.args       == other.args       and
            self.cancelled  == other.cancelled
        )
    
    def __ne__(self, other):
        """Returns whether the two timer handles are not equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return (
            self.when       != other.when       or
            self.func       != other.func       or
            self.args       != other.args       or
            self.cancelled  != other.cancelled
        )
    
    def __le__(self, other):
        """Returns whether this timer handle should be called earlier than the other, or whether the two are equal."""
        if self.when < other.when:
            return True
        
        return self.__eq__(other)
    
    def __lt__(self, other):
        """Returns whether this timer handle should be called earlier than the other."""
        return self.when < other.when


class TimerWeakHandle(TimerHandle):
    """
    Object returned by a callback registration method:
    - ``EventThread.call_after_weak``
    - ``EventThread.call_at_weak``.
    
    Used when the respective `func`, might be garbage collected before it callback would run.
    
    Attributes
    ----------
    func : `callable`
        The wrapped function.
    args : `tuple` of `object`
        Parameters to call ``.func`` with.
    cancelled : `bool`
        Whether the handle is cancelled.
    when : `float`
        The respective loop's time, when the handle should be called.
    
    Notes
    -----
    This class also supports weakreferencing.
    """
    __slots__ = ('__weakref__', )
    
    def __init__(self, when, func, args):
        """
        Creates a new ``TimerWeakHandle`` with the given parameters.
        
        Parameters
        ----------
        when : `float`
            The respective loop's time, when the handle should be called.
        func : `callable`
            The function. to wrap.
        args : `tuple` of `object`
            Parameters to call `func` with.
        
        Raises
        ------
        TypeError
            `func` is not weakreferable.
        """
        self.when = when
        callback = _TimerWeakHandleCallback(self)
        try:
            if type(func) is MethodType:
                func = weak_method.from_method(func, callback)
            else:
                func = WeakCallable(func, callback)
        except:
            # never leave a half finished object behind
            self.func = None
            self.args = None
            self.cancelled = True
            raise
        
        else:
            self.func = func
            self.args = args
            self.cancelled = False
    

class _TimerWeakHandleCallback:
    """
    Weakreference callback used by ``TimerWeakHandle`` to cancel the respective handle, when it's `func` gets
    garbage collected.
    
    Attributes
    ----------
    handle : ``WeakReferer`` (``TimerWeakHandle``)
        The respective handle.
    """
    __slots__ = ('handle', )
    
    def __init__(self, handle):
        """
        Creates a new weakreference callback used by ``TimerWeakHandle``.
        
        Parameters
        ----------
        handle : ``TimerWeakHandle``
            The respective handle.
        """
        self.handle = WeakReferer(handle)
    
    def __call__(self, reference):
        """
        Called, when the respective `TimerWeakHandle.func` is garbage collected.
        
        Parameters
        ----------
        reference : ``WeakReferer``
            Weakreference to the dead `func`.
        """
        handle = self.handle()
        if (handle is not None):
            handle.cancel()
