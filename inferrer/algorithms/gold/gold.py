from inferrer import utils, automaton


class Gold:

    def __init__(self, positive_examples: set, negative_examples: set):
        self._red = {''}
        self._positive_examples = positive_examples
        self._negative_examples = negative_examples
        self._samples = positive_examples.union(negative_examples)

    def learn(self):
        sta, exp, ot = self._build_table()

        max_len = len(max(self._samples, key=len))

        od_row, x = ot.obviously_different_row(exp, max_len)
        while od_row:
            self._red.add(x)

            xa = set([x + a for a in self._alphabet])
            sta.update(xa)
            self._blue.update(xa)
            self._blue.remove(x)

            for u in sta:
                for e in exp:
                    ue = u + e
                    if ue in self._positive_examples:
                        ot.update(u, e, 1)
                    elif ue in self._negative_examples:
                        ot.update(u, e, 0)
                    else:
                        ot.update(u, e, None)

            od_row, x = ot.obviously_different_row(exp, max_len)

        sta, exp, ot, failed = self._fill_holes(sta, exp, ot)

        if failed:
            return automaton.build_pta(self._positive_examples, self._negative_examples)
        else:
            a = self._build_automaton(ot)

            if self._is_consistent(a, ot):
                return a
            else:
                return automaton.build_pta(self._positive_examples, self._negative_examples)

    def _build_table(self):
        sta = {''}

        self._alphabet = utils.determine_alphabet(self._samples)
        self._blue = self._alphabet.copy()

        exp = set(utils.suffix_set(self._samples, self._alphabet))
        exp.add('')

        ot = utils.ObservationTable(self._blue, self._red)

        for p in self._red.union(self._blue):
            for e in exp:
                pe = p + e
                if pe in self._positive_examples:
                    ot.update(p, e, 1)
                else:
                    if pe in self._negative_examples:
                        ot.update(p, e, 0)
                    else:
                        ot.update(p, e, None)

            sta.add(p)

        return sta, exp, ot

    def _fill_holes(self, sta, exp, ot: utils.ObservationTable):
        for p in self._blue:
            r = ot.find_compatible_row(p, exp)
            if r is not None:
                for e in exp:
                    if ot.exists(p, e) and ot.get(p, e) is not None:
                        ot.update(r, e, ot.get(p, e))
            else:
                return sta, exp, ot, True

        for r in self._red:
            for e in exp:
                if ot.exists(r, e) and ot.get(r, e) is None:
                    ot.update(r, e, 1)

        for p in self._blue:
            r = ot.find_compatible_row(p, exp)
            if r is not None:
                for e in exp:
                    if ot.exists(p, e) and ot.get(p, e) is None:
                        if ot.exists(r, e):
                            ot.update(p, e, ot.get(r, e))
            else:
                return sta, exp, ot, True

        return sta, exp, ot, False

    def _build_automaton(self, ot):
        dfa = automaton.Automaton(self._alphabet)

        states = self._red.copy()

        we = utils.break_strings_in_two(self._red)
        for w, e in we:
            if ot.exists(w, e):
                val = ot.get(w, e)
                we = w + e
                if val == 1:
                    dfa.accept_states.add(we)
                    states.add(we)
                elif val == 0:
                    dfa.reject_states.add(we)
                    states.add(we)

        for w in states:
            for a in self._alphabet:
                for u in self._red:
                    wa = w + a
                    if ot.row_exists(u) and ot.row_exists(wa) and \
                            ot.get_row(u) == ot.get_row(wa):
                        dfa.add_transition(w, u, a)

        return dfa

    @staticmethod
    def _is_consistent(dfa, ot):
        for u, col in ot.get_observation_table().items():
            for e, val in col.items():
                ue = u + e
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