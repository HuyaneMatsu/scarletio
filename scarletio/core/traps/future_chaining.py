__all__ = ('shield',)

from .future import Future


class _FutureChainer:
    """
    Chains a future's result into an other one used as a callback of the source future.
    
    Attributes
    ----------
    target : ``Future``
        The target future to chain the result into if applicable.
    """
    __slots__ = ('target',)
    
    def __init__(self, target):
        """
        Creates a new ``_FutureChainer`` with the given target future.
        
        Parameters
        ----------
        target : ``Future``
            The target future to chain the result into if applicable.
        """
        self.target = target
    
    def __call__(self, future):
        """
        Chains the source future's result into the target one.
        
        Parameters
        ----------
        future : ``Future``
            The source future to chain it's result from.
        """
        # remove chain remover
        target = self.target
        callbacks = target._callbacks
        for index in range(len(callbacks)):
            callback = callbacks[index]
            if (type(callback) is _ChainRemover) and (callback.target is future):
                del callbacks[index]
                break
        
        # set result
        if target.is_pending():
            target._state |= future._state
            target._result = future._result
            
            target._loop._schedule_callbacks(target)


class _ChainRemover:
    """
    Removes the ``_FutureChainer`` callback of the source future if the chained target future is marked as done before.
    
    Parameters
    -------
    target : ``Future``
        The source future.
    """
    __slots__ = ('target',)
    
    def __init__(self, target):
        self.target = target
    
    def __call__(self, future):
        # remove chainer
        callbacks = self.target._callbacks
        for index in range(len(callbacks)):
            callback = callbacks[index]
            if (type(callback) is _FutureChainer) and (callback.target is future):
                del callbacks[index]
                # because this might be the only place, where we retrieve the result, we will just silence it.
                future.silence()
                break


def shield(awaitable, loop):
    """
    Protects the given `awaitable` from being cancelled.
    
    Parameters
    ----------
    awaitable : `awaitable`
        The awaitable object to shield.
    loop : ``EventThread``
        The event loop to run the `awaitable` on.
    
    Returns
    -------
    un_protected : ``Future``
        If the given `awaitable` is a finished task, returns it, else returns a ``Future``, to what the original
        awaitable's result will be chained to.
    
    Raises
    -------
    TypeError
        The given `awaitable` is not `awaitable`.
    """
    protected = loop.ensure_future(awaitable)
    if protected.is_done():
        return protected # already done, we can return
    
    un_protected = Future(loop)
    protected._callbacks.append(_FutureChainer(un_protected))
    un_protected._callbacks.append(_ChainRemover(protected))
    return un_protected
