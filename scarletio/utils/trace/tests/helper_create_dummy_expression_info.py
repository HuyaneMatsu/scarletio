from ...highlight import get_highlight_parse_result

from ..expression_parsing import ExpressionInfo, FileInfo
from ..expression_parsing.expression_info import normalize_and_dedent_lines


def create_dummy_expression_info(expression_key, content):
    """
    Creates a dummy expression info.
    
    Parameters
    ----------
    expression_key : ``ExpressionKey``
    content : `str`
    
    Returns
    -------
    expression_info : ``ExpressionInfo``
    """
    parse_result = get_highlight_parse_result(content)
    file_info = FileInfo(expression_key.file_name, 0, 0.0, content, parse_result, False, False)

    expression_line_start_index = expression_key.line_index
    expression_line_end_index = expression_line_start_index + (parse_result.tokens[-1].line_index if content else 0)
    expression_character_start_index = 0
    expression_character_end_index = len(content)
    
    expression_token_start_index = 0
    expression_token_end_index = len(parse_result.tokens)
    
    if expression_character_start_index == expression_character_end_index:
        removed_indentation_characters = 0
        line = ''
    else:
        lines = file_info.content[expression_character_start_index : expression_character_end_index].splitlines()
        removed_indentation_characters = normalize_and_dedent_lines(lines)
        line = '\n'.join(lines)
    
    return ExpressionInfo(
        expression_key,
        file_info,
        expression_line_start_index,
        expression_line_end_index,
        expression_character_start_index,
        expression_character_end_index,
        expression_token_start_index,
        expression_token_end_index,
        removed_indentation_characters,
        line,
    )
