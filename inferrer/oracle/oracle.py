import abc
from inferrer import automaton
from typing import Tuple


class Oracle(abc.ABC):

    def __init__(self):
        """
        An abstract representation of a
        minimally adequate teacher (MAT), who knows the
        target language and can answer some queries.
        The oracle can answer two types of queries, membership
        queries asks the oracle whether a string is in the
        target language or not. Equivalence queries is when the
        learner proposes a hypothesis finite state machine (FSA),
        then the oracle has to answer whether the FSA correctly
        represents the target language. If it does not, then the
        oracle returns a counterexample, where the counterexample
        is a string in the symmetric difference between the target
        language and the submitted hypothesis.
        """
        self._marked = set()

    @abc.abstractmethod
    def membership_query(self, s: str) -> bool:
        """
        Answers a Membership Query (MQ) made by the learner L*.
        If the given string s is in the target language
        then the Oracle will answer with True, if s is not in
        the target language then the oracle will answer False.

        :param s: The membership query string
        :type s: str
        :return: True if s is in the target language, else False
        :rtype: bool
        """
        pass

    @abc.abstractmethod
    def equivalence_query(self, fsa: automaton.FSA) -> Tuple[str, bool]:
        """
        Answers an Equivalence Query (EQ) made by the learner.
        The learner provides the Oracle with some hypothesis.
        The hypothesis is a grammar representing the unknown
        language. The Oracle has to provide the learner with
        a counter-example, i.e. a string that does not belong
        in the target language, but is accepted by the
        proposed grammar. If the Oracle is happy with the
        hypothesis, then it tells the learner that it is satisfied
        and the algorithm will converge.

        :param fsa The 'hypothesis', a finite state acceptor
                    representing the unknown language.
        :type fsa: FSA
        :return: Tuple where the first index is a counter-example
                 and the second index is whether the Oracle is
                 satisfied. If the Oracle is satisfied, then the
                 first index will just be the empty string.
        :rtype: Tuple[str, bool]
        """
        pass
