import abc
from inferrer import automaton
from typing import Set


class Algorithm(abc.ABC):

    def __init__(self, pos_examples: Set[str], neg_examples: Set[str], alphabet: Set[str]):
        """
        :param pos_examples: Set of positive example strings
                             from the target language.
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        """
        self._pos_examples = pos_examples
        self._neg_examples = neg_examples
        self._alphabet = alphabet

    @abc.abstractmethod
    def learn(self) -> automaton.DFA:
        """
        Attempts to learn the grammar of the target
        regular language by using the sets of positive
        and negative example strings. The method returns
        a DFA that is consistent with the sample.
        Known implementations are:
        Gold
        RPNI
        Angluin Learning (L*)

        :return: DFA consistent with the sample.
        :rtype: Automaton
        """
        pass
