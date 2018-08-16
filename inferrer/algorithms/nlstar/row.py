import copy


class Row:

    def __init__(self, prefix):
        self.__prefix = prefix
        self.__columns = {}

    @property
    def prefix(self):
        return self.__prefix

    @property
    def columns(self):
        return self.__columns

    @columns.setter
    def columns(self, columns):
        self.__columns = columns

    def covered_by(self, other_row):
        for v in self.columns.keys():
            if self.columns[v] and not other_row.columns[v]:
                return False
        return True

    def covered_rows(self, rows):
        for row in rows:
            if row == rows:
                continue
            if self.covered_by(row):
                yield row

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
        return self.columns == other.columns
