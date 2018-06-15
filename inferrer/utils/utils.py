"""
Module containing utility functions such as
performing operations on strings and combinatorics
on sets.
"""

import itertools
from typing import Set, Generator, Tuple


def prefix_set(s: Set[str], alphabet: Set[str]=None) -> Generator[str]:
    """
    Calculates the prefix set of the set s given the
    alphabet.

    :param s: The set fo calculate the prefix set on
    :type s: Set[str]
    :param alphabet: Alphabet of the regular language
    :type alphabet: set
    :return: Generator with all the prefixes
    :rtype: Generator[str]
    """
    return _generate_set(s, alphabet, str.startswith)


def suffix_set(s: Set[str], alphabet: Set[str]=None) -> Generator[str]:
    """
    Calculates the suffix set of the set s given the
    alphabet.

    :param s: The set fo calculate the suffix set on
    :type s: set
    :param alphabet: Alphabet of the regular language
    :type alphabet: set
    :return: Generator with all the suffixes
    :rtype: Generator[str]
    """
    return _generate_set(s, alphabet, str.endswith)


def determine_alphabet(s: Set[str]) -> Set[str]:
    """
    Calculates the alphabet (Sigma) of the target
    regular language.

    :param s: Set containing positive and negative
              example strings of the target regular
              language.
    :type s: Set[str]
    :return: Set containing the unique alphabet of the
             regular language.
    :rtype: Set[str]
    """
    return set(''.join(s))


def break_strings_in_two(s: str) -> Set[Tuple[str, str]]:
    """
    Calculates all combinations of the string
    split into two parts.

    :param s: string to break in two
    :type s: str
    :return: Set of all combinations
    :rtype: Set[Tuple[str, str]]
    """
    combs = set()
    for r in s:
        if len(r) == 0:
            combs.add(('', ''))
        elif len(r) == 1:
            combs.update({('', r), (r, '')})
        else:
            combs.update({('', r), (r, '')})
            combs.update({(r[:i], r[i:]) for i in range(len(r))})
    return combs


def _get_all_combinations(s: set, repeat: int) -> Generator[str]:
    for rep in range(repeat + 1):
        for p in itertools.product(s, repeat=rep):
            yield ''.join(p)


def _generate_set(s, alphabet, func) -> Generator[str]:
    if alphabet is None:
        alphabet = determine_alphabet(s)

    longest = len(max(s, key=len))
    for comb in _get_all_combinations(alphabet, longest):
        if any([func(i, comb) for i in s]):
            yield comb
