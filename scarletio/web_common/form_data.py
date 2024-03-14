__all__ = ('FormData', )

from io import IOBase
from urllib.parse import urlencode
from warnings import warn

from ..utils import IgnoreCaseMultiValueDictionary, MultiValueDictionary, RichAttributeErrorBaseType

from .headers import CONTENT_LENGTH, CONTENT_TRANSFER_ENCODING, CONTENT_TYPE
from .multipart import BytesPayload, MultipartWriter, create_payload


class FormData(RichAttributeErrorBaseType):
    """
    Helper class for `multipart/form-data` and `application/x-www-form-urlencoded` body generation.
    
    Attributes
    ----------
    fields : `list<(`MultiValueDictionary<str, str>, IgnoreCaseMultiValueDictionary<str, str>, object)>`
        The fields of the form data. Each element is a tuple, which contains the following elements:
        
        - `type_options` : `MultiValueDictionary<str, str>`;
            Additional information used by the created ``PayloadBase`` when the field is generated.
        - `headers` : `MultiValueDictionary<str, str>`;
            The field specific headers.
        - value : `object`
            The field's value.
    
    multipart : `bool`
        Whether the form data is `multipart/form-data` and not `application/x-www-form-urlencoded` type.
    
    quote_fields : `bool`
        Whether type option field values should be quoted.
    """
    __slots__ = ('fields', 'multipart', 'quote_fields')
    
    def __new__(cls, quote_fields = True):
        """
        Creates a new a form data.
        
        Parameters
        ----------
        quote_fields : `bool` = `True`, Optional
            Whether type option field values should be quoted.
        """
        self = object.__new__(cls)
        self.fields = []
        self.multipart = False
        self.quote_fields = quote_fields
        return self
    
    
    @classmethod
    def from_fields(cls, fields):
        """
        Creates a new form data from the given fields.
        
        Parameters
        ----------
        fields : `dict<str, object> | list<(str, object)> | IOBase`
            The fields to convert to form data.
        
        Returns
        -------
        self : `instance<cls>`
            The created form data instance.
        
        Raises
        ------
        TypeError
            Received unhandleable field.
        """
        if isinstance(fields, dict):
            fields = list(fields.items())
        
        elif isinstance(fields, list) or isinstance(fields, tuple):
            fields = [*fields]
        
        else:
            fields = [fields]
        
        self = cls()
        
        while fields:
            field = fields.pop(0)
            fiend_type = type(field)
            
            if issubclass(fiend_type, IOBase):
                self.add_field(getattr(field, 'name', 'unknown'), field)
            
            elif issubclass(fiend_type, tuple) and len(field) == 2:
                self.add_field(*field)
            
            else:
                raise TypeError(
                    f'`{type(self).__name__}.from_fields` got unhandleable field: {fiend_type.__name__}; {field!r}.'
                )
        
        return self
    
    
    def add_field(self, name, value, content_type = None, filename = ..., file_name = None, transfer_encoding = None):
        """
        Adds a field to the form data.
        
        Parameters
        ----------
        name : `str`
            The field's name.
        value : `object`
            The field's value.
        content_type : `None`, `str` = `None`, Optional
            The field's content type.
        file_name : `None`, `str` = `None`, Optional
            The field's name. If not given or given as `None` (so by the default), and the given `value` is an `IOBase`
            instance then tries to use that's name.
        transfer_encoding : `None`, `str` = `None`, Optional
            The field's transfer encoding.
        
        Raises
        ------
        TypeError
            - If a parameter's type is incorrect.
        """
        if filename is not ...:
            warn(
                (
                    f'`filename` parameter of `{type(self).__name__}.add_field` is deprecated. '
                    f'And will be removed in 2024 August. Please use `file_name` instead.'
                ),
                FutureWarning,
                stacklevel = 2
                
            )
            file_name = filename
        
        if isinstance(value, IOBase):
            self.multipart = True
        
        elif isinstance(value, (bytes, bytearray, memoryview)):
            if (file_name is None) and (transfer_encoding is None):
                file_name = name
        
        type_options = MultiValueDictionary()
        type_options['name'] = name
        
        if (file_name is None) and isinstance(value, IOBase):
            file_name = getattr(value, 'name', name)
        
        if (file_name is not None):
            if not isinstance(file_name, str):
                raise TypeError(
                    f'`file_name` can be `None`, `str`, got {type(file_name).__name__}; {file_name!r}.'
                )
            
            type_options['file_name'] = file_name
            self.multipart = True
        
        headers = IgnoreCaseMultiValueDictionary()
        if (content_type is not None):
            if not isinstance(content_type, str):
                raise TypeError(
                    f'`content_type` can be `None`, `str`, got {type(content_type).__name__}; {content_type!r}.'
                )
            
            headers[CONTENT_TYPE] = content_type
            self.multipart = True
        
        if (transfer_encoding is not None):
            if not isinstance(transfer_encoding, str):
                raise TypeError(
                    f'`transfer_encoding` can be `None`, `str`, got: {type(transfer_encoding).__name__}; '
                    f'{transfer_encoding!r}.'
                )
            
            headers[CONTENT_TRANSFER_ENCODING] = transfer_encoding
            self.multipart = True
        
        self.fields.append((type_options, headers, value))
    
    
    def _generate_form_data(self, encoding):
        """
        Generates `multipart/form-data` payload from the form data fields.
        
        Parameters
        ----------
        encoding : `str`
            The encoding to use to encode the form data's fields.
        
        Returns
        -------
        payload : ``MultipartWriter``
            The generated payload.
        
        Raises
        ------
        TypeError
            Cannot serialize a field.
        RuntimeError
            - If a field's content has unknown content-encoding.
            - If a field's content has unknown content-transfer-encoding.
        """
        writer = MultipartWriter('form-data')
        for type_options, headers, value in self.fields:
            try:
                payload_keyword_parameters = {
                    'headers': headers,
                    'encoding': encoding,
                }
                
                try:
                    content_type = headers[CONTENT_TYPE]
                except KeyError:
                    pass
                else:
                    payload_keyword_parameters['content_type'] = content_type
                    
                    if type_options:
                        payload_keyword_parameters.update(type_options.kwargs())
                
                part = create_payload(value, payload_keyword_parameters)
            
            except Exception as err:
                raise TypeError(
                    f'Can not serialize value type: {type(value).__name__}, headers: {headers!r}, value: {value!r}.'
                ) from err
            
            if type_options:
                part.set_content_disposition_header('form-data', type_options.kwargs(), self.quote_fields)
                part.headers.pop_all(CONTENT_LENGTH, None)
            
            writer.append_payload(part)
        
        return writer
    
    
    def _generate_form_urlencoded(self, encoding):
        """
        Generates `application/x-www-form-urlencoded` payload from the form data's fields.
        
        Parameters
        ----------
        encoding : `str`
            The encoding to use to encode the form data's fields.
        
        Returns
        -------
        payload : ``BytesPayload``
            The generated payload.
        """
        data = []
        for type_options, header, value in self.fields:
            data.append((type_options['name'], value))
        
        if encoding == 'utf-8':
            content_type = 'application/x-www-form-urlencoded'
        else:
            content_type = f'application/x-www-form-urlencoded; charset={encoding}'
        
        return BytesPayload(urlencode(data, doseq = True, encoding = encoding).encode(), {'content_type': content_type})
    
    
    
    
    def generate_form(self, encoding = 'utf-8'):
        """
        Gets the payload of the form data..
        
        Parameters
        ----------
        encoding : `str` = `'utf-8'`, Optional
            The encoding to use to encode the form data's fields.
        
        Returns
        -------
        payload : ``BytesPayload``, ``MultipartWriter``
            The generated payload.
        
        Raises
        ------
        TypeError
            Cannot serialize a field.
        """
        if self.multipart:
            return self._generate_form_data(encoding)
        else:
            return self._generate_form_urlencoded(encoding)
    
    
    def __repr__(self):
        """Returns the representation of the form data."""
        repr_parts = ['<', type(self).__name__]
        
        # fields
        fields = self.fields
        limit = len(fields)
        if not limit:
            field_added = False
        else:
            field_added = True
            
            repr_parts.append(' fields = [')
            index = 0
            while True:
                type_options, headers, value = fields[index]
                repr_parts.append('(')
                repr_parts.append(repr(type_options))
                repr_parts.append(', ')
                repr_parts.append(repr(headers))
                repr_parts.append(', ')
                repr_parts.append(repr(value))
                repr_parts.append(')')
                
                index += 1
                if index == limit:
                    break
                    
                repr_parts.append(', ')
                continue
            
            repr_parts.append(']')
        
        # multipart
        multipart = self.multipart
        if multipart:
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' multipart = ')
            repr_parts.append(repr(multipart))
        
        # quote_fields
        if field_added:
            repr_parts.append(',')
        else:
            field_added = True
        
        repr_parts.append(' quote_fields = ')
        repr_parts.append(repr(self.quote_fields))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    __str__ = __repr__
    
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        
        if self.fields != other.fields:
            return False
        
        if self.multipart != other.multipart:
            return False
        
        if self.quote_fields != other.quote_fields:
            return False
        
        return True
