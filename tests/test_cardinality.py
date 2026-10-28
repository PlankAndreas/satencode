from pysat.solvers import Solver

from satencode.encoder import Encoder
from satencode.cardinality.encodings import exactly_one


def test_exactly_one():

    enc = Encoder()

    x = [
        enc.pool.id(("x", i))
        for i in range(5)
    ]

    exactly_one(enc, x)

    with Solver(name="cadical195", bootstrap_with=enc.cnf) as solver:

        assert solver.solve()

        model = solver.get_model()

        print("Model:", model)

        true_vars = [
            v
            for v in x
            if v in model
        ]

        assert len(true_vars) == 1