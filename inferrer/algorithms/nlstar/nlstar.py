from inferrer.algorithms.algorithm import Algorithm
from inferrer.algorithms.lstar.oracle import Oracle
from inferrer.algorithms.nlstar.observation_table import ObservationTable
from inferrer.algorithms.nlstar.row import Row
from inferrer.automaton import State
from inferrer.automaton.nfa import NFA
from typing import Set


class NLSTAR(Algorithm):
    """
    An implementation of the NL* algorithm, which extends
    Angluin-Style learning to the learning of an NFA.

    The general idea of NL* is to:
    Find a consistent observation table (representing a RFSA).
    Submit is as an equivalence query.
    Use the counter-example to update the table.
    Submit membership queries to make the table closed and complete.
    Iterate until the Oracle tells us the correct language has been
    reached.
    """

    def __init__(self, pos_examples: Set[str],
                 neg_examples: Set[str],
                 alphabet: Set[str],
                 oracle: Oracle):
        """
        :param pos_examples: Set of positive example strings
                             from the target language
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        """
        super().__init__(pos_examples, neg_examples, alphabet)
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

            self._use_eq(answer)

        return self._build_hypothesis()

    def _use_eq(self, eq):
        new_experiments = {eq[:i] for i in range(len(eq) + 1)}
        self._ot.add_new_suffixes(new_experiments)
        self._ot.update_meta_data()

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

        for u in self._ot.rows:
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
