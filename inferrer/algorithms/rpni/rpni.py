import functools
from inferrer import utils, automaton
from typing import Set


class RPNI:
    """
    An implementation of the Regular Positive and Negative Inference (RPNI)
    algorithm. This algorithm tries to make sure that some generalisation
    takes place and, in the best case, returns the correct target automaton.
    """

    def __init__(self, pos_examples: Set[str], neg_examples: Set[str]):
        """
        :param pos_examples: Set of positive example strings
                             from the target language
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        """
        self._pos_examples = pos_examples
        self._neg_examples = neg_examples
        self._samples = pos_examples.union(neg_examples)
        self._alphabet = utils.determine_alphabet(self._pos_examples)

        self._red = {automaton.State('')}
        self._blue = set()

    def learn(self) -> automaton.Automaton:
        """
        Learns the grammar from the sets of positive and negative
        example strings. This method returns a DFA that is
        consistent with the sample.

        :return: DFA
        :rtype: Automaton
        """
        dfa = automaton.build_pta(self._pos_examples)

        pref_set = utils.prefix_set(self._pos_examples, self._alphabet)
        self._blue = {automaton.State(i) for i in self._alphabet.intersection(pref_set)}

        while len(self._blue) != 0:
            qb = choose(self._blue)
            self._blue.remove(qb)

            found = False
            for qr in sorted(self._red, key=functools.cmp_to_key(_cmp)):
                if self.compatible(self.merge(dfa.copy(), qr, qb)):
                    dfa = self.merge(dfa, qr, qb)
                    new_blue_states = set()
                    for q in self._red:
                        for a in self._alphabet:
                            if dfa.transition_exists(q, a) and \
                                    dfa.transition(q, a) not in self._red:
                                new_blue_states.add(dfa.transition(q, a))

                    self._blue.update(new_blue_states)
                    found = True

            if not found:
                dfa = self.promote(qb, dfa)

        for s in self._neg_examples:
            q, accepted = dfa.parse_string(s)
            if not accepted:
                dfa.reject_states.add(q)

        return dfa.minimize()

    def promote(self, qu: automaton.State, dfa: automaton.Automaton) -> automaton.Automaton:
        """
        Given a state blue state qu, this method promotes this state
        ro red and all the successors in the dfa. The method returns
        the updated dfa.

        :param qu: State with colour blue
        :type qu: State
        :param dfa: the dfa
        :type dfa: Automaton
        :return: Updated dfa
        :rtype: Automaton
        """
        self._red.add(qu)

        self._blue.update({
            dfa.transition(qu, a) for a in self._alphabet if dfa.transition_exists(qu, a)
        })
        self._blue.discard(qu)

        return dfa

    def compatible(self, dfa: automaton.Automaton) -> bool:
        """
        Determines whether the current automaton can parse any
        string in the set of negative example strings.
        Returns True if the current automaton cannot parse
        any string from the negative examples, returns False
        if some counter-example is accepted by the current
        automaton.

        :param dfa: the dfa
        :type dfa: Automaton
        :return: Boolean indicating whether the dfa is compatible.
        :rtype: bool
        """
        return not any(dfa.parse_string(w)[1] for w in self._neg_examples)

    def merge(self, dfa: automaton.Automaton,
              q: automaton.State,
              q_prime: automaton.State) -> automaton.Automaton:
        """
        Takes as arguments a red state q and a blue state q'.
        The method first finds the unique pair (qf, a) such
        that q' = delta(qf, a).
        The method then redirects delta(qf, a) to q. After that
        the tree rooted in q' is folded into the rest of the DFA.
        The possible intermediate situations of non-determinism
        are dealt with during the recursive calls to fold.

        :param dfa: the automaton to update with a merge
        :type dfa: Automaton
        :param q: State from the red set
        :type q: State
        :param q_prime: State from the blue
        :type q_prime: State
        :return: updated Automaton
        :rtype: Automaton
        """
        qf, a = dfa.find_transition_to_q(q_prime)

        if qf is None or a is None:
            return dfa

        dfa.add_transition(qf, q, a)

        return self.fold(dfa, q, q_prime)

    def fold(self, dfa: automaton.Automaton,
             q: automaton.State,
             q_prime: automaton.State) -> automaton.Automaton:
        """
        Folds the tree rooted in q' into the rest of the DFA. The
        possible intermediate situations of non-determinism
        are dealt with during the recursive calls.

        :param dfa: the automaton to update with a folding of states
        :type dfa: Automaton
        :param q: State
        :type q: State
        :param q_prime: State to fold
        :type q_prime: State
        :return: updated Automaton
        :rtype: Automaton
        """
        if q_prime in dfa.accept_states:
            dfa.accept_states.add(q)

        for a in self._alphabet:
            if dfa.transition_exists(q_prime, a):
                if dfa.transition_exists(q, a):
                    dfa = self.fold(dfa, dfa.transition(q, a),
                                    dfa.transition(q_prime, a))
                else:
                    dfa.add_transition(q, dfa.transition(q_prime, a), a)

        return dfa


def choose(blue: Set[automaton.State]) -> automaton.State:
    """
    A deterministic function that chooses one of the
    elements in the given blue set. It does so by
    choosing the minimal <u, a> in lexicographic order.

    :param blue: Set of blue states
    :type blue: Set[State]
    :return: One of the elements in the given blue set
    :rtype: State
    """
    return min(blue, key=functools.cmp_to_key(_cmp))


def _cmp(q1: automaton.State, q2: automaton.State) -> int:
    """
    Compares two states by comparing the
    name (string value of the state). If the
    two strings have the same length, then the
    two strings are compared lexicographically.

    :param q1: state 1
    :type q1: State
    :param q2: state 2
    :type q2: State
    :return: 1 of a is greater than b, 0 if a
             is equal to b and -1 if a is less
             than b.
    :rtype: int
    """
    if len(q1.name) == len(q2.name):
        if q1.name > q2.name:
            return 1
        elif q1.name < q2.name:
            return -1
        else:
            return 0
    elif len(q1.name) > len(q2.name):
        return 1
    else:
        return -1
