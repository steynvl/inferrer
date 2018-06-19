import unittest
from inferrer import utils


class TestUtils(unittest.TestCase):

    def test_determine_alphabet_01(self):
        s = {'abcdefghi'}
        alphabet = {'a', 'b', 'c', 'd', 'e',
                    'f', 'g', 'h', 'i'}
        self.assertSetEqual(alphabet, utils.determine_alphabet(s))

    def test_determine_alphabet_02(self):
        s = {'abc', 'cba', 'bca', 'a', 'b',
             'c', 'aa', 'bb', 'cc', 'd'}
        alphabet = {'a', 'b', 'c', 'd'}

        self.assertSetEqual(alphabet, utils.determine_alphabet(s))

    def test_prefix_set_01(self):
        s = {'ab'}
        prefix_set = {'', 'a', 'ab'}

        self.assertSetEqual(prefix_set, set(utils.prefix_set(s)))

    def test_prefix_set_02(self):
        s = {'aaa', 'bbb', 'aba'}
        prefix_set = {'', 'a', 'b', 'aa', 'ab',
                      'bb', 'aaa', 'bbb', 'aba'}

        self.assertSetEqual(prefix_set, set(utils.prefix_set(s)))

    def test_prefix_set_03(self):
        s = {'abcc', 'ccbad', 'ccab'}
        prefix_set = {'', 'a', 'c', 'ab', 'cc', 'cca',
                      'ccb', 'abc', 'ccab', 'ccba',
                      'abcc', 'ccbad'}

        self.assertSetEqual(prefix_set, set(utils.prefix_set(s)))

    def test_suffix_set_01(self):
        s = {'ab'}
        suffix_set = {'', 'b', 'ab'}

        self.assertSetEqual(suffix_set, set(utils.suffix_set(s)))

    def test_suffix_set_02(self):
        s = {'aaa', 'bbb', 'aba'}
        suffix_set = {'', 'a', 'b', 'aa', 'ba',
                      'bb', 'aaa', 'bbb', 'aba'}

        self.assertSetEqual(suffix_set, set(utils.suffix_set(s)))

    def test_suffix_set_03(self):
        s = {'abcc', 'ccbad', 'ccab'}
        suffix_set = {'', 'b', 'c', 'd', 'ab', 'ad',
                      'cc', 'bad', 'bcc', 'cab',
                      'abcc', 'cbad', 'ccab', 'ccbad'}

        self.assertSetEqual(suffix_set, set(utils.suffix_set(s)))

    def test_breaking_strings_in_two_1(self):
        s = {'abcd'}
        combinations = {
            ('', 'abcd'),
            ('abcd', ''),
            ('a', 'bcd'),
            ('abc', 'd'),
            ('ab', 'cd'),
        }
        self.assertSetEqual(combinations, utils.break_strings_in_two(s))

    def test_breaking_strings_in_two_2(self):
        s = {'abcd', 'abc'}
        combinations = {
            ('', 'abcd'),
            ('abcd', ''),
            ('a', 'bcd'),
            ('abc', 'd'),
            ('ab', 'cd'),
            ('', 'abc'),
            ('abc', ''),
            ('a', 'bc'),
            ('ab', 'c')
        }
        self.assertSetEqual(combinations, utils.break_strings_in_two(s))


if __name__ == '__main__':
    unittest.main()
