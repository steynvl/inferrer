import unittest


class TestLSTAR(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
    # pos = {'', 'a', 'b', 'bb', 'abb', 'bba', 'bbb'}
    # neg = {'aa', 'bab'}
    # oracle = Oracle(pos, neg)
    #
    # lstar = LSTAR(oracle, utils.determine_alphabet(pos.union(neg)))
    # dfa = lstar.learn()
    # print(dfa)