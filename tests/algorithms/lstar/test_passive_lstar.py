import unittest
import itertools
import random
from collections import OrderedDict
from typing import Set, Generator
from inferrer import automaton, algorithms, oracle


class TestPassiveLSTAR(unittest.TestCase):

    def test_passive_lstar_01(self):
        s_plus = {'', 'a', 'b', 'ab', 'aba'}
        s_minus = {'abb'}
        teacher = oracle.PassiveOracle(s_plus, s_minus)

        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(5, len(dfa.states))
        self.assertEqual(4, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_02(self):
        s_plus = {'', 'a', 'b', 'ab', 'aa', 'aba', 'aab', 'abab'}
        s_minus = {'abb'}

        teacher = oracle.PassiveOracle(s_plus, s_minus)

        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(3, len(dfa.states))
        self.assertEqual(2, len(dfa.accept_states))

        expected_transitions = OrderedDict({
            automaton.State('0'): OrderedDict({
                'a': automaton.State('0'),
                'b': automaton.State('1'),
            }),
            automaton.State('1'): OrderedDict({
                'a': automaton.State('0'),
                'b': automaton.State('2'),
            }),
            automaton.State('2'): OrderedDict({
                'a': automaton.State('2'),
                'b': automaton.State('2'),
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

    def test_passive_lstar_03(self):
        s_plus = {'a' * i for i in range(25)}

        teacher = oracle.PassiveOracle(s_plus, set())
        lstar = algorithms.LSTAR({'a'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(1, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))
        self.assertTrue(dfa.parse_string('a' * 1000)[1])

    def test_passive_lstar_04(self):
        """
        Try to let L* learn Kleene plus.
        The alphabet is sigma = {a} and the
        language accepts every string with 1
        or more a's.
        """
        s_plus = {'a', 'aa', 'aaa', 'aaaa', 'aaaaaaaa'}
        s_minus = {''}

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_passive_lstar_05(self):
        s_plus = set()
        s_minus = set()
        for i in self._combinations({'a', 'b'}, 4):
            if i == '':
                s_minus.add(i)
            else:
                s_plus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_06(self):
        """
        Try to let L* learn the regular language A.
        A is a language over the alphabet sigma = {a},
        that accepts all strings with an odd number of
        a's.
        """
        s_plus = set()
        s_minus = set()
        for i in range(1, 21, 2):
            s_plus.add('a' * i)
            s_minus.add('a' * (i - 1))

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a'}, teacher)
        dfa = lstar.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_07(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s
        """
        random.seed(10012)
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 7):
            if i.count('1') % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_08(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains 101 as a substring.
        """
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 10):
            if len(i) < 3:
                continue
            if '101' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_09(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string does not contain 101 as a substring.
        """
        s_plus = {''}
        s_minus = set()
        for i in self._combinations({'0', '1'}, 6):
            if '101' in i:
                s_minus.add(i)
            else:
                s_plus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_10(self):
        """
        try to let L* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an even number of 0's and an even
        number of 1's.
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'0', '1'}, 13):
            if i.count('0') % 2 == 0 and i.count('1') % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'0', '1'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_11(self):
        """
        try to let L* learn the regular language L.
        L is a regular language over the alphabet {a, b, c} where
        every string in L is an even length.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b', 'c'}, 6):
            if len(i) % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', 'b', 'c'}, teacher)

        dfa = lstar.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_12(self):
        """
        try to let L* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L, we have the following property,
        the characters at an even position should be a, the
        characters at an odd position can be a or b. The empty
        string is not accepted by the language.
        """
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

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)

        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_13(self):
        """
        try to let L* learn the regular language L.
        L is a regular language over the alphabet {a, b, c} where
        for every string in L, we have the following property,
        the character at the 3rd position from the end of the string
        should be an a.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b', 'c'}, 6):
            if len(i) < 3:
                s_minus.add(i)
                continue

            cpy_1 = list(i)
            cpy_2 = list(i)
            cpy_3 = list(i)
            cpy_1[-3] = 'a'
            cpy_2[-3] = 'b'
            cpy_3[-3] = 'c'

            s_plus.add(''.join(cpy_1))

            s_minus.add(''.join(cpy_2))
            s_minus.add(''.join(cpy_3))

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', 'b', 'c'}, teacher)

        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_14(self):
        """
        try to let L* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L contains exactly two a's.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 11):
            if i.count('a') == 2:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', 'b'}, teacher)

        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_15(self):
        """
        try to let L* learn the regular language L.
        L is a regular language over the alphabet {0, 1, .} where
        for every string in L represent a made up IP address format.
        X.X.X where X is either 0 or 1 and the length of X is 1, 2 or 3.
        """
        s_plus = set()
        s_minus = set()

        valid_length = list(filter(lambda st: st != '', self._combinations({'0', '1'}, 3)))
        invalid_lengths = list(filter(lambda st: len(st) == 0 or len(st) > 3, self._combinations({'0', '1'}, 6)))

        random.seed(10012)
        s_minus.update(random.sample(invalid_lengths, 35))

        random.seed(132)
        first_part = random.sample(invalid_lengths, 15)
        random.seed(1001)
        for i in first_part:
            s_minus.add('{}.'.format(i))
            s_minus.add('{}..'.format(i))
            s_minus.add('{}...'.format(i))
            s_minus.add('{}.{}'.format(i, random.sample(invalid_lengths, 1)[0]))

        random.seed(54328)
        second_part = random.sample(invalid_lengths, 15)
        random.seed(2212)
        for i in second_part:
            s_minus.add('{}.'.format(i))
            s_minus.add('{}.{}'.format(i, random.sample(invalid_lengths, 1)[0]))
            s_minus.add('{}.{}.'.format(i, random.sample(invalid_lengths, 1)[0]))

        first = valid_length[:]
        second = []
        for i in first:
            for j in valid_length:
                second.append('{}.{}'.format(i, j))

        for i in second:
            for j in valid_length:
                s_plus.add('{}.{}'.format(i, j))

        random.seed(90432)

        s_minus.update({
            '10.10',
            '1.0',
            '1.1',
            '0.0',
            '101.001',
            '101.001..10',
            '0.10.10.',
            '0.10.10..',
            '0.10.10...',
            '0.10.10....',
            '0.10..10....',
            '0.10...10....',
            '1..',
            '0..',
            '0...',
            '1...',
            '10...101.10',
            '10...01.10',
            '10.01..10',
            '0.1..10',
            '01.101..10',
            '01...'
            '101..101',
            '.',
            '101..1.01'
        })

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'0', '1', '.'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_16(self):
        s_plus = set()
        s_minus = set()

        reps = set('a' * i for i in range(1, 9))
        for i in reps:
            for j in reps:
                s_plus.add('{}@{}'.format(i, j))

        reps_with_empty = set('a' * i for i in range(9))
        s_minus.add('@')
        for i in reps_with_empty:
            s_minus.add('{}@'.format(i))
            s_minus.add('@{}'.format(i))
            s_minus.add('@{}@'.format(i))
            s_minus.add('@{}@@'.format(i))
            s_minus.add('@{}@@@'.format(i))
            for j in reps_with_empty:
                s_minus.add('@{}@{}'.format(i, j))
                s_minus.add('{}@{}@'.format(i, j))
                s_minus.add('{}@{}@@'.format(i, j))
                s_minus.add('{}@{}@@@'.format(i, j))
                s_minus.add('{}@{}@@@@'.format(i, j))

                s_minus.add('{}@{}@@{}'.format(i, j, i))
                s_minus.add('{}@{}@@@{}'.format(i, j, i))
                s_minus.add('{}@{}@@@@{}'.format(i, j, i))

        s_minus.update(reps_with_empty)

        s_minus.update({
            'a@a@a@a',
            'aa@aa@',
            'aaaa@aaaaa@aaaaa',
            'a@@a@a'
            'aa@@a@a'
            'aa@@aaa@a'
        })

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', '@'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_passive_lstar_17(self):
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', '1', '#'}, 8):
            if 'a' in i and '1' in i and '#' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        lstar = algorithms.LSTAR({'a', '1', '#'}, teacher)
        dfa = lstar.learn()

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
