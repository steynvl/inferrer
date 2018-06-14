import functools
import copy
from inferrer import utils, automaton
from inferrer.algorithms.lstar.oracle import Oracle


class LSTAR:

    def __init__(self, oracle: Oracle, alphabet: set):
        self._oracle = oracle
        self._alphabet = alphabet
        self._red = set()
        self._blue = set()

    def learn(self):
        sta, exp, ot = self._initialise()

        while True:
            is_closed, is_consistent = ot.is_closed_and_consistent()
            while not is_closed or not is_consistent:
                if not is_closed:
                    ot = self._close(ot)

                if not is_consistent:
                    ot = self._consistent(exp, ot)

                is_closed, is_consistent = ot.is_closed_and_consistent()

            answer, satisfied = self._oracle.equivalence_query()

            if satisfied:
                break

            ot = self._useq(exp, ot, answer)

        return self._build_automaton(ot)

    def _initialise(self):
        self._red = {''}
        self._blue = copy.deepcopy(self._alphabet)

        sta = self._red.union(self._blue)
        exp = {''}

        ot = utils.ObservationTable(self._blue, self._red, self._alphabet)

        ot.put('', '', self._oracle.membership_query(''))
        for a in self._alphabet:
            ot.put(a, '', self._oracle.membership_query(a))

        return sta, exp, ot

    def _close(self, ot: utils.ObservationTable):
        _blue = choose(self._blue)
        for s in _blue:
            if not all([ot.get_row(s) != ot.get_row(u) for u in self._red]):
                continue

            self._red.add(s)
            self._blue.remove(s)

            self._blue.update({s + a for a in self._alphabet})

            ot.add_column_to_table(s)

            for u, e in ot.find_holes():
                ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _consistent(self, exp: set, ot: utils.ObservationTable):
        s1, s2, a, e = self._find_inconsistent(exp, ot)

        exp.union(a + e)
        ot.add_column_to_table(a + e)

        for u, e in ot.find_holes():
            ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _find_inconsistent(self, exp: set, ot: utils.ObservationTable):
        for s1 in self._red:
            for s2 in self._red:
                if s1 == s2:
                    continue
                for a in self._alphabet:
                    for e in exp:
                        if ot.get_row(s1) == ot.get_row(s2) and \
                                ot.get(s1 + a, e) != ot.get(s2 + a, e):
                            return s1, s2, a, e

    def _useq(self, exp, ot: utils.ObservationTable, answer: str):
        prefix_set = set(utils.prefix_set({answer}, self._alphabet))

        for p in prefix_set:

            if p not in self._red:
                ot.add_row(p)
                self._red.add(p)
                self._blue.discard(p)

            for a in self._alphabet:
                pa = p + a
                if pa not in prefix_set:
                    if pa not in self._blue:
                        ot.add_row(pa)
                        self._blue.add(pa)
                        self._red.discard(pa)

        for u, e in ot.find_holes():
            ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _build_automaton(self, ot: utils.ObservationTable):
        dfa = automaton.Automaton(self._alphabet)

        for u in self._red:
            for v in ot.get_observation_table().keys():
                if u == v:
                    continue

                if len(v) < len(u) and ot.get_row(v) != ot.get_row(u):
                    dfa.states.add(u)

        for u in dfa.states:
            if ot.entry_exists(u, ''):
                if ot.get(u, '') == 1:
                    dfa.accept_states.add(u)
                elif ot.get(u, '') == 0:
                    dfa.reject_states.add(u)

            for a in self._alphabet:
                for w in dfa.states:
                    if w == u:
                        continue
                    if ot.get_row(u + a) == ot.get_row(w):
                        dfa.add_transition(u, w, a)

        return dfa


def choose(blue: set):
    return sorted(blue, key=functools.cmp_to_key(_cmp))


def _cmp(a: str, b: str):
    if len(a) == len(b):
        if a < b:
            return 1
        elif a > b:
            return -1
        else:
            return 0

    if len(a) > len(b):
        return 1
    else:
        return -1


if __name__ == '__main__':
    pos = {'', 'a', 'b', 'bb', 'abb', 'bba', 'bbb'}
    neg = {'aa', 'bab'}
    oracle = Oracle(pos, neg)

    lstar = LSTAR(oracle, utils.determine_alphabet(pos.union(neg)))
    dfa = lstar.learn()

