__all__ = ('Question',)

from ..utils import RichAttributeErrorBaseType


class Question(RichAttributeErrorBaseType):
    """
    Represents a question of a query or an answer.
    
    Attributes
    ----------
    class_code : `int`
        Class code to query.
    
    labels : `None | tuple<bytes>`
        Labels to query.
    
    resource_record_type : `int`
        Resource record type to query.
    """
    __slots__ = ('class_code', 'labels', 'resource_record_type')
    
    def __new__(cls, labels, resource_record_type, class_code):
        """
        Question of a query or an answer.
        
        Parameters
        ----------
        labels : `None | tuple<bytes>`
            Labels to query.
        
        resource_record_type : `int`
            Resource record type to query.
        
        class_code : `int`
            Class code to query.
        """
        self = object.__new__(cls)
        self.class_code = class_code
        self.labels = labels
        self.resource_record_type = resource_record_type
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # labels
        repr_parts.append(' labels = ')
        repr_parts.append(repr(self.labels))
        
        # resource_record_type
        repr_parts.append(', resource_record_type = ')
        repr_parts.append(repr(self.resource_record_type))
        
        # class_code
        repr_parts.append(', class_code = ')
        repr_parts.append(repr(self.class_code))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # labels
        if self.labels != other.labels:
            return False
        
        # resource_record_type
        if self.resource_record_type != other.resource_record_type:
            return False
        
        # class_code
        if self.class_code != other.class_code:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns hash(self)."""
        hash_value = 0
        
        # labels
        labels = self.labels
        if (labels is not None):
            hash_value ^= 1 << 0
            hash_value ^= hash(labels)
        
        # resource_record_type
        hash_value ^= self.resource_record_type << 1
        
        # class_code
        hash_value ^= self.class_code << 5
        
        return hash_value
