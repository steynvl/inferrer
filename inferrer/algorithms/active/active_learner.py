from inferrer.algorithms.algorithm import Algorithm
from typing import Set
from inferrer.oracle.oracle import Oracle


class ActiveLearner(Algorithm):
    """
    Represents an active learner that learns by making queries
    to an oracle (minimally adequate teacher), who knows the
    target regular language. The oracle can answer membership
    queries (i.e. whether a string is in the language or not)
    and equivalence queries: when the learner proposes a
    hypothesis and the oracle has to answer yes if the inferred
    automaton is correct and no (along with a counterexample) if
    the it is not correct.

    An active learner in most cases infers the minimum
    automaton that correctly describes the target regular language.
    """

    def __init__(self, alphabet: Set[str], oracle: Oracle):
        """
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        """
        super().__init__(alphabet)
        self._oracle = oracle

    def __new__(cls, *args, **kwargs):
        if cls is ActiveLearner:
            raise TypeError('Can\'t instantiate abstract class ActiveLearner')

        return object.__new__(cls)