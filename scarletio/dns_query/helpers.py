__all__ = ()

from itertools import chain

from .constants import (
    IP_TYPE_IP_V4, IP_TYPE_IP_V6, IP_TYPE_NONE, IP_V4_RP, IP_V6_COLON_ONLY, IP_V6_RP, IP_V6_RP_WITH_COLON_AT_START,
    IP_V6_WITH_COLON_AT_END, IP_V6_WITH_COLON_IN_MIDDLE, LABEL_LENGTH_THRESHOLD_UPPER
)


def parse_labels_from_name(name):
    """
    Parses the labels out from the given name.
    
    Parameters
    ----------
    name : `str`
        Name to parse.
    
    Returns
    -------
    labels : `None | tuple<bytes>`
    
    Raises
    ------
    ValueError
        - If the input value is bad.
    """
    # Do split
    split = []
    part_parts = []
    
    # We split each part by `.`
    # Escaping allowed, escape character is `/`:
    #     If a non digit follows the escape character, we add it to the current part as is, even if it is a `.`.
    #     If a digit follows the escape character, we read 2 more digits and get the character representing it.
    index = 0
    name_length = len(name)
    while index < name_length:
        character = name[index]
        if character == '.':
            split.append(''.join(part_parts))
            part_parts.clear()
            index += 1
            continue
        
        if not character == '\\':
            part_parts.append(character)
            index += 1
            continue
        
        index += 1
        # We cannot end on an escape.
        if index == name_length:
            raise ValueError(f'Escape at the end of name is not allowed; name = {name!r}')
        
        character = name[index]
        if not character.isdigit():
            part_parts.append(character)
            index += 1
            continue
        
        total = ord(character) & 15
        
        for _ in range(2):
            index += 1
            if index == name_length:
                # After the first character is a digit, we must consume 2 more.
                raise ValueError(f'Escape code not long enough at the end of the name; name = {name!r}')
            
            character = name[index]
            if not character.isdigit():
                # After the first character is a digit, the next 2 also has to be.
                raise ValueError(
                    f'Escape code too short in the middle of the name; name = {name!r}; index = {index!r}.'
                )
            
            total = total * 10 + (ord(character) & 15)
        
        # Built character cannot be over 255
        if total > 255:
            raise ValueError(
                f'Escaped integer triplet\'s value over 255; name = {name!r}; index = {index!r}; total = {total!r}.'
            )
        
        part_parts.append(chr(total))
        index += 1
        continue
    
    # If the last part is empty, we can ignore it.
    if part_parts:
        split.append(''.join(part_parts))
    part_parts = None
    
    # If we ended up with an empty split, or if the only split is a `@`, we can return nothing.
    if (not split) or ((len(split) == 1)) and (split[0] in ('@', '')):
        return None
    
    # If we have any empty parts after the splitting and exception case handling, we raise an error.
    if '' in split:
        raise ValueError(f'Empty dns label in name; name = {name!r}.')
    
    # Build output
    labels = []
    
    for part in split:
        # Use ascii or idna encoding for each part.
        try:
            label = part.encode('ascii')
        except UnicodeEncodeError:
            label = part.encode('idna')
        
        label_length = len(label)
        # Check label length under limit.
        if label_length > LABEL_LENGTH_THRESHOLD_UPPER:
            raise ValueError(
                f'Label length passing upper label length threshold; '
                f'name = {name!r}; '
                f'part = {part!r}; '
                f'label = {label!r}; '
                f'label_length = {label_length!r}; '
                f'label_length_upper_threshold = {LABEL_LENGTH_THRESHOLD_UPPER!r}.'
            )
        
        labels.append(label)
    
    return tuple(labels)


def parse_reversed_labels_from_address(address):
    """
    Parses reversed labels from the given address.
    
    Parameters
    ----------
    address : `str`
        The address to parse.
    
    Returns
    -------
    labels : `None | tuple<bytes>`
    """
    ip_type, ip_value = parse_ip_string(address)
    if ip_type == IP_TYPE_IP_V4:
        ip_size = 32
        unit_size = 8
        mode = 'd'
        postfix = b'in-addr'
    
    elif ip_type == IP_TYPE_IP_V6:
        ip_size = 128
        unit_size = 4
        mode = 'x'
        postfix = b'ip6'
    
    else:
        raise ValueError(f'Address of unknown type: {address!r}.')
    
    parts = []
    
    mask = (1 << unit_size) - 1
    for shift in range(0, ip_size, unit_size):
        parts.append(format((ip_value >> shift) & mask, mode).encode())
    
    parts.append(postfix)
    parts.append(b'arpa')
    return tuple(parts)


