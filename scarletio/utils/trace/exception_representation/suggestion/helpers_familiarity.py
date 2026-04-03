__all__ = ()

from ....multi_value_dictionary import MultiValueDictionary

from difflib import SequenceMatcher
from heapq import nlargest as get_n_largest
from itertools import permutations as permutate


SUGGESTIONS_MAX = 25


def _split_part_by_numbers(part):
    """
    Splits the given string part by numbers.
    
    This function is an iterable generator.
    
    Examples
    --------
    ```py
    325 -> 325
    koishi -> koishi
    koishi3 -> koishi, 3
    3koishi -> 3, koishi
    46koishi12satori -> 46, satori, 12, satori
    ```
    
    Parameters
    ----------
    part : `str`
        String part.
    
    Yields
    ------
    part : `str`
    """
    previous_characters = []
    
    for character in part:
        if previous_characters and previous_characters[-1].isnumeric() != character.isnumeric():
            yield ''.join(previous_characters)
            previous_characters.clear()
        
        previous_characters.append(character)
        continue
    
    if previous_characters:
        yield ''.join(previous_characters)


def _split_part_by_casing(part):
    """
    Splits the given string parts by casing.
    
    This function is an iterable generator.
    
    Examples
    --------
    ```py
    koishi -> koishi
    KOISHI -> KOISHI
    Koishi -> Koishi
    koishiSatori -> koishi, Satori
    KOISHISatori -> KOISHI, Satori
    koishiSATORI -> koishi, SATORI
    KOISHIsatori -> KOISH, Isatori # There is a limit how much we can do
    ```
    
    Parameters
    ----------
    part : `str`
        String part.
    
    Yields
    ------
    part : `str`
    """
    previous_characters = []
    
    for character in part:
        if previous_characters:
            if character.isupper():
                if not previous_characters[-1].isupper():
                    yield ''.join(previous_characters)
                    previous_characters.clear()
            
            else:
                if previous_characters[-1].isupper() and len(previous_characters) > 1:
                    yield ''.join(previous_characters[:-1])
                    del previous_characters[:-1]
        
        previous_characters.append(character)
        continue
    
    if previous_characters:
        yield ''.join(previous_characters)


def _iter_split_name_to_words(name):
    """
    Splits the given name to words.
    
    This function is an iterable generator.
    
    Examples
    --------
    ```py
    koishi_satori_69 -> koishi, satori, 69
    KoishiSatori69 -> Koishi, Satori, 69
    KOISHI_SATORI_69 -> KOISHI, Satori, 69
    KOISHISATORI69 -> KOISHISATORI, 69 # there is a limit how much we can do
    ```
    
    Parameters
    ----------
    name : `str`
        The name to split.
    
    Yields
    ------
    word : `str`
    """
    for part in name.split('_'):
        if part:
            for part in _split_part_by_numbers(part):
                yield from _split_part_by_casing(part)


def _normalize_name(name):
    """
    Normalize the given name.
    
    Parameters
    ----------
    name : `str`
        The name to normalize.
    
    Returns
    -------
    name : `str`
    """
    return '_'.join([word.casefold() for word in _iter_split_name_to_words(name)])


def _iter_name_aliases(name):
    """
    Alters the given `name`.
    
    This function is an iterable generator.
    
    Parameters
    ----------
    name : `str`
        The name to alter.
    
    Yields
    ------
    alternative_name : `str`
    """
    words = [*_iter_split_name_to_words(name)]
    for permutation in permutate(words, len(words)):
        yield '_'.join([word.casefold() for word in permutation])


def _get_familiar_names(names, name):
    """
    Gets suggestions for the given name.
    
    Parameters
    ----------
    names : `set<str>`
        Names to get suggestions from.
    name : `str`
        Name to get suggestions for.
    
    Returns
    -------
    suggestions : `list<str>`
    """
    name_aliases = [*_iter_name_aliases(name)]
    names_map = MultiValueDictionary((_normalize_name(name), name) for name in names)
    
    sequence_matcher = SequenceMatcher()
    
    matches = {}
    
    for name in name_aliases:
        required_match_level = 0.8 - (20 - min(len(name), 20)) * 0.01
        sequence_matcher.set_seq2(name)
        
        for name in names_map.keys():
            sequence_matcher.set_seq1(name)
            if sequence_matcher.real_quick_ratio() < required_match_level:
                continue
            
            if sequence_matcher.quick_ratio() < required_match_level:
                continue
            
            ratio = sequence_matcher.ratio()
            if ratio < required_match_level:
                continue
            
            # If the same name shows up twice, use the highest available ratio.
            matches[name] = max(ratio, matches.get(name, 0.0))
    
    # Pull suggestions
    suggestions = []
    for match in get_n_largest(SUGGESTIONS_MAX, [(ratio, name) for name, ratio in matches.items()]):
        matches = names_map.get_all(match[1])
        matches.sort()
        suggestions.extend(matches)
    
    return suggestions
