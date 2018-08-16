from inferrer.automaton.state import State
from collections import defaultdict, OrderedDict
from typing import Set


class NFA:
    """
    Implements a non-deterministic finite automaton.
    """

    def __init__(self, alphabet: Set[str]):
        """
        :param alphabet: The alphabet of the regular language
        :type alphabet: set
        """
        self._alphabet = alphabet

        self._start_states = set()
        self._states = set()
        self._accept_states = set()

        self._transitions = defaultdict(OrderedDict)

    def add_start_state(self, state: State):
        """
        Adds a start state to the NFA.
        :param state: start state to add.
        :type state: State
        """
        if state not in self._states:
            self._states.add(state)
        self._start_states.add(state)