def build_name_from_labels(labels):
    """
    Builds name from the given label.
    
    Parameters
    ----------
    labels : `None | tuple<bytes>`
        Labels to convert.
    
    Returns
    -------
    name : `str`
    """
    if labels is None:
        return '@'
    
    characters = []
    
    for index in range(len(labels)):
        if index:
            characters.append('.')
        
        for character in labels[index].decode('idna'):
            if character in ('.', '\\', ';', '@', '$', '(', ')', '"'):
                characters.append('\\')
                characters.append(character)
                continue
            
            if character.isalnum():
                characters.append(character)
                continue
            
            character_code_point = ord(character)
            if (not character.isprintable()) or (character_code_point < 33):
                characters.append('\\')
                if character_code_point < 100:
                    characters.append('0')
                if character_code_point < 10:
                    characters.append('0')
                characters.append(str(character_code_point))
                continue
            
            characters.append(character)
            continue
    
    return ''.join(characters)


def parse_ip_v4_string(ip_string):
    """
    Parses an ip v4 address.
    
    Parameters
    ----------
    ip_string : `str`
        String to parse.
    
    Returns
    -------
    matched_and_ip_value : `(bool, int)`
    """
    ip_value = 0
    matched = False
    
    match = IP_V4_RP.fullmatch(ip_string)
    if (match is not None):
        for value, shift in zip(match.groups(), range(24, -8, -8)):
            ip_value |= int(value) << shift
        
        matched = True
    
    return matched, ip_value


def parse_ip_v6_string(ip_string):
    """
    Parses an ip v6 address.
    
    Parameters
    ----------
    ip_string : `str`
        String to parse.
    
    Returns
    -------
    matched_and_ip_value_and_percentage_index : `(bool, int, int)`
    """
    ip_value = 0
    matched = False

    while True:
        percentage_index = ip_string.find('%')
        if percentage_index == -1:
            end_position = len(ip_string)
        else:
            end_position = percentage_index
        
        if ip_string == IP_V6_COLON_ONLY:
            matched = True
            break
        
        match = IP_V6_RP.fullmatch(ip_string, 0, end_position)
        if (match is not None):
            for value, shift in zip(match.groups(), range(112, -16, -16)):
                ip_value |= int(value, 16) << shift
            
            matched = True
            break
        
        match = IP_V6_RP_WITH_COLON_AT_START.fullmatch(ip_string, 0, end_position)
        if (match is not None):
            for value, shift in zip(match.groups(), range(112 - 16, -16, -16)):
                if value is None:
                    continue
                
                ip_value |= int(value, 16) << shift
                matched = True
            break
        
        match = IP_V6_WITH_COLON_AT_END.fullmatch(ip_string, 0, end_position)
        if (match is not None):
            for value, shift in zip(match.groups(), range(112, 16 - 16, -16)):
                if value is None:
                    continue
                
                ip_value |= int(value, 16) << shift
                matched = True
            break
        
        match = IP_V6_WITH_COLON_IN_MIDDLE.fullmatch(ip_string, 0, end_position)
        if (match is not None):
            element_count = 0
            for value, shift in zip(match.groups(), chain(range(112, 32 - 16, -16), range(112 - 32, -16, -16))):
                if value is None:
                    continue
                
                element_count += 1
                ip_value |= int(value, 16) << shift
            
            if element_count < 8:
                matched = True
                break
            
            # Reset ip_value
            ip_value = 0
        
        break
    
    return matched, ip_value, percentage_index


def parse_ip_string(ip_string):
    """
    Parses the given ip string to an ip-type & ip value pair.
    
    Parameters
    ----------
    ip_string : `str`
        Ip value to parse.
    
    Returns
    -------
    ip_type_and_ip_value : `(int, int)`
    """
    while True:
        matched, ip_value = parse_ip_v4_string(ip_string)
        if matched:
            ip_type = IP_TYPE_IP_V4
            break
        
        matched, ip_value, percentage_index = parse_ip_v6_string(ip_string)
        if matched:
            ip_type = IP_TYPE_IP_V6
            break
        
        ip_type = IP_TYPE_NONE
        break
    
    return ip_type, ip_value


def produce_ip_v4_string(ip_value):
    """
    Produces address string of a ip v4 value.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    ip_value : `int`
        Ip value to produce representation of.
    
    Yields
    ------
    part : `str`
    """
    yield str((ip_value >> 24) & 255)
    yield '.'
    yield str((ip_value >> 16) & 255)
    yield '.'
    yield str((ip_value >> 8) & 255)
    yield '.'
    yield str(ip_value & 255)


