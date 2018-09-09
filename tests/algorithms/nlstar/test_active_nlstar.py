import unittest
from inferrer import automaton, algorithms, oracle


class TestActiveNLSTAR(unittest.TestCase):

    def test_active_nlstar_01(self):
        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q2, 'b')

        expected_dfa.add_transition(q1, q3, 'a')
        expected_dfa.add_transition(q1, q4, 'b')

        expected_dfa.add_transition(q2, q3, 'a')
        expected_dfa.add_transition(q2, q3, 'b')

        expected_dfa.add_transition(q4, q2, 'a')
        expected_dfa.add_transition(q4, q3, 'b')

        expected_dfa.add_transition(q3, q3, 'a')
        expected_dfa.add_transition(q3, q3, 'b')

        expected_dfa.accept_states.update({q0, q1, q2, q4})

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)

        nfa = nlstar.learn()

    def test_active_nlstar_02(self):
        q0 = automaton.State('0')

        expected_dfa = automaton.DFA({'a'}, start_state=q0)

        expected_dfa.add_transition(q0, q0, 'a')
        expected_dfa.accept_states.add(q0)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a'}, teacher)

        nfa = nlstar.learn()

        self.assertEqual(1, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))
        self.assertTrue(nfa.parse_string('a' * 1000)[1])

    def test_active_nlstar_03(self):
        """
        Try to let NL* learn Kleene plus.
        The alphabet is sigma = {a} and the
        language accepts every string with 1
        or more a's.
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'a'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q1, q1, 'a')

        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_active_nlstar_04(self):
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q1, 'b')

        expected_dfa.add_transition(q1, q1, 'a')
        expected_dfa.add_transition(q1, q1, 'b')

        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_active_nlstar_05(self):
        """
        Try to let NL* learn the regular language A.
        A is a language over the alphabet sigma = {a},
        that accepts all strings with an odd number of
        a's.
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'a'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q1, q0, 'a')
        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        self.assertEqual(expected_dfa, dfa)

    def test_active_nlstar_06(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'0', '1'}, start_state=q0)

        expected_dfa.add_transition(q0, q0, '0')
        expected_dfa.add_transition(q0, q1, '1')

        expected_dfa.add_transition(q1, q1, '0')
        expected_dfa.add_transition(q1, q0, '1')

        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'0', '1'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(expected_dfa, dfa)

    def test_active_nlstar_07(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains 101 as a substring.
        """
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')

        expected_dfa = automaton.DFA({'0', '1'}, start_state=q1)

        expected_dfa.add_transition(q1, q1, '0')
        expected_dfa.add_transition(q1, q2, '1')

        expected_dfa.add_transition(q2, q2, '1')
        expected_dfa.add_transition(q2, q3, '0')

        expected_dfa.add_transition(q3, q1, '0')
        expected_dfa.add_transition(q3, q4, '1')

        expected_dfa.add_transition(q4, q4, '0')
        expected_dfa.add_transition(q4, q4, '1')

        expected_dfa.accept_states.add(q4)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'0', '1'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(expected_dfa.rename_states(),
                         dfa.rename_states())

    def test_active_nlstar_08(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an even number of 0's and an even
        number of 1's.
        """
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q1)

        expected_dfa.add_transition(q1, q2, 'b')
        expected_dfa.add_transition(q1, q4, 'a')

        expected_dfa.add_transition(q2, q1, 'b')
        expected_dfa.add_transition(q2, q3, 'a')

        expected_dfa.add_transition(q3, q2, 'a')
        expected_dfa.add_transition(q3, q4, 'b')

        expected_dfa.add_transition(q4, q3, 'b')
        expected_dfa.add_transition(q4, q1, 'a')

        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)

        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertTrue(expected_dfa, dfa)

    def test_active_nlstar_09(self):
        """
        try to let NL* learn the regular language L.
        L is a regular language over the alphabet {a, b, c} where
        every string in L is an even length.
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'a', 'b', 'c'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q1, 'b')
        expected_dfa.add_transition(q0, q1, 'c')

        expected_dfa.add_transition(q1, q0, 'a')
        expected_dfa.add_transition(q1, q0, 'b')
        expected_dfa.add_transition(q1, q0, 'c')

        expected_dfa.accept_states.add(q0)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a', 'b', 'c'}, teacher)
        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(expected_dfa, dfa)

    def test_active_nlstar_10(self):
        """
        try to let NL* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L, we have the following property,
        the characters at an even position should be a, the
        characters at an odd position can be a or b. The empty
        string is not accepted by the language.
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q1, 'b')

        expected_dfa.add_transition(q1, q2, 'b')
        expected_dfa.add_transition(q1, q3, 'a')

        expected_dfa.add_transition(q2, q2, 'a')
        expected_dfa.add_transition(q2, q2, 'b')

        expected_dfa.add_transition(q3, q1, 'a')
        expected_dfa.add_transition(q3, q1, 'b')

        expected_dfa.accept_states.update({q1, q3})

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(expected_dfa.rename_states(),
                         dfa.rename_states())

    def test_active_nlstar_11(self):
        """
        try to let NL* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L contains exactly two a's.
        """
        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q0, 'b')
        expected_dfa.add_transition(q0, q1, 'a')

        expected_dfa.add_transition(q1, q1, 'b')
        expected_dfa.add_transition(q1, q2, 'a')

        expected_dfa.add_transition(q2, q2, 'b')
        expected_dfa.add_transition(q2, q3, 'a')

        expected_dfa.add_transition(q3, q3, 'a')
        expected_dfa.add_transition(q3, q3, 'b')

        expected_dfa.accept_states.add(q2)

        teacher = oracle.ActiveOracle(expected_dfa)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)

        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(expected_dfa, dfa)
