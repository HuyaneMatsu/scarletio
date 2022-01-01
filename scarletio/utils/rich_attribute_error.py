__all__ = ('RichAttributeErrorBaseType',)

from difflib import get_close_matches
from itertools import permutations as permutate


EXCEPTION_MESSAGE_CACHE = {}

LOCKS = set()

# This will avoid recursion error when something goes really bad.
LOCK_MAX_DEEPNESS = 10

def _iterate_alternative_attribute_names(attribute_name):
    """
    Tries to create alternative versions of the given `attribute_name`.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute name to create alternative names of.
    
    Yields
    ------
    alternative_attribute_name : `str`
    """
    yield attribute_name
    
    split = attribute_name.split('_')
    split_count = len(split)
    if split_count > 1:
        for permutation in permutate(split, split_count):
            yield '_'.join(permutation)


def _create_rich_exception_message(instance, attribute_name):
    """
    Creates rich exception message for the given instance's given attribute's name.
    
    Parameters
    ----------
    instance : `object`
        The instance who has no attribute like `attribute_name`.
    attribute_name : `str`
        The evil variable name.
    """
    exception_message_parts = []
    
    exception_message_parts.append('`')
    exception_message_parts.append(type(instance).__name__)
    exception_message_parts.append('` has no attribute `')
    exception_message_parts.append(attribute_name)
    exception_message_parts.append('`')
    
    lock_key = (type(instance), attribute_name)
    
    if (lock_key not in LOCKS) and (len(LOCKS) < LOCK_MAX_DEEPNESS):
        try:
            LOCKS.add(lock_key)
            
            diversity = 0.8 - (20 - min(len(attribute_name), 20)) * 0.01
            
            directory = dir(instance)
            
            collected_matches = set()
            
            for alternative_attribute_name in _iterate_alternative_attribute_names(attribute_name):
                matches = get_close_matches(alternative_attribute_name, directory, n=10, cutoff=diversity)
                collected_matches.update(matches)
            
            sorted_matches = sorted(collected_matches)
            
            
            matches_count = len(sorted_matches)
            if matches_count == 0:
                pass
            
            elif matches_count == 1:
                exception_message_parts.append('; Did you mean: `')
                exception_message_parts.append(sorted_matches[0])
                exception_message_parts.append('`')
            
            else:
                exception_message_parts.append('; Did you mean any of: ')
                
                index = 0
                while True:
                    exception_message_parts.append('`')
                    exception_message_parts.append(sorted_matches[index])
                    exception_message_parts.append('`')
                    
                    index += 1
                    if index == matches_count:
                        break
                    
                    exception_message_parts.append(', ')
                    continue
        finally:
            LOCKS.discard(lock_key)
    
    exception_message_parts.append('.')
    
    return ''.join(exception_message_parts)


class RichAttributeErrorBaseType:
    """
    Base type for generating rich attribute error messages.
    """
    __slots__ = ()
    
    def __getattr__(self, attribute_name):
        """Drops a rich attribute error."""
        
        # Python tries to get `__dict__` even if there is no `__dict__` when calling `dir()`.
        if (attribute_name == '__dict__') and ((type(self), attribute_name) in LOCKS):
            raise AttributeError(attribute_name)
        
        # Use goto to avoid putting `KeyError` on exception traceback context.
        while True:
            if type(self).__getattr__ is not RichAttributeErrorBaseType.__getattr__:
                exception_message = _create_rich_exception_message(self, attribute_name)
                break
            
            key = (getattr(type(self), '__module__', ''), attribute_name)
            
            try:
                exception_message = EXCEPTION_MESSAGE_CACHE[key]
            except KeyError:
                pass
            else:
                break
            
            exception_message = _create_rich_exception_message(self, attribute_name)
            EXCEPTION_MESSAGE_CACHE[key] = exception_message
            break
        
        raise AttributeError(exception_message)
