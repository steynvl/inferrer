import abc
from inferrer import automaton
from typing import Set, Tuple


class FSA(abc.ABC):
    """
    Represents a finite state acceptor that
    accepts or rejects strings of the given
    alphabet.

    The two known implementations of this
    abstract class is dfa.py and nfa.py.
    """
    def __init__(self, alphabet: Set[str]):
        if '' in alphabet:
            raise ValueError('The empty string is not allowed in the alphabet!')
        self.__alphabet = alphabet

    @property
    def alphabet(self):
        return self.__alphabet

    @abc.abstractmethod
    def parse_string(self, s: str) -> Tuple[automaton.State, bool]:
        """
        Parses each character of the input string through
        the finite state acceptor.

        :param s: The string to parse (s element of alphabet*)
        :type s: str
        :return: The state after reading the string s and whether
                 the fsa accepted the input string.
        :rtype: tuple(State, bool)
        """
        pass
