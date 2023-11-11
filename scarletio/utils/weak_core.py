__all__ = ('WeakCallable', 'WeakHasher', 'WeakReferer', 'is_weakreferable', 'weak_method',)

from .compact import NEEDS_DUMMY_INIT
from .docs import has_docs
from .method_like import MethodLike

try:
    from _weakref import ref as WeakrefType
except ImportError:
    from weakref import ref as WeakrefType


@has_docs
def is_weakreferable(object_):
    """
    Returns whether the given object is weakreferable.
    
    Parameters
    ----------
    object_ : `object`
        The object to check.
    
    Returns
    -------
    is_weakreferable : `bool`
    """
    slots = getattr(type(object_), '__slots__', None)
    if (slots is not None) and ('__weakref__' in slots):
        return True
    
    if hasattr(object_, '__dict__'):
        return True
    
    return False


@has_docs
class WeakHasher:
    """
    Object to store unhashable weakreferences.
    
    Attributes
    ----------
    _hash : `int`
        The hash of the respective reference.
    reference : ``WeakReferer``
        A dead reference to hash.
    """
    __slots__ = ('_hash', 'reference',)
    
    @has_docs
    def __init__(self, reference):
        """
        Creates a new ``WeakHasher`` from the given reference.
        
        Parameters
        ----------
        reference : ``WeakReferer``
            A dead reference to hash.
        """
        self._hash = object.__hash__(reference)
        self.reference = reference
    
    @has_docs
    def __hash__(self):
        """Returns the ``WeakHasher``'s hash value."""
        return self._hash
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the two ``WeakHasher``-s are the same."""
        self_reference = self.reference
        if self_reference is other:
            return True
        
        if type(self) is not type(other):
            return NotImplemented
        
        return (self.reference is other.reference)
    
    @has_docs
    def __repr__(self):
        """Returns the ``WeakHasher``'s representation."""
        return f'{self.__class__.__name__}({self.reference!r})'
    
    @has_docs
    def __getattr__(self, name):
        """Returns the attribute of the ``WeakHasher``'s reference."""
        return getattr(self.reference, name)


@has_docs
def add_to_pending_removals(container, reference):
    """
    Adds the given weakreference to the given set.
    
    Parameters
    ----------
    container : `object`
        The parent object, which is iterating right now, so it's items cannot be removed.
    reference : ``WeakReferer``
        The weakreference to add to the set.
    """
    try:
        hash(reference)
    except TypeError:
        reference = WeakHasher(reference)
    
    pending_removals = container._pending_removals
    if pending_removals is None:
        container._pending_removals = pending_removals = set()
    
    pending_removals.add(reference)


# speedup builtin stuff, CPython is welcome
@has_docs
class WeakReferer(WeakrefType):
    """
    Weakreferences to an object.
    
    After calling it returns the referenced object or `None` if already dead.
    """
    __slots__ = ()
    if NEEDS_DUMMY_INIT:
        def __init__(self, *args, **kwargs):
            pass
    else:
        __init__ = object.__init__
    
    
    def __repr__(self):
        repr_parts = ['<', self.__class__.__name__]
        
        value = self()
        if value is None:
            repr_parts.append(' (dead)')
        else:
            repr_parts.append(' value = ')
            repr_parts.append(repr(value))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


del WeakrefType


@has_docs
class KeyedReferer(WeakReferer):
    """
    Weakreferences an object with a key, what can be used to identify it.
    
    Attributes
    ----------
    key : `object`
        Key to identify the weakreferenced object.
    """
    __slots__ = ('key', )
    
    @has_docs
    def __new__(cls, obj, callback, key, ):
        """
        Creates a new ``KeyedReferer`` with the given parameters.
        
        Parameters
        ----------
        obj : `object`
            The object to weakreference.
        callback : `object`
            Callback running when the object is garbage collected.
        key : `object`
            Key to identify the weakreferenced object.
        """
        self = WeakReferer.__new__(cls, obj, callback)
        self.key = key
        return self


@has_docs
class WeakCallable(WeakReferer):
    """
    Weakreferences a callable object.
    
    When the object is called, calls the weakreferenced object if not yet collected.
    """
    __slots__ = ()
    
    @has_docs
    def __call__(self, *args, **kwargs):
        """
        Calls the weakreferenced object if not yet collected.
        
        Parameters
        ----------
        *args : Parameters
            Parameters to call the weakreferenced callable with.
        **kwargs : Keyword parameters
            Keyword parameters to call the weakreferenced callable with..
        
        Returns
        -------
        result : `object`
            The returned value by the referenced object. Returns `None` if the object is already collected.
        
        Raises
        ------
        BaseException
            Raised exception by the referenced callable.
        """
        self = WeakReferer.__call__(self)
        if self is None:
            return
        
        return self(*args, **kwargs)
    
    @has_docs
    def is_alive(self):
        """
        Returns whether the ``WeakCallable`` is still alive (the referred object by it is not collected yet.)
        
        Returns
        -------
        is_alive : `bool`
        """
        return (WeakReferer.__call__(self) is not None)


@has_docs
class weak_method(WeakReferer, MethodLike):
    """
    A method like, what weakreferences it's object not blocking it from being garbage collected.
    
    Attributes
    ----------
    __func__ : `callable`
        The function to call as a method.
    
    Class Attributes
    ----------------
    __reserved_argcount__ : `int` = `1`
        The amount of reserved parameters by weak_method.
    """
    __slots__ = ('__func__',)
    
    __reserved_argcount__ = 1
    
    @has_docs
    def __new__(cls, obj, func, callback = None):
        """
        Creates a new ``weak_method`` with the given parameter.
        
        Parameters
        ----------
        obj : `object`
            The object to weakreference and pass to `func`.
        func : `callable`
            The function to call as a method.
        callback : `object` = `None`, Optional
            Callback running when the object is garbage collected.
        """
        self = WeakReferer.__new__(cls, obj, callback)
        self.__func__ = func
        return self
    
    @property
    @has_docs
    def __self__(self):
        """
        Returns the weakreferenced object by the ``weak_method``. `None` if it was already garbage collected.
        
        Returns
        -------
        obj : `object`
            The weakreferenced object if not yet garbage collected. Defaults to `None`.
        """
        return WeakReferer.__call__(self)
    
    @has_docs
    def __call__(self, *args, **kwargs):
        """
        Calls the weak_method object's function with it's object if not yet collected.
        
        Parameters
        ----------
        *args : Parameters
            Parameters to call the function with.
        **kwargs : Keyword parameters
            Keyword parameters to call the function with.
        
        Returns
        -------
        result : `object`
            The returned value by the function. Returns `None` if the object is already collected.
        
        Raises
        ------
        BaseException
            Raised exception by the function.
        """
        obj = WeakReferer.__call__(self)
        if obj is None:
            return
        
        return self.__func__(obj, *args, **kwargs)
    
    @has_docs
    def is_alive(self):
        """
        Returns whether the ``weak_method``'s object is still alive (the referred object by it is not collected yet.)
        
        Returns
        -------
        is_alive : `bool`
        """
        return (WeakReferer.__call__(self) is not None)
    
    def __getattr__(self, name):
        return getattr(self.__func__, name)
    
    @classmethod
    @has_docs
    def from_method(cls, method_, callback = None):
        """
        Creates a new ``weak_method`` from the given `method`.
        
        Parameters
        ----------
        method_ : `method`
            The method tu turn into ``weak_method``.
        callback : `object`, Optional
            Callback running when the respective object is garbage collected.
        """
        self = WeakReferer.__new__(cls, method_.__self__, callback)
        self.__func__ = method_.__func__
        return self
