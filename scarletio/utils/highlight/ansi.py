__all__ = (
    'ANSITextDecoration', 'create_ansi_format_code', 'iter_produce_ansi_format_code', 'iter_split_ansi_format_codes',
    'stream_split_ansi_format_codes',
)

from ..rich_attribute_error import RichAttributeErrorBaseType


def iter_produce_ansi_format_code(
    reset = False, text_decoration = None, background_color = None, foreground_color = None
):
    """
    Yields an ansi text format code for `ansi` codeblocks.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    reset : `bool` = `False`, Optional
        Whether to reset the previous formatting.
    
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    
    background_color : `None | (int, int, int)` = `None`, Optional
        background color.
    
    foreground_color : `None | (int, int, int)` = `None`, Optional
        Foreground color.
    
    Yields
    -------
    format_code_part : `str`
    """
    field_added = False
    
    if reset:
        field_added = True
        yield '\033['
        yield str(ANSITextDecoration.reset_all)
    
    if (text_decoration is not None):
        if field_added:
            yield ';'
        else:
            field_added = True
            yield '\033['
        
        yield str(text_decoration)
    
    if (background_color is not None):
        if field_added:
            yield ';'
        else:
            field_added = True
            yield '\033['
        
        red, green, blue = background_color
        
        yield '48;2;'
        yield str(red)
        yield ';'
        yield str(green)
        yield ';'
        yield str(blue)
    
    if (foreground_color is not None):
        if field_added:
            yield ';'
        else:
            field_added = True
            yield '\033['
        
        red, green, blue = foreground_color
        
        yield '38;2;'
        yield str(red)
        yield ';'
        yield str(green)
        yield ';'
        yield str(blue)
    
    if field_added:
        yield 'm'


def create_ansi_format_code(reset = False, text_decoration = None, background_color = None, foreground_color = None):
    """
    Creates an ansi text format code for `ansi` codeblocks.
    
    Parameters
    ----------
    reset : `bool` = `False`, Optional
        Whether to reset the previous formatting.
    
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    
    background_color : `None | (int, int, int)` = `None`, Optional
        background color.
    
    foreground_color : `None | (int, int, int)` = `None`, Optional
        Foreground color.
    
    Returns
    -------
    format_code : `str`
    """
    return ''.join([*iter_produce_ansi_format_code(reset, text_decoration, background_color, foreground_color)])


def stream_split_ansi_format_codes(stream):
    """
    Iterates over the given stream and splits the ansi format codes and non ansi format codes.
    
    This function is an iterable coroutine.
    
    Parameters
    ----------
    stream : `iterator<str>`
        Stream to input from.
    
    Yields
    ------
    is_format_code_and_part : `(bool, str)`
    """
    part = None
    while True:
        
        while True:
            if part is None:
                part = next(stream, None)
                if part is None:
                    return
                
                start_index = 0
                end_block = False
                part_length = len(part)
            
            end_index = part.find('\033', start_index)
            if end_index == -1:
                end_index = part_length
            else:
                end_block = True
            
            if start_index != end_index:
                yield (False, part[start_index : end_index])
            
            if end_block:
                break
            
            part = None
            continue
        
        if end_index >= part_length:
            part = None
        
        else:
            start_index = end_index 
        
        while True:
            end_block = False
            
            # First find `[`
            while True:
                if part is None:
                    part = next(stream, None)
                    if part is None:
                        return
                    
                    start_index = 0
                    end_index = 0
                    part_length = len(part)
                
                else:
                    if part[end_index] == '\033':
                        end_index += 1
                
                if end_index >= part_length:
                    yield (True, part[start_index : end_index])
                    part = None
                    continue
                
                code_point = ord(part[end_index])
                if code_point != b'['[0]:
                    end_block = True
                    break
                
                break
            
            if end_block:
                break
            
            
            while True:
                if part is None:
                    part = next(stream, None)
                    if part is None:
                        return
                    
                    start_index = 0
                    end_index = 0
                    part_length = len(part)
                
                else:
                    end_index += 1
                
                if end_index >= part_length:
                    yield (True, part[start_index : end_index])
                    part = None
                    continue
                
                code_point = ord(part[end_index])
                if not (code_point == b';'[0] or (code_point > b'0'[0] - 1 and code_point < b'9'[0] + 1)):
                    break
                
                continue
            
            if end_block:
                break
            
            
            while True:
                if part is None:
                    part = next(stream, None)
                    if part is None:
                        return
                    
                    start_index = 0
                    end_index = 0
                    part_length = len(part)
                
                if end_index >= part_length:
                    yield (True, part[start_index : end_index])
                    part = None
                    continue
                
                code_point = ord(part[end_index])
                if not (
                    (code_point > b'a'[0] - 1 and code_point < b'z'[0] + 1) or
                    (code_point > b'A'[0] - 1 and code_point < b'Z'[0] + 1)
                ):
                    end_block = True
                    break
                
                end_index += 1
                break
            
            if end_block:
                break
            
            break
        
        yield (True, part[start_index : end_index])
        start_index = end_index
        
        if end_index >= part_length:
            part = None


def iter_split_ansi_format_codes(string):
    """
    Iterates over the given string and splits the ansi format codes and non ansi format codes.
    
    This function is an iterable coroutine.
    
    Parameters
    ----------
    string : `str`
        The string to split.
    
    Yields
    ------
    is_format_code_and_part : `(bool, str)`
    """
    content_start_index = 0
    break_after_add = False
    string_length = len(string)
    
    while True:
        content_end_index = string.find('\033', content_start_index)
        if content_end_index == -1:
            content_end_index = string_length
            break_after_add = True
        
        if content_start_index != content_end_index:
            yield (False, string[content_start_index : content_end_index])
        
        if break_after_add:
            break
        
        # We are in an ansi format code
        ansi_end_index = ansi_start_index = content_end_index
        
        while True:
            # First find `[`
            ansi_end_index += 1
            if ansi_end_index >= string_length:
                break_after_add = True
                break
            
            code_point = ord(string[ansi_end_index])
            if code_point != b'['[0]:
                break
            
            # Second consume all `;`, `0 - 9`
            while True:
                ansi_end_index += 1
                if ansi_end_index >= string_length:
                    break_after_add = True
                    break
                
                code_point = ord(string[ansi_end_index])
                if not (code_point == b';'[0] or (code_point > b'0'[0] - 1 and code_point < b'9'[0] + 1)):
                    break
                
                continue
            
            if break_after_add:
                break
            
            # Third, allow any latin
            if ansi_end_index >= string_length:
                break_after_add = True
                break
            
            code_point = ord(string[ansi_end_index])
            if not (
                (code_point > b'a'[0] - 1 and code_point < b'z'[0] + 1) or
                (code_point > b'A'[0] - 1 and code_point < b'Z'[0] + 1)
            ):
                break
            
            ansi_end_index += 1
            break
        
        yield (True, string[ansi_start_index : ansi_end_index])
        
        if break_after_add:
            break
        
        content_start_index = ansi_end_index


class ANSITextDecoration(RichAttributeErrorBaseType):
    """
    Contains the possible text decoration values as type attributes.
    """
    __slots__ = ()
    
    reset_all = 0
    bold = 1
    dim = 2
    italic = 3
    underline = 4
    slow_blink = 5
    rapid_blink = 6
    reverse = 7
    hidden = 8
    crossed = 9
