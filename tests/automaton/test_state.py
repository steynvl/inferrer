import unittest
from inferrer.automaton.state import State


class TestState(unittest.TestCase):

    def test_state_01(self):
        test_set = {
            State(''),
            State('a'),
            State('b'),
            State('c'),
        }
        self.assertEqual(True, State('') in test_set)
        self.assertEqual(True, State('b') in test_set)
        self.assertEqual(False, State('d') in test_set)

    def test_state_02(self):
        test_dict = {
            State(''): '',
            State('a'): '',
            State('b'): '',
            State('c'): ''
        }
        self.assertEqual(True, State('') in test_dict.keys())
        self.assertEqual(True, State('b') in test_dict.keys())
        self.assertEqual(False, State('d') in test_dict.keys())


if __name__ == '__main__':
    unittest.main()
