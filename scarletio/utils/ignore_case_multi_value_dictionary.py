__all__ = ('IgnoreCaseMultiValueDictionary', )

from .docs import copy_docs, has_docs
from .ignore_case_string import IgnoreCaseString
from .multi_value_dictionary import MultiValueDictionary


@has_docs
class IgnoreCaseMultiValueDictionary(MultiValueDictionary):
    """
    ``MultiValueDictionary`` sub-type that can be used to hold http headers.
    
    Its keys ignore casing.
    """
    __slots__ = ()
    
    @copy_docs(MultiValueDictionary.__init__)
    def __init__(self, iterable = None):
        dict.__init__(self)
        
        if (iterable is None) or (not iterable):
            return
        
        get_item = dict.__getitem__
        set_item = dict.__setitem__
        
        if type(iterable) is type(self):
            for key, values in dict.items(iterable):
                set_item(self, key, values.copy())
        
        elif isinstance(iterable, MultiValueDictionary):
            for key, values in dict.items(iterable):
                set_item(self, IgnoreCaseString(key), values.copy())
        
        elif isinstance(iterable, dict):
            for key, value in iterable.items():
                key = IgnoreCaseString(key)
                set_item(self, key, [value])
        
        else:
            for key, value in iterable:
                key = IgnoreCaseString(key)
                try:
                    values = get_item(self, key)
                except KeyError:
                    set_item(self, key, [value])
                else:
                    if value not in values:
                        values.append(value)
    
    
    @copy_docs(MultiValueDictionary.__getitem__)
    def __getitem__(self, key):
        key = IgnoreCaseString(key)
        return dict.__getitem__(self, key)[0]
    
    
    @copy_docs(MultiValueDictionary.__setitem__)
    def __setitem__(self, key, value):
        key = IgnoreCaseString(key)
        MultiValueDictionary.__setitem__(self, key, value)
    
    
    @copy_docs(MultiValueDictionary.__delitem__)
    def __delitem__(self, key):
        key = IgnoreCaseString(key)
        MultiValueDictionary.__delitem__(self, key)
    
    
    @copy_docs(MultiValueDictionary.extend)
    def extend(self, mapping):
        getitem = dict.__getitem__
        setitem = dict.__setitem__
        
        for key, value in mapping.items():
            key = IgnoreCaseString(key)
            try:
                values = getitem(self, key)
            except KeyError:
                setitem(self, key, [value])
            else:
                if value not in values:
                    values.append(value)
    
    
    @copy_docs(MultiValueDictionary.get_all)
    def get_all(self, key, default = None):
        key = IgnoreCaseString(key)
        return MultiValueDictionary.get_all(self, key, default)
    
    
    @copy_docs(MultiValueDictionary.get_one)
    def get_one(self, key, default = None):
        key = IgnoreCaseString(key)
        return MultiValueDictionary.get_one(self, key, default)
    
    
    get = get_one
    
    
    @copy_docs(MultiValueDictionary.setdefault)
    def setdefault(self, key, default = None):
        key = IgnoreCaseString(key)
        return MultiValueDictionary.setdefault(self, key, default)
    
    
    @copy_docs(MultiValueDictionary.pop_all)
    def pop_all(self, key, default = ...):
        key = IgnoreCaseString(key)
        return MultiValueDictionary.pop_all(self, key, default)
    
    
    @copy_docs(MultiValueDictionary.pop_one)
    def pop_one(self, key, default = ...):
        key = IgnoreCaseString(key)
        return MultiValueDictionary.pop_one(self, key, default)
    
    
    pop = pop_one
