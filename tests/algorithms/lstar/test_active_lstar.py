import unittest
import itertools
from inferrer import automaton, algorithms, oracle
from typing import Set, Generator


class TestActiveLSTAR(unittest.TestCase):

    def test_active_lstar_01(self):
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

        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()

    def test_active_lstar_02(self):
        q0 = automaton.State('0')

        expected_dfa = automaton.DFA({'a'}, start_state=q0)

        expected_dfa.add_transition(q0, q0, 'a')
        expected_dfa.accept_states.add(q0)

        teacher = oracle.ActiveOracle(expected_dfa)
        lstar = algorithms.LSTAR({'a'}, teacher)

        dfa = lstar.learn()

        self.assertEqual(1, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))
        self.assertTrue(dfa.parse_string('a' * 1000)[1])

    def test_active_lstar_03(self):
        """
        Try to let L* learn Kleene plus.
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
        lstar = algorithms.LSTAR({'a'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_active_lstar_04(self):
        q0 = automaton.State('0')
        q1 = automaton.State('1')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q1, 'b')

        expected_dfa.add_transition(q1, q1, 'a')
        expected_dfa.add_transition(q1, q1, 'b')

        expected_dfa.accept_states.add(q1)

        teacher = oracle.ActiveOracle(expected_dfa)
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)

        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_active_lstar_05(self):
        """
        Try to let L* learn the regular language A.
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
        lstar = algorithms.LSTAR({'a'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        s_plus = set()
        s_minus = set()
        for i in range(1, 21, 2):
            s_plus.add('a' * i)
            s_minus.add('a' * (i - 1))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
                self.assertFalse(dfa.parse_string(s)[1])

    def test_active_lstar_06(self):
        """
        try to let L* learn the regular language A.
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
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 7):
            if i.count('1') % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_active_lstar_07(self):
        """
        try to let L* learn the regular language A.
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
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 10):
            if len(i) < 3:
                continue
            if '101' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_active_lstar_08(self):
        """
        try to let L* learn the regular language A.
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

        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()

        self.assertTrue(expected_dfa, dfa)

    def test_active_lstar_09(self):
        """
        try to let L* learn the regular language L.
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
        lstar = algorithms.LSTAR({'a', 'b', 'c'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(expected_dfa, dfa)

    def test_active_lstar_10(self):
        """
        try to let L* learn the regular language L.
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
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)

        dfa = lstar.learn()

        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 8):
            if i == '':
                s_minus.add(i)
                continue

            cpy = list(i[:])
            for idx in range(len(i)):
                if idx % 2 == 1:
                    cpy[idx] = 'a'

            s_plus.add(''.join(cpy))

            if all([i[q] == 'a' for q in range(1, len(i), 2)]):
                s_plus.add(i)
            else:
                s_minus.add(i)

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_active_lstar_11(self):
        """
        try to let L* learn the regular language L.
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
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)

        dfa = lstar.learn()

        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 11):
            if i.count('a') == 2:
                s_plus.add(i)
            else:
                s_minus.add(i)

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertEqual(expected_dfa, dfa)

    def test_active_lstar_12(self):
        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')
        q5 = automaton.State('5')
        q6 = automaton.State('6')
        q7 = automaton.State('7')

        expected_dfa = automaton.DFA({'a', '1', '#'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, '#')
        expected_dfa.add_transition(q0, q2, '1')
        expected_dfa.add_transition(q0, q3, 'a')

        expected_dfa.add_transition(q1, q1, '#')
        expected_dfa.add_transition(q1, q4, '1')
        expected_dfa.add_transition(q1, q5, 'a')

        expected_dfa.add_transition(q2, q2, '1')
        expected_dfa.add_transition(q2, q4, '#')
        expected_dfa.add_transition(q2, q6, 'a')

        expected_dfa.add_transition(q3, q3, 'a')
        expected_dfa.add_transition(q3, q5, '#')
        expected_dfa.add_transition(q3, q6, '1')

        expected_dfa.add_transition(q4, q4, '1')
        expected_dfa.add_transition(q4, q4, '#')
        expected_dfa.add_transition(q4, q7, 'a')

        expected_dfa.add_transition(q5, q5, '#')
        expected_dfa.add_transition(q5, q5, 'a')
        expected_dfa.add_transition(q5, q7, '1')

        expected_dfa.add_transition(q6, q6, '1')
        expected_dfa.add_transition(q6, q6, 'a')
        expected_dfa.add_transition(q6, q7, '#')

        expected_dfa.add_transition(q7, q7, '1')
        expected_dfa.add_transition(q7, q7, 'a')
        expected_dfa.add_transition(q7, q7, '#')

        expected_dfa.accept_states.add(q7)

        teacher = oracle.ActiveOracle(expected_dfa)
        lstar = algorithms.LSTAR({'#', '1', 'a'}, teacher)

        dfa = lstar.learn()

        self.assertEqual(8, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        self.assertTrue(dfa.parse_string('#1a')[1])
        self.assertTrue(dfa.parse_string('a#1')[1])

        self.assertFalse(dfa.parse_string('#1')[1])
        self.assertFalse(dfa.parse_string('a')[1])

        self.assertEqual(expected_dfa, dfa)

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)