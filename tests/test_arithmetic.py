from pysat.solvers import Solver

from satencode.encoder import Encoder
from satencode.arithmetic.encodings import (
    half_adder,
    full_adder,
    ripple_carry_adder,
    binary_incrementer,
)


def test_half_adder():

    enc = Encoder()

    a = enc.pool.id("a")
    b = enc.pool.id("b")

    s, c = half_adder(enc, a, b)

    with Solver(bootstrap_with=enc.cnf) as solver:

        # 1 + 1 = 10
        assert solver.solve(assumptions=[a, b, s]) is False
        assert solver.solve(assumptions=[a, b, c]) is True

        # 1 + 0 = 01
        assert solver.solve(assumptions=[a, -b, s]) is True
        assert solver.solve(assumptions=[a, -b, c]) is False

        # 0 + 1 = 01
        assert solver.solve(assumptions=[-a, b, s]) is True 
        assert solver.solve(assumptions=[-a, b, c]) is False

        # 0 + 0 = 00
        assert solver.solve(assumptions=[-a, -b, s]) is False  
        assert solver.solve(assumptions=[-a, -b, -c]) is True



def test_full_adder():

    enc = Encoder()

    a = enc.pool.id("a")
    b = enc.pool.id("b")
    cin = enc.pool.id("cin")

    s, cout = full_adder(enc, a, b, cin)

    with Solver(bootstrap_with=enc.cnf) as solver:

        # 1+1+0 = 10
        assert solver.solve(assumptions=[a, b, -cin, -s, cout])

        # 1+1+1 = 11
        assert solver.solve(assumptions=[a, b, cin, s, cout])

        # 1+0+0 = 01
        assert solver.solve(assumptions=[a, -b, -cin, s, -cout])

        # 0+0+0 = 00
        assert solver.solve(assumptions=[-a, -b, -cin, -s, -cout])


def test_ripple_carry_adder():

    enc = Encoder()

    a = [enc.pool.id(("a", i)) for i in range(2)]
    b = [enc.pool.id(("b", i)) for i in range(2)]

    s, carry = ripple_carry_adder(enc, a, b)

    with Solver(bootstrap_with=enc.cnf) as solver:

        # 01 + 01 = 10
        assumptions = [
            a[0], -a[1],
            b[0], -b[1],

            -s[0],
            s[1],
            -carry
        ]

        assert solver.solve(assumptions=assumptions)

def test_binary_incrementer():

    enc = Encoder()

    bits = [enc.pool.id(("x", i)) for i in range(3)]

    out, carry = binary_incrementer(enc, bits)

    with Solver(bootstrap_with=enc.cnf) as solver:

        # 001 -> 010
        assumptions = [
            bits[0],
            -bits[1],
            -bits[2],

            -out[0],
            out[1],
            -out[2],
            -carry
        ]

        assert solver.solve(assumptions=assumptions)