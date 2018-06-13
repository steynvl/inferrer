import automaton
import utils
import functools


class RPNI:

    def __init__(self, positive_examples: set, negative_examples: set):
        self._positive_examples = positive_examples
        self._negative_examples = negative_examples
        self._samples = positive_examples.union(negative_examples)
        self._alphabet = utils.determine_alphabet(self._samples)

        self._red = {''}
        self._blue = set()

    def learn(self):
        dfa = automaton.build_pta(self._positive_examples)

        pref_set = utils.prefix_set(self._positive_examples, self._alphabet)
        self._blue = self._alphabet.intersection(pref_set)

        while len(self._blue) != 0:
            qb = choose(self._blue)
            self._blue.remove(qb)

            found = False
            for qr in sorted(self._red, key=functools.cmp_to_key(_cmp)):

                if self._compatible(self._merge(dfa.copy(), qr, qb)):
                    dfa = self._merge(dfa, qr, qb)
                    new_blue = set()
                    for q in self._red:
                        for a in self._alphabet:
                            if dfa.transition_exists(q, a) and \
                                    dfa.perform_transition(q, a) not in self._red:
                                new_blue.add(dfa.perform_transition(q, a))

                    self._blue.update(new_blue)
                    found = True

            if not found:
                dfa = self._promote(qb, dfa)

        for s in self._negative_examples:
            q, accepted = dfa.parse_string(s)
            if not accepted:
                dfa.reject_states.add(q)

        return dfa

    def _promote(self, qu,  dfa: automaton.Automaton):
        self._red.add(qu)

        self._blue.update({
            dfa.perform_transition(qu, a) for a in self._alphabet if dfa.transition_exists(qu, a)
        })

        return dfa

    def _compatible(self, dfa: automaton.Automaton):
        for w in self._negative_examples:
            q, accepted = dfa.parse_string(w)

            if q is not None and \
                    len({q}.intersection(dfa.accept_states)) != 0:
                return False

        return True

    def _merge(self, dfa: automaton.Automaton, q, q_prime):
        qf, a = dfa.find_transition_to_q(q_prime)

        if qf is None or a is None:
            return dfa

        dfa.add_transition(qf, q, a)

        return self._fold(dfa, q, q_prime)

    def _fold(self, dfa: automaton.Automaton, q, q_prime):
        if q_prime in dfa.accept_states:
            dfa.accept_states.add(q)

        for a in self._alphabet:
            if dfa.transition_exists(q_prime, a):
                if dfa.transition_exists(q, a):
                    dfa = self._fold(dfa, dfa.perform_transition(q, a),
                                     dfa.perform_transition(q_prime, a))
                else:
                    dfa.add_transition(q, dfa.perform_transition(q_prime, a), a)

        return dfa


def choose(blue: set):
    return sorted(blue, key=functools.cmp_to_key(_cmp))[0]


def _cmp(a: str, b: str):
    if len(a) == len(b):
        if a > b:
            return 1
        elif a < b:
            return -1
        else:
            return 0

    if len(a) > len(b):
        return 1
    else:
        return -1

