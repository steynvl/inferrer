import copy
import itertools


class Row:

    def __init__(self, prefix):
        self.__prefix = prefix
        self.__columns = {}
        self.__prime = None

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, prefix):
        self.__prefix = prefix

    @property
    def columns(self):
        return self.__columns

    @columns.setter
    def columns(self, columns):
        self.__columns = columns

    @property
    def prime(self):
        return self.__prime

    @prime.setter
    def prime(self, prime):
        self.__prime = prime

    def columns_are_equal(self, other):
        return self.columns == other.columns

    def covered_by(self, other_row):
        for v in self.columns.keys():
            if self.columns[v] and not other_row.columns[v]:
                return False
        return True

    def covered_rows(self, rows):
        for row in rows:
            if row == self:
                continue
            if self.covered_by(row):
                yield row

    def is_composed(self, rows):
        for rep in range(2, len(rows) + 1):
            for p in itertools.permutations(rows, rep):
                joined_row = Row.join(list(p))
                if joined_row.columns == self.columns:
                    return True
        return False

    @staticmethod
    def join(rows: list):
        new_prefix = [rows[0].prefix]
        joined_row = Row(rows[0].prefix)
        joined_row.columns = copy.deepcopy(rows[0].columns)

        for i in range(1, len(rows)):
            row = rows[i]
            new_prefix.append(row.prefix)

            for suffix in joined_row.columns.keys():
                joined_row.columns[suffix] = joined_row.columns[suffix] or row.columns[suffix]

        joined_row.prefix = ''.join(new_prefix)

        return joined_row

    def __hash__(self):
        return hash(self.prefix)

    def __eq__(self, other):
        return self.prefix == other.prefix

    def __lt__(self, other):
        return self.prefix < other.prefix

    def __gt__(self, other):
        return self.prefix > other.prefix

    def __le__(self, other):
        return self.prefix <= other.prefix

    def __ge__(self, other):
        return self.prefix >= other.prefix

    def __ne__(self, other):
        return self.prefix != other.prefix

    def __str__(self):
        return self.prefix
