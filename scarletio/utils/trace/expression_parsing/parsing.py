__all__ = ()

from .line_info import get_file_line


EXPRESSION_LINE_COUNT_MAX = 21


ACTION_TYPE_NONE = 0
ACTION_TYPE_PARENTHESES_OPEN_BRACKET = 1
ACTION_TYPE_PARENTHESES_OPEN_BOX = 2
ACTION_TYPE_PARENTHESES_OPEN_CURVY = 3
ACTION_TYPE_PARENTHESES_CLOSE_BRACKET = 4
ACTION_TYPE_PARENTHESES_CLOSE_BOX = 5
ACTION_TYPE_PARENTHESES_CLOSE_CURVY = 6
ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE = 7
ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE = 8
ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE = 9
ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE = 10
ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE = 11
ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE = 12
ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE = 13
ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE = 14
ACTION_TYPE_LINE_ESCAPE = 15
ACTION_FORWARD = 16
ACTION_BACKWARDS = 17


CHARACTER_TO_ACTION = {
    '(': ACTION_TYPE_PARENTHESES_OPEN_BRACKET,
    '{': ACTION_TYPE_PARENTHESES_OPEN_CURVY,
    '[': ACTION_TYPE_PARENTHESES_OPEN_BOX,
    ')': ACTION_TYPE_PARENTHESES_CLOSE_BRACKET,
    ']': ACTION_TYPE_PARENTHESES_CLOSE_BOX,
    '}': ACTION_TYPE_PARENTHESES_CLOSE_CURVY,
}


ACTION_TYPE_STRING_OPEN = {
    ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
    ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE,
    ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE,
    ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE,
}


DIRECTION_NONE = 0
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = 2
DIRECTION_REPEAT_LAST = 3


ACTION_DIRECTIONS = {
    ACTION_TYPE_NONE: DIRECTION_NONE,
    ACTION_TYPE_PARENTHESES_OPEN_BRACKET: DIRECTION_FORWARD,
    ACTION_TYPE_PARENTHESES_OPEN_BOX: DIRECTION_FORWARD,
    ACTION_TYPE_PARENTHESES_OPEN_CURVY: DIRECTION_FORWARD,
    ACTION_TYPE_PARENTHESES_CLOSE_BRACKET: DIRECTION_BACKWARD,
    ACTION_TYPE_PARENTHESES_CLOSE_BOX: DIRECTION_BACKWARD,
    ACTION_TYPE_PARENTHESES_CLOSE_CURVY: DIRECTION_BACKWARD,
    
    ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE: DIRECTION_REPEAT_LAST,
    ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE: DIRECTION_REPEAT_LAST,
    
    ACTION_TYPE_LINE_ESCAPE: DIRECTION_FORWARD,
    ACTION_FORWARD: DIRECTION_FORWARD,
    ACTION_BACKWARDS: DIRECTION_BACKWARD,
}

STRING_OPEN_CLOSE_PAIRS = {
    (ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE, ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE),
    (ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE, ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE),
    (ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE, ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE),
    (ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE, ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE),
    (ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE, ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE),
    (ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE, ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE),
}


PARENTHESES_OPEN_CLOSE_PAIRS = {
    (ACTION_TYPE_PARENTHESES_OPEN_BRACKET, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET),
    (ACTION_TYPE_PARENTHESES_OPEN_BOX, ACTION_TYPE_PARENTHESES_CLOSE_BOX),
    (ACTION_TYPE_PARENTHESES_OPEN_CURVY, ACTION_TYPE_PARENTHESES_CLOSE_CURVY),
}


STRING_MUST_BE_PAIRED = {
    ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
    ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE,
    ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE,
    ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE,
}

