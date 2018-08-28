from inferrer import automaton
from typing import Set, Tuple


class Oracle:

    def __init__(self, s_plus: Set[str], s_minus: Set[str]):
        """
        An implementation of a minimally adequate teacher (MAT),
        which is an oracle that can give answers to membership
        queries and strong equivalence queries.

        :param s_plus: Set of positive example strings, i.e.
                       strings that belong in the
                       target language.
        :type s_plus: Set[str]
        :param s_minus: Set of negative example strings, i.e.
                        strings that do not belong in the
                        target language.
        :type s_minus: Set[str]
        """
        self._s_plus = s_plus
        self._s_minus = s_minus
        self._marked = set()

    def membership_query(self, s: str) -> int:
        """
        Answers a Membership Query (MQ) made by the learner L*.
        If the given string s is in the target language
        then the Oracle will answer with 1, if s is not in
        the target language then the oracle will answer 0.

        :param s: The membership query string
        :type s: str
        :return: 1 if s is in the target language, else 0
        :rtype: int
        """
        # return len(s) % 2 == 0
        return 1 if s in self._s_plus else 0


    def equivalence_query(self, dfa: automaton.DFA) -> Tuple[str, bool]:
        """
        Answers a Equivalence Query (EQ) made by the learner L*.
        The learner provides the Oracle with some hypothesis.
        The hypothesis is a grammar representing the unknown
        language. The Oracle has to provide the learner L* with
        a counter-example, i.e. a string that does not belong
        in the target language, but is accepted by the
        proposed grammar. If the Oracle is happy with the
        hypothesis, then it tells the learner that it is satisfied
        and the algorithm will converge.

        :param dfa: The 'hypothesis', a dfa representing the
                    unknown language.
        :type dfa: Automaton
        :return: Tuple where the first index is a counter-example
                 and the second index is whether the Oracle is
                 satisfied. If the Oracle is satisfied, then the
                 first index will just be the empty string.
        :rtype: Tuple[str, bool]
        """
        # print('EQ start', len(dfa._states))
        # print(dfa)
        # print(sorted(self._s_plus, reverse=True))
        # if 'aaa' not in self._marked:
        #     self._marked.add('aaa')
        #     return 'aaa', False
        for positive_string in sorted(self._s_plus):
            if positive_string not in self._marked and not dfa.parse_string(positive_string)[1]:
                self._marked.add(positive_string)
                # if positive_string == '1111111':
                # print('X' * 100)
                # print(dfa)
                # print(dfa.parse_string('1111111')[0], ' <<<')
                # print(dfa.parse_string('1111111')[1])
                # print('False - positive string')
                return positive_string, False
        for negative_string in sorted(self._s_minus):
            if negative_string not in self._marked and dfa.parse_string(negative_string)[1]:
                self._marked.add(negative_string)
                # print('False - negative string')
                return negative_string, False
        # print('correct hypothesis')
        return '', True
