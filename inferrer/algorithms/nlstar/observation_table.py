from typing import Set
from inferrer.algorithms import Oracle
from inferrer.algorithms.nlstar.row import Row


class ObservationTable:
    """
    An implementation of the observation table for the NL* algorithm.
    """

    def __init__(self, alphabet: Set[str], oracle: Oracle):
        self._alphabet = alphabet
        self._oracle = oracle

        self.__rows = set()

        self.__upper_rows = set()
        self.__lower_rows = set()

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
    def upper_primes(self):
        return self.__upper_primes

    @property
    def suffixes(self):
        return self.__suffixes

    def initialize(self):
        row = Row('')
        self.rows.add(row)
        self.upper_rows.add(row)

        self.add_suffix('')

    def add_suffix(self, suffix):
        self.suffixes.add(suffix)

        for row in self.rows:
            mq = self._oracle.membership_query(row.prefix + suffix)
            row.columns[suffix] = mq

    def is_closed_and_consistent(self):
        return self.is_closed(), self.is_consistent()

    def is_closed(self):
        for row in self.lower_rows:
            covered_rows = [r_prime for r_prime in self.upper_primes if r_prime.covered_by(row)]

            if Row.join(covered_rows) != row:
                return False

        return True

    def is_consistent(self):
        for r1 in self.upper_rows:
            for r2 in r1.covered_rows():
                for a in self._alphabet:

                    if not Row(r1.preifx + a).covered_by(Row(r2.prefix + a)):
                        return False
        return True

    def update_meta_data(self):
        pass
