__all__ = ('URL', )

from itertools import islice
from warnings import warn

from ...utils import RichAttributeErrorBaseType, cached_property

from ..quoting import quote

from .constants import DEFAULT_PORTS, HOST_RP, URL_RP
from .url_fragment import URLFragment
from .url_host_info import URLHostInfo
from .url_path import normalize_path_parts, URLPath
from .url_query import URLQuery, normalize_query
from .url_user_info import URLUserInfo


def _create_host(iterator, encoded):
    """
    Creates an url's host info from the given iterator.
    
    Parameters
    ----------
    iterator : `iterator<None | str>`
        Iterator to go over required amount of elements of it.
    
    encoded : `bool`
        Whether the given `value` is already encoded.
    
    Returns
    -------
    host : `None | URLHostInfo`
    """
    host_local_ip_v4 = next(iterator)
    host_local_name = next(iterator)
    host_local_unambiguous = next(iterator)
    host_external_ip_v4 = next(iterator)
    host_external_ip_v6 = next(iterator)
    host_external_sub_domain_name = next(iterator)
    host_external_main_domain_name = next(iterator)
    host_external_top_level_domain_name = next(iterator)
    host_external_unambiguous = next(iterator)
    
    if (host_local_ip_v4 is not None):
        if encoded:
            host = URLHostInfo.create_from_local_ip_v4_encoded(host_local_ip_v4)
        else:
            host = URLHostInfo.create_from_local_ip_v4_decoded(host_local_ip_v4)
    
    elif (host_local_name is not None):
        unambiguous = (host_local_unambiguous is not None)
        if encoded:
            host = URLHostInfo.create_from_local_name_encoded(host_local_name, unambiguous)
        else:
            host = URLHostInfo.create_from_local_name_decoded(host_local_name, unambiguous)
    
    elif (host_external_ip_v4 is not None):
        if encoded:
            host = URLHostInfo.create_from_external_ip_v4_encoded(host_external_ip_v4)
        else:
            host = URLHostInfo.create_from_external_ip_v4_decoded(host_external_ip_v4)
    
    elif (host_external_ip_v6 is not None):
        if encoded:
            host = URLHostInfo.create_from_external_ip_v6_encoded(host_external_ip_v6)
        else:
            host = URLHostInfo.create_from_external_ip_v6_decoded(host_external_ip_v6)
    
    elif (
        (host_external_sub_domain_name is not None) or
        (host_external_main_domain_name is not None) or
        (host_external_top_level_domain_name is not None)
    ):
        unambiguous = (host_external_unambiguous is not None)
        if encoded:
            host = URLHostInfo.create_from_external_name_encoded(
                host_external_sub_domain_name,
                host_external_main_domain_name,
                host_external_top_level_domain_name,
                unambiguous,
            )
        else:
            host = URLHostInfo.create_from_external_name_decoded(
                host_external_sub_domain_name,
                host_external_main_domain_name,
                host_external_top_level_domain_name,
                unambiguous,
            )
    
    else:
        host = None
    
    return host


