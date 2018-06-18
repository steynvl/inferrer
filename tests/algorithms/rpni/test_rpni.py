import unittest
import random
import itertools
from collections import OrderedDict
from typing import Set, Generator
from inferrer import algorithms, automaton


class TestRPNI(unittest.TestCase):

    def test_rpni_01(self):
        s_plus = {'aaa', 'aaba', 'bba', 'bbaba'}
        s_minus = {'a', 'bb', 'aab', 'aba'}
        rpi = algorithms.RPNI(s_plus, s_minus)
        dfa = rpi.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_02(self):
        s_plus = {'aa', 'aba', 'bba'}
        s_minus = {'ab', 'abab'}
        rpni = algorithms.RPNI(s_plus, s_minus)

        dfa = rpni.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_03(self):
        s_plus = {'a', 'aa', 'aaa'}
        s_minus = set()
        rpni = algorithms.RPNI(s_plus, s_minus)

        dfa = rpni.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

    def test_rpni_04(self):
        s_plus = {'a' * i for i in range(1, 101)}

        rpni = algorithms.RPNI(s_plus, set())
        dfa = rpni.learn()

        self.assertEqual(1, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('a' * 1000)[1])

    def test_rpni_05(self):
        s_plus = set()
        s_minus = set()
        for i in range(1, 101):
            s_plus.add('a' * i)
            s_minus.add('b' * i)

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

        self.assertEqual(1, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('a' * 1000)[1])
        self.assertFalse(dfa.parse_string('b' * 1000)[1])

    def test_rpni_06(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a} where
        each string contains an odd number of a's
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in range(1, 21, 2):
            s_plus.add('a' * i)
            s_minus.add('' * (i - 1))

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

        self.assertSetEqual({automaton.State(''), automaton.State('a')}, dfa.states)
        self.assertSetEqual({automaton.State('a')}, dfa.accept_states)
        self.assertSetEqual({automaton.State('')}, dfa.reject_states)
        expected_transitions = OrderedDict({
            automaton.State(''): OrderedDict({
                'a': automaton.State('a')
            }),
            automaton.State('a'): OrderedDict({
                'a': automaton.State('')
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

    def test_rpni_07(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in range(1, 15, 2):
            positive_example = list('1' * i + '0' * random.randint(0, 6))
            negative_example = list('1' * (i - 1) + '0' * random.randint(0, 6))

            random.shuffle(positive_example)
            random.shuffle(negative_example)

            s_plus.add(''.join(positive_example))
            s_minus.add(''.join(negative_example))

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

        q_lambda = automaton.State('')
        q1 = automaton.State('1')

        self.assertSetEqual({q_lambda, q1}, dfa.states)
        self.assertSetEqual({q1}, dfa.accept_states)
        self.assertSetEqual({q_lambda}, dfa.reject_states)

        expected_transitions = OrderedDict({
            q_lambda: OrderedDict({
                '0': q_lambda,
                '1': q1,
            }),
            automaton.State('1'): OrderedDict({
                '0': q1,
                '1': q_lambda,
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

    def test_rpni_08(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s.
        This is for the same regular language as the test above,
        but with different example strings.
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in range(1, 15, 2):
            s_plus.add('1' * i + '0' * random.randint(0, 6))
            s_minus.add('1' * (i - 1) + '0' * random.randint(0, 6))

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

        self.assertEqual(10, len(dfa.states))
        self.assertSetEqual({automaton.State(''), automaton.State('111111111')}, dfa.accept_states)
        self.assertSetEqual({automaton.State('1'), automaton.State('11'),
                             automaton.State('111111'),
                             automaton.State('1111')}, dfa.reject_states)

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_09(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {0, 1} where
        each string contains 101 as a substring.
        """
        s_plus = {
            '101', '11010', '1101',
            '0101', '11010', '1110100',
            '000101', '11101', '101001',
            '100101', '1100101'
        }
        s_minus = {
            '', '1', '0',
            '10', '01', '100',
            '001', '110', '1100',
            '1001', '10001', '100001'
        }

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

        self.assertEqual(4, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))
        self.assertEqual(3, len(dfa.reject_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_10(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {0, 1} where
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

        rpni = algorithms.RPNI(s_plus, s_minus)
        dfa = rpni.learn()

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
