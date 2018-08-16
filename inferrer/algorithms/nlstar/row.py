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
        for rep in range(1, len(rows) + 1):
            for p in itertools.combinations(rows, rep):
                if Row.join(list(p)).columns_are_equal(self):
                    return True
        return False

    @staticmethod
    def join(rows: list):
        joined_row = Row('')
        joined_row.columns = copy.deepcopy(rows[0].columns)
        if len(rows) == 0:
            raise ValueError('Can\'t join an empty list!')
        elif len(rows) == 1:
            return joined_row

        for i in range(1, len(rows)):
            row = rows[i]

            for suffix in joined_row.columns.keys():
                joined_row.columns[suffix] = joined_row.columns[suffix] or row.columns[suffix]

        return joined_row

    def __eq__(self, other):
        return self.prefix == other.prefix

    def __hash__(self):
        return hash(self.prefix)
