from pysat.solvers import Solver

from satencode.encoder import Encoder


def bits(value, n):
    return [(value >> i) & 1 for i in range(n)]

def test_equal_bits():

    for x in range(4):
        for y in range(4):

            enc = Encoder()

            xb = [enc.pool.id(("x", i)) for i in range(2)]
            yb = [enc.pool.id(("y", i)) for i in range(2)]

            eq = enc.equal_bits(xb, yb)

            assumptions = []

            for lit, bit in zip(xb, bits(x, 2)):
                assumptions.append(lit if bit else -lit)

            for lit, bit in zip(yb, bits(y, 2)):
                assumptions.append(lit if bit else -lit)

            assumptions.append(eq)

            with Solver(bootstrap_with=enc.cnf) as solver:
                assert solver.solve(assumptions=assumptions) == (x == y)

def test_not_equal_bits():

    for x in range(4):
        for y in range(4):

            enc = Encoder()

            xb = [enc.pool.id(("x", i)) for i in range(2)]
            yb = [enc.pool.id(("y", i)) for i in range(2)]

            neq = enc.not_equal_bits(xb, yb)

            assumptions = []

            for lit, bit in zip(xb, bits(x, 2)):
                assumptions.append(lit if bit else -lit)

            for lit, bit in zip(yb, bits(y, 2)):
                assumptions.append(lit if bit else -lit)

            assumptions.append(neq)

            with Solver(bootstrap_with=enc.cnf) as solver:
                assert solver.solve(assumptions=assumptions) == (x != y)

def test_less_than_bits():

    for x in range(4):
        for y in range(4):

            enc = Encoder()

            xb = [enc.pool.id(("x", i)) for i in range(2)]
            yb = [enc.pool.id(("y", i)) for i in range(2)]

            lt = enc.less_than_bits(xb, yb)

            assumptions = []

            for lit, bit in zip(xb, bits(x, 2)):
                assumptions.append(lit if bit else -lit)

            for lit, bit in zip(yb, bits(y, 2)):
                assumptions.append(lit if bit else -lit)

            assumptions.append(lt)

            with Solver(bootstrap_with=enc.cnf) as solver:
                assert solver.solve(assumptions=assumptions) == (x < y)

def test_greater_than_bits():

    for x in range(4):
        for y in range(4):

            enc = Encoder()

            xb = [enc.pool.id(("x", i)) for i in range(2)]
            yb = [enc.pool.id(("y", i)) for i in range(2)]

            gt = enc.greater_than_bits(xb, yb)

            assumptions = []

            for lit, bit in zip(xb, bits(x, 2)):
                assumptions.append(lit if bit else -lit)

            for lit, bit in zip(yb, bits(y, 2)):
                assumptions.append(lit if bit else -lit)

            assumptions.append(gt)

            with Solver(bootstrap_with=enc.cnf) as solver:
                assert solver.solve(assumptions=assumptions) == (x > y)