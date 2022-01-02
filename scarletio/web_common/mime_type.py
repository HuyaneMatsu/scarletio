__all__ = ('MimeType',)

from ..utils import MultiValueDictionary


class MimeType:
    # Parses a MIME type into its components
    __slots__ = ('parameters', 'sub_type', 'suffix', 'type', )
    
    def __init__(self, mime_type):
        
        if (mime_type is None) or (not mime_type):
            self.type = ''
            self.sub_type = ''
            self.suffix = ''
            self.parameters = {}
            return
        
        parts = mime_type.split(';')
        parameters = MultiValueDictionary()
        for item in parts[1:]:
            if not item:
                continue
            
            if '=' in item:
                key, value = item.split('=', 1)
            else:
                key = item
                value = ''
            
            parameters[key.strip().lower()] = value.strip(' "')
        
        
        full_type = parts[0].strip().lower()
        if full_type == '*':
            full_type = '*/*'
        
        if '/' in full_type:
            type_, sub_type = full_type.split('/', 1)
        else:
            type_ = full_type
            sub_type = ''

        if '+' in sub_type:
            sub_type, suffix = sub_type.split('+', 1)
        else:
            suffix = ''
            
        self.type = type_
        self.sub_type = sub_type
        self.suffix = suffix
        self.parameters = parameters
    
    
    def __repr__(self):
        return (
            f'<{self.__class__.__name__} type={self.type!r} sub_type={self.sub_type!r} suffix={self.suffix!r} '
            f'parameters={self.parameters!r}>'
        )