class URL(RichAttributeErrorBaseType):
    """
    Represents an url (Uniform Resource Locator).
    
    Attributes
    ----------
    _cache : `None | dict<str, object>`
        Cache.
    
    _fragment : `None | URLFragment`
        The url's fragment component.
    
    _host : `None | URLHostInfo`
        The url's host component.
    
    _path : `None | URLPath`
        The url's path component.
    
    _port : `None | int`
        The url's port.
    
    _query : `None | URLQuery`
        The url's query component.
    
    _scheme : `None | str`
        The url's scheme.
    
    _user : `None | URLUserInfo``
        The url's user component.
    """
    __slots__ = ('_cache', '_fragment', '_host', '_path', '_port', '_query', '_scheme', '_user')
    
    def __new__(cls, value = '', encoded = False):
        """
        Creates a new url from the given value.
        
        Parameters
        ----------
        value : `str | instance<cls>` = `''`, Optional
            The value to create instance from.
        
        encoded : `bool` = `False`, Optional
            Whether the given `value` is already encoded.
        
        Raises
        -------
        ValueError
            - If a parameter's value is incorrect.
        TypeError
            - If a parameter's type is incorrect.
        """
        if isinstance(value, cls):
            return value
        
        if isinstance(value, str):
            if not value:
                cls._create_empty()
            
            return cls._create_from_string(value, encoded)
            
        raise TypeError(
            f'`value` can be `{cls.__name__}`, `str`. Got '
            f'{type(value).__name__}; {value!r}.'
        )
    
    
    @classmethod
    def _create_empty(cls):
        """
        Creates an empty url.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self._cache = None
        self._fragment = None
        self._host = None
        self._path = None
        self._port = None
        self._query = None
        self._scheme = None
        self._user = None
        return self
    
    
    @classmethod
    def _create_from_string(cls, value, encoded):
        """
        Creates an url from the given string.
        
        Parameters
        ----------
        value : `str`
            the value to create url from.
        
        encoded : `bool`
            Whether the given `value` is already encoded.
        
        Returns
        -------
        self : `instance<cls>`
        """
        match = URL_RP.fullmatch(value)
        if match is None:
            raise ValueError(
                f'The given value is not an url: {value!r}.'
            )
        
        iterator = iter(match.groups())
        
        # scheme
        scheme = next(iterator)
        # nothing to do, we expected it to be already in good format
        
        # user
        user_name = next(iterator)
        user_password = next(iterator)
        if (user_name is not None) or (user_password is not None):
            if encoded:
                user = URLUserInfo.create_from_encoded(user_name, user_password)
            else:
                user = URLUserInfo.create_from_decoded(user_name, user_password)
        
        else:
            user = None
        
        # host
        host = _create_host(iterator, encoded)
        
        # port
        port = next(iterator)
        if (port is not None):
            port = int(port)
        
        # path
        path = next(iterator)
        if (path is not None):
            if encoded:
                path = URLPath.create_from_encoded(path)
            else:
                path = URLPath.create_from_decoded(path)
        
        # query
        query = next(iterator)
        if (query is not None):
            if encoded:
                query = URLQuery.create_from_encoded(query)
            else:
                query = URLQuery.create_from_decoded(query)
        
        # fragment
        fragment = next(iterator)
        if (fragment is not None):
            if encoded:
                fragment = URLFragment.create_from_encoded(fragment)
            else:
                fragment = URLFragment.create_from_decoded(fragment)
        
        # Construct
        self = object.__new__(cls)
        self._cache = None
        self._fragment = fragment
        self._host = host
        self._path = path
        self._port = port
        self._query = query
        self._scheme = scheme
        self._user = user
        return self
    
    
    @cached_property
    def value_decoded(self):
        """
        Returns the decoded value of the url.
        
        Returns
        -------
        value : `str`
        """
        return self._build_value(False)
    
    
    @cached_property
    def value_encoded(self):
        """
        Returns the encoded value of the url.
        
        Returns
        -------
        value : `str`
        """
        return self._build_value(True)
    
    
    def _build_value(self, encoded):
        """
        Builds the string value of the url.
        
        Parameters
        ----------
        encoded : `bool`
            Whether should build an encoded value.
        """
        built = []
        
        # scheme
        scheme = self._scheme
        if (scheme is not None):
            built.append(scheme)
            built.append(':')
        
        # authority (can be missing if relative)
        user = self._user
        port = self._port
        if (user is not None) or (self._host is not None) or (port is not None):
            if built:
                built.append('//')
            
            # user
            if (user is not None):
                if encoded:
                    user_name = user.name_encoded
                    user_password = user.password_encoded
                else:
                    user_name = user.name_decoded
                    user_password = user.password_decoded
                
                if (user_name is not None):
                    built.append(user_name)
                
                built.append(':')
                
                if (user_password is not None):
                    built.append(user_password)
                
                built.append('@')
            
            # host
            built = self._build_host_into(built, encoded)
            
            # port
            if (port is not None):
                built.append(':')
                built.append(str(port))
        
        
        # path
        path = self._path
        if (path is None):
            path_value = None
        else:
            if encoded:
                path_value = path.encoded
            else:
                path_value = path.decoded
        
        if path_value is None:
            path_value = '/'
        
        built.append(path_value)
        
        # query
        query = self._query
        if (query is not None):
            if encoded:
                query_value = query.encoded
            else:
                query_value = query.decoded
            
            if (query_value is not None):
                built.append('?')
                built.append(query_value)
        
        # fragment
        fragment = self._fragment
        if (fragment is not None):
            if encoded:
                fragment_value = fragment.encoded
            else:
                fragment_value = fragment.decoded
            
            if (fragment_value is not None):
                built.append('#')
                built.append(fragment_value)
        
        # Remove `/` if we have only that.
        if len(built) == 1 and built[0] == '/':
            return ''
        
        return ''.join(built)
    
    
    def _build_host_into(self, into, encoded):
        """
        Builds the host section of the url into the given container.
        
        Parameters
        ----------
        into : `list<str>`
            Container to build into.
        
        encoded : `bool`
            Whether should build encoded authority.
        
        Returns
        -------
        into : `list<str>`
        """
        host = self._host
        # host (should never be None if we have this case)
        if (host is not None):
            if encoded:
                host_main_domain = host.main_domain_encoded
                host_sub_domain = host.sub_domain_encoded
                host_top_level_domain = host.top_level_domain_encoded
            else:
                host_main_domain = host.main_domain_decoded
                host_sub_domain = host.sub_domain_decoded
                host_top_level_domain = host.top_level_domain_decoded
            
            if (host_sub_domain is not None):
                into.append(host_sub_domain)
                into.append('.')
            
            # (should never be None)
            if (host_main_domain is not None):
                ip_v6 = host.is_ip_v6()
                if ip_v6:
                    into.append('[')
                
                into.append(host_main_domain)
                
                if ip_v6:
                    into.append(']')
            
            if (host_top_level_domain is not None):
                into.append('.')
                into.append(host_top_level_domain)
            
            if host.is_unambiguous():
                into.append('.')
        
        
        return into
    
    
    def __str__(self):
        """Returns str(self)."""
        return self.value_decoded
    
    
    def __repr__(self):
        """Returns repr(self)."""
        return f'{type(self).__name__}({self.value_decoded!r})'
    
    
    def __hash__(self):
        """Returns hash(self)."""
        return hash(self.value_encoded)
    
    
    def __bool__(self):
        """Returns bool(self)."""
        # fragment
        if (self._fragment is not None):
            return True
        
        # host
        if (self._host is not None):
            return True
        
        # path
        if (self._path is not None):
            return True
        
        # port
        if (self._port is not None):
            return True
        
        # query
        if (self._query is not None):
            return True
        
        # scheme
        if (self._scheme is not None):
            return True
        
        # user
        if (self._user is not None):
            return True
        
        return False
        
    
    def __gt__(self, other):
        """Returns (self > other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded > other.value_encoded
    
    
    def __ge__(self, other):
        """Returns (self >= other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded >= other.value_encoded
        
        
    def __eq__(self, other):
        """Returns (self == other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded == other.value_encoded
    
    
    def __ne__(self, other):
        """Returns (self != other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded != other.value_encoded
    
    
    def __le__(self, other):
        """Returns (self <= other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded <= other.value_encoded
    
    
    def __lt__(self, other):
        """Returns (self < other)."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.value_encoded < other.value_encoded
    
    
    def __truediv__(self, name):
        """Returns self / other"""
        # Join *self.path with name
        path = self._path
        if (path is None):
            split = None
        else:
            split = path.parsed
        
        if split is None:
            split = [name]
        else:
            split = [*split, name]
        
        split = normalize_path_parts(split)
        if split is None:
            path = None
        else:
            path = URLPath.create_from_parsed(tuple(split))
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def is_absolute(self):
        """
        Returns whether the url is absolute (having scheme or starting with //).
        
        Returns
        -------
        is_absolute : `bool`
        """
        return (self._host is not None)
    
    
    def is_default_port(self):
        """
        Returns whether the url's port is default, like: 'https://orindance.party/' or 'https://orindance.party:80/'.
        
        Returns
        -------
        is_default_port : `bool`
        """
        scheme = self._scheme
        if scheme is None:
            return False
        
        scheme_default_port = DEFAULT_PORTS.get(scheme, None)
        if scheme_default_port is None:
            return False
        
        port = self._port
        
        if port is None:
            port = DEFAULT_PORTS.get(scheme, None)
            if port is None:
                return False
        
        return scheme_default_port == port
    
    
    def is_host_ip_v4(self):
        """
        Returns whether the host is an ipv4 address.
        
        Returns
        -------
        is_ip_v4 : `bool`
        """
        host = self._host
        if host is None:
            return False
        
        return host.is_ip_v4()
    
    
    def is_host_ip_v6(self):
        """
        Returns whether the host is an ipv6 address.
        
        Returns
        -------
        is_ip_v6 : `bool`
        """
        host = self._host
        if host is None:
            return False
        
        return host.is_ip_v6()
    
    
    def origin(self):
        """
        Returns an url with scheme, host and port parts only, user, password, path, query and fragment are removed.
        
        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        ValueError
            - If the url is not absolute.
        """
        if not self.is_absolute():
            raise ValueError(
                f'Url should be absolute; self = {self!r}.'
            )
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = None
        new._host = self._host
        new._path = None
        new._port = self._port
        new._query = None
        new._scheme = self._scheme
        new._user = None
        return new

    
    def relative(self):
        """
        Returns a relative part of the url. Scheme, user, password, host and port are removed.
        
        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        ValueError
            If url is not absolute.
        """
        if not self.is_absolute():
            raise ValueError(
                f'Url should be absolute; self = {self!r}.'
            )
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = None
        new._path = self._path
        new._port = None
        new._query = self._query
        new._scheme = None
        new._user = None
        return new
    
    
    @property
    def scheme(self):
        """
        Returns the scheme for absolute url-s. Returns `None` for relatives or if the url has no scheme.
        
        Returns
        -------
        scheme : `None | str`
        """
        return self._scheme

    
    @property
    def raw_user(self):
        """
        Returns the encoded user part of the url. `None` is returned if the user part is missing.
        
        Returns
        -------
        raw_user : `None | str`
        """
        user = self._user
        if (user is not None):
            return user.name_encoded
    
    
    @property
    def user(self):
        """
        Returns the decoded user part of the url. `None` is returned if the user part is missing.
        
        Returns
        -------
        user : `None | str`
        """
        user = self._user
        if (user is not None):
            return user.name_decoded
    
    
    @property
    def raw_password(self):
        """
        Returns the encoded password part of the url. Returns `None` if password is missing.
        
        Returns
        -------
        raw_password : `None | str`
        """
        user = self._user
        if (user is not None):
            return user.password_encoded
    
    
    @property
    def password(self):
        """
        Returns the decoded password part of the url. Returns `None` if password is missing.
        
        Returns
        -------
        password : `None | str`
        """
        user = self._user
        if (user is not None):
            return user.password_decoded

    
    @cached_property
    def raw_host(self):
        """
        Returns the encoded host part of the url. Returns `None` if the host part is missing or if the url is relative.
        
        Returns
        -------
        raw_host : `None | str`
        """
        built = self._build_host_into([], True)
        if built:
            return ''.join(built)
    
    
    @cached_property
    def host(self):
        """
        Returns the decoded host part of the url. Returns `None` if the host part is missing or if the url is relative.
        
        Returns
        -------
        host : `None`, `str`
        """
        built = self._build_host_into([], False)
        if built:
            return ''.join(built)
    
    
    @property
    def raw_subdomain(self):
        """
        Deprecated and will be removed in 2025 November. Use `.raw_sub_domain` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.raw_subdomain` is deprecated and will be removed in 2025 November. '
                f'Please use `.raw_sub_domain` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.raw_sub_domain
    
    
    @property
    def subdomain(self):
        """
        Deprecated and will be removed in 2025 November. Use `.sub_domain` instead.
        """
        warn(
            (
                f'`{type(self).__name__}.subdomain` is deprecated and will be removed in 2025 November. '
                f'Please use `.sub_domain` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return self.sub_domain
    
    
    @property
    def raw_sub_domain(self):
        """
        Returns the encoded sub domain part of the url. Returns `None` if the sub domain part is missing or if
        the url is relative.
        
        Returns
        -------
        raw_sub_domain : `None | str`
        """
        host = self._host
        if (host is not None):
            return host.sub_domain_encoded
    
    
    @property
    def sub_domain(self):
        """
        Returns the decoded sub domain part of the url. Returns `None` if the sub domain part is missing or if
        the url is relative.
        
        Returns
        -------
        sub_domain : `None`, `str`
        """
        host = self._host
        if (host is not None):
            return host.sub_domain_decoded

    
    @property
    def port(self):
        """
        Returns the port part of url. Returns `None` if the url is relative, if the url not contains port part and if
        the port can's be detected from the url's scheme.
        
        Returns
        -------
        port : `None | int`
        """
        port = self._port
        if (port is not None):
            return port
        
        scheme = self._scheme
        if (scheme is not None):
            return DEFAULT_PORTS.get(scheme, None)
    
    
    @property
    def raw_path(self):
        """
        Returns the encoded path part of the url. Returns `None` if the url has no path.
        
        Returns
        -------
        raw_path : `str`
        """
        path = self._path
        if (path is None):
            path_value = None
        else:
            path_value = path.encoded
        
        if path_value is None:
            path_value = '/'
        
        return path_value
    
    
    @property
    def path(self):
        """
        Returns the decoded path part of the url. Returns `None` if the url has no path.
        
        Returns
        -------
        path : `str`
        """
        path = self._path
        if (path is None):
            path_value = None
        else:
            path_value = path.decoded
        
        if path_value is None:
            path_value = '/'
        
        return path_value
    
    
    @property
    def query(self):
        """
        Returns a multi value dictionary representing parsed query parameters in decoded representation.
        
        `None` if returned if the url has no query.
        
        Returns
        -------
        query : `None | MultiValueDictionary<str, str>`
        """
        query = self._query
        if (query is not None):
            return query.parsed
    
    
    @property
    def raw_query_string(self):
        """
        Returns the encoded query string part of url. Returns an `None` if the query part is missing.
        
        Returns
        -------
        raw_query_string : `None | str`
        """
        query = self._query
        if (query is not None):
            return query.encoded
    
    
    @property
    def query_string(self):
        """
        Returns the decoded query string part of url. Returns `None` if the query part is missing.
        
        Returns
        -------
        query_string : `str`
        """
        try:
            query = self._query
            if (query is not None):
                return query.decoded
        except:
            raise ValueError()
    
    
    @property
    def raw_fragment(self):
        """
        Returns the encoded fragment part of the url. Returns `None` if the fragment part is missing.
        
        Returns
        -------
        raw_fragment : `None | str`
        """
        fragment = self._fragment
        if (fragment is not None):
            return fragment.encoded
    
    
    @property
    def fragment(self):
        """
        Returns the decoded fragment part of the url. Returns `None` if the fragment part is missing.
        
        Returns
        -------
        raw_fragment : `None | str`
        """
        fragment = self._fragment
        if (fragment is not None):
            return fragment.decoded
    
    
    @cached_property
    def raw_parts(self):
        """
        Deprecated and will be removed in 2025 November.
        """
        warn(
            f'`{type(self).__name__}.raw_parts` is deprecated and will be removed in 2025 November.',
            FutureWarning,
            stacklevel = 2,
        )
        path = self._path
        if (path is not None):
            return (*(quote(part, safe = '@:', protected = '/') for part in path.parsed),)
    
    
    @property
    def parts(self):
        """
        Returns a `tuple` containing decoded path parts. If the url has no path returns `None`.

        Returns
        -------
        parts : `None | tuple<str>`
        """
        path = self._path
        if (path is not None):
            return path.parsed
    
    
    @cached_property
    def parent(self):
        """
        Returns a new url with last part of path removed without query and fragment.
        
        Returns
        -------
        parent : `instance<type<self>>`
        """
        path = self._path
        if (path is not None):
            path_parts = path.parsed
            if (path_parts is None):
                path = None
            
            elif len(path_parts) == 1:
                path = None
            
            else:
                path = URLPath.create_from_parsed(path_parts[:-1])
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = path
        new._port = self._port
        new._query = None
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    @cached_property
    def raw_name(self):
        """
        Deprecated and will be removed in 2025 November.
        """
        warn(
            f'`{type(self).__name__}.raw_parts` is deprecated and will be removed in 2025 November.',
            FutureWarning,
            stacklevel = 2,
        )
        path = self._path
        if (path is not None):
            path_parts = path.parsed
            if (path_parts is not None):
                return quote(path_parts[-1], safe = '@:', protected = '/')
    
    
    @cached_property
    def name(self):
        """
        Returns the last part of ``.parts``. If there are no parts, returns `None`.
        
        Returns
        -------
        raw_name : `str`
        """
        path = self._path
        if (path is not None):
            path_parts = path.parsed
            if (path_parts is not None):
                return path_parts[-1]
        
        return ''
    
    
    def with_scheme(self, scheme):
        """
        Returns a new url with `scheme` replaced.
        
        Parameters
        ----------
        scheme : `None | str`
            Scheme part for the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            If `scheme` was not given as `None`, `str`.
        ValueError
            If the source url is relative; Scheme replacement is not allowed for relative url-s.
        
        Notes
        -----
        The returned url's `query` and `fragment` will be same as the source one's.
        """
        if (scheme is None):
            pass
        
        elif isinstance(scheme, str):
            if not scheme:
                scheme = None
        
        else:
            raise TypeError(
                f'`scheme` can be `None`, `str`, got {type(scheme).__name__}; {scheme!r}.'
            )
        
        if not self.is_absolute():
            raise ValueError(
                f'`scheme` replacement is not allowed for relative url-s; self = {self!r}; scheme = {scheme!r}.'
            )
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = self._query
        new._scheme = scheme
        new._user = self._user
        return new
    
    
    def with_user(self, user_name):
        """
        Returns a new url with `user` replaced.
        
        Parameters
        ----------
        user_name : `None | str`
            New user name part for the new url.

        Returns
        -------
        new : `instance<type<cls>>`
        
        Raises
        ------
        TypeError
            If `user` was not given neither as `None` nor `str`.
        ValueError
            If the source url is relative; User replacement is not allowed for relative url-s.
        
        Notes
        -----
        The returned url's `query` and `fragment` will be same as the source one's.
        """
        if user_name is None:
            user_password = self.password
        
        elif isinstance(user_name, str):
            if not user_name:
                user_name = None
            
            user_password = self.password
            
        else:
            raise TypeError(
                f'`user_name` can be `None`, `str`, got {type(user_name).__name__}; {user_name!r}.'
            )
        
        if not self.is_absolute():
            raise ValueError(
                f'`user` replacement is not allowed for relative url-s; self = {self!r}; user_name = {user_name!r}.'
            )
        
        if (user_name is None) and (user_password is None):
            user = None
        else:
            user = URLUserInfo.create_from_decoded(user_name, user_password)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = user
        return new
    
    
    def with_password(self, user_password):
        """
        Returns a new url with `password` replaced.
        
        Give `password` as `None` to clear it from the source url.
        
        Parameters
        ----------
        user_password : `None | str`
            New user password part for the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            If `password` was not given neither as `None` nor `str`.
        ValueError
            If the source url is relative; Password replacement is not allowed for relative url-s.
        
        Notes
        -----
        The returned url's `query` and `fragment` will be same as the source one's.
        """
        if (user_password is None):
            user_name = self.user
        
        elif isinstance(user_password, str):
            user_name = self.user
            
            if not user_password:
                user_password = None
        
        else:
            raise TypeError(
                f'`user_password` can be `None`, `str`, got {type(user_password).__name__}; {user_password!r}.'
            )
        
        if not self.is_absolute():
            raise ValueError(
                f'Password replacement is not allowed for relative url-s; '
                f'self = {self!r}; user_password = {user_password}.'
            )
        
        if (user_name is None) and (user_password is None):
            user = None
        else:
            user = URLUserInfo.create_from_decoded(user_name, user_password)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = user
        return new
    

    def with_host(self, host):
        """
        Returns a new url with `host` replaced.
        
        Parameters
        ----------
        host : `str`
            Host part for the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            If `host` was not given as `str`.
        ValueError
            - If the source url is relative; Host replacement is not allowed for relative url-s.
            - If `host` was given as empty string; Removing `host` is not allowed.
            - If `host` could not be matched to any patterns.
        
        Notes
        -----
        The returned url's `query` and `fragment` will be same as the source one's.
        """
        if not isinstance(host, str):
            raise TypeError(
                f'`host` can be `str`, got {type(host).__name__}; {host!r}.'
            )
        
        if not host:
            raise ValueError(
                f'`host` was given as empty string, but removing host is not allowed; self = {self!r}.'
            )
        
        if not self.is_absolute():
            raise ValueError(
                f'`host` replacement is not allowed for relative url-s; self = {self!r}; host = {host!r}.'
            )
        
        match = HOST_RP.fullmatch(host)
        if match is None:
            raise ValueError(
                f'`host` could not be matched to any known pattern: host = {host!r}'
            )
        
        iterator = iter(match.groups())
        host = _create_host(iterator, False)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = host
        new._path = self._path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def with_port(self, port):
        """
        Returns a new url with `port` replaced. Give `port` as None` to clear it to default.
        
        Parameters
        ----------
        port : `None | int`
            Port part of the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            - If `port` was not given neither as `None` nor `int`.
        ValueError
            - If the source url is relative; Port replacement is not allowed for relative url-s.
            - If `port` is negative.
        
        Notes
        -----
        The returned url's `query` and `fragment` will be same as the source one's.
        """
        if (port is None):
            pass
        
        elif isinstance(port, int):
            if port < 0:
                raise ValueError(
                    f'`port` cannot be negative, got {port!r}.'
                )
        
        else:
            raise TypeError(
                f'`port` can be `None`, `int`, got {type(port).__name__}; {port!r}.'
            )
        
        if not self.is_absolute():
            raise ValueError(
                f'`port` replacement is not allowed for relative url-s; self = {self!r}; port = {port}.'
            )
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = port
        new._query = self._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def with_query(self, query):
        """
        Returns a new url with query part replaced. By giving `None` you can clear the actual query.
        
        Parameters
        ----------
        query : `None | str | dict<str, str | int | bool | None | float | DateTime | (list | set)<...>> | (list | set)<(str, ...)>`
            The query to use.
        
        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            - If `query` was given as an invalid type.
            - If `query` was given as `set`, `list`, but `1` of it's elements cannot be unpacked correctly.
            - If a query key was not given as `str`.
            - If a query value was not given as any of the expected types.
        ValueError
            - If a query value was given as `float`, but as `inf`.
            - If a query value was given as `float`, but as `nan`.
        
        Notes
        -----
        The returned url's `fragment` will be same as the source one's.
        """
        query = normalize_query(query)
        if (query is not None):
            query = URLQuery.create_from_parsed(query)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = query
        new._scheme = self._scheme
        new._user = self._user
        return new

    
    def with_fragment(self, fragment):
        """
        Returns a new url with `fragment` replaced. Give `fragment` as None` to clear it.
        
        Parameters
        ----------
        fragment : `None | str`
            Fragment part of the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            If `fragment` was not given neither as `None` nor `str`.
        
        Notes
        -----
        The returned url's `query` will be same as the source one's.
        """
        if fragment is None:
            pass
        
        elif isinstance(fragment, str):
            if not fragment:
                fragment = None
        
        else:
            raise TypeError(
                f'`fragment` can be `None`, `str`, got {type(fragment).__name__}; {fragment!r}.'
            )
        
        if (fragment is not None):
            fragment = URLFragment.create_from_decoded(fragment)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def with_name(self, name):
        """
        Returns a new url with `name` (last part of path) replaced.
        
        Parameters
        ----------
        name : `str`
            Name part of the new url.

        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            If `name` was not given as `str`.
        
        Notes
        -----
        The returned url's `fragment` and `query` will be REMOVED.
        """
        if not isinstance(name, str):
            raise TypeError(
                f'`name` can be `str`, got {type(name).__name__}; {name!r}.'
            )
        
        path = self._path
        if path is None:
            path_parts = None
        else:
            path_parts = path.parsed
        
        if path_parts is None:
            path_parts_length = 0
        else:
            path_parts_length = len(path_parts)
        
        if path_parts_length <= 1:
            path_parts = [name]
        
        else:
            path_parts = [*islice(path_parts, 0, path_parts_length - 1), name]
        
        path_parts = normalize_path_parts(path_parts)
        if (path_parts is not None):
            path_parts = tuple(path_parts)
        
        if path_parts is None:
            path = None
        else:
            path = URLPath.create_from_parsed(path_parts)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = path
        new._port = self._port
        new._query = self._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def join(self, other):
        """
        Joins two urls.
        
        Construct a full ('absolute') url by combining a 'base url' (self) with another one (other).
        
        Informally, this uses components of the base url, in particular the addressing scheme, the network location and
        (part of) the path, to provide missing components in the relative url.
        
        Parameters
        ----------
        other : `instance<type<self>>`
            The other url to join to self.
        
        Raises
        ------
        TypeError
            If `other` was not given as the same type.
        """
        if not isinstance(other, type(self)):
            raise TypeError(
                f'`url` can be `{type(self).__name__}`, got {type(other).__name__}; {other!r}.'
            )
        
        self_path = self._path
        if self_path is None:
            self_path_parts = None
        else:
            self_path_parts = self_path.parsed
        
        other_path = other._path
        if other_path is None:
            other_path_parts = None
        else:
            other_path_parts = other_path.parsed
        
        if self_path_parts is None:
            path_parts = other_path_parts
        
        elif other_path_parts is None:
            path_parts = self_path_parts
        
        else:
            path_parts = [*self_path_parts, *other_path_parts]
            path_parts = normalize_path_parts(path_parts)
            if (path_parts is not None):
                path_parts = tuple(path_parts)
        
        if path_parts is None:
            path = None
        else:
            path = URLPath.create_from_parsed(path_parts)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = other._fragment
        new._host = self._host
        new._path = path
        new._port = self._port
        new._query = other._query
        new._scheme = self._scheme
        new._user = self._user
        return new
    
    
    def extend_query(self, query):
        """
        Returns a new url with it's query parameters extended.
        
        Parameters
        ----------
        query : `None | str | dict<str, str | int | bool | None | float | DateTime | (list | set)<...>> | (list | set)<(str, ...)>`
            The query to use.
        
        Returns
        -------
        new : `instance<type<self>>`
        
        Raises
        ------
        TypeError
            - If `query` was given as an invalid type.
            - If `query` was given as `set`, `list`, but `1` of it's elements cannot be unpacked correctly.
            - If a query key was not given as `str`.
            - If a query value was not given as any of the expected types.
        ValueError
            - If a query value was given as `float`, but as `inf`.
            - If a query value was given as `float`, but as `nan`.
        
        Notes
        -----
        The returned url's `fragment` will be same as the source one's.
        """
        other_query = normalize_query(query)
        
        query = self._query
        if query is None:
            self_query = None
        else:
            self_query = query.parsed
        
        if other_query is None:
            if self_query is None:
                query = None
            else:
                query = self_query.copy()
        
        else:
            if self_query is None:
                query = other_query
            else:
                query = self_query.copy()
                query.extend(other_query)
        
        if (query is not None):
            query = URLQuery.create_from_parsed(query)
        
        # Construct
        new = object.__new__(type(self))
        new._cache = None
        new._fragment = self._fragment
        new._host = self._host
        new._path = self._path
        new._port = self._port
        new._query = query
        new._scheme = self._scheme
        new._user = self._user
        return new
