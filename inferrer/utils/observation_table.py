import collections


class ObservationTable:

    def __init__(self, blue, red):
        self._blue = blue
        self._red = red
        self._ot = collections.defaultdict(dict)

    def get_observation_table(self):
        return self._ot

    def set_observation_table(self, ot):
        self._ot = ot

    def update(self, p, e, val):
        self._ot[p][e] = val

    def get(self, p, e):
        return self._ot[p][e]

    def exists(self, p, e):
        return p in self._ot and e in self._ot[p]

    def get_row(self, r):
        return self._ot[r]

    def row_exists(self, r):
        return r in self._ot

    def obviously_different_row(self, exp, max_len):
        for u in self._blue:

            for v in self._ot.keys():
                if u == v or len(u) == max_len or len(v) == max_len:
                    continue
                for e in exp:
                    if self.exists(u, e) and self.exists(v, e):
                        ue = self.get(u, e)
                        ve = self.get(v, e)

                        if ue is not None and ve is not None \
                                and ue != ve:
                            return True, u
        return False, None

    def is_closed(self):
        for u in self._blue:
            if not any([self._ot[u] == self._ot[s] for s in self._red]):
                return False, u

        return True, None

    def find_compatible_row(self, p, exp):
        for r in self._red:

            if p not in self._ot or r not in self._ot:
                continue

            p1 = self._ot[p]
            r1 = self._ot[r]

            if not any([
                (e in p1 and e in r1) and ((p1[e] == 0 and r1[e] == 1)
                    or (p1[e] == 1 and r1[e] == 0)) for e in exp
            ]):
                return r

        return None
