from collections import deque
from inferrer import automaton
from typing import Tuple, List
from inferrer.oracle.oracle import Oracle


class PhaseOracle(Oracle):

    MAX_SELF_LOOP_DEPTH = 10
    MAX_VISIT_DEPTH = 50

    @property
    def curr_phase(self):
        return self.__curr_phase

    def inc_curr_phase(self):
        if self.curr_phase + 1 == len(self._fsas):
            raise ValueError('Phase {} does not exist!'.format(self.curr_phase + 1))
        self._counterexamples.clear()
        self.__curr_phase += 1

    def __init__(self, fsas: Tuple[List[automaton.DFA], List[automaton.State]], final_fsa: automaton.DFA):
        super().__init__()
        self._counterexamples = set()

        if type(final_fsa) is not automaton.DFA or \
                not all(type(f) is automaton.DFA for f in fsas):
            raise ValueError('Phase oracle only works on DFAs')

        self._fsas, self._delim_states = fsas
        assert len(self._fsas) == len(self._delim_states)

        self._fsas = [f.minimize() for f in self._fsas]

        self._final_fsa = final_fsa.minimize()
        self.__curr_phase = 0

    def num_of_phases(self) -> int:
        return len(self._fsas)

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
        return self._final_fsa.parse_string(s)[1]

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
        if type(fsa) is not automaton.DFA:
            raise ValueError('fsa has to be a DFA or NFA!')

        curr_fsa = self._fsas[self.curr_phase]

        if type(fsa) is automaton.DFA and curr_fsa == fsa:
            return '', True

        queue = deque([(curr_fsa._start_state, 0, '')])
        visited = {curr_fsa._start_state : 0}

        while len(queue) > 0:
            state, loop_depth, word = queue.popleft()

            if word not in self._counterexamples:
                expected = curr_fsa.parse_string(word)[1]
                actual = fsa.parse_string(word)[1]

                if expected != actual:
                    self._counterexamples.add(word)
                    return word, False

            trans = curr_fsa._transitions[state]

            for sym, to_state in trans.items():
                if to_state == state and loop_depth < self.MAX_SELF_LOOP_DEPTH and \
                        visited[to_state] < self.MAX_VISIT_DEPTH:
                    queue.append((state,
                                  loop_depth + 1,
                                  '{}{}'.format(word, sym)))

                if to_state not in visited or visited[to_state] < self.MAX_VISIT_DEPTH:
                    if to_state not in visited:
                        visited[to_state] = 0
                    else:
                        visited[to_state] += 1

                    queue.append((to_state,
                                 loop_depth + 1,
                                 '{}{}'.format(word, sym)))

        return '', True
