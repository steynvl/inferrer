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
        rpi = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpi.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_02(self):
        s_plus = {'aa', 'aba', 'bba'}
        s_minus = {'ab', 'abab'}
        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})

        dfa = rpni.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_03(self):
        s_plus = {'a', 'aa', 'aaa'}
        s_minus = set()
        rpni = algorithms.RPNI(s_plus, s_minus, {'a'})

        dfa = rpni.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

    def test_rpni_04(self):
        s_plus = {'a' * i for i in range(50)}

        rpni = algorithms.RPNI(s_plus, set(), {'a'})
        dfa = rpni.learn()

        self.assertEqual(1, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('a' * 1000)[1])

    def test_rpni_05(self):
        s_plus = {'a' * i for i in range(1, 51)}
        s_minus = {''}

        rpni = algorithms.RPNI(s_plus, s_minus, {'a'})
        dfa = rpni.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('a' * 1000)[1])

    def test_rpni_06(self):
        s_plus = set()
        s_minus = set()
        for i in self._combinations({'a', 'b'}, 4):
            if i == '':
                s_minus.add(i)
            else:
                s_plus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpni.learn()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_07(self):
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
            s_minus.add('a' * (i - 1))

        rpni = algorithms.RPNI(s_plus, s_minus, {'a'})
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

    def test_rpni_08(self):
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'0', '1'})
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

    def test_rpni_09(self):
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'0', '1'})
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

    def test_rpni_10(self):
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'0', '1'})
        dfa = rpni.learn()

        self.assertEqual(4, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))
        self.assertEqual(3, len(dfa.reject_states))

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_11(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        each string contains an even number of a's and an even
        number of b's.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
            if i.count('a') % 2 == 0 and i.count('b') % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertTrue(dfa.parse_string('aabaab')[1])

    def test_rpni_12(self):
        """
        try to let RPNI learn the regular language L.
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b', 'c'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_13(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b, c} where
        every string in L is a odd length.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b', 'c'}, 6):
            if len(i) % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b', 'c'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_14(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L, we have the following property,
        the characters at an even position should be a, the
        characters at an odd position can be a or b. The empty
        string is not accepted by the language.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_15(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b, c, d, e} where
        for every string in L, we have the following property,
        the characters at an even position should be a or b, the
        characters at an odd position can be any symbol in the
        alphabet. The empty string is not accepted by the language.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b', 'c', 'd', 'e'}, 6):
            if len(i) < 2:
                s_minus.add(i)
                continue

            cpy_1 = list(i[:])
            cpy_2 = list(i[:])
            for idx in range(len(i)):
                if idx % 2 == 1:
                    cpy_1[idx] = 'a'
                    cpy_2[idx] = 'b'

            s_plus.add(''.join(cpy_1))
            s_plus.add(''.join(cpy_2))

            if all([i[q] == 'a' or i[q] == 'b' for q in range(1, len(i), 2)]):
                s_plus.add(i)
            else:
                s_minus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b', 'c', 'd', 'e'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertFalse(dfa.parse_string('abacab')[1])
        self.assertFalse(dfa.parse_string('abaaabeafacbfabe')[1])

    def test_rpni_16(self):
        """
        try to let RPNI learn the regular language L.
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b', 'c'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_17(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L contains exactly two a's.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
            if i.count('a') == 2:
                s_plus.add(i)
            else:
                s_minus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_18(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        for every string in L does not contain the substring abb
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
            if 'abb' in i:
                s_minus.add(i)
            else:
                s_plus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', 'b'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    @unittest.SkipTest
    def test_rpni_19(self):
        """
        try to let RPNI learn the regular language L.
        L is a regular language over the alphabet {0, 1, .} where
        for every string in L represent a made up IP address format.
        X.X.X where X is either 0 or 1 and the length of X is 1, 2 or 3.
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()
        s_minus_reduce = set()

        three_nums = list(filter(lambda st: st != '', self._combinations({'0', '1'}, 4)))

        first = three_nums[:]
        second = []
        for i in first:
            for j in three_nums:
                second.append('{}.{}'.format(i, j))
                s_minus_reduce.add('{}.{}'.format(i, j))

        for i in second:
            for j in three_nums:
                string = '{}.{}'.format(i, j)
                if len(string) > 11:
                    s_minus.add(string)
                else:
                    s_plus.add(string)

        s_plus_reduce = set(random.sample(s_plus, 150))
        neg = set(random.sample(s_minus, 150))
        s_minus_reduce.update(neg)

        s_minus_reduce.update({
            '',
            '.',
            '0.',
            '1.',
            '01.',
            '10.',
            '001.',
            '111.',
            '101.',
            '0',
            '1',
            '01',
            '10',
            '101',
            '001',
        })

        s_plus_reduce.update({
            '1.00.00',
            '0.1.001',
            '0.0.100',
            '1.1.100',
            '10.0.101',
            '00.0.10',
            '11.0.100',
            '00.1.101',
            '1.1.11',
            '11.1.100',
            '00.0.00',
            '0.0.111',
            '0.01.101',
            '0.0.01',
            '0.0.10'
        })

        rpni = algorithms.RPNI(s_plus_reduce, s_minus_reduce, {'0', '1', '.'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    @unittest.SkipTest
    def test_rpni_20(self):
        """
        try to let RPNI learn the regular language L.
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
        s_plus_reduce = set(random.sample(s_plus, 125))

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

        rpni = algorithms.RPNI(s_plus_reduce, s_minus, {'0', '1', '.'})
        dfa = rpni.learn()

        for s in s_plus_reduce:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

        self.assertFalse(dfa.parse_string('10.10')[1])

    def test_rpni_21(self):
        s_plus = set()
        s_minus = set()

        reps = set('a' * i for i in range(1, 7))
        for i in reps:
            for j in reps:
                s_plus.add('{}@{}'.format(i, j))

        reps_with_empty = set('a' * i for i in range(7))
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

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', '@'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_22(self):
        s_plus = set()
        s_minus = set()

        s_plus.add('4{}'.format('d' * 12))
        s_plus.add('4{}'.format('d' * 15))

        s_minus.add('d{}'.format('d' * 12))
        s_minus.add('d{}'.format('d' * 15))
        s_minus.add('')

        for i in range(20):
            if i == 12 or i == 15:
                s_minus.add('d' * i)
                continue
            s_minus.add('4{}'.format('d' * i))
            s_minus.add('d' * i)

            neg = '{}4'.format('d' * i)
            neg1 = 'd' * (13 - len(neg))
            neg2 = 'd' * (16 - len(neg))
            s_minus.add(neg1)
            s_minus.add(neg2)

        rpni = algorithms.RPNI(s_plus, s_minus, {'4', 'd'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_rpni_23(self):
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', '1', '#'}, 6):
            if 'a' in i and '1' in i and '#' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        rpni = algorithms.RPNI(s_plus, s_minus, {'a', '1', '#'})
        dfa = rpni.learn()

        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)

    @staticmethod
    def _combinations_with_length(s: Set[str], repeat: int) -> Generator:
        for p in itertools.product(s, repeat=repeat):
            yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
