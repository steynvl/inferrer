from inferrer import utils


class Oracle:

    def __init__(self, s_plus: set, s_minus: set):
        self._s_plus = s_plus
        self._s_minus = s_minus
        self._first = True

    def membership_query(self, s):
        if s == '' or s == 'a' or s == 'b' or s == 'ab' or s == 'aa' or s == 'aba' or s == 'aab' or s == 'abab':
            return True
        else:
            return False

    def equivalence_query(self):
        if self._first:
            self._first = False
            return 'abb', False
        return None, True
