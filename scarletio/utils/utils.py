__all__ = (
    'IS_UNIX', 'any_to_any', 'change_on_switch', 'get_short_executable', 'is_hashable', 'is_iterable',
    'list_difference', 'relative_index', 'un_map_pack', 'where'
)

import sys
from os import sep as PATH_SEPARATOR

from .docs import has_docs


IS_UNIX = (sys.platform != 'win32')

@has_docs
def any_to_any(container1, container2):
    """
    Returns whether any value of `container1` is in `container2` as well.
    
    Parameters
    ----------
    container1 : `iterable-container`
        Any iterable container.
    container2 : `iterable-container`
        Any iterable container.

    Returns
    -------
    contains : `bool`
    """
    for value in container1:
        if value in container2:
            return True
    
    return False


@has_docs
def get_short_executable():
    """
    Gets short executable name.
    
    Returns
    -------
    executable : `str`
    """
    executable = sys.executable
    
    index = executable.rfind(PATH_SEPARATOR)
    if index != -1:
        executable = executable[index + 1:]
    
    if (not IS_UNIX) and executable.endswith('.exe'):
        executable = executable[:-len('.exe')]
    
    return executable


@has_docs
def where(container, key):
    """
    Returns the first element from the given container on what `key` returns `True`.
    
    Parameters
    ----------
    container : `iterable-container`
        Any iterable container.
    key : `function`
        Function used to determine whether an element of `container` meets our expectations.
    
    Returns
    -------
    value : `object`
        An element of `container`.
    
    Raises
    ------
    LookupError
        On non of the elements was `true` returned by they `key.
    """
    for value in container:
        if key(value):
            break
    else:
        raise LookupError(key)
    
    return value


@has_docs
def relative_index(list_, value):
    """
    Returns on which the given `value` would be inserted into the given list.
    
    Parameters
    ----------
    list_ : `list` of `object`
        The list o which value would be inserted.
    value : `object`
        The value what would be inserted.
    
    Returns
    -------
    relative_index : `int`
    """
    bot = 0
    top = len(list_)
    
    while True:
        if bot < top:
            half = (bot + top) >> 1
            if list_[half] < value:
                bot = half + 1
            else:
                top = half
            continue
        return bot


@has_docs
def change_on_switch(list_, value, new_position, key = None):
    """
    Calculates the changes if the given `value` would be moved to an another position.
    
    Parameters
    ----------
    list_ : `list` of `object`
        The list on what the changes will be calculated.
    value : `object`
        The object, what would be moved.
    new_position : `int`
        The new position of the value.
    key : `None`, `callable`
        A special callable what would be used to used to build each element of the result.
    
    Returns
    -------
    result : `list` of (`tuple` (`int`, `object`)) or `callable` returns
        The changed positions.
    
    Raises
    ------
    ValueError
        The given `value` is not in the list.
    """
    ln = len(list_)
    
    old_position = relative_index(list_, value)
    if (old_position == ln) or (list_[old_position] != value):
        raise ValueError(f'{value!r} is not in the {list_.__class__.__name__}.')
    
    if new_position >= ln:
        new_position = ln - 1
    elif new_position < 0:
        new_position = 0
    
    result = []
    if new_position == old_position:
        return result
    
    if new_position < old_position:
        index = new_position
        limit = old_position
        change = +1
    
    else:
        index = old_position + 1
        limit = new_position + 1
        change = -1
    
    while True:
        actual = list_[index]
        index += 1
        
        position = index + change
        if key is None:
            element = (actual, position)
        else:
            element = key(actual, position)
        
        result.append(element)
        
        if index == limit:
            break
        
        continue
    
    if key is None:
        element = (value, new_position)
    else:
        element = key(value, new_position)
    
    if change > 0:
        result.index(0, element)
    else:
        result.append(element)
    
    return result



@has_docs
def list_difference(list1, list2):
    """
    Returns the difference of the two given lists.
    
    Parameters
    ----------
    list1 : `None`, `list`, `set`
        The first list, what's inclusive elements should go into the return's zero-th element.
    list2 : `None`, `list`, `set`
        The second list, what's inclusive elements should go into the return's one-th element.
    
    Returns
    -------
    difference : `tuple` (`list` of `object`, `list` of `object`)
        A tuple containing the inclusive element of the given parameters.
    
    Notes
    -----
    `list1` and `list2` should be given as sorted lists, but `None` and `set`-s are also accepted.
    """
    difference = ([], [])
    
    if list1 is None:
        if list2 is None:
            return difference
        else:
            difference[1].extend(list2)
            return difference
    else:
        if list2 is None:
            difference[0].extend(list1)
            return difference
    
    if isinstance(list1, set):
        list1 = sorted(list1)
    if isinstance(list2, set):
        list2 = sorted(list2)
        
    ln1 = len(list1)
    ln2 = len(list2)
    index1 = 0
    index2 = 0

    #some quality python here again *cough*
    while True:
        if index1 == ln1:
            while True:
                if index2 == ln2:
                    break
                value2 = list2[index2]
                difference[1].append(value2)
                index2 += 1

            break
        if index2 == ln2:
            while True:
                if index1 == ln1:
                    break
                value1 = list1[index1]
                difference[0].append(value1)
                index1 += 1

            break
        
        value1 = list1[index1]
        value2 = list2[index2]
        if value1 < value2:
            difference[0].append(value1)
            index1 += 1
            continue
        if value1 > value2:
            difference[1].append(value2)
            index2 += 1
            continue
        if value1 != value2:
            difference[0].append(value1)
            difference[1].append(value2)
        index1 += 1
        index2 += 1
    
    return difference


@has_docs
class un_map_pack:
    """
    Helper class for un-map-packing generators.
    
    Attributes
    ----------
    generator : ``GeneratorType``
        The generator to unpack.
    next_value : `object`
        The next key to return on get-item.
    """
    def __init__(self, generator):
        """
        Creates a new generator into mapping unpacker.
        
        Parameters
        ----------
        generator : ``GeneratorType``
            A generator to un-map-pack.
        """
        self.generator = generator
        self.next_value = None
    
    @has_docs
    def keys(self):
        """
        Calling ``.keys`` returns itself.
        
        Returns
        -------
        self: `instance<cls>`
        """
        return self
    
    @has_docs
    def __iter__(self):
        """Iterating an un map packer returns itself."""
        return self
    
    @has_docs
    def __next__(self):
        """Gets the next key of the un-map-packer"""
        key, value = next(self.generator)
        self.next_value = value
        return key
    
    @has_docs
    def __getitem__(self, key):
        """Gets the next value of the un-map-packer."""
        return self.next_value


@has_docs
def is_iterable(object_):
    """
    Returns whether the object is iterable.
    
    Parameters
    ----------
    object_ : `object`
        The object to check.
    
    Returns
    -------
    is_iterable : `bool`
    """
    return hasattr(type(object_), '__iter__')


@has_docs
def is_hashable(object_):
    """
    Returns whether the object is hashable.
    
    Parameters
    ----------
    object_ : `object`
        The object to check.
    
    Returns
    -------
    is_hashable : `bool`
    """
    try:
        hasher_function = getattr(type(object_), '__hash__')
    except AttributeError:
        return False
    
    try:
        hasher_function(object_)
    except (TypeError, NotImplementedError):
        return False
    
    return True
