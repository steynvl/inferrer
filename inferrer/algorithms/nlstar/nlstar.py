from inferrer.algorithms.lstar.oracle import Oracle
from typing import Set

from inferrer.algorithms.nlstar.observation_table import ObservationTable
from inferrer.algorithms.nlstar.row import Row
from inferrer.automaton import State
from inferrer.automaton.nfa import NFA


class NLSTAR:

    def __init__(self, alphabet: Set[str], oracle: Oracle):
        self._alphabet = alphabet
        self._oracle = oracle

        self._ot = ObservationTable(self._alphabet, oracle)
        self._hypothesis = None

    def learn(self):
        self._ot.initialize()

        while True:
            is_closed, is_consistent = self._ot.is_closed_and_consistent()
            while not is_closed or not is_consistent:
                if not is_closed:
                    self._close_table()

                if not is_consistent:
                    self._make_table_consistent()

                is_closed, is_consistent = self._ot.is_closed_and_consistent()

            nfa = self._build_hypothesis()
            answer, satisfied = self._oracle.equivalence_query(nfa)

            if satisfied:
                break

            new_expiriments = set()
            for i in range(len(answer)):
                new_expiriments.add(answer[:i])
            new_expiriments.add(answer)
            print(new_expiriments)

            self._ot.add_new_suffixes(new_expiriments)
            self._ot.update_meta_data()

        return self._build_hypothesis()

    def _close_table(self):
        for row in self._ot.upper_rows:
            for a in self._alphabet:
                ua = self._ot.get_row_by_prefix(row.prefix + a)

                if ua in self._ot.primes and ua not in self._ot.upper_primes:
                    self._ot.upper_rows.add(ua)
                    self._ot.lower_rows.remove(ua)
                    self._ot.upper_primes.add(ua)

                    for symbol in self._alphabet:
                        new_row = Row(ua.prefix + symbol)
                        self._ot.rows.add(new_row)
                        self._ot.lower_rows.add(new_row)

                        self._ot.add_columns_to_row(new_row)

                    self._ot.update_meta_data()
                    return

    def _make_table_consistent(self):
        for r1 in self._ot.upper_rows:
            for r2 in r1.covered_rows(self._ot.upper_rows):
                for a in self._alphabet:
                    for v in self._ot.suffixes:
                        u_prime = Row(r1 + a)
                        u = Row(r2 + a)

                        if not u.columns[v] and u_prime.columns[v]:
                            new_suffixes = {sym + v for sym in self._alphabet}

                            self._ot.add_new_suffixes(new_suffixes)
                            self._ot.update_meta_data()

    def _build_hypothesis(self) -> NFA:
        nfa = NFA(self._alphabet)
        epsilon_row = self._ot.get_epsilon_row()

        for row in self._ot.upper_primes:
            state = State(row.prefix)
            nfa.add_state(state)

            if row.covered_by(epsilon_row):
                nfa.add_start_state(state)

            if row.columns['']:
                nfa.add_accepting_state(state)

        for u in self._ot.upper_rows:
            state = State(u.prefix)
            if state not in nfa.get_states():
                continue

            for a in self._alphabet:
                ua_row = self._ot.get_row_by_prefix(u.prefix + a)

                if ua_row is None:
                    continue

                for r in nfa.get_states():
                    row = self._ot.get_row_by_prefix(r.name)
                    if row.covered_by(ua_row):
                        nfa.add_transition(state, r, a)

        return nfa


if __name__ == '__main__':
    # ot = ObservationTable({'a', 'b'}, Oracle(set(), set()))
    # row1 = Row('')
    # row2 = Row('a')
    # row3 = Row('ab')
    # row4 = Row('abb')
    # row5 = Row('b')
    # row6 = Row('aa')
    #
    # row7 = Row('aba')
    # row8 = Row('abbb')
    # row9 = Row('abba')
    #
    # ot.suffixes = {'', 'aaa', 'aa', 'a'}
    #
    # ot.rows = {row1, row2, row3, row4, row5, row6, row7, row8, row9}
    #
    # ot.upper_rows = {row1, row2, row3, row4}
    # ot.lower_rows = {row5, row6, row7, row8, row9}
    #
    # ot.primes = {row1, row2, row3, row4, row5, row8, row9}
    # ot.upper_primes = {row1, row2, row3, row4}
    #
    # row1.columns = { '': 0, 'aaa': 1, 'aa': 0, 'a': 0 }
    # row2.columns = { '': 0, 'aaa': 1, 'aa': 1, 'a': 0 }
    #
    # row3.columns = { '': 0, 'aaa': 1, 'aa': 0, 'a': 1 }
    # row4.columns = { '': 1, 'aaa': 1, 'aa': 0, 'a': 0 }
    #
    # row5.columns = { '': 0, 'aaa': 1, 'aa': 0, 'a': 0 }
    # row6.columns = { '': 0, 'aaa': 1, 'aa': 1, 'a': 1 }
    # row7.columns = { '': 1, 'aaa': 1, 'aa': 1, 'a': 0 }
    # row8.columns = { '': 0, 'aaa': 1, 'aa': 0, 'a': 0 }
    # row9.columns = { '': 0, 'aaa': 1, 'aa': 1, 'a': 0 }

    # ot = ObservationTable({'a', 'b'}, Oracle(set(), set()))
    # row1 = Row('')
    # row2 = Row('a')
    # row3 = Row('ab')
    # row4 = Row('b')
    # row5 = Row('aa')
    # row6 = Row('abb')
    # row7 = Row('aba')
    #
    # ot.suffixes = {'', 'aaa', 'aa', 'a'}
    #
    # ot.rows = {row1, row2, row3, row4, row5, row6, row7}
    #
    # ot.upper_rows = {row1, row2, row3}
    # ot.lower_rows = {row4, row5, row6, row7}
    #
    # ot.primes = {row1, row2, row3, row4, row6}
    # ot.upper_primes = {row1, row2, row3}
    #
    # row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
    # row2.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}
    #
    # row3.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 1}
    # row4.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
    #
    # row5.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 1}
    # row6.columns = {'': 1, 'aaa': 1, 'aa': 0, 'a': 0}
    # row7.columns = {'': 1, 'aaa': 1, 'aa': 1, 'a': 0}

    # ot.update_meta_data()
    #
    # nlstar = NLSTAR({'a', 'b'}, Oracle(set(), set()))
    #
    # nlstar._ot = ot
    # print(nlstar._build_hypothesis())
    #
    # print(len(nlstar._ot.primes))
    #
    # for prime in nlstar._ot.primes:
    #     print(prime.prefix)
    #
    # composed_rows = ot.primes.symmetric_difference(ot.rows)
    #
    # print('----')
    # print(len(composed_rows))
    # for composed in composed_rows:
    #     print(composed)

    import random
    random.seed(10012)
    s_plus = set()
    s_minus = set()

    for i in range(1, 21, 2):
        s_plus.add('a' * i)
        s_minus.add('a' * (i - 1))

    oracle = Oracle(s_plus, s_minus)

    nlstar = NLSTAR({'a'}, oracle)
    dfa = nlstar.learn()

    print(dfa)