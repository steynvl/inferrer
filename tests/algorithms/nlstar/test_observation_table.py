import unittest
from inferrer import oracle
from inferrer.algorithms.active.nlstar.observation_table import ObservationTable
from inferrer.algorithms.active.nlstar.row import Row


class TestObservationTable(unittest.TestCase):

    def test_ot_01(self):
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

        ot.update_meta_data()

        composed_rows = ot.primes.symmetric_difference(ot.rows)

        self.assertEqual(5, len(ot.primes))
        self.assertEqual(2, len(composed_rows))

        for i in ['', 'a', 'ab', 'b', 'abb']:
            self.assertTrue(i in map(lambda r: r.prefix, ot.primes))

        for i in ['aa', 'aba']:
            self.assertTrue(i in map(lambda r: r.prefix, composed_rows))

    def test_ot_02(self):
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

        ot.update_meta_data()

        composed_rows = ot.primes.symmetric_difference(ot.rows)

        self.assertEqual(7, len(ot.primes))
        self.assertEqual(2, len(composed_rows))

        for i in ['', 'a', 'ab', 'abb', 'b', 'abbb', 'abba']:
            self.assertTrue(i in map(lambda r: r.prefix, ot.primes))

        for i in ['aa', 'aba']:
            self.assertTrue(i in map(lambda r: r.prefix, composed_rows))


if __name__ == '__main__':
    unittest.main()
