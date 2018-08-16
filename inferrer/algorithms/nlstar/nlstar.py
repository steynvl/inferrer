from inferrer.algorithms.lstar.oracle import Oracle
from typing import Set

from inferrer.algorithms.nlstar.observation_table import ObservationTable
from inferrer.algorithms.nlstar.row import Row


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

            while not is_closed and not is_consistent:

                if not is_closed:
                    self._close_table()

                if not is_consistent:
                    self._make_table_consistent()

                is_closed, is_consistent = self._ot.is_closed_and_consistent()

            # dfa = self._build_automaton(ot)
            # answer, satisfied = self._oracle.equivalence_query(dfa)
            #
            # if satisfied:
            #     break
            #
            # ot = self._useq(ot, answer)

    def _close_table(self):
        for row in self._ot.upper_rows:
            for a in self._alphabet:
                ua = Row(row.prefix + a)

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
