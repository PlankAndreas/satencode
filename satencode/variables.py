from itertools import product
from pysat.formula import IDPool


class VariableFamily:
    def __init__(self, mapping):
        self._mapping = mapping

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        return self._mapping[key]


class Variables:
    def __init__(self, pool=None):
        # Pass enc.pool to share variable IDs with an Encoder
        self._pool = pool if pool is not None else IDPool()

    def new(self, name, *domains):
        mapping = {}

        for index in product(*domains):
            mapping[index] = self._pool.id((name, *index))

        return VariableFamily(mapping)