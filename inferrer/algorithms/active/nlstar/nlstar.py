from inferrer.algorithms.active.active_learner import ActiveLearner
from inferrer.oracle.oracle import Oracle
from inferrer.oracle.active_oracle import ActiveOracle
from inferrer.algorithms.active.nlstar.observation_table import ObservationTable
from inferrer.algorithms.active.nlstar.row import Row
from inferrer.automaton import State
from inferrer.automaton.nfa import NFA
from inferrer.logger.logger import Logger
from typing import Set


class NLSTAR(ActiveLearner):
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

    def __init__(self, alphabet: Set[str], oracle: Oracle):
        """
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        """
        super().__init__(alphabet, oracle)

        self._logger = Logger().get_logger()
        self._logger.info('Created Active Learner [NLSTAR] instance with {} oracle'
                          .format('Active' if type(oracle) is ActiveOracle else 'Passive'))

        self._oracle = oracle

        self._logger.info('Initialising the table.')
        self._ot = ObservationTable(self._alphabet, oracle)
        self._hypothesis = None

    def learn(self) -> NFA:
        """
        Infers an initially unknown regular language
        from a minimally adequate Teacher (Oracle).

        :return: The nfa accepting the target language.
        :rtype: NFA
        """
        self._logger.info('Start learning.')
        self._ot.initialize()

        while True:
            closed_info, consistency_info = self._ot.is_closed_and_consistent()

            is_closed, unclosed = closed_info
            is_consistent, sym, suffix = consistency_info

            while not is_closed or not is_consistent:
                if not is_closed:
                    self._close_table(unclosed)

                if not is_consistent:
                    self._make_table_consistent(sym, suffix)

                closed_info, consistency_info = self._ot.is_closed_and_consistent()

                is_closed, unclosed = closed_info
                is_consistent, sym, suffix = consistency_info

            hypothesis = self._build_hypothesis()

            self._logger.info('Submitting equivalence query.')
            answer, satisfied = self._oracle.equivalence_query(hypothesis)

            if satisfied:
                self._logger.info('Oracle happy with our hypothesis.')
                break

            self._logger.info('Oracle return {} as counterexample.'.format(answer))
            self._use_eq(answer)

        return hypothesis

    def _use_eq(self, eq: str):
        """
        When the Oracle is not happy with our
        hypothesis and returns a counterexample,
        this method adds the new suffixes to the
        observation table and updates all the rows.

        :param eq: Counterexample returned
                   by the oracle.
        :type eq: str
        """
        new_suffixes = {eq[i:] for i in range(len(eq) + 1)}

        self._logger.info('Updating table by adding the following suffixes: {}'
                          .format(', '.join(new_suffixes)))

        self._ot.add_new_suffixes(new_suffixes)
        self._ot.update_meta_data()

    def _close_table(self, unclosed_row):
        """
        Attempts to close the observation table
        by adding a new row to the table.
        """
        self._logger.info('Attempting to close the table by adding a new row.')

        self._ot.upper_rows.add(unclosed_row)
        self._ot.lower_rows.remove(unclosed_row)
        self._ot.upper_primes.add(unclosed_row)

        for symbol in self._alphabet:
            new_row = Row(unclosed_row.prefix + symbol)

            self._ot.rows.add(new_row)
            self._ot.lower_rows.add(new_row)
            self._ot.prefix_to_row[new_row.prefix] = new_row

            self._ot.add_columns_to_row(new_row)

        self._ot.update_meta_data()

    def _make_table_consistent(self, sym, suffix):
        """
        Attempts to make the observation table
        consistent by adding a new column (experiment)
        to the table.
        """
        self._logger.info('Attempting to make the table consistent by adding a new column.')

        new_suffix = '{}{}'.format(sym, suffix)
        self._ot.add_suffix(new_suffix)
        self._ot.update_meta_data()

    def _build_hypothesis(self) -> NFA:
        """
        Builds a NFA from the observation table,
        which we will use when making an
        equivalence query to the Oracle.

        :return: The "hypothesis" NFA.
        :rtype: NFA
        """
        self._logger.info('Building NFA from the table.')
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

        return nfa.rename_states()