PARENTHESES_INVALID_PAIRS = {
    (ACTION_TYPE_PARENTHESES_OPEN_BRACKET, ACTION_TYPE_PARENTHESES_CLOSE_BOX),
    (ACTION_TYPE_PARENTHESES_OPEN_BRACKET, ACTION_TYPE_PARENTHESES_CLOSE_CURVY),
    (ACTION_TYPE_PARENTHESES_OPEN_BOX, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET),
    (ACTION_TYPE_PARENTHESES_OPEN_BOX, ACTION_TYPE_PARENTHESES_CLOSE_CURVY),
    (ACTION_TYPE_PARENTHESES_OPEN_CURVY, ACTION_TYPE_PARENTHESES_CLOSE_BRACKET),
    (ACTION_TYPE_PARENTHESES_OPEN_CURVY, ACTION_TYPE_PARENTHESES_CLOSE_BOX),
}


def _parse_forward_next_action(line, index, length, source_action):
    """
    Parses the next action forward.
    
    Parameters
    ----------
    line : `str`
        The line to parse from.
    index : `int`
        The index to start parsing at.
    length : `int`
        Index to parse till.
    source_action : `int`
        The previous action.
    
    Returns
    -------
    index : `int`
    action : `int`
    """
    if source_action in ACTION_TYPE_STRING_OPEN:
        return _parse_forward_next_string(line, index, length, source_action)
    
    return _parse_forward_next_any(line, index, length)


def _parse_forward_next_string(line, index, length, source_action):
    """
    Parses till the string is ended.
    
    Parameters
    ----------
    line : `str`
        The line to parse from.
    index : `int`
        The index to start parsing at.
    length : `int`
        Index to parse till.
    
    Returns
    -------
    index : `int`
    action : `int`
    """
    if source_action == ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE:
        end_character = '\''
        triple_quited = False
        closer_action = ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE
    elif source_action == ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE:
        end_character = '"'
        triple_quited = False
        closer_action = ACTION_TYPE_STRING_CLOSE_DOUBLE_QUOTE
    elif source_action == ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE:
        end_character = '\''
        triple_quited = True
        closer_action = ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE
    elif source_action == ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE:
        end_character = '"'
        triple_quited = True
        closer_action = ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE
    else:
        end_character = '\''
        triple_quited = False
        closer_action = ACTION_TYPE_STRING_CLOSE_SINGLE_QUOTE
    
    
    while True:
        if index >= length:
            action = ACTION_TYPE_NONE
            break
        
        character = line[index]
        if character == '\\':
            index += 2
            continue
        
        if character == end_character:
            if triple_quited:
                if (
                    (index + 2 < length) and
                    (line[index + 1] == end_character) and
                    (line[index + 2] == end_character)
                ):
                    index += 2
                else:
                    index += 1
                    continue
            
            index += 1
            action = closer_action
            break
        
        index += 1
        continue
    
    return index, action


def _parse_forward_next_any(line, index, length):
    """
    Parses one forward till hits any action.
    
    Parameters
    ----------
    line : `str`
        The line to parse from.
    index : `int`
        The index to start parsing at.
    length : `int`
        Index to parse till.
    
    Returns
    -------
    index : `int`
    action : `int`
    """
    while True:
        if index >= length:
            action = ACTION_TYPE_NONE
            break
        
        character = line[index]
        
        if character == '#':
            action = ACTION_TYPE_NONE
            index = length
            break
        
        if character == '\\':
            action = ACTION_TYPE_LINE_ESCAPE
            index = length
            break
        
        try:
            action = CHARACTER_TO_ACTION[character]
        except KeyError:
            pass
        else:
            index += 1
            break
        
        if character in ('\'', '"'):
            if (
                (index + 2 < length) and
                (line[index + 1] == character) and
                (line[index + 2] == character)
            ):
                index += 2
                
                if character == '\'':
                    action = ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE
                else:
                    action = ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE
                    
            else:
                if character == '\'':
                    action = ACTION_TYPE_STRING_OPEN_SINGLE_QUOTE
                else:
                    action = ACTION_TYPE_STRING_OPEN_DOUBLE_QUOTE
            
            index += 1
            break
  
        index += 1
        continue
    
    return index, action


