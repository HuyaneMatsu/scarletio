__all__ = ('NameServerConfiguration', 'ResolveConfiguration', 'SortListElement')

from os import listdir as list_directory
from os.path import isdir as is_directory, isfile as is_file, join as join_paths

from ..utils import RichAttributeErrorBaseType

from .constants import (
    IP_TYPE_IP_V4, IP_TYPE_NONE, NAME_SERVERS_FALLBACK_DEFAULT,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_MAYBE,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO, OPTION_ATTEMPTS_DEFAULT,
    OPTION_ATTEMPTS_THRESHOLD_LOWER, OPTION_ATTEMPTS_THRESHOLD_UPPER, OPTION_REQUIRED_DOT_COUNT_DEFAULT,
    OPTION_REQUIRED_DOT_COUNT_THRESHOLD_LOWER, OPTION_REQUIRED_DOT_COUNT_THRESHOLD_UPPER, OPTION_TIMEOUT_DEFAULT,
    OPTION_TIMEOUT_THRESHOLD_LOWER, OPTION_TIMEOUT_THRESHOLD_UPPER, QUERY_TRANSPORT_TYPE_AUTO,
    RESOLVE_CONFIGURATION_PATH, RESOLVE_MD_CONFIGURATION_PATHS, RESOLVE_MD_IP_TYPE, RESOLVE_MD_IP_VALUE,
    SEARCHES_FALLBACK_DEFAULT
)
from .helpers import parse_ip_string, parse_ip_v4_string, parse_ip_v6_string, parse_labels_from_name


# This type implements some parts of:
# https://www.man7.org/linux/man-pages/man5/resolved.conf.5.html
# Because turns out, these settings are by server.
#
# Implemented this because turns out systemd does not support `supports_multiple_questions_in_queries`.
# Good job.

class NameServerConfiguration(RichAttributeErrorBaseType):
    """
    Represents a name server specific configuration.
    
    Attributes
    ----------
    ip_type : `int`
        The name server's ip's type.
    
    ip_value : `int`
        The name server's ip's value.
    
    supports_multiple_questions_in_queries : `bool`
        Whether the name server supports multiple questions in a single query.
    
    secure_connection_support_level : `int`
        Whether the server supports secure connections.
    """
    __slots__ = ('ip_type', 'ip_value', 'supports_multiple_questions_in_queries', 'secure_connection_support_level')
    
    def __new__(cls, ip_type, ip_value, supports_multiple_questions_in_queries, secure_connection_support_level):
        """
        Creates a new name server configuration.
        
        Parameters
        ----------
        ip_type : `int`
            The name server's ip's type.
        
        ip_value : `int`
            The name server's ip's value.
        
        supports_multiple_questions_in_queries : `bool`
            Whether the name server supports multiple questions in a single query.
        
        secure_connection_support_level : `int`
            Whether the server supports secure connections.
        """
        self = object.__new__(cls)
        self.ip_type = ip_type
        self.ip_value = ip_value
        self.supports_multiple_questions_in_queries = supports_multiple_questions_in_queries
        self.secure_connection_support_level = secure_connection_support_level
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # ip_type
        repr_parts.append(' ip_type = ')
        repr_parts.append(repr(self.ip_type))
        
        # ip_value
        repr_parts.append(', ip_value = ')
        repr_parts.append(repr(self.ip_value))
        
        # supports_multiple_questions_in_queries
        supports_multiple_questions_in_queries = self.supports_multiple_questions_in_queries
        if supports_multiple_questions_in_queries:
            repr_parts.append(', supports_multiple_questions_in_queries = ')
            repr_parts.append(repr(supports_multiple_questions_in_queries))
        
        # secure_connection_support_level
        secure_connection_support_level = self.secure_connection_support_level
        if secure_connection_support_level:
            repr_parts.append(', secure_connection_support_level = ')
            repr_parts.append(repr(secure_connection_support_level))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # ip_type
        if self.ip_type != other.ip_type:
            return False
        
        # ip_value
        if self.ip_value != other.ip_value:
            return False
        
        # supports_multiple_questions_in_queries
        if self.supports_multiple_questions_in_queries != other.supports_multiple_questions_in_queries:
            return False
        
        # secure_connection_support_level
        if self.secure_connection_support_level != other.secure_connection_support_level:
            return False
        
        return True


