from itertools import chain, combinations
from inferrer.automaton.fsa import FSA
from inferrer.automaton.state import State
from inferrer.automaton.dfa import DFA
from collections import defaultdict, OrderedDict, deque
from typing import Set, List, Tuple
import copy
import graphviz
import tempfile


class NFA(FSA):
    """
    Implements a non-deterministic finite automaton.
    """

    def __init__(self, alphabet: Set[str]):
        """
        :param alphabet: The alphabet of the regular language
        :type alphabet: set
        """
        super().__init__(alphabet)
        self._start_states = set()
        self._states = set()
        self._accept_states = set()

        self._transitions = defaultdict(OrderedDict)

    def add_transition(self, q1: State, q2: State, a: str):
        """
        Adds the transition, delta(q1, a) = q2 to the
        transition table.

        :param q1: from state
        :type q1: automaton.State
        :param q2: to state
        :type q2: automaton.State
        :param a: letter in alphabet
        :type a: str
        """
        if a not in self.alphabet and a != '':
            raise ValueError('\'{}\' is not in the alphabet of the nfa!'.format(a))

        from_map = self._transitions[q1]

        if a not in from_map:
            from_map[a] = set()

        from_map[a].add(q2)

    def transition_exists(self, q1: State, a: str) -> bool:
        """
        Checks whether the transition
        delta(q1, a) is defined.

        :param q1: from state
        :type q1: automaton.State
        :param a: letter in alphabet
        :type a: str
        :return: True if it exists
        :rtype: bool
        """
        return q1 in self._transitions and \
               a in self._transitions[q1]

    def parse_string(self, s: str) -> Tuple[State, bool]:
        """
        Parses each character of the input string through
        the nfa.

        :param s: The string to parse (s element of alphabet*)
        :type s: str
        :return: The state after reading the string s and whether
                 the nfa accepted the input string.
        :rtype: tuple(State, bool)
        """
        for start_state in self._start_states:
            stack = [(start_state, 0)]

            while len(stack) > 0:
                state, index = stack.pop()

                if index == len(s):
                    if state in self._accept_states:
                        return state, True
                    else:
                        continue

                symbols = self._transitions[state]
                for symbol, to_states in symbols.items():
                    for to_state in to_states:
                        if symbol == '':
                            stack.append((to_state, index))
                        elif symbol == s[index]:
                            stack.append((to_state, index + 1))

        return next(iter(self._start_states)), False

    def add_state(self, state: State):
        """
        Adds a state to the NFA.
        :param state: state to add to NFA.
        :type state: State
        """
        self._states.add(state)

    def add_accepting_state(self, state: State):
        """
        Makes the state an accepting state in
        the NFA.
        :param state: state to make accepting state.
        :type state: State
        """
        self._accept_states.add(state)

    def add_start_state(self, state: State):
        """
        Adds a start state to the NFA.
        :param state: start state to add.
        :type state: State
        """
        if state not in self._states:
            self._states.add(state)
        self._start_states.add(state)

    def get_states(self) -> Set[State]:
        """
        Returns the states in the NFA.
        :return: Set of states
        :rtype: Set[State]
        """
        return self._states

    def transition(self, q1: State, a: str) -> List[State]:
        """
        Performs the transition delta(q1, a) and
        then return the list of states that can be
        reached with this transition.

        :param q1: from state
        :type q1: automaton.State
        :param a: letter in alphabet
        :type a: str
        :return: List of reachable states
        :rtype: List[State]
        """
        return self._transitions[q1][a]

    def rename_states(self):
        """
        Renames all the states in the nfa

        :return: Original NFA with states renamed.
        :rtype: NFA
        """
        alphabet = sorted([''] + list(self.alphabet))
        nfa = NFA(self.alphabet)

        old_to_new = {}
        cnt = 0
        for s in self._start_states:
            new_state = State(str(cnt))
            nfa.add_start_state(new_state)
            old_to_new[s] = new_state
            cnt += 1

        queue = deque([s for s in self._start_states])
        visited = {s for s in self._start_states}

        while len(queue) > 0:
            state = queue.popleft()

            for a in alphabet:
                if state in self._transitions and a in self._transitions[state]:
                    for to_states in self._transitions[state].values():
                        for to_state in to_states:
                            if to_state not in visited:
                                queue.append(to_state)
                                visited.add(to_state)

                                old_to_new[to_state] = State(str(cnt))
                                cnt += 1

        for old, new in old_to_new.items():
            old_transitions = self._transitions[old]

            for sym, states in old_transitions.items():
                for state in states:
                    nfa.add_transition(new, old_to_new[state], sym)
                    nfa.add_state(new)

            if old in self._accept_states:
                nfa.add_accepting_state(new)

        return nfa

    def create_graphviz_object(self) -> graphviz.Digraph:
        """
        Creates a Graphviz object representing the
        NFA of the current instance.
        """
        digraph = graphviz.Digraph('dfa')
        digraph.graph_attr['rankdir'] = 'LR'

        edges = defaultdict(lambda: defaultdict(list))

        for state in self._states:
            shape = 'doublecircle' if state in self._accept_states else 'circle'
            digraph.node(name='q{}'.format(state.name), shape=shape, constraint='false')

            if state in self._transitions:
                for letter, to_states in self._transitions[state].items():
                    for to_state in to_states:
                        edges[state][to_state].append(letter)

        for from_state in edges:
            for to_state, letters in edges[from_state].items():
                digraph.edge('q{}'.format(from_state.name),
                             'q{}'.format(to_state.name),
                             ', '.join(letters))

        digraph.node('', shape='plaintext', constraint='true')

        for start_state in self._start_states:
            digraph.edge('', 'q{}'.format(start_state.name))

        return digraph

    def show(self):
        """
        Graphs the NFA using graphviz, the NFA will
        immediately be shown in a PDF file when this
        method is called.
        """
        self.create_graphviz_object().view(tempfile.mkstemp('gv')[1], cleanup=True)

    def copy(self):
        """
        Performs a deep copy of the instance.

        :return: A deep copy of the nfa.
        :rtype: NFA
        """
        nfa = NFA(self.alphabet)

        nfa._start_states = self._start_states.copy()
        nfa._states = self._states.copy()
        nfa._accept_states = self._accept_states.copy()

        nfa._transitions = copy.deepcopy(self._transitions)

        return nfa

    def to_dfa(self) -> DFA:
        """
        Converts the nfa instance to its
        equivalent deterministic finite
        state machine.
        Please consult Sipser for an explanation of this algorithm:
        https://www.amazon.com/Introduction-Theory-Computation-Michael-Sipser/dp/113318779X

        :return: the equivalent dfa
        :rtype: DFA
        """

        if len(self._start_states) > 1:
            cpy = self.copy()
            new_q = State('__q0__')
            cpy._states.add(new_q)
            for q in cpy._start_states:
                cpy.add_transition(new_q, q, '')
            cpy._start_states = {new_q}
        else:
            cpy = self.copy()

        q_prime = set()
        power_set_to_states = {}
        for q in cpy._power_set(cpy._states):
            new_state = State(''.join(sorted(map(str, q))))
            q_prime.add(new_state)
            power_set_to_states[new_state] = set(q)

        accept_prime = set()
        transitions = defaultdict(OrderedDict)
        q0_prime = self._epsilon_closure(cpy,
                                         next(iter(cpy._start_states)))

        for r in q_prime:
            for a in cpy.alphabet:
                transitions[r][a] = set()
                for state in power_set_to_states[r]:

                    if cpy.transition_exists(state, a):
                        for ts in cpy.transition(state, a):
                            for to_state in self._epsilon_closure(cpy, ts):
                                transitions[r][a].add(to_state)

            if any([s in cpy._accept_states for s in power_set_to_states[r]]):
                accept_prime.add(r)

        start_state = State(''.join(sorted(map(str, q0_prime))))
        dfa = DFA(self.alphabet, start_state)

        dfa.states = q_prime.copy()
        dfa.accept_states = accept_prime.copy()

        for from_state in transitions.keys():
            for symbol, to_states in transitions[from_state].items():
                to_state = State(''.join(sorted(map(str, to_states))))
                dfa.add_transition(from_state, to_state, symbol)

        return dfa.minimize()

    @staticmethod
    def _epsilon_closure(nfa, q: State):
        closure_set = {q}
        stack = [q]

        while len(stack) > 0:
            state = stack.pop()

            if nfa.transition_exists(state, ''):
                for to_state in nfa.transition(state, ''):
                    if to_state not in closure_set:
                        closure_set.add(to_state)
                        stack.append(to_state)

        return closure_set

    @staticmethod
    def _power_set(q):
        return chain.from_iterable(combinations(q, r) for r in range(len(q) + 1))

    def __str__(self):
        """
        ToString implementation for the class, only used
        for debugging purposes.

        :return: String representation of the nfa
        :rtype: str
        """
        rep = [
            'Initial states:    = {}'.format(set(map(lambda s: s.name, self._start_states))),
            'Alphabet:          = {}'.format(self.alphabet),
            'States:            = {}'.format(set(map(str, self._states))),
            'Accepting states:  = {}'.format(set(map(str, self._accept_states))),
            '\nTransition function: delta'
        ]

        for state in sorted(self._transitions.keys()):
            rep.append('state = q_{}'.format(state))
            for letter, to_state in self._transitions[state].items():
                rep.append('delta(q_{}, {}) = q_{}'.format(state, letter, ', '.join(map(str, to_state))))
            rep.append('')

        return '\n'.join(rep)
