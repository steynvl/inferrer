from typing import Union, Set, Tuple

from inferrer import Learner
from inferrer.automaton.dfa import DFAWrapper, DFA
from inferrer.oracle import PassiveOracle
from inferrer.utils.utils import ALPHANUMERIC, ALPHANUMERIC_SET, determine_alphabet


def read_examples(file: str, separator: str = "") -> Union[Set[str], Set[Tuple[str]]]:
    try:
        with open(file, 'r') as f:
            if separator == "":
                return set(line.strip() for line in f)
            else:
                return set(tuple(line.strip().split(separator)) for line in f)
    except IOError:
        raise Exception('\'{}\' does not exist'.format(file))


def _char_generator():
    for i in ALPHANUMERIC:
        yield i


def _preprocess_symbol(symbol):
    """Preprocess """
    if symbol == "":
        symbol = "''"
    return symbol


def _process_traces(pos_examples, neg_examples):
    if len(pos_examples) == 0 and len(neg_examples) == 0:
        return pos_examples, neg_examples, None
    if len(pos_examples) > 0 and isinstance(next(iter(pos_examples)), str) or \
       len(neg_examples) > 0 and isinstance(next(iter(neg_examples)), str):
        return pos_examples, neg_examples, None
    else:
        gen = _char_generator()
        sym2char = dict()

        def _translate_trace(trace):
            new_trace = ""
            for symbol in trace:
                assert len(sym2char) < len(ALPHANUMERIC_SET)
                if symbol not in sym2char:
                    symbol = _preprocess_symbol(symbol)
                    sym2char[symbol] = next(gen)
                new_trace += sym2char[symbol]
            return new_trace

        new_pos_examples = {_translate_trace(t) for t in pos_examples}
        new_neg_examples = {_translate_trace(t) for t in neg_examples}
        return new_pos_examples, new_neg_examples, sym2char


def learn(pos_examples_filepath, neg_examples_filepath, algorithm_id, separator="") -> DFA:
    pos_examples = read_examples(pos_examples_filepath, separator=separator)
    neg_examples = read_examples(neg_examples_filepath, separator=separator)
    pos_examples, neg_examples, sym2char = _process_traces(pos_examples, neg_examples)
    alphabet = determine_alphabet(pos_examples.union(neg_examples))

    if algorithm_id in ['rpni', 'gold']:
        learner = Learner(alphabet=alphabet,
                          pos_examples=pos_examples,
                          neg_examples=neg_examples,
                          algorithm=algorithm_id)
    elif algorithm_id in ['lstar', 'nlstar']:
        learner = Learner(alphabet=alphabet,
                          oracle=PassiveOracle(pos_examples, neg_examples),
                          algorithm=algorithm_id)

    dfa = learner.learn_grammar()
    if sym2char:
        dfa = DFAWrapper(dfa, sym2char)

    return dfa
