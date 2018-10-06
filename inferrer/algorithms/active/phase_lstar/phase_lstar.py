from inferrer import automaton
from inferrer.oracle.oracle import Oracle
from inferrer.oracle.phase_oracle import PhaseOracle
from inferrer.algorithms.active.active_learner import ActiveLearner
from inferrer.algorithms.active.lstar.lstar import LSTAR
from inferrer.logger.logger import Logger
from typing import Set, List


class PhaseLSTAR(ActiveLearner):
    """
    An implementation of Dana Angluin's L* algorithm, which
    learns regular languages from queries and counterexamples.

    The general idea of L* is to:
    Find a consistent observation table (representing a DFA).
    Submit is as an equivalence query.
    Use the counter-example to update the table.
    Submit membership queries to make the table closed and complete.
    Iterate until the Oracle tells us the correct language has been
    reached.
    """

    def __init__(self, alphabet: Set[str], oracle: PhaseOracle):
        """
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        """
        super().__init__(alphabet, oracle)

        self._logger = Logger().get_logger()
        self._oracle = oracle

        self._logger.info('Created Active Learner [Phase L*]')

    def learn(self) -> automaton.DFA:
        assert self._oracle.curr_phase == 0
        self._logger.info('Start learning process')

        partial_automatons = self._learn_phases()
        return self._construct_final_automaton(partial_automatons)

    def _learn_phases(self) -> List[automaton.DFA]:
        partial_automatons = []

        for _ in range(self._oracle.num_of_phases()):
            self._logger.info('L* learning phase {}'.format(self._oracle.curr_phase))
            partial_automatons.append(LSTAR(self._alphabet, self._oracle).learn())
            self._oracle.inc_curr_phase()

        return partial_automatons

    def _construct_final_automaton(self, automatons: List[automaton.DFA]) -> automaton.DFA:
        assert len(automatons) > 0
        self._logger.info('Phase L*, constructing final automaton')

        label = 0
        new_labels = []
        for machine in automatons:
            old_to_new = {}
            for state in machine.states:
                old_to_new[state] = automaton.State(str(label))
                label += 1
            new_labels.append(old_to_new)

        dfa = automaton.DFA(self._alphabet, start_state=automatons[0]._start_state)
        for i, machine in enumerate(automatons):
            old_to_new = new_labels[i]

            for state in machine.states:
                dfa.states.add(old_to_new[state])

                for letter, to_state in machine._transitions[state]:
                    dfa.add_transition(old_to_new[state.name],
                                       old_to_new[to_state.name],
                                       letter)

        old_to_new = automatons[len(automatons) - 1]
        for accept_state in automatons[-1].accept_states:
            dfa.accept_states.add(old_to_new[accept_state])

        return dfa
