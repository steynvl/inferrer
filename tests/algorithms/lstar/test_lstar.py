import unittest
import itertools
import random
from collections import OrderedDict
from typing import Set, Generator
from inferrer import utils, automaton, algorithms


class TestLSTAR(unittest.TestCase):

    def test_lstar_01(self):
        s_plus = {'', 'a', 'b', 'ab', 'aba'}
        s_minus = {'abb'}
        oracle = algorithms.Oracle(s_plus, s_minus)

        lstar = algorithms.LSTAR(oracle, utils.determine_alphabet(s_plus.union(s_minus)))
        dfa = lstar.learn()

        self.assertEqual(5, len(dfa.states))
        self.assertEqual(4, len(dfa.accept_states))
        self.assertEqual(1, len(dfa.reject_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_02(self):
        s_plus = {'', 'a', 'b', 'ab', 'aa', 'aba', 'aab', 'abab'}
        s_minus = {'abb'}

        oracle = algorithms.Oracle(s_plus, s_minus)

        lstar = algorithms.LSTAR(oracle, utils.determine_alphabet(s_plus.union(s_minus)))
        dfa = lstar.learn()

        self.assertEqual(3, len(dfa.states))
        self.assertEqual(2, len(dfa.accept_states))
        self.assertEqual(1, len(dfa.reject_states))

        expected_transitions = OrderedDict({
            automaton.State(''): OrderedDict({
                'a': automaton.State(''),
                'b': automaton.State('ab'),
            }),
            automaton.State('ab'): OrderedDict({
                'a': automaton.State(''),
                'b': automaton.State('abb'),
            }),
            automaton.State('abb'): OrderedDict({
                'a': automaton.State('abb'),
                'b': automaton.State('abb'),
            })
        })
        self.assertSetEqual(set(map(str, expected_transitions.keys())),
                            set(map(str, dfa._transitions.keys())))

        for k in expected_transitions.keys():
            for a in expected_transitions[k].keys():
                self.assertEqual(expected_transitions[k][a],
                                 dfa._transitions[k][a])

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_03(self):
        """
        Try to let L* learn Kleene plus.
        The alphabet is sigma = {a} and the
        language accepts every string with 1
        or more a's.
        """
        s_plus = {'a', 'aa', 'aaa', 'aaaa', 'aaaaaaaa'}
        s_minus = {''}

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'a'})
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))
        self.assertEqual(1, len(dfa.reject_states))

    def test_lstar_04(self):
        """
        Try to let L* learn the regular language A.
        A is a language over the alphabet sigma = {a},
        that accepts all strings with an odd number of
        a's and the empty string.
        """
        s_plus = set()
        s_minus = set()
        for i in range(1, 21, 2):
            s_plus.add('a' * i)
            s_minus.add('a' * (i - 1))

        s_minus.discard('')
        s_plus.add('')

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'a'})
        dfa = lstar.learn()

        self.assertEqual(3, len(dfa.states))
        self.assertEqual(2, len(dfa.accept_states))
        self.assertEqual(1, len(dfa.reject_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_05(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s
        """
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 5):
            if i.count('1') % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'0', '1'})
        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_06(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains 101 as a substring.
        """
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 5):
            if '101' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'0', '1'})
        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_07(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string does not contain 101 as a substring.
        """
        s_plus = {''}
        s_minus = set()
        for i in self._combinations({'0', '1'}, 5):
            if '101' in i:
                s_minus.add(i)
            else:
                s_plus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'0', '1'})
        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_lstar_08(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an even number of 0's and an even
        number of 1's.
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'0', '1'}, 6):
            if i.count('0') % 2 == 0 and i.count('1') % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        lstar = algorithms.LSTAR(oracle, {'0', '1'})
        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('110110')[1])

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
