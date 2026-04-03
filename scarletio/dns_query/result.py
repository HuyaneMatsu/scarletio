__all__ = ('Result',)

from ..utils import RichAttributeErrorBaseType


class Result(RichAttributeErrorBaseType):
    """
    Represents a responded result.
    
    Attributes
    ----------
    additional_resource_records : ``None | tuple<ResourceRecord>``
        Returned additional resource records.
    
    answers : ``None | tuple<ResourceRecord>``
        Returned answers.
    
    authority_resource_records : ``None | tuple<ResourceRecord>``
        Returned authority resource records.
    
    data_verified : `bool`
        Whether the server claims the data to be verified.
    
    questions : ``None | tuple<Question>``
        Questions to request.
    
    recursion_available : `bool`
        Whether the responding server supports recursion.
    
    response_code : `int`
        Response code.
    
    transaction_id : `int`
        The transaction's identifier.
    
    truncated : `bool`
        Whether the result was truncated.
    """
    __slots__ = (
        'additional_resource_records', 'answers', 'authority_resource_records', 'data_verified', 'questions',
        'recursion_available', 'response_code', 'transaction_id', 'truncated'
    )
    
    def __new__(
        cls,
        transaction_id,
        data_verified,
        truncated,
        recursion_available,
        response_code,
        questions,
        answers,
        authority_resource_records,
        additional_resource_records,
    ):
        """
        Creates a new result.
        
        Parameters
        ----------
        transaction_id : `int`
            The transaction's identifier.
        
        data_verified : `bool`
            Whether the server claims the data to be verified.
        
        truncated : `bool`
            Whether the result was truncated.
        
        recursion_available : `bool`
            Whether the responding server supports recursion.
        
        response_code : `int`
            Response code.
        
        questions : ``None | tuple<Question>``
            Questions to request.
        
        answers : ``None | tuple<ResourceRecord>``
            Returned answers.
        
        authority_resource_records : ``None | tuple<ResourceRecord>``
            Returned authority resource records.
        
        additional_resource_records : ``None | tuple<ResourceRecord>``
            Returned additional resource records.
        """
        self = object.__new__(cls)
        self.additional_resource_records = additional_resource_records
        self.answers = answers
        self.authority_resource_records = authority_resource_records
        self.data_verified = data_verified
        self.questions = questions
        self.recursion_available = recursion_available
        self.response_code = response_code
        self.transaction_id = transaction_id
        self.truncated = truncated
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # transaction_id
        repr_parts.append(' transaction_id = ')
        repr_parts.append(repr(self.transaction_id))
        
        # data_verified
        repr_parts.append(', data_verified = ')
        repr_parts.append(repr(self.data_verified))
        
        # truncated
        repr_parts.append(', truncated = ')
        repr_parts.append(repr(self.truncated))
        
        # recursion_available
        repr_parts.append(', recursion_available = ')
        repr_parts.append(repr(self.recursion_available))
        
        # response_code
        repr_parts.append(', response_code = ')
        repr_parts.append(repr(self.response_code))
        
        # questions
        repr_parts.append(', questions = ')
        repr_parts.append(repr(self.questions))
        
        # answers
        repr_parts.append(', answers = ')
        repr_parts.append(repr(self.answers))
        
        # authority_resource_records
        repr_parts.append(', authority_resource_records = ')
        repr_parts.append(repr(self.authority_resource_records))
        
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
        
        # data_verified
        if self.data_verified != other.data_verified:
            return False
        
        # truncated
        if self.truncated != other.truncated:
            return False
        
        # recursion_available
        if self.recursion_available != other.recursion_available:
            return False
        
        # response_code
        if self.response_code != other.response_code:
            return False
        
        # questions
        if self.questions != other.questions:
            return False
        
        # answers
        if self.answers != other.answers:
            return False
        
        # authority_resource_records
        if self.authority_resource_records != other.authority_resource_records:
            return False
        
        # additional_resource_records
        if self.additional_resource_records != other.additional_resource_records:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns hash(self)"""
        hash_value = 0
        
        # transaction_id
        hash_value ^= self.transaction_id
        
        # data_verified
        hash_value ^= self.data_verified << 16
        
        # truncated
        hash_value ^= self.truncated << 17
        
        # recursion_available
        hash_value ^= self.recursion_available << 18
        
        # response_code
        hash_value ^= self.response_code << 19
        
        # questions
        questions = self.questions
        if (questions is not None):
            hash_value ^= 1 << 23
            hash_value ^= hash(questions)
        
        # answers
        answers = self.answers
        if (answers is not None):
            hash_value ^= 1 << 24
            hash_value ^= hash(answers)
        
        # authority_resource_records
        authority_resource_records = self.authority_resource_records
        if (authority_resource_records is not None):
            hash_value ^= 1 << 25
            hash_value ^= hash(authority_resource_records)
        
        # additional_resource_records
        additional_resource_records = self.additional_resource_records
        if (additional_resource_records is not None):
            hash_value ^= 1 << 26
            hash_value ^= hash(additional_resource_records)
        
        return True
