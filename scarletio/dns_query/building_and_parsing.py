__all__ = ()

from .constants import (
    DATA_VERIFICATION_DESIRED_SHIFT, DATA_VERIFIED_SHIFT, OPERATION_CODE_QUERY_STANDARD, OPERATION_CODE_SHIFT,
    RECURSION_AVAILABLE_SHIFT, RECURSION_DESIRED_SHIFT, RESPONSE_CODE_MASK, RESPONSE_CODE_SHIFT,
    RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
    RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
    RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND, TRUNCATED_SHIFT
)
from .helpers import build_name_from_labels
from .question import Question
from .resource_record import ResourceRecord
from .response_parsing_error import ResponseParsingError
from .result import Result


def build_query_data(query, resolve_configuration):
    """
    Builds query data.
    
    Parameters
    ----------
    query : ``Query``
        Query to build data for.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    Returns
    -------
    output : `bytes`
    """
    questions = query.questions
    additional_resource_records = query.additional_resource_records
    
    parts = [
        query.transaction_id.to_bytes(2, 'big'),
        (
            # (False << MESSAGE_TYPE_SHIFT) |
            (OPERATION_CODE_QUERY_STANDARD << OPERATION_CODE_SHIFT) |
            (query.recursion_desired << RECURSION_DESIRED_SHIFT) |
            (resolve_configuration.option_set_verified_data_in_requests << DATA_VERIFIED_SHIFT) |
            (query.data_verification_desired << DATA_VERIFICATION_DESIRED_SHIFT)
        ).to_bytes(2, 'big'),
        (0 if (questions is None) else len(questions)).to_bytes(2, 'big'),
        (
            b'\x00\x00' # Number of answers
            b'\x00\x00' # Number of authorized resource records
        ),
        (0 if (additional_resource_records is None) else len(additional_resource_records)).to_bytes(2, 'big'),
    ]
    
    if (questions is not None):
        for question in questions:
            labels = question.labels
            if (labels is not None):
                for label in labels:
                    parts.append(len(label).to_bytes(1, 'big'))
                    parts.append(label)
            
            parts.append(b'\x00')
            parts.append(question.resource_record_type.to_bytes(2, 'big'))
            parts.append(question.class_code.to_bytes(2, 'big'))
    
    if (additional_resource_records is not None):
        for resource_record in additional_resource_records:
            labels = resource_record.labels
            if (labels is not None):
                for label in labels:
                    parts.append(len(label).to_bytes(1, 'big'))
                    parts.append(label)
            
            parts.append(b'\x00')
            parts.append(resource_record.resource_record_type.to_bytes(2, 'big'))
            parts.append(resource_record.class_code.to_bytes(2, 'big'))
            parts.append(resource_record.validity_duration.to_bytes(4, 'big'))
            
            data = resource_record.data
            parts.append((0 if (data is None) else len(data)).to_bytes(2, 'big'))
            if (data is not None):
                parts.append(data)
    
    return b''.join(parts)


def _parse_labels(data, index):
    """
    Parses labels from the given data.
    
    Parameters
    ----------
    data : `bytes`
        Data to read from.
    
    index : `int`
        Index to start at.
    
    Returns
    -------
    labels_and_index_and_response_parsing_error : ``((None | tuple<bytes>, int), None | ResponseParsingError)``
        The parsed labels and the ending index.
    
    Raises
    ------
    ValueError
        - Label length out of expected range.
        - Label containing forward reference.
    """
    labels = None
    data_length = len(data)
    furthest_index = index
    
    while True:
        # Bound check index
        if index >= data_length:
            response_parsing_error = ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND,
                data,
                (),
            )
            break
        
        label_length = data[index]
        index += 1
        furthest_index = max(furthest_index, index)
        if label_length == 0:
            response_parsing_error = None
            break
        
        if label_length < 64:
            end = index + label_length
            # Bound check end
            if end > data_length:
                response_parsing_error = ResponseParsingError(
                    RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
                    data,
                    (index, end),
                )
                break
            
            label_value = data[index : end]
            index = end
            
            if labels is None:
                labels = []
            
            labels.append(label_value)
            continue
        
        # Label length cannot be within 64 and 192.
        if label_length < 192:
            response_parsing_error = ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
                data,
                (label_length, index),
            )
            break
        
        # Bound check index for label jump
        if index >= data_length:
            response_parsing_error = ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND,
                data,
                (),
            )
            break
        
        addition = data[index]
        index += 1
        furthest_index = max(furthest_index, index)
        index = ((label_length & 0x3f) << 8) | addition
        
        # Only backwards jumps are allowed.
        if index > furthest_index:
            response_parsing_error =  ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
                data,
                (furthest_index, index),
            )
            break
    
    if (response_parsing_error is not None):
        return (None, response_parsing_error)
    
    if (labels is not None):
        labels = tuple(labels)
    
    return (labels, furthest_index), None


def _parse_questions(data, index, count):
    """
    Parses labels from the given data.
    
    Parameters
    ----------
    data : `bytes`
        Data to read from.
    
    index : `int`
        Index to start at.
    
    count : `int`
        The amount of questions to parse.
    
    Returns
    -------
    questions_and_index_and_response_parsing_error : `˙((None | tuple<Question>, int), None | ResponseParsingError)``
        The parsed questions and the ending index.
    
    Raises
    ------
    ValueError
        - Label length out of expected range.
        - Label containing forward reference.
    """
    questions = None
    data_length = len(data)
    
    for _ in range(count):
        labels_and_index, response_parsing_error = _parse_labels(data, index)
        if (response_parsing_error is not None):
            break
        
        labels, index = labels_and_index
        end = index + 4
        if end > data_length:
            response_parsing_error = ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
                data,
                (end, ),
            )
            break
        
        resource_record_type = int.from_bytes(data[index : index + 2], 'big')
        class_code = int.from_bytes(data[index + 2: end], 'big')
        index = end
        
        if questions is None:
            questions = []
        
        questions.append(Question(labels, resource_record_type, class_code))
    
    else:
        response_parsing_error = None
    
    if (response_parsing_error is not None):
        return (None, response_parsing_error)
    
    if (questions is not None):
        questions = tuple(questions)
    
    return (questions, index), None


