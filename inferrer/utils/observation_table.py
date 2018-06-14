import collections


class ObservationTable:

    def __init__(self, blue: set, red: set, alphabet: set):
        """
        Represents a ObservationTable, which is a 2-dimensional table
        that gives information about some target language.

        :param blue: set containing blue states
        :type blue: set
        :param red: set containing red states
        :type red: set
        :param alphabet: alphabet of the regular language
        :type alphabet: set
        """
        self._blue = blue
        self._red = red
        self._alphabet = alphabet

        self.__ot = collections.defaultdict(dict)
        self.__exp = set()
        self.__sta = set()

    @property
    def ot(self):
        return self.__ot

    @ot.setter
    def ot(self, ot):
        self.__ot = ot

    @property
    def exp(self):
        return self.__exp

    @exp.setter
    def exp(self, exp):
        self.__exp = exp

    @property
    def sta(self):
        return self.__sta

    @sta.setter
    def sta(self, sta):
        self.__sta = sta

    def put(self, r: str, c: str, val):
        """
        Puts a value in the observation table

        :param r: row in the table
        :type r: str
        :param c: column in the table
        :type c: str
        :param val: to put in table:
        :type val: 1, 0 or None
        """
        self.ot[r][c] = val

    def get(self, r: str, c: str):
        """
        Gets a value in the observation table

        :param r: row in the table
        :type r: str
        :param c: column in the table
        :type c: str
        :return: 1, 0 or None
        """
        return self.ot[r][c]

    def entry_exists(self, r: str, col: str) -> bool:
        """
        Determine whether an entry in the 2-dimensional
        table exists by checking if the row and column
        are both defined in the table.

        :param r: row
        :type r: str
        :param col: column
        :type col: str
        :rtype: bool
        """
        return r in self.ot and col in self.ot[r]

    def get_row(self, r: str) -> dict:
        """
        Gets the row in the observation table.

        :param r: row in the table
        :type r: str
        :return: columns of the row
        :rtype: dict
        """
        return self.ot[r]

    def row_exists(self, r: str) -> bool:
        """
        Determines if a row exists in the table.

        :param r:
        :type r: str
        :rtype: bool
        """
        return r in self.ot

    def obviously_different_row(self, max_len):
        for u in self._blue:

            for v in self.__ot.keys():
                if u == v or len(u) == max_len or len(v) == max_len:
                    continue
                for e in self.exp:
                    if self.entry_exists(u, e) and self.entry_exists(v, e):
                        ue = self.get(u, e)
                        ve = self.get(v, e)

                        if ue is not None and ve is not None \
                                and ue != ve:
                            return True, u
        return False, None

    def is_closed_and_consistent(self) -> (bool, bool):
        return self.is_closed()[0], self.is_consistent()

    def is_closed(self):
        for u in self._blue:
            if not any([self.__ot[u] == self.__ot[s] for s in self._red]):
                return False, u

        return True, None

    def is_consistent(self):
        for s1 in self._red:
            for s2 in self._red:
                if s1 == s2 or self.__ot[s1] != self.__ot[s2]:
                    continue

                if not all([self.get_row(s1 + a) == self.get_row(s2 + a) for a in self._alphabet]):
                    return False

        return True

    def find_compatible_row(self, p, exp):
        for r in self._red:

            if p not in self.__ot or r not in self.__ot:
                continue

            p1 = self.__ot[p]
            r1 = self.__ot[r]

            if not any([
                (e in p1 and e in r1) and ((p1[e] == 0 and r1[e] == 1)
                    or (p1[e] == 1 and r1[e] == 0)) for e in exp
            ]):
                return r

        return None

    def add_row(self, r: str, exp: set):
        if r not in self.__ot.keys():
            self.__ot[r] = {i: None for i in exp}

    def add_column_to_table(self, c):
        for row in self.ot.keys():
            self.ot[row][c] = None

    def find_holes(self):
        for u, col in self.__ot.items():
            for e, val in col.items():
                if val is None:
                    yield u, e
