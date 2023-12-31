__all__ = ()


def get_repeat_with_strategy_top(items):
    """
    Gets the top-most repeat on the given items.
    
    Parameters
    ----------
    items : `None | list`
        Items to get repeated part of.
    
    Returns
    -------
    repeat : `None | (int, int, int)`
        On detected repeat returns a tuple of `3` elements:
        - `start_shift` How much is the first element shifted
        - `chunk_size` How big 1 repeated chunk is.
        - `repeat` How much times was the chunk repeated.
    """
    if items is None:
        return
    
    items_length = len(items)
    for chunk_size in range(1, (items_length >> 1) + 1):
        for start_shift in range(0, items_length - chunk_size - 1):
            repeat = 0
            for additional_element_index in range(start_shift + chunk_size, items_length - chunk_size + 1, chunk_size):
                for shift in range(0, chunk_size):
                    if not (items[start_shift + shift] % items[additional_element_index + shift]):
                        break
                else:
                    repeat += 1
                    continue
                break
            
            if repeat * chunk_size >= 2:
                return start_shift, chunk_size, repeat + 1


def get_repeat_with_strategy_bot(items):
    """
    Gets the bot-most repeat on the given items.
    
    Parameters
    ----------
    items : `None | list`
        Items to get repeated part of.
    
    Returns
    -------
    repeat : `None | (int, int, int)`
        On detected repeat returns a tuple of `3` elements:
        - `start_shift` How much is the first element shifted
        - `chunk_size` How big 1 repeated chunk is.
        - `repeat` How much times was the chunk repeated.
    """
    if items is None:
        return
    
    items_length = len(items)
    for chunk_size in range(1, (items_length >> 1) + 1):
        for start_shift in range(items_length - chunk_size, chunk_size - 1, -1):
            repeat = 0
            for additional_element_index in range(start_shift - chunk_size, -1, -chunk_size):
                for shift in range(0, chunk_size):
                    if not (items[start_shift + shift] == items[additional_element_index + shift]):
                        break
                else:
                    repeat += 1
                    continue
                break
            
            if repeat * chunk_size >= 2:
                return start_shift - (chunk_size * repeat), chunk_size, repeat + 1
