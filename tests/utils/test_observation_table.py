import unittest
from inferrer.utils import ObservationTable


class TestObservationTable(unittest.TestCase):

    def test_ot_01(self):
        ot = ObservationTable(set(), {''}, set())
        ot.put('', '', 1)
        self.assertEqual(1, ot.get('', ''))
        self.assertEqual({'': 1}, ot.get_row(''))

    def test_ot_02(self):
        ot = ObservationTable(set(), {''}, set())
        ot.add_row('a')
        self.assertEqual({}, ot.get_row('a'))
        ot.put('a', 'b', 0)
        self.assertEqual(0, ot.get('a', 'b'))

    def test_ot_03(self):
        ot = ObservationTable(set(), {''}, set())
        ot.add_row('a')
        self.assertEqual({}, ot.get_row('a'))
        ot.put('a', 'a', 1)
        ot.put('a', 'b', 0)
        self.assertEqual(0, ot.get('a', 'b'))
        self.assertEqual(True, ot.row_exists('a'))
        self.assertEqual(False, ot.row_exists('b'))
        try:
            ot.get('a', 'c')
            self.fail('Indexing row and column that'
                      ' is not defined should throw an exception!')
        except KeyError:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
