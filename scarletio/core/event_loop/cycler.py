__all__ = ('Cycler',)

from threading import current_thread

from ...utils import CallableAnalyzer, include

from ..time import LOOP_TIME
from ..traps import Task


write_exception_async = include('write_exception_async')


class CyclerCallable:
    """
    An element of a ``Cycler``, which describes whether the stored callable is sync or async and what is it's ordering
    priority.
    
    Attributes
    ----------
    func : `callable`
        The function to call.
    is_async : `bool`
        Whether `func` is async.
    priority : `int`
        Call order priority inside of a ``Cycler``.
    """
    __slots__ = ('func', 'is_async', 'priority')
    
    def __new__(cls, func, priority):
        """
        Creates a new ``CyclerCallable`` with the given parameters.
        
        Parameters
        ----------
        func : `callable`
            The function to call.
        priority : `int`
            Call order priority inside of a ``Cycler``.
        
        Raises
        ------
        TypeError
            - `priority` is not `int`, neither other numeric convertible to it.
            - `func` is not `callable`.
            - `func` accepts less or more reserved positional parameters than `1`.
        """
        if type(func) is cls:
            return func
        
        priority_type = type(priority)
        if (priority_type is not int):
            try:
                __int__ = getattr(priority, '__int__')
            except AttributeError:
                raise TypeError(
                    f'`priority` can be `int`, `numeric`, got {priority_type.__name__}; {priority!r}.'
                ) from None
            
            priority = __int__(priority)
        
        analyzer = CallableAnalyzer(func)
        min_, max_ = analyzer.get_non_reserved_positional_parameter_range()
        if min_ > 1:
            raise TypeError(
                f'`{func!r}` excepts at least `{min_!r}` non reserved parameters, meanwhile `1` would be '
                'passed to it.'
            )
        
        if not ((min_ == 1) or max_ >= 1 or analyzer.accepts_args()):
            raise TypeError(
                f'`{func!r}` expects maximum `{max_!r}` non reserved parameters, meanwhile the event '
                'expects to pass `1`.'
            )
        
        is_async = analyzer.is_async()
        
        self = object.__new__(cls)
        self.func = func
        self.is_async = is_async
        self.priority = priority
        
        return self
    
    def __repr__(self):
        """Returns the cycler callable's representation."""
        return f'{self.__class__.__name__}(func={self.func!r}, priority={self.priority!r})'
    
    def __gt__(self, other):
        """Returns whether the priority of this cycler callable is greater than the other's."""
        return self.priority > other.priority
    
    def __ge__(self, other):
        """
        Returns whether the priority of this cycler callable is greater than the other's, or if both instance is equal.
        """
        self_priority = self.priority
        other_priority = other.priority
        if self_priority > other_priority:
            return True
        
        if other_priority == other_priority:
            if self.func == other.func:
                return True
        
        return False
    
    def __eq__(self, other):
        """Returns whether this cycler callable equals to the other."""
        if self.priority != other.priority:
            return False
        
        if self.func != other.func:
            return False
        
        return True
    
    def __ne__(self, other):
        """Returns whether this cycler callable not equals to the other."""
        if self.priority != other.priority:
            return True
        
        if self.func != other.func:
            return True
        
        return False
    
    def __le__(self, other):
        """
        Returns whether the priority of this cycler callable is less than the other's, or if both instance is equal.
        """
        self_priority = self.priority
        other_priority = other.priority
        if self_priority < other_priority:
            return True
        
        if other_priority == other_priority:
            if self.func == other.func:
                return True
        
        return False

    def __lt__(self, other):
        """Returns whether the priority of this cycler callable is less than the other's."""
        return self.priority < other.priority



