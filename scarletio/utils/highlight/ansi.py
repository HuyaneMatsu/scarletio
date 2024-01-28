__all__ = ('AnsiTextDecoration', 'create_ansi_format_code',)

from ..rich_attribute_error import RichAttributeErrorBaseType


def create_ansi_format_code(text_decoration = None, background_color = None, foreground_color = None):
    """
    Creates an ansi text format code for `ansi` codeblocks.
    
    > If no parameter is given, will generate a format reset code.
    
    Parameters
    ----------
    text_decoration : `None | int` = `None`, Optional
        Text decoration.
    background_color : `None | (int, int, int) = `None`, Optional
        background color.
    foreground_color : `None | (int, int, int) = `None`, Optional
        Foreground color.
    
    Returns
    -------
    format_code : `str`
    """
    format_code_parts = ['\033[']
    
    field_added = False
    
    if (text_decoration is not None):
        field_added = True
        
        format_code_parts.append(str(text_decoration))
    
    if (background_color is not None):
        if field_added:
            format_code_parts.append(';')
        else:
            field_added = True
        
        red, green, blue = background_color
        
        format_code_parts.append('48;2;')
        format_code_parts.append(str(red))
        format_code_parts.append(';')
        format_code_parts.append(str(green))
        format_code_parts.append(';')
        format_code_parts.append(str(blue))
    
    if (foreground_color is not None):
        if field_added:
            format_code_parts.append(';')
        else:
            field_added = True
        
        red, green, blue = foreground_color
        
        format_code_parts.append('38;2;')
        format_code_parts.append(str(red))
        format_code_parts.append(';')
        format_code_parts.append(str(green))
        format_code_parts.append(';')
        format_code_parts.append(str(blue))
    
    if not field_added:
        format_code_parts.append(str(AnsiTextDecoration.reset_all))
    
    format_code_parts.append('m')
    
    return ''.join(format_code_parts)


class AnsiTextDecoration(RichAttributeErrorBaseType):
    """
    Contains the possible text decoration values as type attributes.
    """
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
