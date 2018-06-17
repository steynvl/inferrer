import unittest
from collections import OrderedDict
from inferrer import utils, automaton, algorithms


class TestGold(unittest.TestCase):

    def test_build_automaton_01(self):
        blue = {'b', 'aa', 'ab'}
        red = {'', 'a'}
        ot = utils.ObservationTable(blue, red, {'a', 'b'})

        ot.put('', '', 0)
        ot.put('', 'a', 1)
        ot.put('a', '', 1)
        ot.put('a', 'a', 0)
        ot.put('b', '', 1)
        ot.put('b', 'a', 0)
        ot.put('aa', '', 0)
        ot.put('aa', 'a', 1)
        ot.put('ab', '', 1)
        ot.put('ab', 'a', 0)

        self.assertTrue(ot.is_closed()[0])
        self.assertTrue(ot.is_consistent())
        self.assertEqual((True, True), ot.is_closed_and_consistent())

        gold = algorithms.Gold({'a', 'b'}, set())
        gold._blue = blue
        gold._red = red
        dfa = gold._build_automaton(ot)

        self.assertSetEqual({'a', 'b'}, dfa._alphabet)
        self.assertTrue(2, len(dfa.states))
        self.assertTrue(1, len(dfa.accept_states))
        self.assertTrue(1, len(dfa.reject_states))

        q1 = automaton.State('')
        q2 = automaton.State('a')
        expected_transitions = OrderedDict({
            q1: OrderedDict({
                'a': q2,
                'b': q2
            }),
            q2: OrderedDict({
                'a': q1,
                'b': q2
            })
        })
        self.assertSetEqual(set(map(str, expected_transitions.keys())),
                            set(map(str, dfa._transitions.keys())))

        for k in expected_transitions.keys():
            for a in expected_transitions[k].keys():
                self.assertEqual(expected_transitions[k][a],
                                 dfa._transitions[k][a])

    def test_gold_01(self):
        s_plus = {'bb', 'abb', 'bba', 'bbb'}
        s_minus = {'a', 'b', 'aa', 'bab'}
        gold = algorithms.Gold(s_plus, s_minus)

        expected_table = {
            '': {'': None,
                 'a': 0,
                 'aa': 0,
                 'ab': None,
                 'abb': 1,
                 'b': 0,
                 'ba': None,
                 'bab': 0,
                 'bb': 1,
                 'bba': 1,
                 'bbb': 1
                 },
            'a': {'': 0,
                  'a': 0,
                  'aa': None,
                  'ab': None,
                  'abb': None,
                  'b': None,
                  'ba': None,
                  'bab': None,
                  'bb': 1,
                  'bba': None,
                  'bbb': None
                  },
            'b': {'': 0,
                  'a': None,
                  'aa': None,
                  'ab': 0,
                  'abb': None,
                  'b': 1,
                  'ba': 1,
                  'bab': None,
                  'bb': 1,
                  'bba': None,
                  'bbb': None
                  }
        }
        ot = gold._build_table()
        self.assertDictEqual(expected_table, ot.ot)

    def test_gold_02(self):
        s_plus = {'bb', 'abb', 'bba', 'bbb'}
        s_minus = {'a', 'b', 'aa', 'bab'}
        gold = algorithms.Gold(s_plus, s_minus)

        dfa = gold.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_gold_03(self):
        s_plus = {'aa', 'aba', 'bba'}
        s_minus = {'ab', 'abab'}
        gold = algorithms.Gold(s_plus, s_minus)

        dfa = gold.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])

    def test_gold_04(self):
        s_plus = {'a', 'aa', 'aaa'}
        s_minus = set()
        gold = algorithms.Gold(s_plus, s_minus)

        dfa = gold.learn()
        for s in s_plus:
            self.assertTrue(dfa.parse_string(s)[1])

        for s in s_minus:
            self.assertFalse(dfa.parse_string(s)[1])


if __name__ == '__main__':
    unittest.main()
