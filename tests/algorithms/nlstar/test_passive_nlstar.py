import unittest
import itertools
import random
from typing import Set, Generator
from inferrer import algorithms, oracle
from inferrer.algorithms.active.nlstar.observation_table import ObservationTable
from inferrer.algorithms.active.nlstar.row import Row


class TestPassiveNLSTAR(unittest.TestCase):

    def test_build_hypothesis_01(self):
        ot = ObservationTable({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        row1 = Row('')
        row2 = Row('a')
        row3 = Row('ab')
        row4 = Row('abb')
        row5 = Row('b')
        row6 = Row('aa')

        row7 = Row('aba')
        row8 = Row('abbb')
        row9 = Row('abba')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}

        ot.rows = {row1, row2, row3, row4, row5, row6, row7, row8, row9}

        ot.upper_rows = {row1, row2, row3, row4}
        ot.lower_rows = {row5, row6, row7, row8, row9}

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        row3.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 1}
        row4.columns = {'': 1, 'aaa': 1, 'aa': 0, 'a': 0}

        row5.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row6.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 1}
        row7.columns = {'': 1, 'aaa': 1, 'aa': 1, 'a': 0}
        row8.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row9.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        ot.prefix_to_row = {r.prefix: r for r in ot.rows}

        ot.update_meta_data()

        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        nlstar._ot = ot

        nfa = nlstar._build_hypothesis()
        self.assertEqual(4, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

        s_plus = set()
        s_minus = set()

        so_long = []

        for i in self._combinations({'a', 'b'}, 6):
            so_long.append(i)

        for i in self._combinations({'a', 'b'}, 2):
            if len(i) != 2:
                continue

            for pre in so_long:
                s_plus.add('{}a{}'.format(pre, i))
                s_minus.add('{}b{}'.format(pre, i))

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_closed_and_consistent_01(self):
        ot = ObservationTable({'a', 'b'}, oracle.PassiveOracle(set(), set()))

        row1 = Row('')
        row2 = Row('b')
        row3 = Row('a')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}
        ot.rows = [row1, row2, row3]
        ot.upper_rows = [row1]
        ot.lower_rows = [row2, row3]

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row3.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        ot.update_meta_data()

        self.assertEqual(2, len(ot.primes))

        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        nlstar._ot = ot

        self.assertFalse(ot.is_closed()[0])
        self.assertTrue(ot.is_consistent()[0])

    def test_closed_and_consistent_02(self):
        ot = ObservationTable({'a', 'b'}, oracle.PassiveOracle(set(), set()))

        row1 = Row('')
        row2 = Row('b')
        row3 = Row('a')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}
        ot.rows = {row1, row2, row3}
        ot.upper_rows = {row1}
        ot.lower_rows = {row2, row3}

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row3.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        ot.update_meta_data()

        self.assertEqual(2, len(ot.primes))
        self.assertEqual(1, len(ot.rows.symmetric_difference(ot.primes)))

        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        nlstar._ot = ot

        closed_info, consistency_info = ot.is_closed_and_consistent()
        is_closed, unclosed_rows = closed_info
        is_consistent, _, _ = consistency_info

        self.assertFalse(is_closed)
        self.assertTrue(is_consistent)

        nlstar._close_table(unclosed_rows)

        self.assertEqual(5, len(nlstar._ot.rows))

    def test_closed_and_consistent_03(self):
        ot = ObservationTable({'a', 'b'}, oracle.PassiveOracle(set(), set()))

        row1 = Row('')
        row2 = Row('a')
        row3 = Row('b')
        row4 = Row('ab')
        row5 = Row('aa')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}
        ot.rows = {row1, row2, row3, row4, row5}
        ot.upper_rows = {row1, row2}
        ot.lower_rows = {row3, row4, row5}

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}
        row3.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row4.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 1}
        row5.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 1}

        ot.prefix_to_row = {r.prefix: r for r in ot.rows}

        ot.update_meta_data()

        self.assertEqual(4, len(ot.primes))
        self.assertEqual(1, len(ot.rows.symmetric_difference(ot.primes)))

        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        nlstar._ot = ot

        closed_info, consistency_info = ot.is_closed_and_consistent()
        is_closed, unclosed_rows = closed_info
        is_consistent, _, _ = consistency_info

        self.assertFalse(is_closed)
        self.assertTrue(is_consistent)

        nlstar._close_table([next(iter(unclosed_rows))])

        nlstar._ot.update_meta_data()

        self.assertEqual(7, len(nlstar._ot.rows))

    def test_closed_and_consistent_04(self):
        ot = ObservationTable({'a', 'b'}, oracle.PassiveOracle(set(), set()))

        row1 = Row('')
        row2 = Row('a')
        row3 = Row('ab')
        row4 = Row('b')
        row5 = Row('aa')
        row6 = Row('abb')
        row7 = Row('aba')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}
        ot.rows = {row1, row2, row3, row4, row5, row6, row7}
        ot.upper_rows = {row1, row2, row3}
        ot.lower_rows = {row4, row5, row6, row7}

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}
        row3.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 1}
        row4.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row5.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 1}
        row6.columns = {'': 1, 'aaa': 1, 'aa': 0, 'a': 0}
        row7.columns = {'': 1, 'aaa': 1, 'aa': 1, 'a': 0}

        ot.prefix_to_row = {r.prefix: r for r in ot.rows}

        ot.update_meta_data()

        self.assertEqual(5, len(ot.primes))
        self.assertEqual(2, len(ot.rows.symmetric_difference(ot.primes)))

        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle.PassiveOracle(set(), set()))
        nlstar._ot = ot

        closed_info, consistency_info = ot.is_closed_and_consistent()
        is_closed, unclosed_rows = closed_info
        is_consistent, _, _ = consistency_info

        self.assertFalse(is_closed)
        self.assertTrue(is_consistent)

        nlstar._close_table([next(iter(unclosed_rows))])

        nlstar._ot.update_meta_data()

        self.assertEqual(9, len(nlstar._ot.rows))

    def test_passive_nlstar_01(self):
        s_plus = {'a' * i for i in range(25)}

        teacher = oracle.PassiveOracle(s_plus, set())
        nlstar = algorithms.NLSTAR({'a'}, teacher)
        nfa = nlstar.learn()

        self.assertEqual(1, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))
        self.assertTrue(nfa.parse_string('a' * 1000)[1])

    def test_passive_nlstar_02(self):
        """
        Try to let NL* learn Kleene plus.
        The alphabet is sigma = {a} and the
        language accepts every string with 1
        or more a's.
        """
        s_plus = {'a', 'aa', 'aaa', 'aaaa', 'aaaaaaaa'}
        s_minus = {''}

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a'}, teacher)
        nfa = nlstar.learn()

        self.assertEqual(2, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

    def test_passive_nlstar_03(self):
        s_plus = set()
        s_minus = set()
        for i in self._combinations({'a', 'b'}, 4):
            if i == '':
                s_minus.add(i)
            else:
                s_plus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()
        dfa = nfa.to_dfa()

        self.assertEqual(2, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_04(self):
        """
        Try to let NL* learn the regular language A.
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
        nlstar = algorithms.NLSTAR({'a'}, teacher)
        nfa = nlstar.learn()

        self.assertEqual(2, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_05(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {a, b, c} where
        each string contains an even number of a's
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()
        for i in self._combinations({'a', 'b', 'c'}, 6):
            if i == '':
                continue
            if i.count('a') % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a', 'b', 'c'}, teacher)
        nfa = nlstar.learn()

        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_06(self):
        """
        try to let NL* learn the regular language A.
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
        nlstar = algorithms.NLSTAR({'0', '1'}, teacher)
        nfa = nlstar.learn()

        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_07(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an even number of 1's
        """
        random.seed(10012)
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'0', '1'}, 7):
            if i.count('1') % 2 == 0:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'0', '1'}, teacher)
        nfa = nlstar.learn()

        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_08(self):
        """
        try to let NL* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        every string in L is an odd length
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
            if len(i) % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_09(self):
        """
        try to let NL* learn the regular language L.
        L is a regular language over the alphabet {a, b} where
        every string in L is an odd length.
        """
        s_plus = set()
        s_minus = set()

        for i in self._combinations({'a', 'b'}, 6):
            if len(i) % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        teacher = oracle.PassiveOracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_10(self):
        """
        try to let NL* learn the regular language A.
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
        nlstar = algorithms.NLSTAR({'0', '1'}, teacher)
        nfa = nlstar.learn()

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_passive_nlstar_11(self):
        """
        try to let NL* learn the regular language L.
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
        nlstar = algorithms.NLSTAR({'a', 'b'}, teacher)
        nfa = nlstar.learn()

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