def produce_ip_v6_string(ip_value):
    """
    Produces address string of a ip v4 value.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    ip_value : `int`
        Ip value to produce representation of.
    
    Yields
    ------
    part : `str`
    """
    largest_sequence_start = 0
    largest_sequence_length = 0
    
    current_sequence_start = 0
    current_sequence_length = 0
    
    for shift in range(128 - 16, -6, - 16):
        value = (ip_value >> shift) & 0xffff
        if not value:
            if current_sequence_length:
                current_sequence_length += 16
                continue
            
            current_sequence_start = shift
            current_sequence_length = 16
            continue
        
        if not current_sequence_length:
            continue
        
        if (
            # First 0 sequence.
            (not largest_sequence_length) or
            # Longer 0 sequence than the previous.
            (largest_sequence_length < current_sequence_length) or
            # Same length 0 sequence as the previous and the previous is a starting one.
            ((largest_sequence_length == current_sequence_length) and (largest_sequence_start == 128 - 16))
        ):
            largest_sequence_start = current_sequence_start
            largest_sequence_length = current_sequence_length
        
        current_sequence_length = 0
        continue
    
    if current_sequence_length and (largest_sequence_length < current_sequence_length):
        largest_sequence_start = current_sequence_start
        largest_sequence_length = current_sequence_length
    
    if largest_sequence_length == 0:
        # No 0 sequence.
        for shift in range(128 - 16, -16, -16):
            yield format((ip_value >> shift) & 0xffff, 'x')
            if shift:
                yield ':'
    
    elif largest_sequence_length == 128:
        # Full 0 sequence.
        yield '::'
    
    elif largest_sequence_start == 128 - 16:
        # Starting with 0 sequence.
        yield ':'
        for shift in range(128 - 16 - largest_sequence_length, -16, -16):
            yield ':'
            yield format((ip_value >> shift) & 0xffff, 'x')
    
    elif largest_sequence_start - largest_sequence_length == -16:
        # Ending with 0 sequence.
        for shift in range(128 - 16, largest_sequence_length - 16, -16):
            yield format((ip_value >> shift) & 0xffff, 'x')
            yield ':'
        
        yield ':'
    
    else:
        # Middling with 0 sequence.
        for shift in range(128 - 16, largest_sequence_start, -16):
            yield format((ip_value >> shift) & 0xffff, 'x')
            yield ':'
    
        for shift in range(largest_sequence_start - largest_sequence_length, -16, -16):
            yield ':'
            yield format((ip_value >> shift) & 0xffff, 'x')


def produce_ip_string(ip_type, ip_value):
    """
    Produces the ip's representation.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    ip_type : `int`
        The ip's type.
    
    ip_value : `int`
        Ip value.
    
    Yields
    ------
    part : `str`
    """
    if ip_type == IP_TYPE_IP_V4:
        yield from produce_ip_v4_string(ip_value)
    
    elif ip_type == IP_TYPE_IP_V6:
        yield from produce_ip_v6_string(ip_value)
    
    else:
        yield 'unknown'


def iter_intermediate_intermediate_addresses_ordered(resolve_configuration, intermediate_addresses):
    """
    Iterates over the intermediate_addresses as the sort list allows them.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    intermediate_addresses : `list<(int, int, None | str, int)>`
        Packed middle step intermediate_addresses.
    
    Yields
    ------
    address : `(int, int, None | str, int)`
    """
    sort_list = resolve_configuration.sort_list
    if (sort_list is not None):
        address_count = len(intermediate_addresses)
        for sort_list_element in sort_list:
            index = 0
            while index < address_count:
                intermediate_address = intermediate_addresses[index]
                
                if (
                    (intermediate_address[0] != sort_list_element.ip_type) or
                    (intermediate_address[1] & sort_list_element.ip_mask != sort_list_element.ip_value)
                ):
                    index += 1
                    continue
                
                del intermediate_addresses[index]
                address_count -= 1
                yield intermediate_address
                
                if not address_count:
                    return
                
                continue
    
    yield from intermediate_addresses


def iter_labels_with_searches(resolve_configuration, initial_labels):
    """
    Iterates over the labels applying searches.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    initial_labels : `None | tuple<bytes>`
        Labels to query.
    
    Yields
    ------
    labels : `tuple<bytes>`
    """
    while True:
        if (initial_labels is not None) and (len(initial_labels) > resolve_configuration.option_required_dot_count):
            break
        
        searches = resolve_configuration.searches
        if (searches is not None):
            searches_to_use = searches
        else:
            searches_fallback = resolve_configuration.searches_fallback
            if (searches_fallback is not None):
                searches_to_use = searches_fallback
            else:
                break
        
        for labels_prefix in searches_to_use:
            labels = labels_prefix
            if (initial_labels is not None):
                labels += initial_labels
            yield labels
            continue
        
        break
    
    if (initial_labels is not None):
        yield initial_labels
