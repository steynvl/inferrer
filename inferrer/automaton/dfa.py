import graphviz
import tempfile
import copy
from inferrer import utils
from inferrer.automaton.state import State
from inferrer.automaton.fsa import FSA
from collections import defaultdict, OrderedDict, deque
from typing import Set, Tuple, List, Generator



class DFA(FSA):
    """
    Implements a deterministic finite automaton.
    """

    def __init__(self, alphabet: Set[str], start_state: State=State('')):
        """
        :param alphabet: The alphabet of the regular language
        :type alphabet: set
        :param start_state: the initial state of the dfa
        :type start_state: State
        """
        super().__init__(alphabet)

        self._start_state = start_state

        self.states = {self._start_state}

        self.accept_states = set()

        self.reject_states = set()

        self._transitions = defaultdict(OrderedDict)

    def parse_string(self, s: str) -> Tuple[State, bool]:
        """
        Parses each character of the input string through
        the dfa.

        :param s: The string to parse (s element of alphabet*)
        :type s: str
        :return: The state after reading the string s and whether
                 the dfa accepted the input string.
        :rtype: tuple(State, bool)
        """
        q = self._start_state
        for letter in s:
            if not self.transition_exists(q, letter):
                return q, False
            q = self.transition(q, letter)

        return q, q in self.accept_states

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
        if a not in self.alphabet:
            raise ValueError('\'{}\' is not in the alphabet of the dfa!'.format(a))

        self.states.update({q1, q2})
        self._transitions[q1][a] = q2

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
               a in self._transitions[q1] and \
               self._transitions[q1][a] in self.states

    def transition(self, q1: State, a: str) -> State:
        """
        Performs the transition delta(q1, a) and
        then return the state reached after the
        transition.

        :param q1: from state
        :type q1: automaton.State
        :param a: letter in alphabet
        :type a: str
        :return: to state
        :rtype: automaton.State
        """
        return self._transitions[q1][a]

    def walk_path(self, q: State, a: str) -> Generator:
        """
        Traverses the string a through the dfa
        starting at state q. This method returns
        a generator of the states visited while walking
        through the dfa.

        :param q: State the dfa should starts
                  in when traversing a.
        :type q: State
        :param a: String with symbols from the alphabet.
        :type a: str
        :return: Generator of visited states
        :rtype: Generator[State]
        """
        yield q
        for letter in a:
            if not self.transition_exists(q, letter):
                return
            q = self.transition(q, letter)
            yield q

    def find_transition_to_q(self, q: State) -> Tuple:
        """
        Finds the State r that satisfies
        delta(q, a) = r where a is a string in the
        alphabet

        :param q: Target state
        :type q: automaton.State
        :return: The state and whether or not the transition exists
        :rtype: tuple(State, str)
        """
        for qf in self._transitions.keys():
            for letter, to_state in self._transitions[qf].items():
                if to_state == q:
                    return qf, letter
        return None, None

    def find_transitions_to_q_with_letter(self, q: State, a: str) -> Set[State]:
        """
        Finds the State(s) r that satisfies
        delta(r, a) = a, where a is a symbol
        in the alphabet.

        :param q: Target state
        :type q: automaton.State
        :param a: Symbol
        :type a: str
        :return: The set of states
        :rtype: Set[State]
        """
        states = set()
        for qf in self._transitions.keys():
            for letter, to_state in self._transitions[qf].items():
                if to_state == q and letter == a:
                    states.add(qf)
        return states

    def minimize(self):
        """
        Minimizes the dfa using Hopcroft's algorithm.
        Please consult the following paper
        https://pdfs.semanticscholar.org/e622/10eea9d53bc36af50675017a830c967fea3f.pdf
        for an explanation of this algorithm.

        :return: Minimized dfa
        :rtype: DFA
        """
        p = self._hopcroft()

        start = [state_set for state_set in p if self._start_state in state_set]
        assert len(start) == 1

        minimized_dfa = DFA(self.alphabet, State(''.join(map(str, start[0]))))
        for state_set in p:
            for a in self.alphabet:
                for state in state_set:
                    if self.transition_exists(state, a):
                        to_state = self.transition(state, a)
                        to = [s for s in p if to_state in s]
                        assert len(to) == 1

                        to_state_set = to[0]
                        minimized_dfa.add_transition(State(''.join(map(str, state_set))),
                                                     State(''.join(map(str, to_state_set))),
                                                     a)
                        break

            if any(s in self.accept_states for s in state_set):
                minimized_dfa.accept_states.add(State(''.join(map(str, state_set))))

        return minimized_dfa.rename_states()

    def _hopcroft(self):
        qf = self.states - self.accept_states
        if len(self.accept_states) < len(self.states - self.accept_states):
            p = [qf, self.accept_states]
            l = deque([self.accept_states])
        else:
            p = [self.accept_states, qf]
            l = deque([qf])

        while len(l) > 0:
            s = l.popleft()
            for a in self.alphabet:
                for b in p.copy():
                    b1, b2 = self._split(b, s, a)
                    p.remove(b)
                    if len(b1) > 0:
                        p.append(b1)
                    if len(b2) > 0:
                        p.append(b2)

                    if len(b1) < len(b2):
                        if len(b1) > 0:
                            l.append(b1)
                    else:
                        if len(b2) > 0:
                            l.append(b2)
        return p

    def _split(self, b_prime, b, a):
        ba = set()
        for state in b:
            ba.update(self.find_transitions_to_q_with_letter(state, a))

        ba_comp = ba.symmetric_difference(self.states)
        return b_prime.intersection(ba), b_prime.intersection(ba_comp)

    def remove_dead_states(self):
        """
        Minimizes the dfa by removing all
        states (and transitions) that cannot be
        reached from the initial state. This is
        done by performing an iterative dept-first
        search over the execution tree given the
        initial state and alphabet.

        :return: minimized dfa
        :rtype: DFA
        """
        new_dfa = DFA(self.alphabet, self._start_state)
        stack = [self._start_state]
        visited_states = {self._start_state}
        while stack:
            state = stack.pop()

            new_dfa.states.add(state)

            for a in self.alphabet:
                if state in self._transitions and a in self._transitions[state]:
                    to_state = self.transition(state, a)
                    new_dfa.add_transition(state, to_state, a)
                    if to_state not in visited_states:
                        stack.append(to_state)
                        visited_states.add(to_state)

            if state in self.accept_states:
                new_dfa.accept_states.add(state)
            elif state in self.reject_states:
                new_dfa.reject_states.add(state)

        return new_dfa

    def rename_states(self):
        """
        Renames all the states in the dfa.

        :return: Original DFA with states renamed.
        :rtype: DFA
        """
        alphabet = sorted(self.alphabet)
        dfa = DFA(self.alphabet, State('0'))

        queue = deque([self._start_state])
        visited = {self._start_state}
        cnt = 1
        old_to_new = {self._start_state: State('0')}

        while len(queue) > 0:
            state = queue.popleft()

            for a in alphabet:
                if state in self._transitions and a in self._transitions[state]:
                    to_state = self.transition(state, a)

                    if to_state not in visited:
                        queue.append(to_state)
                        visited.add(to_state)

                        old_to_new[to_state] = State(str(cnt))
                        cnt += 1

        for old, new in old_to_new.items():
            old_transitions = self._transitions[old]

            for sym, state in old_transitions.items():
                dfa.add_transition(new, old_to_new[state], sym)

            if old in self.accept_states:
                dfa.accept_states.add(new)

        return dfa

    def copy(self):
        """
        Performs a deep copy of this instance.

        :return: A copied dfa
        :rtype: DFA
        """
        cp = DFA(self.alphabet, start_state=self._start_state)

        cp.states = self.states.copy()
        cp.accept_states = self.accept_states.copy()
        cp.reject_states = self.reject_states.copy()
        cp._transitions = copy.deepcopy(self._transitions)

        return cp

    def to_regex(self) -> str:
        """
        Converts a DFA to an equivalent regular expression.
        Please consult Sipser for an explanation of this algorithm:
        https://www.amazon.com/Introduction-Theory-Computation-Michael-Sipser/dp/113318779X

        :return: DFA converted to regular expression.
        :rtype: str
        """
        initial = State('__initial__')
        final = State('__final__')
        states = sorted(set(self.states).union({initial, final}), reverse=True)

        dfa_states = sorted(self.states, reverse=True)

        expressions = {}
        for x in states:
            for y in states:
                expressions[x, y] = None
        for x in dfa_states:
            expressions[x, x] = ''
            if x == self._start_state:
                expressions[initial, x] = ''
            if x in self.accept_states:
                expressions[x, final] = ''
        for x in dfa_states:
            for a in sorted(self.alphabet, reverse=True):
                if not self.transition_exists(x, a):
                    continue
                y = self.transition(x, a)
                if expressions[x, y]:
                    expressions[x, y] += '|{}'.format(a)
                else:
                    expressions[x, y] = a

        for s in dfa_states:
            states.remove(s)
            for x in states:
                for y in states:
                    if expressions[x, s] is not None \
                            and expressions[s, y] is not None:
                        xsy = []
                        if expressions[x, s]:
                            xsy.extend(self._parenthesize(expressions[x, s]))
                        if expressions[s, s]:
                            xsy.extend(self._parenthesize(expressions[s, s], True))
                            xsy.append('*')
                        if expressions[s, y]:
                            xsy.extend(self._parenthesize(expressions[s, y]))
                        if expressions[x, y] is not None:
                            xsy.extend(['|', expressions[x, y] or '()'])
                        expressions[x, y] = ''.join(xsy)

        return expressions[initial, final]

    @staticmethod
    def _parenthesize(expr: str, starring: bool=False) -> List[str]:
        """
        Returns a list of strings with or without parentheses. This method
        is used to simplify the expression returned. By omitting parentheses
        or other expression features when unnecessary.

        :param expr: Expression
        :type expr: str
        :type starring: bool
        :return: List of expressions
        :rtype: List[str]
        """
        if len(expr) == 1 or (not starring and '|' not in expr):
            return [expr]
        elif starring and expr.endswith('|()'):
            return ['(', expr[:-3], ')']
        else:
            return ['(', expr, ')']

    def create_graphviz_object(self) -> graphviz.Digraph:
        """
        Creates a Graphviz object representing the
        DFA of the current instance.
        """
        digraph = graphviz.Digraph('dfa')
        digraph.graph_attr['rankdir'] = 'LR'

        edges = defaultdict(lambda: defaultdict(list))

        for state in self.states:
            shape = 'doublecircle' if state in self.accept_states else 'circle'
            digraph.node(name='q{}'.format(state.name), shape=shape, constraint='false')

            if state in self._transitions:
                for letter, to_state in self._transitions[state].items():
                    edges[state][to_state].append(letter)

        for from_state in edges:
            for to_state, letters in edges[from_state].items():
                digraph.edge('q{}'.format(from_state.name),
                             'q{}'.format(to_state.name),
                             ', '.join(letters))

        digraph.node('', shape='plaintext', constraint='true')
        digraph.edge('', 'q{}'.format(self._start_state.name))

        return digraph

    def show(self):
        """
        Graphs the DFA using graphviz, the DFA will
        immediately be shown in a PDF file when this
        method is called.
        """
        self.create_graphviz_object().view(tempfile.mkstemp('gv')[1], cleanup=True)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        """
        Checks whether two DFA's are equivalent.

        :param other: dfa to compare to instance
        :type other: DFA
        :return: Whether the dfa is equal to
                 the current instance.
        :rtype: bool
        """
        tests = self._start_state == other._start_state and \
            self.states == other.states and \
            self.accept_states == other.accept_states

        if not tests:
            return False

        if sorted(self._transitions.keys()) != sorted(other._transitions.keys()):
            return False

        for k in self._transitions.keys():
            if sorted(self._transitions[k].keys()) != sorted(other._transitions[k].keys()):
                return False

            if sorted(self._transitions[k].values()) != sorted(other._transitions[k].values()):
                return False
        return True

    def __str__(self):
        """
        ToString implementation for the class, only used
        for debugging purposes.

        :return: String representation of the dfa
        :rtype: str
        """
        rep = [
            'Initial state:    = {}'.format(self._start_state),
            'Alphabet:         = {}'.format(self.alphabet),
            'States:           = {}'.format(set(map(str, self.states))),
            'Accepting states: = {}'.format(set(map(str, self.accept_states))),
            'Rejecting states: = {}'.format(set(map(str, self.reject_states))),
            '\nTransition function: delta'
        ]

        for state in sorted(self._transitions.keys()):
            rep.append('state = q_{}'.format(state))
            for letter, to_state in self._transitions[state].items():
                rep.append('delta(q_{}, {}) = q_{}'.format(state, letter, to_state))
            rep.append('')

        return '\n'.join(rep)


def build_pta(s_plus: Set[str], s_minus: Set[str]=set()) -> DFA:
    """
    Function that builds a prefix tree acceptor from the example strings
    S = S+ union S-

    :param s_plus: Set containing positive examples of the target language
    :type s_plus: set
    :param s_minus: Set containing negative examples of the target language
    :type s_minus: set
    :return: An dfa representing a prefix tree acceptor
    :rtype: DFA
    """
    samples = s_plus.union(s_minus)

    alphabet = utils.determine_alphabet(samples)
    pta = DFA(alphabet)

    for letter in alphabet:
        pta.add_transition(State(''), State(letter), letter)

    states = {
        State(u) for u in utils.prefix_set(samples, alphabet)
    }

    new_states = set()
    for u in states:
        for a in alphabet:
            ua = State(u.name + a)
            if ua not in states:
                new_states.add(ua)

            pta.add_transition(u, ua, a)

    states.update(new_states)

    for u in states:
        if u.name in s_plus:
            pta.accept_states.add(u)
        if u.name in s_minus:
            pta.reject_states.add(u)

    pta.states = states

    return pta
