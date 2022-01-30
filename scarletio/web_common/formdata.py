__all__ = ('Formdata', )

from io import IOBase
from urllib.parse import urlencode

from ..utils import MultiValueDictionary

from .headers import CONTENT_LENGTH, CONTENT_TRANSFER_ENCODING, CONTENT_TYPE
from .multipart import BytesPayload, MultipartWriter, create_payload


class Formdata:
    """
    Helper class for `multipart/form-data` and `application/x-www-form-urlencoded` body generation.
    
    Attributes
    ----------
    fields : `list` of `tuple` (`MultiValueDictionary` of (`str`, `str`) items, `MultiValueDictionary` of (`str`, `str`) items, `Any`)
        The fields of the formdata. Each element is a tuple, which contains the following elements:
        - `type_options` : `MultiValueDictionary` of (`str`, `str`) items;
            Additional information used by the created ``PayloadBase`` when the field is generated.
        - `headers` : `MultiValueDictionary` of (`str`, `str`) items;
            The field specific headers.
        - value : `Any`;
            The field's value.
    
    is_multipart : `bool`
        Whether the formdata is `multipart/form-data` and not `application/x-www-form-urlencoded` type.
    
    quote_fields : `bool`
        Whether type option field values should be quoted.
    """
    __slots__ = ('fields', 'is_multipart', 'quote_fields', )
    
    def __init__(self, quote_fields=True):
        """
        Creates a new a ``Formdata``.
        
        Parameters
        ----------
        quote_fields : `bool` = `True`, Optional
            Whether type option field values should be quoted.
        """
        self.fields = []
        self.is_multipart = False
        self.quote_fields = quote_fields
    
    
    @classmethod
    def from_fields(cls, fields):
        """
        Creates a new ``Formdata`` from the given fields.
        
        Parameters
        ----------
        fields : `dict` of (`str`, `Any`) items, `list` of `tuple` (`str`, `Any`), `IOBase`
            The fields to convert to ``Formdata``.
        
        Returns
        -------
        self : ``Formdata``
            The created formdata instance.
        
        Raises
        ------
        TypeError
            Received unhandleable field.
        """
        if isinstance(fields, dict):
            fields = list(fields.items())
        elif isinstance(fields, (list, tuple)):
            fields = list(fields)
        else:
            fields = [fields]
        
        self = cls()
        
        while fields:
            field = fields.pop(0)
            fiend_type = field.__class__
            if issubclass(fiend_type, IOBase):
                self.add_field(getattr(field, 'name', 'unknown'), field)
            elif issubclass(fiend_type, (tuple, list)) and len(field) == 2:
                self.add_field(*field)
            else:
                raise TypeError(
                    f'`Formdata.from_fields` got unhandleable field: {fiend_type.__name__}; {field!r}.'
                )
        
        return self
    
    
    def add_field(self, name, value, content_type=None, filename=None, transfer_encoding=None):
        """
        Adds a field to the formdata.
        
        Parameters
        ----------
        name : `str`
            The field's name.
        value : `Any`
            The field's value.
        content_type : `None`, `str` = `None`, Optional
            The field's content type.
        filename : `None`, `str` = `None`, Optional
            The field's name. If not given or given as `None` (so by the default), and the given `value` is an `IOBase`
            instance then tries to use that's name.
        transfer_encoding : `None`, `str` = `None`, Optional
            The field's transfer encoding.
        
        Raises
        ------
        AssertionError
            - If `content_type` was not given as `None`, neither as `str`.
            - If `filename` was not given as `None`, neither as `str`.
            - If `transfer_encoding` was not given as `None`, neither as `str`.
        """
        if isinstance(value, IOBase):
            self.is_multipart = True
        elif isinstance(value, (bytes, bytearray, memoryview)):
            if (filename is None) and (transfer_encoding is None):
                filename = name
        
        type_options = MultiValueDictionary()
        type_options['name'] = name
        
        if (filename is not None):
            if __debug__:
                if not isinstance(filename, str):
                    raise AssertionError(f'`filename` can be `None`, `str`, got '
                        f'{filename.__class__.__name__}.')
        
        if (filename is None) and isinstance(value, IOBase):
            filename = getattr(value, 'name', name)
        
        if (filename is not None):
            type_options['filename'] = filename
            self.is_multipart = True
        
        headers = {}
        if (content_type is not None):
            if __debug__:
                if not isinstance(content_type, str):
                    raise AssertionError('`content_type` can be `None`, `str`, got '
                        f'{content_type.__class__.__name__}.')
            
            headers[CONTENT_TYPE] = content_type
            self.is_multipart = True
        
        if (transfer_encoding is not None):
            if __debug__:
                if not isinstance(transfer_encoding, str):
                    raise AssertionError('`transfer_encoding` can be `None`, `str`, got: '
                        f'{transfer_encoding.__class__.__name__}.')
            
            headers[CONTENT_TRANSFER_ENCODING] = transfer_encoding
            self.is_multipart = True
        
        self.fields.append((type_options, headers, value))
    
    
    def _gen_form_urlencoded(self, encoding):
        """
        Generates `application/x-www-form-urlencoded` payload from the ``Formdata``'s fields.
        
        Parameters
        ----------
        encoding : `str`
            The encoding to use to encode the formdata's fields.
        
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
        
        return BytesPayload(urlencode(data, doseq=True, encoding=encoding).encode(), {'content_type': content_type})
    
    
    def _gen_form_data(self, encoding):
        """
        Generates `multipart/form-data` payload from the ``Formdata``'s fields.
        
        Parameters
        ----------
        encoding : `str`
            The encoding to use to encode the formdata's fields.
        
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
                payload_kwargs = {
                    'headers': headers,
                    'encoding': encoding,
                }
                
                try:
                    content_type = headers[CONTENT_TYPE]
                except KeyError:
                    pass
                else:
                    payload_kwargs['content_type'] = content_type
                    
                    if type_options:
                        payload_kwargs.update(type_options.kwargs())
                
                part = create_payload(value, payload_kwargs)
            
            except BaseException as err:
                raise TypeError(f'Can not serialize value type: {value.__class__.__name__}, headers: {headers!r}, '
                    f'value: {value!r}.') from err
            
            if type_options:
                part.set_content_disposition('form-data', type_options.kwargs(), self.quote_fields)
                part.headers.pop_all(CONTENT_LENGTH, None)
            
            writer.append_payload(part)
        
        return writer
    
    def __call__(self, encoding='utf-8'):
        """
        Gets the payload of the ``Formdata``.
        
        Parameters
        ----------
        encoding : `str` = `'utf-8'`, Optional
            The encoding to use to encode the formdata's fields.
        
        Returns
        -------
        payload : ``BytesPayload``, ``MultipartWriter``
            The generated payload.
        
        Raises
        ------
        TypeError
            Cannot serialize a field.
        """
        if self.is_multipart:
            return self._gen_form_data(encoding)
        else:
            return self._gen_form_urlencoded(encoding)
    
    
    def __repr__(self):
        """Returns the representation of the formdata."""
        repr_parts = ['<', self.__class__.__name__, ' [']
        
        fields = self.fields
        limit = len(fields)
        if limit:
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
        
        repr_parts.append(']>')
        
        return ''.join(repr_parts)
    
    __str__ = __repr__
