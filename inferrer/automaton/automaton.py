import utils
import copy
from collections import defaultdict, OrderedDict


class Automaton:

    def __init__(self, alphabet, start_state=''):

        self._start_state = start_state

        self._alphabet = alphabet

        self.states = set()

        self.accept_states = set()

        self.reject_states = set()

        self._transitions = defaultdict(OrderedDict)

    def add_transition(self, from_state, to_state, letter):
        self._transitions[from_state][letter] = to_state

    def transition_exists(self, from_state, letter):
        return from_state in self._transitions and \
               letter in self._transitions[from_state] and \
               self._transitions[from_state][letter] in self._transitions

    def perform_transition(self, from_state, letter):
        if from_state in self._transitions and \
                letter in self._transitions[from_state]:
            return self._transitions[from_state][letter]

    def find_transition_to_q(self, q):
        for qf in self._transitions.keys():
            for letter, to_state in self._transitions[qf].items():
                if to_state == q:
                    return qf, letter
        return None, None

    def parse_string(self, s: str):
        q = self._start_state
        for letter in s:
            if not self.transition_exists(q, letter):
                return q, False
            q = self.perform_transition(q, letter)

        return q, q in self.accept_states

    def minimize(self):
        _states = set()
        for state in self.states:
            if state in self._transitions.keys():
                _states.add(state)
            else:
                if state in self.accept_states:
                    self.accept_states.remove(state)
                elif state in self.reject_states:
                    self.reject_states.remove(state)

        self.states = _states
        return self

    def copy(self):
        cp = Automaton(self._alphabet)

        cp.states = self.states.copy()
        cp.accept_states = self.accept_states.copy()
        cp.reject_states = self.reject_states.copy()
        cp._transitions = copy.deepcopy(self._transitions)

        return cp

    def __str__(self):
        rep = [
            'q     = {}'.format(self._start_state),
            'Sigma = {}'.format(self._alphabet),
            'Q     = {}'.format(self.states),
            'Fa    = {}'.format(self.accept_states),
            'Fr    = {}'.format(self.reject_states),
            '\nTransition function: delta'
        ]

        for state in sorted(self._transitions.keys()):
            rep.append('state = q_{}'.format(state))
            for letter, to_state in self._transitions[state].items():
                if to_state in self._transitions:
                    rep.append('delta(q_{}, {}) = q_{}'.format(state, letter, to_state))
            rep.append('')

        return '\n'.join(rep)


def build_pta(s_plus: set, s_minus: set=set()):
    samples = s_plus.union(s_minus)

    alphabet = utils.determine_alphabet(samples)
    pta = Automaton(alphabet)

    for letter in alphabet:
        pta.add_transition('', letter, letter)

    states = {
        u for u in utils.prefix_set(samples, alphabet)
    }

    new_states = set()
    for u in states:
        for a in alphabet:
            ua = u + a
            if ua not in states:
                new_states.add(ua)

            pta.add_transition(u, ua, a)

    states.update(new_states)

    for u in states:
        if u in s_plus:
            pta.accept_states.add(u)
        if u in s_minus:
            pta.reject_states.add(u)

    pta.states = states

    return pta
