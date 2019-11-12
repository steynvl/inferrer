import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))


from inferrer.inferrer import Learner
from inferrer import utils
from inferrer import automaton
from inferrer import algorithms
from inferrer import oracle
