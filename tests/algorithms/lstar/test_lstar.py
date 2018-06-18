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
    # if s == '' or s == 'a' or s == 'b' or s == 'ab' or s == 'aa' or s == 'aba' or s == 'aab' or s == 'abab':
    #     return True
    # else:
    #     return False

    # if self._first:
    #     self._first = False
    #     return 'abb', False
    # return None, True