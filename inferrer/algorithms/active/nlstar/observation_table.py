from inferrer.oracle.oracle import Oracle
from inferrer.algorithms.active.nlstar.row import Row
from typing import Set, Tuple


class ObservationTable:
    """
    An implementation of the observation table for
    the NL* algorithm, which is a 2-dimensional table
    that gives information about some target language.
    """

    def __init__(self, alphabet: Set[str], oracle: Oracle):
        """
        :param alphabet: alphabet of the regular language
        :type alphabet: set
        :param oracle: Minimally adequate teacher (MAT)
        :type oracle: Oracle
        """
        self._alphabet = alphabet
        self._oracle = oracle

        self.__rows = set()

        self.__upper_rows = set()
        self.__lower_rows = set()

        self.__primes = set()
        self.__upper_primes = set()

        self.__suffixes = set()

    @property
    def rows(self):
        return self.__rows

    @property
    def upper_rows(self):
        return self.__upper_rows

    @property
    def lower_rows(self):
        return self.__lower_rows

    @property
    def primes(self):
        return self.__primes

    @property
    def upper_primes(self):
        return self.__upper_primes

    @property
    def suffixes(self):
        return self.__suffixes

    @suffixes.setter
    def suffixes(self, suffixes):
        self.__suffixes = suffixes

    @upper_rows.setter
    def upper_rows(self, rows):
        self.__upper_rows = rows

    @lower_rows.setter
    def lower_rows(self, rows):
        self.__lower_rows = rows

    @primes.setter
    def primes(self, rows):
        self.__primes = rows

    @upper_primes.setter
    def upper_primes(self, rows):
        self.__upper_primes = rows

    @rows.setter
    def rows(self, rows):
        self.__rows = rows

    def initialize(self):
        """
        Initializes the observation table.
        The prefix-closed set is initialized
        with the empty string and all of the
        symbols in the alphabet of the regular
        language we are trying to infer.
        The suffix-closed set is initialized
        with the empty string.
        """
        row = Row('')
        self.rows.add(row)
        self.upper_rows.add(row)

        for symbol in self._alphabet:
            row = Row(symbol)
            self.rows.add(row)
            self.lower_rows.add(row)

        self.add_suffix('')

        self.update_meta_data()

    def add_columns_to_row(self, row: Row):
        """
        Adds all of the suffixes that are
        currently in the observation table
        to the given row.
        :param row: Row to whom the suffixes
                    should be added for.
        :type row: Row
        """
        for suffix in self.suffixes:
            mq = self._oracle.membership_query(row.prefix + suffix)
            row.columns[suffix] = mq

    def add_suffix(self, suffix: str):
        """
        Adds a new suffix (experiment) to
        the observation table.

        :param suffix: suffix to add to suffix-set.
        :type suffix: str
        """
        self.suffixes.add(suffix)

        for row in self.rows:
            mq = self._oracle.membership_query(row.prefix + suffix)
            row.columns[suffix] = mq

    def is_closed_and_consistent(self) -> Tuple[bool, bool]:
        """
        Tells us whether the observation table is closed
        and consistent.
        :return: Whether the table is closed and whether
                 the table is consistent.
        :rtype: Tuple[bool, bool]
        """
        return self.is_closed(), self.is_consistent()

    def is_closed(self) -> bool:
        """
        An observation table is closed if and only if
        any prime row of the lower part is a prime row
        of the upper part.

        :return: Whether the table is closed.
        :rtype: Tuple[bool, Row]
        """
        for row in self.lower_rows:
            covered = [r_prime for r_prime in self.upper_primes if r_prime.covered_by(row)]

            if len(covered) == 0 or \
                    not Row.join(covered).columns_are_equal(row):
                return False

        return True

    def is_consistent(self) -> bool:
        """
        Determines whether the observation table is
        consistent.

        :return: Whether the table is consistent.
        :rtype: bool
        """
        for r1 in self.upper_rows:
            for r2 in r1.covered_rows(self.upper_rows):
                for a in self._alphabet:
                    row1_succ = self.get_row_by_prefix(r1.prefix + a)
                    row2_succ = self.get_row_by_prefix(r2.prefix + a)

                    if not row1_succ.covered_by(row2_succ):
                        return False
        return True

    def add_new_suffixes(self, suffixes: Set[str]):
        """
        Adds new suffixes to the observation table.

        :param suffixes: Suffixes to add.
        :type suffixes: Set[str]
        """
        for suffix in suffixes:
            if suffix not in self.suffixes:
                self.suffixes.add(suffix)
                for row in self.rows:
                    row.columns[suffix] = self._oracle.membership_query(row.prefix + suffix)

    def update_meta_data(self):
        """
        Recalculate for all the rows in the
        observation table whether the rows is a
        prime row or a composed row.
        """
        self.primes.clear()
        self.upper_primes.clear()

        for row in self.rows:

            candidates = list(filter(lambda r: r != row and not row.covered_by(r), self.rows))

            if row in self.upper_rows or not row.is_composed(candidates):
                row.prime = True
                self.primes.add(row)
                if row in self.upper_rows:
                    self.upper_primes.add(row)

    def get_epsilon_row(self) -> Row:
        """
        Gets the epsilon row in the table.

        :return: Epsilon row in the table.
        :rtype: Row
        """
        for row in self.upper_rows:
            if row.prefix == '':
                return row

    def get_row_by_prefix(self, prefix: str) -> Row:
        """
        Gets the row in the observation table
        corresponding to the given prefix.

        :param prefix: Prefix of the row we
                       are looking for
        :type prefix: str
        :return: Row corresponding to the prefix.
        :rtype: Row
        """
        for row in self.rows:
            if row.prefix == prefix:
                return row
