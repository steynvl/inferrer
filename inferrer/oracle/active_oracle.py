from inferrer import automaton
from typing import Tuple
from inferrer.oracle.oracle import Oracle


class ActiveOracle(Oracle):

    def __init__(self, fsa: automaton.FSA):
        """
        An implementation of a passive oracle. The oracle only
        has access to two sets. A set of positive example strings
        and a set of negative strings. It answers membership
        queries and equivalence queries based of these two sets.
        :param fsa:
        :type fsa: FSA
        """
        super().__init__()
        self._fsa = fsa

    def membership_query(self, s: str) -> bool:
        """
        Answers a Membership Query (MQ) made by the learner.
        If the given string s is in the set of positive example
        strings then the Oracle will answer with True, if s is not
        in the set of negative example strings then the oracle will
        answer False.

        :param s: The membership query string
        :type s: str
        :return: True if s is in the set of positive
                 example strings, else False
        :rtype: bool
        """
        return self._fsa.parse_string(s)[1]

    def equivalence_query(self, fsa: automaton.FSA) -> Tuple[str, bool]:
        """
        Answers a Equivalence Query (EQ) made by the learner.
        The learner provides the Oracle with some hypothesis.
        The hypothesis is a grammar representing the unknown
        language. The Oracle has to provide the learner with
        a counter-example, i.e. a string that does not belong
        in the target language, but is accepted by the
        proposed grammar. If the Oracle is happy with the
        hypothesis, then it tells the learner that it is satisfied
        and the algorithm will converge.

        :param fsa: The 'hypothesis', a finite state acceptor
                    representing the unknown language.
        :type fsa: FSA
        :return: Tuple where the first index is a counter-example
                 and the second index is whether the Oracle is
                 satisfied. If the Oracle is satisfied, then the
                 first index will just be the empty string.
        :rtype: Tuple[str, bool]
        """
        # TODO
        return '', True
