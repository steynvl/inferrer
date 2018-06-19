import copy
from inferrer import utils, automaton
from inferrer.algorithms.lstar.oracle import Oracle
from inferrer.algorithms.algorithm import Algorithm
from typing import Set, Tuple


class LSTAR(Algorithm):
    """
    An implementation of Dana Angluin's L* algorithm, which
    learns regular languages from queries and counterexamples.

    The general idea of L* is to:
    Find a consistent observation table (representing a DFA).
    Submit is as an equivalence query.
    Use the counter-example to update the table.
    Submit membership queries to make the table closed and complete.
    Iterate until the Oracle, tells us the correct language has been
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
        self._red = set()
        self._blue = set()

    def learn(self) -> automaton.Automaton:
        """
        Efficiently learns an initially unknown regular language
        from a minimally adequate Teacher (Oracle).

        :return: The dfa accepting the target language.
        :rtype: Automaton
        """
        ot = self._initialise()

        while True:
            is_closed, is_consistent = ot.is_closed_and_consistent()
            while not is_closed or not is_consistent:
                if not is_closed:
                    ot = self._close(ot)

                if not is_consistent:
                    ot = self._consistent(ot)

                is_closed, is_consistent = ot.is_closed_and_consistent()

            dfa = self._build_automaton(ot)
            answer, satisfied = self._oracle.equivalence_query(dfa)

            if satisfied:
                break

            ot = self._useq(ot, answer)

        return dfa

    def _initialise(self) -> utils.ObservationTable:
        """
        Initialises an observation table. This consists of
        building one red row and as many blue rows as there
        are symbols in the alphabet.

        :return: Initialised observation table
        :rtype: ObservationTable
        """
        self._red = {''}
        self._blue = copy.deepcopy(self._alphabet)

        ot = utils.ObservationTable(self._blue, self._red, self._alphabet)

        ot.sta = self._red.union(self._blue)
        ot.exp = {''}

        ot.put('', '', self._oracle.membership_query(''))
        for a in self._alphabet:
            ot.put(a, '', self._oracle.membership_query(a))

        return ot

    def _close(self, ot: utils.ObservationTable) -> utils.ObservationTable:
        """
        Closes the observation table by adding an extra row.

        :param ot: The observation table to close.
        :type ot: ObservationTable
        :return: The closed and updated observation table
        :rtype: ObservationTable
        """
        for s in self._blue.copy():
            if not all([ot.get_row(s) != ot.get_row(u) for u in self._red]):
                continue

            self._red.add(s)
            self._blue.remove(s)

            for a in self._alphabet:
                sa = s + a
                if sa not in self._blue:
                    self._blue.add(sa)
                    ot.add_row(sa)

            for u, e in ot.find_holes():
                ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _consistent(self, ot: utils.ObservationTable) -> utils.ObservationTable:
        """
        Makes the observation table consistent by adding an extra
        column.

        :param ot: The observation table to make consistent.
        :type ot: ObservationTable
        :return: The consistent and updated observation table
        :rtype: ObservationTable
        """
        s1, s2, a, e = self._find_inconsistent(ot)

        ae = a + e
        ot.exp.add(ae)
        ot.add_column_to_table(ae)

        for u, e in ot.find_holes():
            ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _find_inconsistent(self, ot: utils.ObservationTable) -> Tuple[str, str, str, str]:
        """
        Tries to find two inconsistent rows s1 and s2 in the
        observation table. s1 and s2 are elements of red.
        OT[s1] == OT[s2] and OT[s1.a][e] != OT[s2.a][e] where
        a is an element in the alphabet and e is an
        experiment (element in the set ot.exp)

        :param ot: The observation table to find two inconsistent
                   red states.
        :type ot: ObservationTable
        :return: Inconsistent row
        :rtype: Tuple[str, str, str, str]
        """
        for s1 in self._red:
            for s2 in self._red:
                if s1 == s2:
                    continue
                for a in self._alphabet:
                    for e in ot.exp:
                        if ot.get_row(s1) == ot.get_row(s2) and \
                            ot.entry_exists(s1 + a, e) and ot.entry_exists(s2 + a, e) \
                                and ot.get(s1 + a, e) != ot.get(s2 + a, e):
                            return s1, s2, a, e
        return '', '', '', ''

    def _useq(self, ot: utils.ObservationTable, answer: str) -> utils.ObservationTable:
        """
        This method is called when the table is closed and complete.
        The algorithm then makes an equivalence query to the oracle,
        if the oracle is not satisfied and provides us with a
        counterexample, then this method is called with that counterexample.
        The method adds new rows to the observation table, to account
        for the new counterexample.

        :param ot: The observation table to update
        :type ot: ObservationTable
        :param answer: The counter-example given by the oracle
        :type answer: str
        :return: Updated ObservationTable
        :rtype: ObservationTable
        """
        prefix_set = set(utils.prefix_set({answer}, self._alphabet))

        for p in prefix_set:

            if p not in self._red:
                if p not in self._blue:
                    ot.add_row(p)
                self._red.add(p)
                self._blue.discard(p)

            for a in self._alphabet:
                pa = p + a
                if pa not in prefix_set:
                    if pa not in self._blue:
                        if pa not in self._red:
                            ot.add_row(pa)
                        self._blue.add(pa)
                        self._red.discard(pa)

        for u, e in ot.find_holes():
            ot.put(u, e, self._oracle.membership_query(u + e))

        return ot

    def _build_automaton(self, ot: utils.ObservationTable) -> automaton.Automaton:
        """
        Builds an automaton from the observation table.

        :param ot: The data to build the dfa from.
        :type ot: ObservationTable
        :return: The dfa built from the observation table.
        :rtype: Automaton
        """
        dfa = automaton.Automaton(self._alphabet)

        for u in self._red:
            for v in ot.ot.keys():
                if u == v:
                    continue

                if len(v) < len(u) and ot.get_row(v) != ot.get_row(u):
                    dfa.states.add(automaton.State(u))

        for u in dfa.states:
            if ot.entry_exists(u.name, ''):
                if ot.get(u.name, '') == 1:
                    dfa.accept_states.add(u)
                elif ot.get(u.name, '') == 0:
                    dfa.reject_states.add(u)

            for a in self._alphabet:
                for w in dfa.states:
                    if ot.get_row(u.name + a) == ot.get_row(w.name):
                        dfa.add_transition(u, w, a)

        return dfa.minimize()
