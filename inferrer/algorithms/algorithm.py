import abc
from inferrer import automaton
from typing import Set


class Algorithm(abc.ABC):

    def __init__(self, alphabet: Set[str]):
        """
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        """
        self._alphabet = alphabet

    @abc.abstractmethod
    def learn(self) -> automaton.FSA:
        """
        Attempts to learn the grammar of the target
        regular language by using the sets of positive
        and negative example strings. The method returns
        a DFA that is consistent with the sample.
        Known implementations are:
        Gold
        RPNI
        Angluin Learning (L*)
        NL*

        :return: DFA consistent with the sample.
        :rtype: Automaton
        """
        pass
