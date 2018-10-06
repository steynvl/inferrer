import unittest
import itertools
from inferrer import automaton, algorithms, oracle
from typing import Set, Generator


class TestPhaseLSTAR(unittest.TestCase):

    def test_active_lstar_01(self):
        q0 = automaton.State('0')
        q1 = automaton.State('1')
        q2 = automaton.State('2')
        q3 = automaton.State('3')
        q4 = automaton.State('4')

        expected_dfa = automaton.DFA({'a', 'b'}, start_state=q0)

        expected_dfa.add_transition(q0, q1, 'a')
        expected_dfa.add_transition(q0, q2, 'b')

        expected_dfa.add_transition(q1, q3, 'a')
        expected_dfa.add_transition(q1, q4, 'b')

        expected_dfa.add_transition(q2, q3, 'a')
        expected_dfa.add_transition(q2, q3, 'b')

        expected_dfa.add_transition(q4, q2, 'a')
        expected_dfa.add_transition(q4, q3, 'b')

        expected_dfa.add_transition(q3, q3, 'a')
        expected_dfa.add_transition(q3, q3, 'b')

        expected_dfa.accept_states.update({q0, q1, q2, q4})

        teacher = oracle.ActiveOracle(expected_dfa)

        lstar = algorithms.LSTAR({'a', 'b'}, teacher)
        dfa = lstar.learn()