class Cycler:
    """
    Cycles the given functions on an event loop, by calling them after every `n` amount of seconds.
    
    Attributes
    ----------
    cycle_time : `float`
        The time interval of the cycler to call the added functions.
    funcs : `list` of ``CyclerCallable``
        Callables of a cycler containing whether they are sync, async, and what is their priority order.
    handle : ``TimerHandle``
        Handler, what will call the cycler when cycle time is over.
    loop : ``EventThread``
        The async event loop of the cycler, what it uses to ensure itself.
    """
    __slots__ = ('cycle_time', 'funcs', 'handle', 'loop',)
    
    def __new__(cls, loop, cycle_time, *funcs, priority = 0):
        """
        Creates a new ``Cycler`` with the given parameters.
        
        Parameters
        ----------
        loop : ``EventThread``
            The async event loop of the cycler, what it uses to ensure itself.
        cycle_time : `float`
            The time interval of the cycler to call the added functions.
        *funcs : `callable`
            Callables, what the cycler will call.
        priority : `int` = `0`, Optional (Keyword only)
            Priority order of the added callables, which define in which order the given `funcs` will be called.
        
        Raises
        ------
        RuntimeError
            Event loop closed.
        TypeError
            - `cycle_time` is not `float`, neither other numeric convertible to it.
            - `priority` is not `int`, neither other numeric convertible to it.
            - Any `func` is not `callable`.
            - Any `func` accepts less or more reserved positional parameters than `1`.
        ValueError
            If `cycle_time` is negative or `0`.
        
        Notes
        -----
        If the respective event loop is not running yet, then creating a ``Cycler`` will not start it either.
        """
        if not loop.running and not loop.should_run:
            raise RuntimeError('Event loop is closed.')
        
        cycle_time_type = cycle_time.__class__
        if cycle_time_type is not float:
            try:
                __float__ = getattr(cycle_time_type, '__float__')
            except AttributeError:
                raise TypeError(
                    f'`cycle_time` can be `float`, `numeric`, got {cycle_time_type.__name__}; {cycle_time!r}.'
                ) from None
            
            cycle_time = __float__(cycle_time)
        
        if cycle_time <= 0.0:
            raise ValueError(
                f'{cycle_time} cannot be `0` or less, got {cycle_time!r}.'
            )
        
        priority_type = type(priority)
        if (priority_type is not int):
            try:
                __int__ = getattr(priority, '__int__')
            except AttributeError:
                raise TypeError(
                    f'`priority` can be `int`, `numeric`, got {priority_type.__name__}; {priority!r}.'
                ) from None
            
            priority = __int__(priority)
        
        validated_funcs = []
        
        if funcs:
            for func in funcs:
                validated_func = CyclerCallable(func, priority)
                validated_funcs.append(validated_func)
            
            validated_funcs.sort()
        
        self = object.__new__(cls)
        self.loop = loop
        self.funcs = validated_funcs
        self.cycle_time = cycle_time
        if current_thread() is loop:
            handle = loop.call_after(cycle_time, cls._run, self)
        else:
            handle = loop.call_soon_thread_safe_lazy(loop.__class__.call_after, loop, cycle_time, cls._run, self)
        
        self.handle = handle
        
        return self
    
    def _run(self):
        """
        Runs all the functions added to the cycler.
        """
        for func in self.funcs:
            try:
                result = func.func(self)
                if func.is_async:
                    Task(self.loop, result)
            except BaseException as err:
                write_exception_async(
                    err,
                    [
                        self.__class__.__name__,
                        ' exception occurred\nat calling ',
                        repr(func),
                        '\n',
                    ],
                    loop = self.loop,
                )
        
        self.handle = self.loop.call_after(self.cycle_time, self.__class__._run, self)
    
    def __repr__(self):
        """Returns the cycler's representation."""
        repr_parts = [
            self.__class__.__name__,
            '(',
            repr(self.loop),
            ', ',
            str(self.cycle_time)
        ]
        
        funcs = self.funcs
        limit = len(funcs)
        if limit:
            priority = funcs[0].priority
            
            index = 1
            while index < limit:
                func = funcs[index]
                if func.priority == priority:
                    index += 1
                    continue
                
                for func in funcs:
                    repr_parts.append(', ')
                    repr_parts.append(repr(func))
                break
            
            else:
                for func in funcs:
                    repr_parts.append(', ')
                    repr_parts.append(repr(func.func))
                
                repr_parts.append(', priority = ')
                repr_parts.append(repr(priority))
        
        repr_parts.append(')')
        return ''.join(repr_parts)
    
    
    def cancel(self):
        """
        Cancels the cycler.
        
        If called from an other thread than it's event loop, then ensures ``._cancel`` on it instead of calling it
        right away.
        """
        loop = self.loop
        if current_thread() is loop:
            self._cancel()
            return
        
        loop.call_soon_thread_safe_lazy(self.__class__._cancel, self)
    
    
    def _cancel(self):
        """
        Cancels the cycler.
        
        This method always runs on the cycler's event loop.
        """
        handle = self.handle
        if (handle is not None):
            self.handle = None
            handle.cancel()
    
    
    def call_now(self):
        """
        Calls the cycler now, doing it's cycle.
        
        If called from an other thread than it's event loop, then ensures ``._call_now`` on it instead of calling it
        right away.
        """
        loop = self.loop
        if current_thread() is loop:
            self._call_now()
            return
        
        loop.call_soon_thread_safe_lazy(self.__class__._call_now, self)
    
    
    def _call_now(self):
        """
        Calls the cycler now, doing it's cycle.
        
        This method always runs on the cycler's event loop.
        """
        handle = self.handle
        if (handle is not None):
            handle.cancel()
        
        self._run()
    
    
    def reschedule(self):
        """
        Reschedules the cycler, making it's cycle to start since now. If the cycler is not running, also starts it.
        
        If called from an other thread than it's event loop, then ensures ``._reschedule`` on it instead of calling it
        right away.
        """
        loop = self.loop
        if current_thread() is loop:
            self._reschedule()
            return
        
        loop.call_soon_thread_safe_lazy(self.__class__._reschedule, self)
    
    
    def _reschedule(self):
        """
        Reschedules the cycler, making it's cycle to start since now. If the cycler is not running, also starts it.
        
        This method always runs on the cycler's event loop.
        """
        handle = self.handle
        if (handle is not None):
            handle.cancel()
        
        self.handle = self.loop.call_after(self.cycle_time, self.__class__._run, self)
    
    
    @property
    def running(self):
        """
        Returns whether the cycler is currently running.
        
        Returns
        -------
        running : `str`
        """
        return (self.handle is not None)
    
    
    def set_cycle_time(self, cycle_time):
        """
        Sets the cycle time of the cycler to the given value.
        
        Parameters
        ----------
        cycle_time : `float`
            The time interval of the cycler to call the added functions.
        
        Raises
        ------
        TypeError
            `cycle_time` is not `float`, neither other numeric convertible to it.
        ValueError
            If `cycle_time` is negative or `0`.
        """
        cycle_time_type = cycle_time.__class__
        if cycle_time_type is not float:
            try:
                __float__ = getattr(cycle_time_type, '__float__')
            except AttributeError:
                raise TypeError(
                    f'`cycle_time` can be `float`, `numeric`, got {cycle_time_type.__name__}; {cycle_time!r}.'
                ) from None
            
            cycle_time = __float__(cycle_time)
        
        if cycle_time <= 0.0:
            raise ValueError(
                f'{cycle_time} cannot be `0` or less, got {cycle_time!r}.'
            )
        
        self.cycle_time = cycle_time
    
    
    def append(self, func, priority = 0):
        """
        Adds the given `func` to the cycler to call.
        
        If called from an other thread than it's event loop, then it will ensure adding the `func` on it's own.
        
        Parameters
        ----------
        func : `callable`
            Callable, what the cycler will call.
        priority : `int` = `0`, Optional
            Priority order of the added callables, which define in which order the given `funcs` will be called.
        
        Raises
        ------
        TypeError
            - `priority` is not `int`, neither other numeric convertible to it.
            - Any `func` is not `callable`.
            - Any `func` accepts less or more reserved positional parameters than `1`.
        """
        validated_func = CyclerCallable(func, priority)
        
        loop = self.loop
        if current_thread() is loop:
            self._append(validated_func)
            return
        
        loop.call_soon_thread_safe_lazy(self.__class__._append, self, validated_func)
    
    
    def _append(self, validated_func):
        """
        Adds the given `func` to the cycler to call.
        
        This method always runs on the cycler's event loop.
        
        Parameters
        ----------
        validated_func : ``CyclerCallable``
            The already validated function to add.
        """
        funcs = self.funcs
        funcs.append(validated_func)
        funcs.sort()
    
    
    def remove(self, func):
        """
        Removes the given `func` from the cycler, so it will stop calling it.
        
        If called from an other thread than it's event loop, then ensures ``._remove`` on it instead of calling it
        right away.
        
        Parameters
        ----------
        func : `callable`
            The function to remove.
        """
        loop = self.loop
        if current_thread() is loop:
            self._remove(func)
            return
        
        loop.call_soon_thread_safe_lazy(self.__class__._remove, self, func)
    
    
    def _remove(self, func):
        """
        Removes the given `func` from the cycler, so it will stop calling it.
        
        This method always runs on the cycler's event loop.
        
        Parameters
        ----------
        func : `callable`
            The function to remove.
        """
        index = 0
        funcs = self.funcs
        limit = len(funcs)
        
        is_cycler_callable = (type(func) is CyclerCallable)
        
        while index < limit:
            to_compare = funcs[index]
            if (not is_cycler_callable):
                to_compare = to_compare.func
            
            if to_compare == func:
                del funcs[index]
                break
            
            index += 1
            continue
    
    
    def get_time_till_next_call(self):
        """
        Returns how much time is left till the next cycle call.
        
        Might return `-1.` if the cycler is closed, or `0.` if the calls are taking place right now.
        
        Returns
        -------
        time_till_next_call : `float`
        """
        handle = self.handle
        if handle is None:
            return -1.0 # wont be be called
        
        at = handle.when - LOOP_TIME()
        
        if at < 0.0:
            return 0.0 # right now
        
        return at
    
    
    def get_time_of_next_call(self):
        """
        Returns when the next cycle call will be.
        
        Might return `-1.` if the cycler is closed.
        
        Returns
        -------
        ime_of_next_call : `float`
        """
        handle = self.handle
        if handle is None:
            return -1. # wont be be called
        return handle.when