def _parse_resource_records(data, index, count):
    """
    Parses labels from the given data.
    
    Parameters
    ----------
    data : `bytes`
        Data to read from.
    
    index : `int`
        Index to start at.
    
    count : `int`
        The amount of resource records to parse.
    
    Returns
    -------
    resource_records_and_index_and_response_parsing_error : `˙((None | tuple<ResourceRecord>, int), None | ResponseParsingError)``
        The parsed resource records and the ending index.
    
    Raises
    ------
    ValueError
        - Label length out of expected range.
        - Label containing forward reference.
    """
    resource_records = None
    data_length = len(data)
    
    for _ in range(count):
        labels_and_furthest_index, response_parsing_error = _parse_labels(data, index)
        if (response_parsing_error is not None):
            break
        
        labels, index = labels_and_furthest_index
        end = index + 10
        if end > data_length:
            response_parsing_error = ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND,
                data,
                (end, ),
            )
            break
        
        resource_record_type = int.from_bytes(data[index : index + 2], 'big')
        class_code = int.from_bytes(data[index + 2: index + 4], 'big')
        validity_duration = int.from_bytes(data[index + 4: index + 8], 'big')
        record_data_length = int.from_bytes(data[index + 8: end], 'big')
        index = end
        
        if not record_data_length:
            record_data = None
        
        else:
            end = index + record_data_length
            if end > data_length:
                response_parsing_error = ResponseParsingError(
                    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
                    data,
                    (index, end),
                )
                break
            
            record_data = data[index : end]
            index = end
        
        if resource_records is None:
            resource_records = []
        
        resource_records.append(
            ResourceRecord(labels, resource_record_type, class_code, validity_duration, record_data)
        )
        continue
    
    else:
        response_parsing_error = None
    
    if (response_parsing_error is not None):
        return (None, response_parsing_error)
    
    if (resource_records is not None):
        resource_records = tuple(resource_records)
    
    return (resource_records, index), None


def parse_result_data(data):
    """
    Parses response data from the given data.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    result_and_response_parsing_error : ``(None | Result, None | ResponseParsingError)``
    
    Raises
    ------
    ValueError
        - Label length out of expected range.
        - Label containing forward reference.
    """
    while True:
        data_length = len(data)
        if data_length < 12:
            response_parsing_error =  ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND,
                data,
                (),
            )
            break
        
        transaction_id = int.from_bytes(data[0:2], 'big')
        flags = int.from_bytes(data[2:4], 'big')
        question_count = int.from_bytes(data[4:6], 'big')
        answer_count = int.from_bytes(data[6:8], 'big')
        authorized_resource_record_count = int.from_bytes(data[8:10], 'big')
        addition_resource_record_count = int.from_bytes(data[10:12], 'big')
        
        questions_and_index, response_parsing_error = _parse_questions(data, 12, question_count)
        if (response_parsing_error is not None):
            break
        questions, index = questions_and_index
        
        answers_and_index, response_parsing_error = _parse_resource_records(data, index, answer_count)
        if (response_parsing_error is not None):
            break
        answers, index = answers_and_index
        
        authority_resource_records_and_index, response_parsing_error = _parse_resource_records(
            data, index, authorized_resource_record_count
        )
        if (response_parsing_error is not None):
            break
        authority_resource_records, index = authority_resource_records_and_index
        
        additional_resource_records_and_index, response_parsing_error = _parse_resource_records(
            data, index, addition_resource_record_count
        )
        if (response_parsing_error is not None):
            break
        additional_resource_records, index = additional_resource_records_and_index
        
        break
    
    if (response_parsing_error is not None):
        return (
            None,
            response_parsing_error,
        )
    
    
    return (
        Result(
            transaction_id,
            (True if ((flags >> DATA_VERIFIED_SHIFT) & 1) else False),
            (True if ((flags >> TRUNCATED_SHIFT) & 1) else False),
            (True if ((flags >> RECURSION_AVAILABLE_SHIFT) & 1) else False),
            ((flags >> RESPONSE_CODE_SHIFT) & RESPONSE_CODE_MASK),
            questions,
            answers,
            authority_resource_records,
            additional_resource_records,
        ),
        None,
    )


def parse_ip_v4_data(data):
    """
    Parses an ip v4 address from the given data.
    
    Parameters
    ----------
    data : `None | bytes`
        Data to parse from.
    
    Returns
    --------
    ip_v4 : `None | int`
    """
    if (data is None) or (len(data) != 4):
        return None
    
    return int.from_bytes(data, 'big')


def parse_ip_v6_data(data):
    """
    Parses an ip v6 address from the given data.
    
    Parameters
    ----------
    data : `None | bytes`
        Data to parse from.
    
    Returns
    --------
    ip_v6 : `None | int`
    """
    if (data is None) or (len(data) != 16):
        return None
    
    return int.from_bytes(data, 'big')


def parse_domain_name_pointer_data(data):
    """
    Parses the given domain name pointer.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    --------
    domain_name_pointer : `None | str`
    """
    if (data is None) or (not len(data)):
        return None
    
    labels_and_furthest_index, response_parsing_error = _parse_labels(data, 0)
    
    labels, furthest_index = labels_and_furthest_index
    if labels is None:
        return None
    
    return build_name_from_labels(labels)
