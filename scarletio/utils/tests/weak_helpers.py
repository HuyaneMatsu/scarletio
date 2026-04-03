import gc


def gc_collect():
    gc.collect()
    gc.collect()
    gc.collect()


class WeakReferencable:
    __slots__ = ('__weakref__', 'value')
    
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value == other.value
    
    def __gt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value > other.value
    
    def __lt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value < other.value
    
    def __ne__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value != other.value
    
    def __hash__(self):
        return self.value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'


def sort_by_type_first_key(key):
    return (key.__class__.__name__, key)
