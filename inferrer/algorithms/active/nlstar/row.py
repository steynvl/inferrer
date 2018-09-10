import copy
from typing import Generator


class Row:
    """
    Represents a row in the observation table
    used by the NL* algorithm.
    """

    def __init__(self, prefix: str):
        """
        :param prefix: The prefix of the row in
                       the observation table.
        :type prefix: str
        """
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

    def columns_are_equal(self, other) -> bool:
        """
        Determines whether two rows are equal by
        looking at the all the columns of both rows.

        :param other: other row to compare this instance to.
        :type other: Row
        :return: Whether the two rows are equal.
        :rtype: bool
        """
        return self.columns == other.columns

    def covered_by(self, other_row) -> bool:
        """
        Determines whether this instance is
        covered by the other row.

        :param other_row: Row to check whether it
                          covers this instance.
        :type other_row: Row
        :return: Whether this instance is covered
                 by the other row.
        :rtype: bool
        """
        for v in self.columns.keys():
            if self.columns[v] and not other_row.columns[v]:
                return False
        return True

    def covered_rows(self, rows: set) -> Generator:
        """
        Determines all of the rows in the observation
        table that is covered by this instance.

        :param rows: A set containing all of the
                     rows in the observation table.
        :type rows: Set[Row]
        :return: All of the rows in the observation table
                 that is covered by this instance.
        :rtype: Generator
        """
        for row in rows:
            if self != row and self.covered_by(row):
                yield row

    def is_composed(self, rows: list) -> bool:
        """
        Determines if the given row instance
        can be composed by a subset of the given
        rows.

        :param rows: rows to check, if this instance
                     can be composed by them.
        :type rows: List[Row]
        :return: Whether this row can be
                 composed by the other rows.
        :rtype: bool
        """
        if len(rows) == 0:
            return True

        return self.join(rows).columns == self.columns

    @staticmethod
    def join(rows: list):
        """
        Joins the given rows.

        :param rows: Rows to join.
        :type rows: List[Row]
        :return: The result of joining the rows.
        :rtype: Row
        """
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
