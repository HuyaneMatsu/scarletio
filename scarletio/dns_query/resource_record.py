__all__ = ('ResourceRecord',)

from ..utils import RichAttributeErrorBaseType


class ResourceRecord(RichAttributeErrorBaseType):
    """
    Represents a resource record included in a answer.
    
    Attributes
    ----------
    class_code : `int`
        The resource record's class code.
    
    labels : `None | tuple<bytes>`
        Labels to query.
    
    resource_record_type : `int`
        Resource record's type.
    
    validity_duration : `int`
        For how long the entry is valid.
    
    data : `None | bytes`
        The included data within the record.
    """
    __slots__ = ('class_code', 'data', 'labels', 'resource_record_type', 'validity_duration')
    
    def __new__(cls, labels, resource_record_type, class_code, validity_duration, data):
        """
        Creates a resource record included in an answer.
        
        Parameters
        ----------
        labels : `None | tuple<bytes>`
            Labels to query.
        
        resource_record_type : `int`
            Resource record's type.
        
        class_code : `int`
            The resource record's class code.
        
        validity_duration : `int`
            For how long the entry is valid.
        
        data : `None | bytes`
            The included data within the record.
        """
        self = object.__new__(cls)
        self.class_code = class_code
        self.labels = labels
        self.resource_record_type = resource_record_type
        self.validity_duration = validity_duration
        self.data = data
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
        
        # validity_duration
        repr_parts.append(', validity_duration = ')
        repr_parts.append(repr(self.validity_duration))
        
        # data
        repr_parts.append(', data = ')
        repr_parts.append(repr(self.data))
        
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
        
        # validity_duration
        if self.validity_duration != other.validity_duration:
            return False
        
        # data
        if self.data != other.data:
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
        hash_value ^= self.resource_record_type << 5
        
        # class_code
        hash_value ^= self.class_code << 9
        
        # validity_duration
        hash_value ^= self.validity_duration
        
        # data
        data = self.data
        if (data is not None):
            hash_value ^= hash(self.data)
        
        return hash_value
