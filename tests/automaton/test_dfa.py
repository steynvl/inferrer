import unittest
from collections import OrderedDict
from inferrer import automaton


class TestAutomaton(unittest.TestCase):

    def test_dfa_01(self):
        dfa = automaton.DFA({'a', 'b'})

        self.assertTrue(automaton.State('') in dfa.states)
        dfa.add_transition(automaton.State(''), automaton.State('a'), 'a')
        self.assertTrue(dfa.transition_exists(automaton.State(''), 'a'))
        self.assertEqual(automaton.State('a'), dfa.transition(automaton.State(''), 'a'))

        try:
            dfa.add_transition(automaton.State(''), automaton.State('a'), 'c')
            self.fail('Automaton should throw ValueError when trying to add'
                      'transition with letter that is not in the alphabet!')
        except ValueError:
            self.assertTrue(True)

    def test_automaton_02(self):
        start_state = automaton.State('')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        dfa = automaton.DFA({'a', 'b'}, start_state)

        dfa.add_transition(start_state, start_state, 'a')
        dfa.add_transition(start_state, q1, 'b')
        dfa.add_transition(q1, q2, 'a')
        dfa.add_transition(q1, q2, 'b')

        self.assertEqual(3, len(dfa.states))
        self.assertEqual(2, len(dfa._transitions.keys()))
        self.assertTrue(dfa.transition_exists(start_state, 'a'))
        self.assertTrue(dfa.transition_exists(start_state, 'b'))
        self.assertTrue(dfa.transition_exists(q1, 'a'))

        self.assertFalse(dfa.transition_exists(q2, 'a'))
        self.assertFalse(dfa.transition_exists(q2, 'b'))

        q, a = dfa.find_transition_to_q(start_state)
        self.assertEqual('a', a)
        self.assertEqual(start_state, q)

        q, a = dfa.find_transition_to_q(q2)
        self.assertEqual('a', a)
        self.assertEqual(q1, q)

    def test_build_pta_01(self):
        positive_examples = {'aa', 'aba', 'bba'}
        negative_examples = {'ab', 'abab'}

        pta = automaton.build_pta(positive_examples, negative_examples)
        accept_states = {automaton.State('aa'), automaton.State('aba'), automaton.State('bba')}
        reject_states = {automaton.State('ab'), automaton.State('abab')}

        self.assertSetEqual(accept_states, pta.accept_states)
        self.assertSetEqual(reject_states, pta.reject_states)

        q, accepted = pta.parse_string('aba')
        self.assertTrue(accepted)
        self.assertEqual(automaton.State('aba'), q)

        q, accepted = pta.parse_string('abab')
        self.assertFalse(accepted)
        self.assertEqual(automaton.State('abab'), q)

    def test_build_pta_02(self):
        positive_examples = {'aa', 'aba', 'bba'}

        pta = automaton.build_pta(positive_examples)
        accept_states = {automaton.State('aa'), automaton.State('aba'), automaton.State('bba')}

        self.assertSetEqual(accept_states, pta.accept_states)
        self.assertTrue(len(pta.reject_states) == 0)

        q, accepted = pta.parse_string('aba')
        self.assertTrue(accepted)
        self.assertEqual(automaton.State('aba'), q)

        q, accepted = pta.parse_string('a')
        self.assertFalse(accepted)
        self.assertEqual(automaton.State('a'), q)

        q, accepted = pta.parse_string('')
        self.assertFalse(accepted)
        self.assertEqual(automaton.State(''), q)

    def test_build_pta_04(self):
        positive_examples = {'aaaa', 'aaba', 'bba', 'bbaba'}
        negative_examples = {'a', 'bb', 'aab', 'aba'}

        pta = automaton.build_pta(positive_examples, negative_examples)

        self.assertEqual(4, len(pta.accept_states))
        self.assertEqual(4, len(pta.reject_states))

        for s in positive_examples:
            self.assertTrue(pta.parse_string(s)[1])
        for s in negative_examples:
            self.assertFalse(pta.parse_string(s)[1])

    def test_remove_dead_states_01(self):
        alphabet = {'a', 'b', 'c'}
        dfa = automaton.DFA(alphabet)

        dfa.add_transition(automaton.State(''), automaton.State('2'), 'a')

        dfa.add_transition(automaton.State(''), automaton.State('3'), 'b')
        dfa.add_transition(automaton.State(''), automaton.State('3'), 'c')

        dfa.add_transition(automaton.State('3'), automaton.State('3'), 'a')
        dfa.add_transition(automaton.State('3'), automaton.State('3'), 'b')
        dfa.add_transition(automaton.State('3'), automaton.State(''), 'c')

        dfa.add_transition(automaton.State('2'), automaton.State('4'), 'a')
        dfa.add_transition(automaton.State('2'), automaton.State('4'), 'b')
        dfa.add_transition(automaton.State('2'), automaton.State('4'), 'c')

        dfa.add_transition(automaton.State('4'), automaton.State('2'), 'a')
        dfa.add_transition(automaton.State('4'), automaton.State('2'), 'b')
        dfa.add_transition(automaton.State('4'), automaton.State('2'), 'c')

        dfa.add_transition(automaton.State('5'), automaton.State('4'), 'a')
        dfa.add_transition(automaton.State('5'), automaton.State('4'), 'b')
        dfa.add_transition(automaton.State('5'), automaton.State('6'), 'c')

        dfa.states.add(automaton.State('7'))

        dfa.accept_states.update({automaton.State(''), automaton.State('6')})
        dfa.reject_states.update({automaton.State('3'), automaton.State('4'), automaton.State('7')})

        minimized_dfa = dfa.remove_dead_states()

        self.assertEqual(4, len(minimized_dfa.states))
        self.assertSetEqual({automaton.State('')}, minimized_dfa.accept_states)
        self.assertSetEqual({automaton.State('3'), automaton.State('4')}, minimized_dfa.reject_states)

        expected_transition_table = {
            automaton.State(''): OrderedDict({
                'a': automaton.State('2'),
                'b': automaton.State('3'),
                'c': automaton.State('3')
            }),
            automaton.State('3'): OrderedDict({
                'a': automaton.State('3'),
                'b': automaton.State('3'),
                'c': automaton.State('')
            }),
            automaton.State('2'): OrderedDict({
                'a': automaton.State('4'),
                'b': automaton.State('4'),
                'c': automaton.State('4')
            }),
            automaton.State('4'): OrderedDict({
                'a': automaton.State('2'),
                'b': automaton.State('2'),
                'c': automaton.State('2')
            })
        }
        transitions = minimized_dfa._transitions

        self.assertSetEqual(set(map(str, expected_transition_table.keys())),
                                set(map(str, transitions.keys())))

        for k in expected_transition_table.keys():
            for a in expected_transition_table[k].keys():
                self.assertEqual(expected_transition_table[k][a],
                                 transitions[k][a])

    def test_minimize_01(self):
        alphabet = {'0', '1'}

        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')
        q5 = automaton.State('5')

        dfa = automaton.DFA(alphabet, q0)

        dfa.add_transition(q0, q3, '0')
        dfa.add_transition(q0, q1, '1')

        dfa.add_transition(q1, q2, '0')
        dfa.add_transition(q1, q5, '1')

        dfa.add_transition(q2, q2, '0')
        dfa.add_transition(q2, q5, '1')

        dfa.add_transition(q3, q4, '1')
        dfa.add_transition(q3, q0, '0')

        dfa.add_transition(q4, q2, '0')
        dfa.add_transition(q4, q5, '1')

        dfa.add_transition(q5, q5, '0')
        dfa.add_transition(q5, q5, '1')

        dfa.accept_states.update({q1, q2, q4})
        minimized_dfa = dfa.minimize()

        self.assertEqual(3, len(minimized_dfa.states))
        self.assertEqual(1, len(minimized_dfa.accept_states))

    def test_minimize_02(self):
        alphabet = {'0', '1'}

        qa = automaton.State('a')
        qb = automaton.State('b')
        qc = automaton.State('c')
        qd = automaton.State('d')
        qe = automaton.State('e')
        qf = automaton.State('f')

        dfa = automaton.DFA(alphabet, qa)

        dfa.add_transition(qa, qb, '0')
        dfa.add_transition(qa, qc, '1')

        dfa.add_transition(qb, qa, '0')
        dfa.add_transition(qb, qd, '1')

        dfa.add_transition(qc, qe, '0')
        dfa.add_transition(qc, qf, '1')

        dfa.add_transition(qd, qe, '0')
        dfa.add_transition(qd, qf, '1')

        dfa.add_transition(qe, qe, '0')
        dfa.add_transition(qe, qf, '1')

        dfa.add_transition(qf, qf, '0')
        dfa.add_transition(qf, qf, '1')

        dfa.accept_states.update({qc, qd, qe})

        minimized_dfa = dfa.minimize()

        self.assertEqual(3, len(minimized_dfa.states))
        self.assertEqual(1, len(minimized_dfa.accept_states))

    def test_renamed_and_eq_01(self):
        alphabet = {'0', '1'}

        qa = automaton.State('a')
        qb = automaton.State('b')
        qc = automaton.State('c')
        qd = automaton.State('d')
        qe = automaton.State('e')
        qf = automaton.State('f')

        dfa = automaton.DFA(alphabet, qa)

        dfa.add_transition(qa, qb, '0')
        dfa.add_transition(qa, qc, '1')

        dfa.add_transition(qb, qa, '0')
        dfa.add_transition(qb, qd, '1')

        dfa.add_transition(qc, qe, '0')
        dfa.add_transition(qc, qf, '1')

        dfa.add_transition(qd, qe, '0')
        dfa.add_transition(qd, qf, '1')

        dfa.add_transition(qe, qe, '0')
        dfa.add_transition(qe, qf, '1')

        dfa.add_transition(qf, qf, '0')
        dfa.add_transition(qf, qf, '1')

        dfa.accept_states.update({qc, qd, qe})

        dfa = dfa.minimize()

        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')

        expected_dfa = automaton.DFA(alphabet, q0)

        expected_dfa.add_transition(q0, q1, '1')
        expected_dfa.add_transition(q0, q0, '0')

        expected_dfa.add_transition(q1, q2, '1')
        expected_dfa.add_transition(q1, q1, '0')

        expected_dfa.add_transition(q2, q2, '1')
        expected_dfa.add_transition(q2, q2, '0')

        expected_dfa.accept_states.add(q1)

        self.assertEqual(expected_dfa, dfa)

if __name__ == '__main__':
    unittest.main()
