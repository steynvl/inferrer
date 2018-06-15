"""
Module containing utility functions such as
performing operations on strings and combinatorics
on sets.
"""

import itertools
from typing import Set, Generator, Tuple, Callable


def prefix_set(s: Set[str], alphabet: Set[str]=None) -> Generator:
    """
    Calculates the prefix set of the set s given the
    alphabet.

    >>> s = {'aaa', 'bbb', 'aba'}
    >>> print(' '.join(prefix_set(s)))
     b a bb ab aa bbb aba aaa

    :param s: The set fo calculate the prefix set on
    :type s: set
    :param alphabet: Alphabet of the regular language
    :type alphabet: set
    :return: Generator with all the prefixes
    :rtype: Generator[str]
    """
    return _generate_set(s, alphabet, str.startswith)


def suffix_set(s: Set[str], alphabet: Set[str]=None) -> Generator:
    """
    Calculates the suffix set of the set s given the
    alphabet.

    >>> s = {'aaa', 'bbb', 'aba'}
    >>> print(' '.join(prefix_set(s)))
     a b aa ba bb aaa aba bbb

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

    >>> s = {'abc', 'cba', 'bca', 'a', 'b', 'c', 'aa', 'bb', 'cc', 'd'}
    >>> print(determine_alphabet(s))
    {'b', 'd', 'c', 'a'}

    :param s: Set containing positive and negative
              example strings of the target regular
              language.
    :type s: Set[str]
    :return: Set containing the unique alphabet of the
             regular language.
    :rtype: Set[str]
    """
    return set(''.join(s))


def break_strings_in_two(red: Set[str]) -> Set[Tuple[str, str]]:
    """
    Calculates all possible combinations of splitting a
    string in two parts. Performs this operation on every
    element in the set red and returns a set containing all
    these different combinations.

    >>> s = {'abcd'}
    >>> print(break_strings_in_two(s))
    {('', 'abcd'), ('abcd', ''), ('a', 'bcd'), ('abc', 'd'), ('ab', 'cd')}

    :param red: Set with strings to break up
    :type red: Set[str]
    :return: Set containing all possible combinations.
    :rtype: Set[Tuple[str, str]]
    """
    we = set()
    for r in red:
        if len(r) == 0:
            we.add(('', ''))
        elif len(r) == 1:
            we.update({('', r), (r, '')})
        else:
            we.update({('', r), (r, '')})
            we.update({(r[:i], r[i:]) for i in range(len(r))})
    return we


def _get_all_combinations(s: Set[str], repeat: int) -> Generator:
    for rep in range(repeat + 1):
        for p in itertools.product(s, repeat=rep):
            yield ''.join(p)


def _generate_set(s: Set[str], alphabet: Set[str], func: Callable) -> Generator:
    if alphabet is None:
        alphabet = determine_alphabet(s)

    longest = len(max(s, key=len))
    for comb in _get_all_combinations(alphabet, longest):
        if any([func(i, comb) for i in s]):
            yield comb
