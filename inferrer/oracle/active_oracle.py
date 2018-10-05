from collections import deque
from inferrer import automaton
from typing import Tuple
from inferrer.oracle.oracle import Oracle


class ActiveOracle(Oracle):

    MAX_SELF_LOOP_DEPTH = 10
    MAX_VISIT_DEPTH = 50

    def __init__(self, fsa: automaton.FSA):
        """
        An implementation of a active oracle. The oracle only
        has access to two sets. A set of positive example strings
        and a set of negative strings. It answers membership
        queries and equivalence queries based of these two sets.
        :param fsa:
        :type fsa: FSA
        """
        super().__init__()
        self._counterexamples = set()

        if type(fsa) is automaton.NFA:
            self._fsa = fsa.to_dfa().minimize()
        elif type(fsa) is automaton.DFA:
            self._fsa = fsa.minimize()
        else:
            raise ValueError('fsa has to be a DFA or NFA!')

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
        if type(fsa) is not automaton.NFA and type(fsa) is not automaton.DFA:
            raise ValueError('fsa has to be a DFA or NFA!')

        if type(fsa) is automaton.DFA and self._fsa == fsa:
            return '', True
        # elif type(fsa) is automaton.NFA and \
        #         self._fsa == fsa.to_dfa():
        #     return '', True

        queue = deque([(self._fsa._start_state, 0, '')])
        visited = {self._fsa._start_state : 0}

        while len(queue) > 0:
            state, loop_depth, word = queue.popleft()

            if word not in self._counterexamples:
                expected = self._fsa.parse_string(word)[1]
                actual = fsa.parse_string(word)[1]

                if expected != actual:
                    self._counterexamples.add(word)
                    return word, False

            trans = self._fsa._transitions[state]

            for sym, to_state in trans.items():
                if to_state == state and loop_depth < ActiveOracle.MAX_SELF_LOOP_DEPTH and \
                        visited[to_state] < ActiveOracle.MAX_VISIT_DEPTH:
                    queue.append((state,
                                  loop_depth + 1,
                                  '{}{}'.format(word, sym)))

                if to_state not in visited or visited[to_state] < ActiveOracle.MAX_VISIT_DEPTH:
                    if to_state not in visited:
                        visited[to_state] = 0
                    else:
                        visited[to_state] += 1

                    queue.append((to_state,
                                 loop_depth + 1,
                                 '{}{}'.format(word, sym)))

        return '', True
