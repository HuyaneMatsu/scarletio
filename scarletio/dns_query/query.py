__all__ = ('Query',)

from ..utils import RichAttributeErrorBaseType


class Query(RichAttributeErrorBaseType):
    """
    Represents a query to request.
    
    Attributes
    ----------
    additional_resource_records : ``None | tuple<ResourceRecord>``
        Additional resource records to send.
    
    data_verification_desired : `bool`
        Whether the server should respond with verified data.
    
    questions : ``None | tuple<Question>``
        Questions to request.
    
    recursion_desired : `bool`
        Whether recursion is desired.
        
    transaction_id : `int`
        The transaction's identifier.
    """
    __slots__ = (
        'additional_resource_records', 'data_verification_desired', 'questions', 'recursion_desired', 'transaction_id'
    )
    
    def __new__(
        cls, transaction_id, recursion_desired, data_verification_desired, questions, additional_resource_records
    ):
        """
        Creates a new query.
        
        Parameters
        ----------
        transaction_id : `int`
            The transaction's identifier.
        
        recursion_desired : `bool`
            Whether recursion is desired.
        
        data_verification_desired : `bool`
            Whether the server should respond with verified data.
        
        questions : ``None | tuple<Question>``
            Questions to request.
        
        additional_resource_records : ``None | tuple<ResourceRecord>``
            Additional resource records to send.
        """
        self = object.__new__(cls)
        self.additional_resource_records = additional_resource_records
        self.data_verification_desired = data_verification_desired
        self.questions = questions
        self.recursion_desired = recursion_desired
        self.transaction_id = transaction_id
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # transaction_id
        repr_parts.append(' transaction_id = ')
        repr_parts.append(repr(self.transaction_id))
        
        # recursion_desired
        repr_parts.append(', recursion_desired = ')
        repr_parts.append(repr(self.recursion_desired))
        
        # data_verification_desired
        repr_parts.append(', data_verification_desired = ')
        repr_parts.append(repr(self.data_verification_desired))
        
        # questions
        repr_parts.append(', questions = ')
        repr_parts.append(repr(self.questions))
        
        # additional_resource_records
        repr_parts.append(', additional_resource_records = ')
        repr_parts.append(repr(self.additional_resource_records))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # transaction_id
        if self.transaction_id != other.transaction_id:
            return False
        
        # recursion_desired
        if self.recursion_desired != other.recursion_desired:
            return False
        
        # data_verification_desired
        if self.data_verification_desired != other.data_verification_desired:
            return False
        
        # questions
        if self.questions != other.questions:
            return False
        
        # additional_resource_records
        if self.additional_resource_records != other.additional_resource_records:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns hash(self)."""
        hash_value = 0
        
        # transaction_id
        hash_value ^= self.transaction_id
        
        # recursion_desired
        hash_value ^= self.recursion_desired << 16
        
        # data_verification_desired
        hash_value ^= self.data_verification_desired << 17
        
        # questions
        questions = self.questions
        if (questions is not None):
            hash_value ^= 1 << 18
            hash_value ^= hash(questions)
        
        # additional_resource_records
        additional_resource_records = self.additional_resource_records
        if (additional_resource_records is not None):
            hash_value ^= 1 << 19
            hash_value ^= hash(additional_resource_records)
        
        return hash_value
