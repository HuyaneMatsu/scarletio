__all__ = ('name_deduplicator_default',)

from re import compile as re_compile


NAME_DEDUPLICATOR_REGEX_PATTERN_DEFAULT = re_compile('((?:.*/)?.*?)(?: \\((\\d+)\\))?(?:\\.(.*?))?')


def name_deduplicator_name_reconstructor_default(path, index, extension):
    """
    Default deduplicator name reconstructor that is used.
    
    Parameters
    ----------
    path : `int`
        Path of the file without the index and the extension.
    
    index : `int`
        Index to postfix the file with.
    
    extension : `None | str`
        File extension.
    
    Returns
    -------
    name : `str`
    """
    name_parts = [path]
    
    if index:
        name_parts.append(' (')
        name_parts.append(str(index))
        name_parts.append(')')
    
    if (extension is not None):
        name_parts.append('.')
        name_parts.append(extension)
    
    return ''.join(name_parts)


def name_deduplicator_default(regex_pattern, name_reconstructor):
    """
    Regular name deduplicator. When calling `.send(name)` it produces a deduplicated version of the name.
    
    This function is a generator.
    
    Parameters
    ----------
    regex_pattern : `re.Pattern`
        Regex pattern to match names against.
    
    name_reconstructor : `FunctionType`
        Function to call when a name should be reconstructed.
    
    Yields
    ------
    name : `str`
    """
    collected = {}
    name = yield
    
    while True:
        match = regex_pattern.fullmatch(name)
        if match is None:
            path = name
            index = -1
            extension = None
        
        else:
            path, index, extension = match.groups()
            if index is None:
                index = -1
            else:
                index = int(index)
        
        key = (path, extension)
        counter, taken_values = collected.get(key, (-1, None))
        
        if (index > counter) and ((taken_values is None) or (index not in taken_values)):
            new_index = index
            
            if (taken_values is None):
                taken_values = set()
            
            taken_values.add(new_index)
        
        else:
            new_index = counter + 1
            if (taken_values is not None):
                while True:
                    try:
                        taken_values.remove(new_index)
                    except KeyError:
                        break
                    
                    new_index += 1
                    
                    if not taken_values:
                        taken_values = None
                        break
            
            counter = new_index
        
        collected[key] = (counter, taken_values)
        
        if (index != new_index):
            name = name_reconstructor(path, new_index, extension)
        
        name = yield name
