from inferrer import utils, automaton, algorithms
from typing import Set


class Learner:
    """
    Attempts to learn a target regular language provided
    a set of positive example strings, i.e. strings that
    are in the target language and a set of negative
    example strings, i.e. strings that do not belong in
    the target language.

    One of the following algorithms can be used when attempting
    to learn the target language:

    GOLD: An implementation of E. Mark GOLD's algorithm, which
          tries to find the minimum DFA consistent with the sample.

    RPNI: The Regular Positive and Negative Inference (RPNI) algorithm
          tries to make sure that some generalisation takes place and,
          in the best case, returns the correct target automaton.

    L*  : An implementation of Dana Angluin's L* algorithm, which
          learns regular languages from queries and counterexamples.
    """

    def __init__(self, pos_examples: Set[str],
                 neg_examples: Set[str],
                 algorithm: str='rpni'):
        """
        :param pos_examples: Set of positive example strings
                             from the target language.
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e. strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        :param algorithm: The algorithm to use when attempting to
                          learn the grammar from the example strings.
                          The options are:
                          gold
                          rpni
                          lstar
        :type algorithm: str
        """
        if not isinstance(pos_examples, set):
            raise ValueError('pos_examples should be a set')
        if not isinstance(neg_examples, set):
            raise ValueError('neg_examples should be a set')

        if len(pos_examples.intersection(neg_examples)) != 0:
            raise ValueError('The sets of positive and negative example '
                             'strings should not contain the same string(s)')

        self._alphabet = utils.determine_alphabet(pos_examples.union(neg_examples))

        self._learners = {
            'gold' : algorithms.Gold(pos_examples, neg_examples, self._alphabet),
            'rpni' : algorithms.RPNI(pos_examples, neg_examples, self._alphabet),
            'lstar': algorithms.LSTAR(pos_examples, neg_examples, self._alphabet,
                                      algorithms.Oracle(pos_examples,
                                                        neg_examples))
        }

        if algorithm not in self._learners:
            raise ValueError('Algorithm \'{}\' unknown, the following '
                             'algorithms are available:\n{}'
                             .format(algorithms, '\n'.join(self._learners.keys())))

        self._algorithm = algorithm

    def learn_grammar(self) -> automaton.Automaton:
        """
        Learns the regular language using the positive and negative
        example strings. The algorithm specified when instantiating
        this instance will be used to attempt to learn the grammar.

        :return: DFA consistent with the positive and negative
        example strings.
        :rtype: Automaton
        """
        learner = self._learners[self._algorithm]
        return learner.learn()