def _try_parse_triple_quote_from_behind(line, source_action):
    """
    Tries to parse a triple quoted string from behind returning the where it started and whether it was closed.
    
    Parameters
    ----------
    line : `str`
        Line to parse.
    source_action : `int`
        The last action executed.
    
    Returns
    -------
    length : `int`
    action : `int`
    """
    if source_action == ACTION_TYPE_STRING_OPEN_TRIPLE_SINGLE_QUOTE:
        end_character = '\''
        closer_action = ACTION_TYPE_STRING_CLOSE_TRIPLE_SINGLE_QUOTE
    elif source_action == ACTION_TYPE_STRING_OPEN_TRIPLE_DOUBLE_QUOTE:
        end_character = '"'
        closer_action = ACTION_TYPE_STRING_CLOSE_TRIPLE_DOUBLE_QUOTE
    else:
        return len(line), ACTION_TYPE_NONE 
    
    for index in range(2, len(line)):
        if line[index] != end_character:
            continue
        
        if line[index - 1] != end_character:
            continue
        
        if line[index - 2] != end_character:
            continue
        
        if index - 3 >= 0 and line[index - 3] == '\\':
            continue
        
        return index - 2, closer_action
    
    return 0, ACTION_TYPE_NONE


def _normalize_and_dedent(lines):
    """
    Normalises the lines and dedents them.
    
    Parameters
    ----------
    lines : `list<str>`
        The lines to work on.
    """
    if not lines:
        return
    
    for index in range(len(lines)):
        lines[index] = lines[index].rstrip()
    
    indentation_to_remove = -1
    for line in lines:
        if not line:
            continue
        
        count = 0
        for character in line:
            if character not in (' ', '\t'):
                break
            
            count += 1
            continue
        
        if indentation_to_remove == -1:
            indentation_to_remove = count
            continue
        
        if count < indentation_to_remove:
            indentation_to_remove = count
        continue
    
    
    if indentation_to_remove != -1:
        for index in range(len(lines)):
            lines[index] = lines[index][indentation_to_remove:]


def _is_syntax_valid(action_stack):
    """
    Returns whether the syntax looks valid.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to read the syntax from.
    
    Returns
    -------
    is_syntax_valid : `bool`
    """
    if not action_stack:
        return True
    
    for action in action_stack:
        if action in STRING_MUST_BE_PAIRED:
            return False
    
    last_action = action_stack[0]
    for index in range(1, len(action_stack)):
        action = action_stack[index]
        if (last_action, action) in PARENTHESES_INVALID_PAIRS:
            return False
        
        last_action = action
        continue
    
    return True


def _get_action_direction(action_stack, last_direction):
    """
    Gets the direction for the next action.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to pull the last action from.
    last_direction : `int`
        The last direction.
    
    Returns
    -------
    new_direction : `int`
    """
    if last_direction == DIRECTION_FORWARD:
        action = action_stack[-1]
    else:
        action = action_stack[0]
    
    new_direction = ACTION_DIRECTIONS.get(action, DIRECTION_NONE)
    if new_direction == DIRECTION_REPEAT_LAST:
        new_direction = last_direction
    
    return new_direction


def _pop_forward_actions(action_stack):
    """
    Pops every forward action.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to pop from.
    """
    for index in reversed(range(len(action_stack))):
        if ACTION_DIRECTIONS.get(action_stack[index], DIRECTION_NONE) == DIRECTION_FORWARD:
            del action_stack[index - 1:]
            break


def _pop_backward_actions(action_stack):
    """
    Pops every backward action.
    
    Parameters
    ----------
    action_stack : `list<int>`
        Action stack to pop from.
    """
    for index in range(len(action_stack)):
        if ACTION_DIRECTIONS.get(action_stack[index], DIRECTION_NONE) != DIRECTION_BACKWARD:
            del action_stack[: index]
            break


