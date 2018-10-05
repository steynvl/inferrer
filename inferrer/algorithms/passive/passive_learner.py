from inferrer.algorithms.algorithm import Algorithm
from typing import Set


class PassiveLearner(Algorithm):
    """
    Represents a passive learner that only has access to
    two sets: A set of positive examples strings, i.e. strings
    that belong in the target language and a set of negative
    example strings, i.e. strings that do not belong in the
    target language.

    A passive learner tries to find the minimum DFA consistent
    with the sample strings and in most cases infers the minimum
    DFA that correctly describes the target regular language.
    """

    def __init__(self, alphabet: Set[str], pos_examples: Set[str], neg_examples: Set[str]):
        """
        :param alphabet: The alphabet (Sigma) of the target
                         regular language.
        :type alphabet: Set[str]
        :param pos_examples: Set of positive example strings
                             from the target language.
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        """
        super().__init__(alphabet)
        self._pos_examples = pos_examples
        self._neg_examples = neg_examples

    def __new__(cls, *args, **kwargs):
        if cls is PassiveLearner:
            raise TypeError('Can\'t instantiate abstract class PassiveLearner')

        return object.__new__(cls)
