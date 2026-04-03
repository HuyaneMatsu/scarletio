__all__ = ('DOCS_ENABLED', 'copy_docs',  'has_docs', 'set_docs', )

from functools import partial as partial_func


# Future reference
DOCS_ENABLED = True


def has_docs(target):
    """
    Modifies the target object's docstring if applicable.
    
    Parameter
    ---------
    target : `object`
        The object to modify the docstring of.
    
    Returns
    -------
    target : `target`
        The target object.
    """
    if not DOCS_ENABLED:
        target.__doc__ = None
    
    return target

if DOCS_ENABLED and (has_docs.__doc__ is None):
    DOCS_ENABLED = False

if not DOCS_ENABLED:
    has_docs.__doc__ = None


@has_docs
def set_docs(target, docs):
    """
    Sets docstring to the target object.
    
    Parameter
    ---------
    target : `object`
        The object to set the docstring to.
    docs : `str`
        Docstring to set.
    
    Returns
    -------
    target : `object`
        The target object.
    """
    if DOCS_ENABLED:
        target.__doc__ = docs
    
    return target


@has_docs
def _do_copy_docs(source, target):
    """
    Does the actual doc-string copy described by ``copy_docs``.
    
    Parameters
    ----------
    source : `object`
        The source object to copy it's doc-string from.
    target : `object`
        The target object to copy it's doc-string to.
    
    Returns
    -------
    target : `object`
        The target object.
    """
    target.__doc__ = source.__doc__
    return target


@has_docs
def copy_docs(source):
    """
    Copies a function's doc-string to an other one.
    
    Parameters
    ----------
    source : `object`
        The source object to copy it's docs from.
    
    Returns
    -------
    wrapper : ``functools.partial``
        Wrapper which will change the target object's docstring.
    
    Examples
    --------
    
    ```py
    def eat():
        \"\"\"Cakes are great\"\"\"
        pass
    
    @copy_docs(eat)
    def taste():
        pass
    ```
    """
    return partial_func(_do_copy_docs, source)