def _merge_actions(action_stack):
    """
    Merges actions as applicable. Also returns the dummy ones.
    
    Parameters
    ----------
    action_stack : `list<int>`
        The action stack to operate on.
    """
    # remove in-middle escapes
    for index in reversed(range(len(action_stack) - 1)):
        if action_stack[index] == ACTION_TYPE_LINE_ESCAPE:
            del action_stack[index]
    
    # remove nulled actions
    for index in reversed(range(len(action_stack))):
        if action_stack[index] in (ACTION_TYPE_NONE, ACTION_FORWARD, ACTION_BACKWARDS):
            del action_stack[index]
    
    if len(action_stack) >= 2:
        # remove continuous strings.
        last_action = action_stack[-1]
        for index in reversed(range(len(action_stack) - 1)):
            action = action_stack[index]
            if (action, last_action) not in STRING_OPEN_CLOSE_PAIRS:
                last_action = action
                continue
            
            del action_stack[index: index + 2]
            last_action = ACTION_TYPE_NONE
            continue
    
    
    # Yeet parsed parentheses repeatedly
    while True:
        if len(action_stack) < 2:
            break
        
        hit_any = False
        
        last_action = action_stack[-1]
        for index in reversed(range(len(action_stack) - 1)):
            action = action_stack[index]
            if (action, last_action) not in PARENTHESES_OPEN_CLOSE_PAIRS:
                last_action = action
                continue
            
            del action_stack[index : index + 2]
            last_action = ACTION_TYPE_NONE
            hit_any = True
            continue
        
        if not hit_any:
            break


def get_expression_lines(file_name, line_index):
    """
    Tries the expression's lines at the given position.
    
    Parameters
    ----------
    file_name : `str`
        The file's name to get the expressions for.
    line_index : `int`
        The line's index in the file.
    
    Returns
    -------
    lines : `list<str>`
    shift : `int`
    syntax_valid : `bool`
    """
    action_stack = [ACTION_FORWARD]
    lines = []
    
    forward_line_index = line_index - 1
    backwards_line_index = line_index
    
    direction = DIRECTION_FORWARD
    syntax_valid = True
    
    while True:
        if not action_stack:
            break
        
        direction = _get_action_direction(action_stack, direction)
        if direction == DIRECTION_NONE:
            break
        
        if direction == DIRECTION_FORWARD:
            hit, line = get_file_line(file_name, forward_line_index + 1)
            if hit:
                forward_line_index += 1
            else:
                _pop_forward_actions(action_stack)
                direction = DIRECTION_BACKWARD
                continue
        else:
            hit, line = get_file_line(file_name, backwards_line_index - 1)
            if hit:
                backwards_line_index -= 1
            else:
                _pop_backward_actions(action_stack)
                direction = DIRECTION_FORWARD
                continue
        
        # Append line
        if direction == DIRECTION_FORWARD:
            lines.append(line)
        else:
            lines.insert(0, line)
        
        # Check max allowed length
        if len(lines) > EXPRESSION_LINE_COUNT_MAX:
            break
        
        # Get last action
        line_action_stack = []
        if direction == DIRECTION_FORWARD:
            action = action_stack[-1]
        else:
            action = action_stack[0]
        
        # Continue
        if DIRECTION_FORWARD:
            length = len(line)
            character_index = 0
            
            while character_index < length:
                character_index, action = _parse_forward_next_action(line, character_index, length, action)
                line_action_stack.append(action)
        else:
            length, action = _try_parse_triple_quote_from_behind(line, action)
            action_stack.insert(0, action)
            action = ACTION_TYPE_NONE
            
            character_index = 0
            
            while character_index < length:
                character_index, action = _parse_forward_next_action(line, character_index, length, action)
                line_action_stack.append(action)
        
        # Add newly parsed actions
        if direction == DIRECTION_FORWARD:
            action_stack.extend(line_action_stack)
        else:
            action_stack[:0] = line_action_stack
        
        _merge_actions(action_stack)
        syntax_valid = _is_syntax_valid(action_stack)
        if not syntax_valid:
            break
        
        continue
    
    _normalize_and_dedent(lines)
    return lines, line_index - backwards_line_index, syntax_valid
