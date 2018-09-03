import unittest
import itertools
from inferrer import automaton
from typing import Set, Generator


class TestNFA(unittest.TestCase):

    def test_nfa_01(self):
        nfa = automaton.NFA({'0', '1'})

        q1 = automaton.State('q1')
        q2 = automaton.State('q2')
        q3 = automaton.State('q3')
        q4 = automaton.State('q4')

        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)
        nfa.add_state(q4)

        nfa.add_transition(q1, q1, '0')
        nfa.add_transition(q1, q1, '1')
        nfa.add_transition(q1, q2, '1')

        nfa.add_transition(q2, q3, '0')
        nfa.add_transition(q2, q3, '')

        nfa.add_transition(q3, q4, '1')

        nfa.add_transition(q4, q4, '0')
        nfa.add_transition(q4, q4, '1')

        nfa.add_accepting_state(q4)
        nfa.add_start_state(q1)

        state, accepted = nfa.parse_string('010110')
        self.assertTrue(accepted)
        self.assertEqual(state.name, 'q4')

    def test_nfa_02(self):
        nfa = automaton.NFA({'0', '1'})

        q1 = automaton.State('q1')
        q2 = automaton.State('q2')
        q3 = automaton.State('q3')
        q4 = automaton.State('q4')

        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)
        nfa.add_state(q4)

        nfa.add_transition(q1, q1, '0')
        nfa.add_transition(q1, q1, '1')
        nfa.add_transition(q1, q2, '1')

        nfa.add_transition(q2, q3, '0')
        nfa.add_transition(q2, q3, '1')

        nfa.add_transition(q3, q4, '0')
        nfa.add_transition(q3, q4, '1')

        nfa.add_accepting_state(q4)
        nfa.add_start_state(q1)

        s_plus = set()
        s_minus = set()
        for comb in self._combinations({'0', '1'}, 8):
            if len(comb) < 3:
                s_minus.add(comb)
            elif comb[-3] == '1':
                s_plus.add(comb)
            else:
                s_minus.add(comb)

        for s in s_plus:
            state, accepted = nfa.parse_string(s)
            self.assertTrue(accepted)
            self.assertEqual(state.name, 'q4')

        for s in s_minus:
            _, accepted = nfa.parse_string(s)
            self.assertFalse(accepted)

    def test_nfa_03(self):
        nfa = automaton.NFA({'a', 'b'})

        q1 = automaton.State('q1')
        q2 = automaton.State('q2')
        q3 = automaton.State('q3')

        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)

        nfa.add_transition(q1, q2, 'b')
        nfa.add_transition(q1, q3, '')

        nfa.add_transition(q2, q2, 'a')
        nfa.add_transition(q2, q3, 'a')
        nfa.add_transition(q2, q3, 'b')

        nfa.add_transition(q3, q1, 'a')

        nfa.add_accepting_state(q1)
        nfa.add_start_state(q1)

        state, accepted = nfa.parse_string('')
        self.assertTrue(accepted)
        self.assertEqual(state.name, 'q1')

        state, accepted = nfa.parse_string('a')
        self.assertTrue(accepted)
        self.assertEqual(state.name, 'q1')

        state, accepted = nfa.parse_string('baba')
        self.assertTrue(accepted)
        self.assertEqual(state.name, 'q1')

        state, accepted = nfa.parse_string('baa')
        self.assertTrue(accepted)
        self.assertEqual(state.name, 'q1')

        _, accepted = nfa.parse_string('b')
        self.assertFalse(accepted)

        _, accepted = nfa.parse_string('bb')
        self.assertFalse(accepted)

        _, accepted = nfa.parse_string('babba')
        self.assertFalse(accepted)

    def test_nfa_to_dfa_01(self):
        nfa = automaton.NFA({'a', 'b'})

        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')

        nfa.add_state(q0)
        nfa.add_state(q1)
        nfa.add_state(q2)

        nfa.add_transition(q0, q0, 'a')
        nfa.add_transition(q0, q0, 'b')
        nfa.add_transition(q0, q1, 'a')

        nfa.add_transition(q1, q2, 'b')

        nfa.add_accepting_state(q2)
        nfa.add_start_state(q0)

        dfa = nfa.to_dfa()

        self.assertEqual(3, len(dfa.states))
        self.assertEqual(1, len(dfa.accept_states))

    def test_nfa_to_dfa_02(self):
        nfa = automaton.NFA({'a', 'b'})

        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')

        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)

        nfa.add_transition(q1, q2, '')
        nfa.add_transition(q1, q3, 'a')

        nfa.add_transition(q2, q1, 'a')

        nfa.add_transition(q3, q3, 'b')
        nfa.add_transition(q3, q2, 'a')
        nfa.add_transition(q3, q2, 'b')

        nfa.add_accepting_state(q2)
        nfa.add_start_state(q1)

        dfa = nfa.to_dfa()

        self.assertEqual(4, len(dfa.states))
        self.assertEqual(3, len(dfa.accept_states))

    def test_nfa_to_dfa_03(self):
        nfa = automaton.NFA({'a', 'b'})

        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')

        nfa.add_state(q0)
        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)

        nfa.add_transition(q0, q0, 'a')
        nfa.add_transition(q0, q0, 'b')
        nfa.add_transition(q0, q1, 'a')

        nfa.add_transition(q1, q1, 'a')
        nfa.add_transition(q1, q2, 'b')
        nfa.add_transition(q1, q2, 'a')
        nfa.add_transition(q1, q0, 'a')
        nfa.add_transition(q1, q0, 'b')

        nfa.add_transition(q2, q3, 'b')
        nfa.add_transition(q2, q3, 'a')
        nfa.add_transition(q2, q0, 'b')
        nfa.add_transition(q2, q0, 'a')
        nfa.add_transition(q2, q1, 'a')

        nfa.add_transition(q3, q1, 'a')
        nfa.add_transition(q3, q0, 'a')
        nfa.add_transition(q3, q0, 'b')

        nfa.add_accepting_state(q3)
        nfa.add_start_state(q0)

        dfa = nfa.to_dfa()
        self.assertEqual(8, len(dfa.states))
        self.assertEqual(4, len(dfa.accept_states))

    def test_nfa_to_dfa_04(self):
        nfa = automaton.NFA({'a', 'b'})

        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')

        nfa.add_state(q0)
        nfa.add_state(q1)
        nfa.add_state(q2)
        nfa.add_state(q3)

        nfa.add_transition(q0, q1, '')

        nfa.add_transition(q1, q2, '')
        nfa.add_transition(q1, q3, 'a')

        nfa.add_transition(q2, q1, 'a')

        nfa.add_transition(q3, q3, 'b')
        nfa.add_transition(q3, q2, 'a')
        nfa.add_transition(q3, q2, 'b')

        nfa.add_accepting_state(q2)

        nfa.add_start_state(q0)
        nfa.add_start_state(q1)

        dfa = nfa.to_dfa().minimize()

        self.assertEqual(4, len(dfa.states))
        self.assertEqual(3, len(dfa.accept_states))

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
