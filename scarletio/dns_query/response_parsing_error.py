__all__ = ('ResponseParsingError', 'get_response_parsing_error_message_producer')


from socket import EAI_FAIL as ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE, gaierror as GetAddressInfoError


ERROR_CODE = ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE
ERROR_MESSAGE = 'Parsing dns response failed.'


def _produce_response_parsing_error_message__label_length_invalid_range(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Label length in invalid range (64, 192); label_length = '
    yield repr(metadata[0])
    yield '; index = '
    yield repr(metadata[1])
    yield '.'


def _produce_response_parsing_error_message__label_jump_backwards(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Label reading jumped forward; furthest_index = '
    yield repr(metadata[0])
    yield '; index = '
    yield repr(metadata[1])
    yield '.'


def _produce_response_parsing_error_message__label_length_read_out_of_bound(response_parsing_error):
    yield 'Could not read label length due to it being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '.'


def _produce_response_parsing_error_message__label_read_end_out_of_bound(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Could not read label due to its end being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '; start = '
    yield repr(metadata[0])
    yield '; end = '
    yield repr(metadata[1])
    yield '.'


def _produce_response_parsing_error_message__label_jump_read_out_of_bound(response_parsing_error):
    yield 'Could not read label jump due to it being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '.'


def _produce_response_parsing_error_message__header_out_of_bound(response_parsing_error):
    yield 'Could not read header (length 12) due to its end being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '.'


def _produce_response_parsing_error_message__question_header_out_of_bound(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Could not read question header (length 4) due to its end being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '; end = '
    yield repr(metadata[0])
    yield '.'


def _produce_response_parsing_error_message__resource_record_header_out_of_bound(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Could not read resource record header (length 10) due to its end being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '; end = '
    yield repr(metadata[0])
    yield '.'


def _produce_response_parsing_error_message__resource_record_data_out_of_bound(response_parsing_error):
    metadata = response_parsing_error.parsing_error_metadata
    yield 'Could not read resource record data due to its end being out of bound; data_length = '
    yield repr(len(response_parsing_error.parsing_error_response_data))
    yield '; start = '
    yield repr(metadata[0])
    yield '; end = '
    yield repr(metadata[1])
    yield '.'


PARSING_ERROR_MESSAGE_BUILDER = (
    None,
    _produce_response_parsing_error_message__label_length_invalid_range,
    _produce_response_parsing_error_message__label_jump_backwards,
    _produce_response_parsing_error_message__label_length_read_out_of_bound,
    _produce_response_parsing_error_message__label_read_end_out_of_bound,
    _produce_response_parsing_error_message__label_jump_read_out_of_bound,
    _produce_response_parsing_error_message__header_out_of_bound,
    _produce_response_parsing_error_message__question_header_out_of_bound,
    _produce_response_parsing_error_message__resource_record_header_out_of_bound,
    _produce_response_parsing_error_message__resource_record_data_out_of_bound,
)


def get_response_parsing_error_message_producer(parsing_error_code):
    """
    Gets error message producer.
    
    Parameters
    ----------
    parsing_error_code : `int`
        Parsing error code.
    
    Returns
    -------
    producer : `None | GeneratorType`
    """
    if (parsing_error_code >= 0) and (parsing_error_code < len(PARSING_ERROR_MESSAGE_BUILDER)):
        return PARSING_ERROR_MESSAGE_BUILDER[parsing_error_code]


class ResponseParsingError(GetAddressInfoError):
    """
    Response parsing error.
    
    Attributes
    ----------
    args : `tuple<int>`
        Parameters the exception was created with.
    
    characters_written : `int`
        Then umber of bytes written to a socket before it was blocked.
    
    filename : `None | str`
        File name in context the exception occurred with..
    
    filename2 : `None | str`
        Another file name.
    
    errno : `None | int`
        Error code.
    
    parsing_error_code : `int`
        Parsing error code.
    
    parsing_error_metadata : `tuple<int>`
        Additional error metadata.
    
    parsing_error_response_data : `bytes`
        Received response data.
    
    strerror : `Non | str`
        Error message.
    """
    __slots__ = ('parsing_error_code', 'parsing_error_metadata', 'parsing_error_response_data')
    __init__ = object.__init__
    
    
    # Fix up `characters_written`; you are welcome.
    @property
    def characters_written(self):
        try:
            value = OSError.characters_written.__get__(self, type(self))
        except AttributeError:
            value = -1
        
        return value
    
    
    @characters_written.setter
    def characters_written(self, value):
        OSError.characters_written.__set__(self, value)
    
    
    def __new__(cls, parsing_error_code, parsing_error_response_data, parsing_error_metadata):
        """
        Creates a new response parsing error.
        
        Parameters
        ----------
        parsing_error_code : `int`
            Parsing error code.
        
        parsing_error_response_data : ``bytes`
            Received response data.
        
        parsing_error_metadata : `tuple<<object>`
            Additional metadata.
        """
        self = GetAddressInfoError.__new__(cls, ERROR_CODE, ERROR_MESSAGE)
        self.args = (ERROR_CODE, ERROR_MESSAGE, parsing_error_code, parsing_error_response_data, parsing_error_metadata)
        self.parsing_error_code = parsing_error_code
        self.parsing_error_response_data = parsing_error_response_data
        self.parsing_error_metadata = parsing_error_metadata
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        producer = get_response_parsing_error_message_producer(self.parsing_error_code)
        if (producer is not None):
            repr_parts.append(' message = ')
            repr_parts.extend(producer(self))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        if self.parsing_error_code != other.parsing_error_code:
            return False
        
        if self.parsing_error_response_data != other.parsing_error_response_data:
            return False
        
        if self.parsing_error_metadata != other.parsing_error_metadata:
            return False
        
        return True
