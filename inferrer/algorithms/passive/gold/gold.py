from inferrer import utils, automaton
from inferrer.algorithms.passive.passive_learner import PassiveLearner
from inferrer.logger.logger import Logger
from typing import Set, Tuple


class Gold(PassiveLearner):
    """
    An implementation of E. Mark GOLD's algorithm, which tries
    to find the minimum DFA consistent with the sample.
    """

    def __init__(self, pos_examples: Set[str], neg_examples: Set[str], alphabet: Set[str]):
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
        """
        super().__init__(alphabet, pos_examples, neg_examples)

        self._logger = Logger().get_logger()
        self._samples = pos_examples.union(neg_examples)

        self._red = {''}
        self._blue = set()

        self._logger.info('Created Passive Learner [Gold] instance')

    def learn(self) -> automaton.DFA:
        """
        Learns the grammar from the sets of positive and negative
        example strings. This method returns the minimal DFA
        consistent with the sample.

        :return: The minimum DFA consistent with the sample
        :rtype: Automaton
        """
        self._logger.info('Start learning with alphabet = {}\n'
                          'positive samples = {}\n'
                          'negative samples = {}'.format(self._alphabet,
                                                         self._pos_examples,
                                                         self._neg_examples))
        ot = self._build_table()

        od_row, x = ot.obviously_different_row()
        while od_row:
            self._logger.info('Processing obviously different row: {}.'.format(x))
            xa = [x + a for a in self._alphabet]
            ot.sta.update(xa)

            self._blue.update(xa)
            self._blue.discard(x)

            for u in ot.sta:
                for e in ot.exp:
                    ue = u + e
                    if ue in self._pos_examples:
                        ot.put(u, e, 1)
                    elif ue in self._neg_examples:
                        ot.put(u, e, 0)
                    else:
                        ot.put(u, e, None)

            od_row, x = ot.obviously_different_row()

        ot, failed = self._fill_holes(ot)

        if failed:
            self._logger.info('Failed to make table complete.')
            return automaton.build_pta(self._pos_examples, self._neg_examples)
        else:
            self._logger.info('Successfully completed table.')
            a = self._build_automaton(ot)

            if self._is_consistent(a, ot):
                self._logger.info('DFA and table is consistent, returning DFA.')
                return a.remove_dead_states()
            else:
                self._logger.info('DFA and table is not consistent, building PTA from samples.')
                return automaton.build_pta(self._pos_examples, self._neg_examples)

    def _build_table(self) -> utils.ObservationTable:
        """
        Obtains a table from the sample.

        :return: Initial observation table
        :rtype: ObservationTable
        """
        self._logger.info('Building table from sample.')
        sta = {''}

        self._blue = self._alphabet.copy()

        exp = set(utils.suffix_set(self._samples, self._alphabet))

        ot = utils.ObservationTable(self._blue, self._red, self._alphabet)

        for p in self._red.union(self._blue):
            for e in exp:
                pe = p + e
                if pe in self._pos_examples:
                    ot.put(p, e, 1)
                elif pe in self._neg_examples:
                    ot.put(p, e, 0)
                else:
                    ot.put(p, e, None)

            sta.add(p)

        ot.sta = sta
        ot.exp = exp

        return ot

    def _fill_holes(self, ot: utils.ObservationTable) -> Tuple[utils.ObservationTable, bool]:
        """
        Tries to make the table complete by filling in all the entries that
        are None.

        :param ot: the updated observation table
        :return: updated ObservationTable and whether the method was successful.
        :rtype: tuple(ObservationTable, bool)
        """
        self._logger.info('Try to make table complete by filling in * entries.')
        for p in self._blue:
            r = ot.find_compatible_row(p)
            if r is not None:
                for e in ot.exp:
                    if ot.entry_exists(p, e) and ot.get(p, e) is not None:
                        ot.put(r, e, ot.get(p, e))
            else:
                return ot, True

        for r in self._red:
            for e in ot.exp:
                if ot.entry_exists(r, e) and ot.get(r, e) is None:
                    ot.put(r, e, 1)

        for p in self._blue:
            r = ot.find_compatible_row(p)
            if r is not None:
                for e in ot.exp:
                    if ot.entry_exists(p, e) and ot.get(p, e) is None:
                        if ot.entry_exists(r, e):
                            ot.put(p, e, ot.get(r, e))
            else:
                return ot, True

        return ot, False

    def _build_automaton(self, ot: utils.ObservationTable) -> automaton.DFA:
        """
        Builds an automaton from the observation table.

        :type ot: ObservationTable
        :return: Automaton built from the observation table
        :rtype: Automaton
        """
        dfa = automaton.DFA(self._alphabet)

        states = {
            automaton.State(i) for i in self._red
        }

        we = utils.break_strings_in_two(self._red)
        for w, e in we:
            we = w + e
            if we in self._red and ot.entry_exists(w, e):
                val = ot.get(w, e)
                state = automaton.State(we)
                if val == 1:
                    dfa.accept_states.add(state)
                    states.add(state)
                elif val == 0:
                    dfa.reject_states.add(state)
                    states.add(state)

        for w in states:
            for a in self._alphabet:
                for u in self._red:
                    wa = w.name + a
                    if ot.row_exists(u) and ot.row_exists(wa) and \
                            ot.get_row(u) == ot.get_row(wa):
                        dfa.add_transition(w, automaton.State(u), a)

        return dfa

    def _is_consistent(self, dfa: automaton.DFA, ot: utils.ObservationTable) -> bool:
        """
        Determines whether the automaton is consistent with the
        observation table ot.

        :type dfa: Automaton
        :type ot: ObservationTable
        :return: Whether the automaton and observation table are consistent.
        :rtype: bool
        """
        self._logger.info('Determine whether the DFA is consistent with the table.')
        for u, col in ot.ot.items():
            for e, val in col.items():
                ue = automaton.State(u + e)
                if val == 1:
                    if ue not in dfa.accept_states:
                        return False
                elif val == 0:
                    if ue not in dfa.reject_states:
                        return False
        return True
