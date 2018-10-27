from inferrer import utils, automaton, algorithms
from inferrer.oracle.oracle import Oracle
from typing import Set


class Learner:
    """
    Attempts to learn a target regular language provided
    a set of positive example strings, i.e. strings that
    are in the target language and a set of negative
    example strings, i.e. strings that do not belong in
    the target language, or an Oracle that can answer
    membership queries and equivalence queries.

    One of the following algorithms can be used when attempting
    to learn the target language:

    GOLD: An implementation of E. Mark GOLD's algorithm, which
          tries to find the minimum DFA consistent with the sample.

    RPNI: The Regular Positive and Negative Inference (RPNI) algorithm
          tries to make sure that some generalisation takes place and,
          in the best case, returns the correct target automaton.

    L*  : An implementation of Dana Angluin's L* algorithm, which
          learns regular languages from queries and counterexamples.

    NL* : An implementation of the NL* algorithm, which extends
          Angluin-Style learning to the learning of an NFA.
    """

    def __init__(self, alphabet: Set[str],
                 pos_examples: Set[str]=None,
                 neg_examples: Set[str]=None,
                 oracle: Oracle=None,
                 algorithm: str='rpni'):
        """
        :param alphabet: Alphabet of the target language we are
                         trying to learn.
        :type alphabet: Set[str]
        :param pos_examples: Set of positive example strings
                             from the target language.
        :type pos_examples: Set[str]
        :param neg_examples: Set of negative example strings,
                             i.e. strings that do not belong in
                             the target language.
        :type neg_examples: Set[str]
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        :param algorithm: The algorithm to use when attempting to
                          learn the grammar from the example strings.
                          The options are:
                          gold
                          rpni
                          lstar
                          nlstar
        :type algorithm: str
        """
        if not isinstance(alphabet, set) or len(alphabet) == 0:
            raise ValueError('The alphabet has to be a set with at least one element')

        self._alphabet = alphabet

        self._learners = {
            'gold'  : lambda: algorithms.Gold(pos_examples, neg_examples, self._alphabet).learn(),
            'rpni'  : lambda: algorithms.RPNI(pos_examples, neg_examples, self._alphabet).learn(),
            'lstar' : lambda: algorithms.LSTAR(self._alphabet, oracle).learn(),
            'nlstar': lambda: algorithms.NLSTAR(self._alphabet, oracle).learn()
        }

        if algorithm not in self._learners:
            raise ValueError('Algorithm \'{}\' unknown, the following '
                             'algorithms are available:\n{}'
                             .format(algorithms, '\n'.join(self._learners.keys())))

        if algorithm in ['rpni', 'gold']:
            if not isinstance(pos_examples, set):
                raise ValueError('pos_examples should be a set')
            if not isinstance(neg_examples, set):
                raise ValueError('neg_examples should be a set')

            if len(pos_examples.intersection(neg_examples)) != 0:
                raise ValueError('The sets of positive and negative example '
                                 'strings should not contain the same string(s)')

            if pos_examples is None or neg_examples is None:
                raise ValueError('pos_examples and neg_examples can not be None '
                                 'for algorithm \'{}\''.format(algorithm))

            self._alphabet = utils.determine_alphabet(pos_examples.union(neg_examples))

        elif algorithm in ['lstar', 'nlstar']:
            if oracle is None:
                raise ValueError('oracle can not be None for algorithm \'{}\''.format(algorithm))

        self._algorithm = algorithm

    def learn_grammar(self) -> automaton.DFA:
        """
        Learns the regular language using the positive and negative
        example strings. The algorithm specified when instantiating
        this instance will be used to attempt to learn the grammar.

        :return: DFA consistent with the positive and negative
        example strings.
        :rtype: Automaton
        """
        fsa = self._learners[self._algorithm]()

        return fsa.to_dfa() if type(fsa) is automaton.NFA else fsa.rename_states()