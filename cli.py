import argparse
import sys

from inferrer.learn import learn


def main(args):

    dfa = learn(args.positive_examples, args.negative_examples, args.algorithm, separator=args.separator)
    print(dfa.to_regex())

    if args.show_dfa:
        dfa.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is the CLI tool for the '
                                                 'grammatical inference library '
                                                 'inferrer. The library tries to'
                                                 ' learn regular languages using '
                                                 'positive and negative example '
                                                 'strings from the target language.')

    parser.add_argument('positive_examples', type=str, metavar='positive-examples',
                        help='Path to the file containing positive example strings, '
                             'i.e. strings that belong in the target language separated '
                             'by newlines.')

    parser.add_argument('negative_examples', type=str, metavar='negative-examples',
                        help='Path to the file containing negative example strings, '
                             'i.e. strings that do not belong in the target language'
                             ' separated by newlines.')

    parser.add_argument('--separator', type=str, default="", metavar='SEP',
                        help='The separator between different symbols.')

    parser.add_argument('algorithm', type=str,
                        choices=['gold', 'rpni', 'lstar', 'nlstar'],
                        help='The algorithm that should be used to learn the grammar.'
                             ' The options are: gold, rpni, lstar, and nlstar')

    parser.add_argument('--show-dfa', action='store_true',
                        help='If this argument is given, the DFA learned by the '
                             'specified algorithm will be shown.')

    options = parser.parse_args()
    sys.exit(main(options))