class SortListElement(RichAttributeErrorBaseType):
    """
    An element in sort list, helping ordering ip addresses.
    
    Attributes
    ----------
    ip_mask : `int`
        Ip mask to apply before comparing with value.
    
    ip_type : `int`
        The matched ip's type.
    
    ip_value : `int`
        The ip's value.
    """
    __slots__ = ('ip_mask', 'ip_type', 'ip_value')
    
    def __new__(cls, ip_type, ip_value, ip_mask):
        """
        Creates a new sort list configuration.
        
        Parameters
        ----------
        ip_type : `int`
            The matched ip's type.
            
        ip_value : `int`
            The ip's value.
        
        ip_mask : `int`
            Ip mask to apply before comparing with value.
        """
        self = object.__new__(cls)
        self.ip_mask = ip_mask
        self.ip_type = ip_type
        self.ip_value = ip_value
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        # ip_type
        repr_parts.append(' ip_type = ')
        repr_parts.append(repr(self.ip_type))
        
        # ip_value
        repr_parts.append(' ip_value = ')
        repr_parts.append(repr(self.ip_value))
        
        # ip_mask
        repr_parts.append(' ip_mask = ')
        repr_parts.append(repr(self.ip_mask))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns self == other."""
        if type(self) is not type(other):
            return NotImplemented
        
        # ip_type
        if self.ip_type != other.ip_type:
            return False
        
        # ip_value
        if self.ip_value != other.ip_value:
            return False
        
        # ip_mask
        if self.ip_mask != other.ip_mask:
            return False
        
        return True


def parse_sort_list_element(string):
    """
    Parses a sort list element, On failure returns `None`.
    
    Parameters
    ----------
    string : `str`
        String to parse. Should not be empty.
    
    Returns
    -------
    sort_list_element : ``None | SortListElement``
    """
    slash_index = string.find('/')
    string_length = len(string)
    
    while True:
        # Case: no slash.
        if slash_index == -1:
            ip_string = string
            mask_string = None
            break
        
        # Case: only slash or starts with slash.
        if not slash_index:
            return None
        
        # Case: with slash, after slash can be empty.
        ip_string = string[: slash_index]
        slash_index += 1
        if slash_index == string_length:
            mask_string = None
        else:
            mask_string = string[slash_index :]
        break
    
    ip_type, ip_value = parse_ip_string(ip_string)
    if ip_type == IP_TYPE_NONE:
        return None
    
    while True:
        # Case: no mask.
        if mask_string is None:
            if ip_type == IP_TYPE_IP_V4:
                ip_mask = 0xffffffff
            else:
                ip_mask = 0xffffffffffffffffffffffffffffffff
            break
        
        # Case: mask given in checked upper bits.
        if mask_string.isdecimal():
            checked_upper_bit_count = int(mask_string)
            if ip_type == IP_TYPE_IP_V4:
                ip_mask = 0xffffffff
                if checked_upper_bit_count < 32:
                    ip_mask ^= (1 << (32 - checked_upper_bit_count)) - 1
            else:
                ip_mask = 0xffffffffffffffffffffffffffffffff
                if checked_upper_bit_count < 128:
                    ip_mask ^= (1 << (128 - checked_upper_bit_count)) - 1
            break
        
        # Case: mask given as ip.
        if ip_type == IP_TYPE_IP_V4:
            matched, ip_mask = parse_ip_v4_string(mask_string)
        else:
            matched, ip_mask, percentage_index = parse_ip_v6_string(mask_string)
        
        if not matched:
            return None
        break
    
    return SortListElement(ip_type, ip_value, ip_mask)


# Reference:
# https://www.man7.org/linux/man-pages/man5/resolv.conf.5.html

class ResolveConfiguration(RichAttributeErrorBaseType):
    """
    Represents a resolve configuration.
    
    Attributes
    ----------
    name_server_configurations : ``None | tuple<NameServerConfiguration>``
        Internet address of the name servers to contact. They can be either ip v4 or v6 addresses.
    
    name_server_configurations_fallback : ``None | tuple<NameServerConfiguration>``
        Fallback name servers in case no name servers are defined.
    
    option_attempts : `int`
        The amount of attempts to try to send out queries for.
    
    option_debug : `bool`
        Unused.
    
    option_disable_bind_checking : `bool`
        Disabled bind checking. Unused.
    
    option_enable_dns_extension : `bool`
        Enabled support for dns extensions. Unused.
    
    option_force_tcp : `bool`
        Whether to always use tcp over udp.
    
    option_limit_to_single_request : `bool`
        Whether to limit dns queries that can be done in parallel to one at a time.
        
        Some domain name system servers cannot handle this and will timeout the connection.
        The documentation says it should work since glibc 2.10. I have 2.31 and it is still not working.
    
    option_no_ip_v6_lookups : `bool`
        Suppresses ip v6 lookups.
    
    option_no_reload : `bool`
        Whether to not watch for config updated. Unused.
    
    option_no_unqualified_name_resolving : `bool`
        Causes unqualified names by ``option_required_dot_count.`` to not being tried to be resolved with
        ``.searches``.
    
    option_prefer_ip_v6 : `bool`
        Makes do ip v6 queries before v4.
    
    option_required_dot_count : `int`
        The required amount of dots for an address to be valid. If it has less than the required amount,
        then it will be tried to be resolved by post-fixing them with ``.searches``.
    
    option_rotate : `bool`
        Whether to rotate the domain name system addresses.
    
    option_set_verified_data_in_requests : `bool`
        Sets the verified data bit in the requests.
    
    option_single_request_re_open : `bool`
        Whether to use a single connection only a single time.
    
    option_timeout : `float`
        Timeout duration in seconds.
    
    preference_query_transport_type : `int`
        What should be the preferred way to execute the queries.
    
    preference_raise_upon_response_parsing_error : `bool`
        Whether an exception should be raised upon failed response parsing.
    
    searches : `None | tuple<tuple<bytes>>`
        A list of names that will postfix the search query if it contains less than the required amount of dots.
    
    searches_fallback : `None | tuple<tuple<bytes>>`
        Fallback searches if no searches are defined.
    
    sort_list : ``None | tuple<SortListElement>``
        Ip preference order applied to outputs.
    """
    __slots__ = (
        'name_server_configurations', 'name_server_configurations_fallback', 'option_attempts', 'option_debug',
        'option_disable_bind_checking', 'option_enable_dns_extension', 'option_force_tcp',
        'option_limit_to_single_request', 'option_no_ip_v6_lookups', 'option_no_reload',
        'option_no_unqualified_name_resolving', 'option_prefer_ip_v6', 'option_required_dot_count', 'option_rotate',
        'option_set_verified_data_in_requests', 'option_single_request_re_open', 'option_timeout',
        'preference_query_transport_type', 'preference_raise_upon_response_parsing_error', 'searches',
        'searches_fallback', 'sort_list'
    )
    
    def __new__(cls):
        """Returns a new instance."""
        self = object.__new__(cls)
        self.name_server_configurations = None
        self.name_server_configurations_fallback = (*(
            NameServerConfiguration(*item) for item in NAME_SERVERS_FALLBACK_DEFAULT
        ),)
        self.option_attempts = OPTION_ATTEMPTS_DEFAULT
        self.option_debug = False
        self.option_disable_bind_checking = False
        self.option_enable_dns_extension = False
        self.option_force_tcp = False
        self.option_limit_to_single_request = False
        self.option_no_ip_v6_lookups = False
        self.option_no_reload = False
        self.option_no_unqualified_name_resolving = False
        self.option_prefer_ip_v6 = False
        self.option_required_dot_count = OPTION_REQUIRED_DOT_COUNT_DEFAULT
        self.option_rotate = False
        self.option_set_verified_data_in_requests = False
        self.option_single_request_re_open = False
        self.option_timeout = OPTION_TIMEOUT_DEFAULT
        self.preference_query_transport_type = QUERY_TRANSPORT_TYPE_AUTO
        self.preference_raise_upon_response_parsing_error = False
        self.searches = None
        self.searches_fallback = SEARCHES_FALLBACK_DEFAULT
        self.sort_list = None
        return self
    
    
    def __repr__(self):
        """Returns repr(self)."""
        repr_parts = ['<', type(self).__name__]
        
        while True:
            # name_server_configurations
            name_server_configurations = self.name_server_configurations
            if (name_server_configurations is not None):
                repr_parts.append(' name_server_configurations = ')
                repr_parts.append(repr(name_server_configurations))
                field_added = True
                break
            
            # name_server_configurations_fallback
            name_server_configurations_fallback = self.name_server_configurations_fallback
            if (name_server_configurations_fallback is not None):
                repr_parts.append(' name_server_configurations_fallback = ')
                repr_parts.append(repr(name_server_configurations_fallback))
                field_added = True
                break
            
            field_added = False
            break
        
        # option_attempts
        if field_added:
            repr_parts.append(',')
        repr_parts.append(' option_attempts = ')
        repr_parts.append(repr(self.option_attempts))
        
        # option_debug
        option_debug = self.option_debug
        if option_debug:
            repr_parts.append(', option_debug = ')
            repr_parts.append(repr(option_debug))
        
        # option_disable_bind_checking
        option_disable_bind_checking = self.option_disable_bind_checking
        if option_disable_bind_checking:
            repr_parts.append(', option_disable_bind_checking = ')
            repr_parts.append(repr(option_disable_bind_checking))
        
        # option_enable_dns_extension
        option_enable_dns_extension = self.option_enable_dns_extension
        if option_enable_dns_extension:
            repr_parts.append(', option_enable_dns_extension = ')
            repr_parts.append(repr(option_enable_dns_extension))
        
        # option_force_tcp
        option_force_tcp = self.option_force_tcp
        if option_force_tcp:
            repr_parts.append(', option_force_tcp = ')
            repr_parts.append(repr(option_force_tcp))
        
        # option_limit_to_single_request
        option_limit_to_single_request = self.option_limit_to_single_request
        if option_limit_to_single_request:
            repr_parts.append(', option_limit_to_single_request = ')
            repr_parts.append(repr(option_limit_to_single_request))
        
        # option_no_ip_v6_lookups
        option_no_ip_v6_lookups = self.option_no_ip_v6_lookups
        if option_no_ip_v6_lookups:
            repr_parts.append(', option_no_ip_v6_lookups = ')
            repr_parts.append(repr(option_no_ip_v6_lookups))
        
        # option_no_reload
        option_no_reload = self.option_no_reload
        if option_no_reload:
            repr_parts.append(', option_no_reload = ')
            repr_parts.append(repr(option_no_reload))
        
        # option_no_unqualified_name_resolving
        option_no_unqualified_name_resolving = self.option_no_unqualified_name_resolving
        if option_no_unqualified_name_resolving:
            repr_parts.append(', option_no_unqualified_name_resolving = ')
            repr_parts.append(repr(option_no_unqualified_name_resolving))
        
        # option_prefer_ip_v6
        option_prefer_ip_v6 = self.option_prefer_ip_v6
        if option_prefer_ip_v6:
            repr_parts.append(', option_prefer_ip_v6 = ')
            repr_parts.append(repr(option_prefer_ip_v6))
        
        # option_required_dot_count
        repr_parts.append(', option_required_dot_count = ')
        repr_parts.append(repr(self.option_required_dot_count))
        
        # option_rotate
        option_rotate = self.option_rotate
        if option_rotate:
            repr_parts.append(', option_rotate = ')
            repr_parts.append(repr(option_rotate))
        
        # option_set_verified_data_in_requests
        option_set_verified_data_in_requests = self.option_set_verified_data_in_requests
        if option_set_verified_data_in_requests:
            repr_parts.append(', option_set_verified_data_in_requests = ')
            repr_parts.append(repr(option_set_verified_data_in_requests))
        
        # option_single_request_re_open
        option_single_request_re_open = self.option_single_request_re_open
        if option_single_request_re_open:
            repr_parts.append(', option_single_request_re_open = ')
            repr_parts.append(repr(option_single_request_re_open))
        
        # option_timeout
        repr_parts.append(', option_timeout = ')
        repr_parts.append(repr(self.option_timeout))
        
        while True:
            # searches
            searches = self.searches
            if (searches is not None):
                repr_parts.append(', searches = ')
                repr_parts.append(repr(searches))
                break
            
            # searches_fallback
            searches_fallback = self.searches_fallback
            if (searches_fallback is not None):
                repr_parts.append(', searches_fallback = ')
                repr_parts.append(repr(searches_fallback))
                break
            
            break
        
        # sort_list
        sort_list = self.sort_list
        if (sort_list is not None):
            repr_parts.append(', sort_list = ')
            repr_parts.append(repr(sort_list))
        
        # preference_query_transport_type
        preference_query_transport_type = self.preference_query_transport_type
        if preference_query_transport_type:
            repr_parts.append(', preference_query_transport_type = ')
            repr_parts.append(repr(preference_query_transport_type))
        
        # preference_raise_upon_response_parsing_error
        preference_raise_upon_response_parsing_error = self.preference_raise_upon_response_parsing_error
        if preference_raise_upon_response_parsing_error:
            repr_parts.append(', preference_raise_upon_response_parsing_error = ')
            repr_parts.append(repr(preference_raise_upon_response_parsing_error))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


def update_resolve_configuration_from_file_content(resolve_configuration, content):
    """
    Updates the resolve configuration from the given file.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    content : `str`
        The file's content.
    """
    name_servers_mentioned = False
    name_servers = None
    searches_mentioned = False
    searches = None
    sort_list_mentioned = False
    sort_list = None
    
    for line in content.splitlines():
        if (not line) or line[0] in ('#', ';'):
            continue
        
        split = line.split()
        split_length = len(split)
        if split_length == 0:
            continue
        
        key = split[0]
        if split_length == 1:
            while True:
                if key == 'nameserver':
                    name_servers_mentioned = True
                    break
                
                if key == 'search':
                    searches_mentioned = True
                    break
                
                if key == 'sortlist':
                    sort_list_mentioned = True
                    break
                
                break
            
            continue
        
        if key == 'nameserver':
            ip_type, ip_value = parse_ip_string(split[1])
            if ip_type == IP_TYPE_NONE:
                continue
            
            name_servers_mentioned = True
            if (name_servers is None):
                name_servers = []
            
            name_servers.append((ip_type, ip_value),)
            continue
        
        if key == 'search':
            searches_mentioned = True
            for index in range(1, len(split)):
                search = parse_labels_from_name(split[index])
                if (search is None):
                    continue
                
                if searches is None:
                    searches = []
                
                searches.append(search)
                continue
            
            continue
        
        if key == 'sortlist':
            sort_list_mentioned = True
            for index in range(1, len(split)):
                sort_list_element = split[index]
                if sort_list_element is None:
                    continue
                
                if (sort_list is None):
                    sort_list = []
                
                sort_list.append(sort_list_element)
                continue
            continue
        
        if key != 'options':
            continue
        
        option_name = split[1]
        if option_name == 'debug':
            resolve_configuration.option_debug = True
            continue
        
        if option_name == 'rotate':
            resolve_configuration.option_rotate = True
            continue
        
        if option_name == 'no-aaaa':
            resolve_configuration.option_no_ip_v6_lookups = True
            continue
        
        if option_name == 'no-check-names':
            resolve_configuration.option_disable_bind_checking = True
            continue
        
        if option_name == 'inet6':
            resolve_configuration.option_prefer_ip_v6 = True
            continue
        
        if option_name == 'edns0':
            resolve_configuration.option_enable_dns_extension = True
            continue
        
        if option_name == 'single-request':
            resolve_configuration.option_limit_to_single_request = True
            continue
        
        if option_name == 'single-request-reopen':
            resolve_configuration.option_single_request_re_open = True
            continue
        
        if option_name == 'no-tld-query':
            resolve_configuration.option_no_unqualified_name_resolving = True
            continue
        
        if option_name == 'use-vc':
            resolve_configuration.option_force_tcp = True
            continue
        
        if option_name == 'no-reload':
            resolve_configuration.option_no_reload = True
            continue
        
        if option_name == 'trust-ad':
            resolve_configuration.option_set_verified_data_in_requests = True
            continue
        
        if option_name in (
            'ip6-bytestring',
            'ip6-dotint',
            'no-ip6-dotint',
        ):
            # oldge
            continue
        
        option_split = option_name.split(':', 1)
        if len(option_split) != 2:
            continue
        
        option_name, option_value = option_split
        if not option_value.isdigit():
            continue
        
        option_value = int(option_value)
        
        if option_name == 'ndots':
            if option_value < OPTION_REQUIRED_DOT_COUNT_THRESHOLD_LOWER:
                option_value = OPTION_REQUIRED_DOT_COUNT_THRESHOLD_LOWER
            
            elif option_value > OPTION_REQUIRED_DOT_COUNT_THRESHOLD_UPPER:
                option_value = OPTION_REQUIRED_DOT_COUNT_THRESHOLD_UPPER
            
            resolve_configuration.option_required_dot_count = option_value
            continue
        
        if option_name == 'timeout':
            option_value = float(option_value)
            if option_value < OPTION_TIMEOUT_THRESHOLD_LOWER:
                option_value = OPTION_TIMEOUT_THRESHOLD_LOWER
            
            elif option_value > OPTION_TIMEOUT_THRESHOLD_UPPER:
                option_value = OPTION_TIMEOUT_THRESHOLD_UPPER
            
            resolve_configuration.option_timeout = option_value
            continue
        
        if option_name == 'attempts':
            if option_value < OPTION_ATTEMPTS_THRESHOLD_LOWER:
                option_value = OPTION_ATTEMPTS_THRESHOLD_LOWER
            
            elif option_value > OPTION_ATTEMPTS_THRESHOLD_UPPER:
                option_value = OPTION_ATTEMPTS_THRESHOLD_UPPER
            
            resolve_configuration.option_attempts = option_value
            continue
        
        continue
    
    if name_servers_mentioned:
        if (name_servers is None):
            name_server_configurations = None
        else:
            name_server_configurations = (*(
                NameServerConfiguration(*item, False, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO)
                for item in name_servers
            ),)
        
        resolve_configuration.name_server_configurations = name_server_configurations
        
    if searches_mentioned:
        if (searches is not None):
            searches = tuple(searches)
        
        resolve_configuration.searches = searches
    
    if sort_list_mentioned:
        if (sort_list is not None):
            sort_list = tuple(sort_list)
        
        resolve_configuration.sort_list = sort_list


def parse_configuration_file_content(content):
    """
    Parses a configuration file's content.
    
    Parameters
    ----------
    content : `str`
        The file's content.
    
    Returns
    -------
    configuration : `dict<str, dict<str, str>>`
    """
    configuration = {}
    current_section_name = ''
    
    for line in content.splitlines():
        # Remove everything after #
        double_cross_index = line.find('#')
        if double_cross_index != -1:
            line = line[:double_cross_index]
        
        # Strip the line
        line = line.strip()
        
        # Skip if empty
        if not line:
            continue
        
        # Sections start with [ and end with ]
        if line.startswith('[') and line.endswith(']'):
            current_section_name = line[1:-1].strip()
            continue
        
        # Key value pairs always have an equal in them.
        equal_sign_index = line.find('=')
        if equal_sign_index == -1:
            key = line
            value = ''
        
        else:
            key = line[: equal_sign_index].rstrip()
            value = line[equal_sign_index + 1 :].lstrip()
        
        # Inject
        try:
            section = configuration[current_section_name]
        except KeyError:
            section = {}
            configuration[current_section_name] = section
        
        section[key] = value
        continue
    
    return configuration


def merge_configuration(merge_to, merge_from):
    """
    Merges two configuration.
    
    Parameters
    ----------
    merge_to : `dict<str, dict<str, str>>`
        The original configuration to merge the other one to.
    
    merge_from : `dict<str, dict<str, str>>`
        Configuration to merge from.
    """
    for section_name, section_from in merge_from.items():
        try:
            section_to = merge_to[section_name]
        except KeyError:
            merge_to[section_name] = {**section_from}
            continue
        
        for key, value in section_from.items():
            if value:
                section_to[key] = value
            else:
                section_to.setdefault(key, value)
        continue


def update_name_server_configuration_from_parsed(name_server_configuration, configuration):
    """
    Updates the given name server configuration from the given parsed configuration.
    
    Parameters
    ----------
    name_server_configuration : ``NameServerConfiguration``
        Name server configuration.
    
    configuration : `dict<str, dict<str, str>>`
        Configuration to update with.
    """
    # Update secure_connection_support_level
    while True:
        try:
            section = configuration['Resolve']
        except KeyError:
            break
        
        try:
            value = section['DNSOverTLS']
        except KeyError:
            break
        
        value = value.casefold()
        if value == 'yes':
            # Just because it says yes and you restart it, it can still happen to ignore it.
            # Good job systemd.
            secure_connection_support_level = NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_MAYBE
        elif value == 'no':
            secure_connection_support_level = NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO
        else:
            break
        
        name_server_configuration.secure_connection_support_level = secure_connection_support_level
        break
    
    # No other sections to update, returning.
    return


RESOLVE_CONFIGURATION_DEFAULT = ResolveConfiguration()


def _load():
    """
    Loads the resolve configuration and other files as required.
    """
    # Load resolve configuration
    
    if not is_file(RESOLVE_CONFIGURATION_PATH):
        return
    
    try:
        file = open(RESOLVE_CONFIGURATION_PATH, 'r')
    except PermissionError:
        return
    
    try:
        content = file.read()
    finally:
        file.close()
    
    update_resolve_configuration_from_file_content(RESOLVE_CONFIGURATION_DEFAULT, content)
    
    # Check whether we need md configuration loading
    name_server_configurations = RESOLVE_CONFIGURATION_DEFAULT.name_server_configurations
    if name_server_configurations is None:
        return
    
    for name_server_configuration in name_server_configurations:
        if (
            (name_server_configuration.ip_type == RESOLVE_MD_IP_TYPE) and
            (name_server_configuration.ip_value == RESOLVE_MD_IP_VALUE)
        ):
            break
    else:
        return
    
    # Load resolve md configuration
    
    configuration_file_paths = []
    for directory_path, look_for_end, end in RESOLVE_MD_CONFIGURATION_PATHS:
        if not is_directory(directory_path):
            continue
        
        if not look_for_end:
            file_path = join_paths(directory_path, end)
            if is_file(file_path):
                configuration_file_paths.append(file_path)
            continue
        
        try:
            node_names = list_directory()
        except PermissionError:
            continue
        
        for node_name in node_names:
            if not node_name.endswith(end):
                continue
            
            file_path = join_paths(directory_path, end)
            if is_file(file_path):
                configuration_file_paths.append(file_path)
            continue
    
    if not configuration_file_paths:
        return
    
    merged_configuration = {}
    for configuration_file_path in configuration_file_paths:
        try:
            file = open(configuration_file_path, 'r')
        except PermissionError:
            continue
        
        try:
            content = file.read()
        finally:
            file.close()
        
        merge_configuration(merged_configuration, parse_configuration_file_content(content))
    
    if not merged_configuration:
        return
    
    update_name_server_configuration_from_parsed(name_server_configuration, merged_configuration)
    return


_load()
