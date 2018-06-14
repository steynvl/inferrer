from inferrer import utils, automaton


class Gold:

    def __init__(self, pos_examples: set, neg_examples: set):
        """
        An implementation of E. Mark GOLD's algorithm, which tries
        to find the minimum DFA consistent with the sample.

        :param pos_examples: Set of positive example strings
                             from the target language
        :param neg_examples: Set of negative example strings,
                             i.e strings that do not belong in
                             the target language.
        """
        self._pos_examples = pos_examples
        self._neg_examples = neg_examples
        self._samples = pos_examples.union(neg_examples)
        self._alphabet = utils.determine_alphabet(self._samples)

        self._red = {''}
        self._blue = set()

    def learn(self) -> automaton.Automaton:
        """
        Learns the grammar from the sets of positive and negative
        example strings. This method returns the minimal DFA
        consistent with the sample.

        :return: The minimum DFA consistent with the sample
        :rtype: Automaton
        """
        ot = self._build_table()

        od_row, x = ot.obviously_different_row()
        while od_row:
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
            return automaton.build_pta(self._pos_examples, self._neg_examples)
        else:
            a = self._build_automaton(ot)

            if self._is_consistent(a, ot):
                return a
            else:
                return automaton.build_pta(self._pos_examples, self._neg_examples)

    def _build_table(self) -> utils.ObservationTable:
        """
        Obtains a table from the sample.

        :return: Initial observation table
        :rtype: ObservationTable
        """
        sta = {''}

        self._blue = self._alphabet.copy()

        exp = set(utils.suffix_set(self._samples, self._alphabet))

        ot = utils.ObservationTable(self._blue, self._red, self._alphabet)

        for p in self._red.union(self._blue):
            for e in exp:
                pe = p + e
                if pe in self._pos_examples:
                    ot.put(p, e, 1)
                else:
                    if pe in self._neg_examples:
                        ot.put(p, e, 0)
                    else:
                        ot.put(p, e, None)

            sta.add(p)

        ot.sta = sta
        ot.exp = exp

        return ot

    def _fill_holes(self, ot: utils.ObservationTable) -> (utils.ObservationTable, bool):
        """
        Tries to make the table complete by filling in all the entries that
        are None.

        :param ot: the updated observation table
        :return: updated ObservationTable and whether the method was successful.
        :rtype: tuple(ObservationTable, bool)
        """
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

    def _build_automaton(self, ot) -> automaton.Automaton:
        """
        Builds an automaton from the observation table.

        :type ot: ObservationTable
        :return: Automaton built from the observation table
        :rtype: Automaton
        """
        dfa = automaton.Automaton(self._alphabet)

        states = {
            automaton.State(i) for i in self._red
        }

        we = utils.break_strings_in_two(self._red)
        for w, e in we:
            if ot.entry_exists(w, e):
                val = ot.get(w, e)
                state = automaton.State(w + e)
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

    @staticmethod
    def _is_consistent(dfa: automaton.Automaton, ot: utils.ObservationTable) -> bool:
        """
        Determines whether the automaton is consistent with the
        observation table ot.

        :type dfa: Automaton
        :type ot: ObservationTable
        :return: Whether the automaton and observation table are consistent.
        :rtype: bool
        """
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


if __name__ == '__main__':
    s_plus = {'bb', 'abb', 'bba', 'bbb'}
    s_minus = {'a', 'b', 'aa', 'bab'}
    gold = Gold(s_plus, s_minus)
    gold.learn()

    # s_plus = {'aa', 'aba', 'bba'}
    # s_minus = {'ab', 'abab'}
    # gold = Gold(s_plus, s_minus)
    # gold.learn()

    # s_plus = {'a', 'aa', 'aaa'}
    # s_minus = set()
    # gold = Gold(s_plus, s_minus)
    # gold.learn()